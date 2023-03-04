import cv2

from detectors import FaceDetector
from hanlders import TelloHandler
from trackers import FaceTracker


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
        if cv2.waitKey(1) and 0xFF == ord("q"):
            break

    drone.disconnect()
