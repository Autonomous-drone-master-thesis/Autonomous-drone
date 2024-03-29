from detectors import FaceDetector

# 0 for computer camera, or path to video file
video_path = 0
#video_path = "video1.mp4"

threshold = 0.5

detector = FaceDetector(threshold)

# Video prediction
detector.predict_video(video_path)