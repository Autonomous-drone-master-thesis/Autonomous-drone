import logging

from detectors import FaceDetector

logging.basicConfig(level=logging.INFO)
video_path = 0
#video_path = "video1.mp4"

threshold = 0.5

detector = FaceDetector(threshold)
detector.load_model()

# Video prediction
detector.predict_video(video_path)