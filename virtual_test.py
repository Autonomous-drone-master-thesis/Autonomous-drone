import cv2
import numpy as np
import os

from handlers import TelloHandler
from detectors import ObjectDetector
from trackers import HumanCircler


class VirtualTelloHandler(TelloHandler):
    def __init__(self, video_file):
        self.cap = cv2.VideoCapture(video_file)
        self.frame = None
        self.update_frame()

    def update_frame(self):
        ret, self.frame = self.cap.read()

    def send_rc_control(self, lr_velocity, fb_velocity, ud_velocity, yaw_velocity):
        print(f"LR: {lr_velocity}, FB: {fb_velocity}, UD: {ud_velocity}, YAW: {yaw_velocity}")

    def get_frame(self):
        return self.frame


os.environ["HTTP_PROXY"] = "http://10.246.170.130:3128"
os.environ["HTTPS_PROXY"] = "http://10.246.170.130:3128"


def main():
    video_file = "video.mp4"
    model_file = "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"

    # Initialize virtual drone handler
    drone = VirtualTelloHandler(video_file)
    detector = ObjectDetector(model_file, 0.5, True)
    tracker = HumanCircler(drone)

    previous_error_x = 0
    previous_error_y = 0

    while drone.cap.isOpened():
        frame = drone.get_frame()
        if frame is None:
            break

        img, center, bbox_height = detector.predict(frame)

        previous_error_x, previous_error_y = tracker.track(bbox_height, (previous_error_x, previous_error_y))
        cv2.imshow("Face detection", img)
        drone.update_frame()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    drone.cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
