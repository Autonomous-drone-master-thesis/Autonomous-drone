"""Module containing the BaseDetector class."""

from abc import ABC, abstractmethod
import logging
import time
from typing import Any, Tuple, Union

import cv2
import numpy as np


class BaseDetector(ABC):
    """Base class for all detection models."""

    def __init__(self, threshold: float = 0.5) -> None:
        """
        Initialize the BaseDetector object with the given threshold.
        :param threshold: the minimum confidence score for a detected object to be considered valid
        """
        self.threshold: float = threshold
        self.model = None

        self.logger = logging.getLogger(__name__)
        self._load_model()

    @abstractmethod
    def predict(self, img: np.ndarray) -> Tuple[bool, np.ndarray, Tuple[int, int], float]:
        """
        Perform object detection on the input image.
        :param img: the input image to perform object detection on
        :return: a boolean value indicating whether a target object was detected,
        the resulting image with the bounding boxes added,
        the center of the bounding box, and the metric (area or height) of the bounding box
        """

    @abstractmethod
    def _load_model(self) -> None:
        """
        Abstract method for loading the object detection model.
        """

    @abstractmethod
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Abstract method for preprocessing the input image.
        :param img: the input image to be preprocessed
        :return: the preprocessed image
        """

    @abstractmethod
    def _visualize_bounding_box(self, img: np.ndarray, detections: Any) -> np.ndarray:
        """
        Abstract method for visualizing the bounding boxes around the detected objects.
        :param img: the input image with the detected objects
        :param detections: the object detection results
        :return: the image with the bounding boxes added
        """

    @abstractmethod
    def _model_process(self, img: np.ndarray) -> Any:
        """
        Abstract method for performing the object detection.
        :param img: the preprocessed input image
        :return: the object detection results
        """

    def predict_video(self, video: Union[int, str]) -> None:
        """
        Perform object detection on a video file or camera stream.
        :param video: the path to the video file or the index of the camera device
        """
        cap = self._initiate_video_writer(video)
        self.logger.info("Video initiated.")

        success, img = cap.read()
        start_time = 0

        while success:
            current_time = time.time()


            fps = 1 / (current_time - start_time)
            start_time = current_time

            _, img, _, _ = self.predict(img)

            cv2.putText(
                img, f"FPS: {fps:.2f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
                )
            cv2.imshow("Detector", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            success, img = cap.read()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

    def _initiate_video_writer(self, video_path: Union[int, str]) -> cv2.VideoCapture:
        """
        Open a video file or camera stream using the OpenCV library
        and return the VideoCapture instance.
        :param video_path: the path to the video file or the index of the camera device
        :return: the VideoCapture instance
        """
        self.logger.info("Initiating a video")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error("Cannot open camera")
            raise ValueError("Cannot open camera")

        return cap
