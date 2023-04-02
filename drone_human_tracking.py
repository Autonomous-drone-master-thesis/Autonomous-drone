import cv2

from detectors import ObjectDetector
from handlers import TelloHandler
from trackers import HumanTracker


def main():
    drone = TelloHandler()
    drone.connect_and_initiate()

    detector = ObjectDetector(model_url="https://path/to/your/model", human=True)

    tracker = HumanTracker(drone)

    previous_error_x = 0
    previous_error_y = 0

    drone.takeoff_and_hover()
    try:
        while True:
            frame = drone.get_frame_read().frame

            img, center, bbox_height = detector.predict(frame)

            previous_error_x, previous_error_y = tracker.track(bbox_height, center, (previous_error_x, previous_error_y))

            cv2.imshow("Image", img)
            if cv2.waitKey(1) and 0xFF == ord("q"):
                break
    except:
        print('error')
    finally:
        drone.disconnect()


if __name__ == "__main__":
    main()