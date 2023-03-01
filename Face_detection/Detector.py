import cv2
import time
import mediapipe as mp
from typing import Union


class Detector:
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def load_model(self):
        self.model = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=self.threshold
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def predict_video(self, video: Union[int, str]) -> None:
        cap = cv2.VideoCapture(video)
        if not cap.isOpened():
            print("Cannot open camera")
            return

        success, image = cap.read()

        start_time = 0

        while success:
            current_time = time.time()

            fps = 1 / (current_time - start_time)
            start_time = current_time

            image = self._predict(image)
            cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Face detection", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            success, image = cap.read()

        cv2.destroyAllWindows()

    def _predict(self, img):
        img = self._preprocess_image(img)
        results = self.model.process(img)
        img, middle, area = self._visualize_bounding_box(img, results)
        return img

    def _preprocess_image(self, img):
        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    
    def _visualize_bounding_box(self, img, results):
        if results.detections:
            detection = results.detections[0]
            middle, area, x , y = self._get_box_coordinates(img, detection)
            self._draw_bounding_boxes(img, detection, x, y)
            return img, middle, area
        return img, (0, 0), 0
                
    def _draw_bounding_boxes(self, img, detection, x, y):
        self.mp_drawing.draw_detection(img, detection)
        cv2.circle(img, (int(x * img.shape[1]), int(y * img.shape[0])), 5, (0, 255, 0), -1)
        
    def _get_box_coordinates(self, img, detection):
        bounding_box = detection.location_data.relative_bounding_box
        width = bounding_box.width
        height = bounding_box.height
        x = bounding_box.xmin + (width / 2)
        y = bounding_box.ymin + (height / 2)
        middle = (int(x * img.shape[1]), int(y * img.shape[0]))
        area = width * height
        return middle, area, x, y
    
        
