import logging

from detectors import ObjectDetector

logging.basicConfig(level=logging.INFO)

model_path = (
    "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
)

video_path = 0
#video_path = "video.mp4"

threshold = 0.5

detector = ObjectDetector(model_path, threshold, True)
detector.predict_video(video_path)