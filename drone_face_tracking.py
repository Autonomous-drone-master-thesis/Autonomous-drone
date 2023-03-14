import cv2

from detectors import FaceDetector
from handlers import TelloHandler
from trackers import FaceTracker


def main():
    drone = TelloHandler()
    drone.connect_and_initiate()

    detector = FaceDetector()

    tracker = FaceTracker(drone)

    previous_error = 0

    drone.takeoff_and_hover()

    while True:
        frame = drone.get_frame_read().frame

        img, middle, area = detector.predict(frame)
        previous_error = tracker.track(area, middle, previous_error)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) and 0xFF == ord("q"):
            break

    drone.disconnect()

main()