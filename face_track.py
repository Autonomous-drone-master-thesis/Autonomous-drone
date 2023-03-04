import cv2
import numpy as np
from djitellopy import Tello

from Detectors import FaceDetector


class TelloHandler(Tello):
    def connect_and_initiate(self) -> None:
        self.connect()
        if self.stream_on:
            self.streamoff()
        self.streamon()
        self.takeoff()
        self.send_rc_control(0, 0, 25, 0)

    def disconnect(self) -> None:
        self.land()

    @property
    def battery(self) -> int:
        return self.get_battery()


class FaceTracker:
    def __init__(self, drone: TelloHandler) -> None:
        self.drone = drone
        self.area_range = [0.03, 0.05]
        self.pid = [0.3, 0.3, 0]
        self.width = 360
        self.height = 240
    
    def track(self, area, center, previous_error):
        x, y = center
        forward_backward = 0
        current_error = x - self.width // 2
        speed = self.pid[0] * current_error + self.pid[1] * (current_error - previous_error)
        speed = int(np.clip(speed, -100, 100))
        if area > self.area_range[1]:
            forward_backward = -10
            print("Too close")
        elif area < self.area_range[0] and area != 0:
            forward_backward = 10
            print("Too far")
        self.drone.send_rc_control(0, forward_backward, 0, speed)

        return current_error

def main():
    drone = TelloHandler()
    drone.connect_and_initiate()
    
    detector = FaceDetector()
    
    tracker = FaceTracker(drone)
    
    previous_error = 0
    
    while True:
        frame = drone.get_frame_read().frame
        img = cv2.resize(frame, (360, 240))
        
        img, middle, area = detector._predict(img)
        previous_error = tracker.track(area, middle, previous_error)
        
        cv2.imshow("Image", img)
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break
    
    drone.disconnect()
        