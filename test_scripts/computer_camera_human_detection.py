from detectors import HumanDetector

model_path = (
    "./models/checkpoints/ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model"
)

#video_path = 0
video_path = "video.mp4"

detector = HumanDetector(model_path, 320, 320)
detector.predict_video(video_path)
