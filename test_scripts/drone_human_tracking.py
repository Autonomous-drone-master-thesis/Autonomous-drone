import cv2

from detectors import ObjectDetector
from handlers import TelloHandler
from trackers import HumanTracker

model_path = (
    "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
)

def main():
    drone = TelloHandler()
    drone.connect_and_initiate()

    detector = ObjectDetector(model_url=model_path)

    tracker = HumanTracker(drone)

    previous_error_x = 0
    previous_error_y = 0
    previous_error_z = 0

    drone.takeoff_and_hover()
    while True:
        frame = drone.get_frame_read().frame

        img, center, bbox_height = detector.predict(frame)

        previous_error_x, previous_error_y, previous_error_z = tracker.track(bbox_height, center, (previous_error_x, previous_error_y, previous_error_z))

        cv2.imshow("Image", img)
        if cv2.waitKey(1) and 0xFF == ord("q"):
            drone.disconnect()
            break


if __name__ == "__main__":
    main()