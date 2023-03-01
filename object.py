from Object_detection.Detector import Detector

model_path = (
    "http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz"
)

class_file = "utils\coco.names"
video_path = 0
threshold = 0.5

detector = Detector()
detector.read_classes(class_file)
detector.download_model(model_path)
detector.load_model()
detector.predict_video(video_path, threshold)