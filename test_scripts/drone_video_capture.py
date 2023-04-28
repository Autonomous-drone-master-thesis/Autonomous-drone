import time
import cv2
from threading import Thread
from djitellopy import Tello


class Drone:
    def __init__(self):
        self.tello = Tello()
        self.recording = False
        self.video = None
        self.recorder_thread = None
        self.tello.connect()
        self.tello.streamon()

    def run(self):
        while True:
            frame = self.tello.get_frame_read().frame

            cv2.imshow("Tello", frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                self.stop_recording()
                self.tello.streamoff()
                break
    
    def start_recording(self):
        print('starting recording')
        height, width, _ = self.tello.get_frame_read().frame.shape
        self.video = cv2.VideoWriter('test_video.avi', cv2.VideoWriter_fourcc(*"XVID"), 30, (width, height))
        self.recording = True
        print('starting threads')
        self.recorder_thread = Thread(target=self._keep_recording)
        self.recorder_thread.start()
        print('Threads started')
    
    def _keep_recording(self) -> None:
        while self.recording:
            self.video.write(self.tello.get_frame_read().frame)
            time.sleep(1 / 30)
        self.video.release()
    
    def stop_recording(self) -> None:
        self.recording = False
        self.recorder_thread.join()

if __name__ == "__main__":
    drone = Drone()
    drone.start_recording()
    drone.run()
