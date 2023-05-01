"""Module for performing face detection using the Mediapipe library."""

from typing import Tuple

import cv2
import mediapipe as mp
import numpy as np

from .base_detector import BaseDetector


class FaceDetector(BaseDetector):
    """Class for performing face detection using the Mediapipe library."""

    def predict(self, img: np.ndarray) -> Tuple[bool, np.ndarray, Tuple[int, int], float]:
        """
        Perform object detection on the input image and return the resulting
        :param img: the input image to perform object detection on
        :return: a boolean value indicating whether a face was detected,
        the resulting image with the bounding boxes added,
        the center of the bounding box, and the area of the bounding box
        """
        img.flags.writeable = False # Set the image to read-only mode to improve performance

        results = self._model_process(self._preprocess_image(img))

        img.flags.writeable = True # Set the image back to writeable mode

        detected, img, center, area = self._visualize_bounding_box(img, results)
        return detected, img, center, area

    def _load_model(self) -> None:
        """
        Load the face detection model from the Mediapipe library and initialize the drawing utility.
        """
        self.logger.info("Loading face detection model")
        self.model = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=self.threshold
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
        img = cv2.resize(img, (640, 480))
        return img

    def _visualize_bounding_box(
        self, img: np.ndarray, detections: mp.solutions.face_detection.FaceDetection
    ) -> Tuple[bool, np.ndarray, Tuple[int, int], float]:
        """
        Visualize the bounding boxes around the detected faces.
        :param img: the input image with the detected faces
        :param results: the face detection results
        :return: a boolean value indicating whether a face was detected,
        the resulting image with the bounding boxes added,
        the center of the bounding box, and the area of the bounding box
        """
        face_centers = []
        face_areas = []
        detected = False
        if detections.detections:
            detected = True
            for detection in detections.detections:
                middle, area, x, y = self._get_box_coordinates(img, detection)
                face_centers.append(middle)
                face_areas.append(area)
                self._draw_bounding_boxes(img, detection, x, y)
            closest_face_index = face_areas.index(max(face_areas))
            return detected, img, face_centers[closest_face_index], face_areas[closest_face_index]
        return detected, img, (0, 0), 0.0

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
        self.mp_drawing.draw_detection(img, detection) # Draw the bounding box around the face

        # Draw a small circle at the middle of the bounding box
        cv2.circle(img, (int(x * img.shape[1]), int(y * img.shape[0])), 5, (0, 255, 0), -1)

        # Draw the confidence score as text above the bounding box
        height, width, _ = img.shape
        bbox = detection.location_data.relative_bounding_box
        xmin, ymin = int(bbox.xmin * width), int(bbox.ymin * height)
        confidence = round(detection.score[0] * 100, 2)
        text = f"{confidence}%"
        cv2.putText(img, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
