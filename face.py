from Face_detection.Detector import Detector

video_path = 0
threshold = 0.5

detector = Detector(threshold)
detector.load_model()

# Video prediction
detector.predict_video(0)