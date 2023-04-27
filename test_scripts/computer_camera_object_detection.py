import logging

from detectors import HumanDetector

logging.basicConfig(level=logging.INFO)

model_path = (
    "./models/checkpoints/centernet_resnet101_v1_fpn_512x512_coco17_tpu-8/saved_model"
)

video_path = 0
#video_path = "1682006597205.mp4"

threshold = 0.5

detector = HumanDetector(model_path, threshold)
detector.predict_video(video_path)
