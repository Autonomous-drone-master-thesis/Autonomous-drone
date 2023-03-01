import logging

from Detectors import ObjectDetector

logging.basicConfig(level=logging.INFO)

model_path = (
    "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
)

video_path = 0
video_path = "video.mp4"

threshold = 0.5

detector = ObjectDetector(threshold)
detector.download_model(model_path)
detector.load_model()
detector.predict_video(video_path)