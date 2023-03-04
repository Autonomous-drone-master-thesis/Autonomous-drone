"""Module for performing face detection using the Mediapipe library."""

from typing import Tuple

try:
    import cv2
    import mediapipe as mp
    import numpy as np
except ImportError:
    cv2 = None
    mediapipe = None
    numpy = None

from .base_detector import BaseDetector


class FaceDetector(BaseDetector):
    """Class for performing face detection using the Mediapipe library."""

    def __init__(self, threshold: float = 0.5):
        """
        Initialize the FaceDetector object with the given threshold.
        :param threshold: the minimum confidence score for a detected face to be considered valid
        """
        super().__init__(threshold)
        self._load_model()

    def _load_model(self) -> None:
        """
        Load the face detection model from the Mediapipe library and initialize the drawing utility.
        """
        self.logger.info("Loading face detection model")
        self.model = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=self.threshold
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.logger.info("Face detection model loaded")

    def _model_process(self, img: np.ndarray) -> mp.solutions.face_detection.FaceDetection:
        """
        Perform face detection on the input image using the loaded model.
        :param img: the preprocessed input image
        :return: the face detection results
        """
        return self.model.process(img)

    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess the input image by converting it from BGR to RGB format.
        :param img: the input image to be preprocessed
        :return: the preprocessed image
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def _visualize_bounding_box(
        self, img: np.ndarray, detections: mp.solutions.face_detection.FaceDetection
    ) -> Tuple[np.ndarray, Tuple[int, int], float]:
        """
        Visualize the bounding boxes around the detected faces.
        :param img: the input image with the detected faces
        :param results: the face detection results
        :return: the image with the bounding boxes added
        """
        face_centers = []
        face_areas = []
        if detections.detections:
            for detection in detections.detections:
                middle, area, x, y = self._get_box_coordinates(img, detection)
                face_centers.append(middle)
                face_areas.append(area)
                self._draw_bounding_boxes(img, detection, x, y)
            closest_face_index = face_areas.index(max(face_areas))
            return img, face_centers[closest_face_index], face_areas[closest_face_index]
        return img, (0, 0), 0.0

    def _get_box_coordinates(
        self, img: np.ndarray, detection: mp.solutions.face_detection.FaceDetection
    ) -> Tuple[Tuple[int, int], float, float, float]:
        """
        Calculate the middle point, area, and relative position of the bounding box
        for a detected face.
        :param img: the input image with the detected face
        :param detection: the face detection results for the current image
        :return: a tuple with the middle point, area, and relative position of the bounding box
        """
        bounding_box = detection.location_data.relative_bounding_box
        width = bounding_box.width
        height = bounding_box.height
        x = bounding_box.xmin + (width / 2)
        y = bounding_box.ymin + (height / 2)
        middle = (int(x * img.shape[1]), int(y * img.shape[0]))
        area = width * height
        return middle, area, x, y

    def _draw_bounding_boxes(
        self,
        img: np.ndarray,
        detection: mp.solutions.face_detection.FaceDetection,
        x: float,
        y: float,
    ) -> None:
        """
        Draw the bounding box and confidence score on the input image for a detected face.
        :param img: the input image with the detected face
        :param detection: the face detection results for the current image
        :param x: the relative position of the bounding box on the x-axis
        :param y: the relative position of the bounding box on the y-axis
        """
        # Draw the bounding box around the face
        self.mp_drawing.draw_detection(img, detection)

        # Draw a small circle at the middle of the bounding box
        cv2.circle(img, (int(x * img.shape[1]), int(y * img.shape[0])), 5, (0, 255, 0), -1)

        # Draw the confidence score as text above the bounding box
        height, width, _ = img.shape
        bbox = detection.location_data.relative_bounding_box
        xmin, ymin = int(bbox.xmin * width), int(bbox.ymin * height)
        confidence = round(detection.score[0] * 100, 2)
        text = f"{confidence}%"
        cv2.putText(img, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
