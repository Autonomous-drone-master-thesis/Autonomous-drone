import cv2

from detectors import HumanDetector
from handlers import TelloHandler
from trackers import HumanTracker

model_path = (
    "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
)

def main():
    drone = TelloHandler()
    drone.initiate_video_stream()

    detector = HumanDetector(model_path, 320, 320)

    tracker = HumanTracker(drone, 300, 300, 180)

    previous_error_x = 0
    previous_error_y = 0
    previous_error_z = 0

    drone.takeoff_and_hover()
    while True:
        frame = drone.get_frame_read().frame

        _, img, center, bbox_height = detector.predict(frame)

        previous_error_x, previous_error_y, previous_error_z = tracker.track(center, (previous_error_x, previous_error_y, previous_error_z), bbox_height, True)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) and 0xFF == ord("q"):
            drone.disconnect()
            break


if __name__ == "__main__":
    main()