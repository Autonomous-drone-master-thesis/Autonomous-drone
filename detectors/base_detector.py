"""Module containing the BaseDetector class."""

import abc
import logging
import time
from typing import Union, Any, Tuple

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


class BaseDetector(abc.ABC):
    """Base class for all detection models."""

    def __init__(self, threshold: float = 0.5) -> None:
        """
        Initialize the BaseDetector object with the given threshold.
        :param threshold: the minimum confidence score for a detected object to be considered valid
        """
        self.threshold: float = threshold
        self.logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def _load_model(self) -> None:
        """
        Abstract method for loading the object detection model.
        """

    @abc.abstractmethod
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Abstract method for preprocessing the input image.
        :param img: the input image to be preprocessed
        :return: the preprocessed image
        """

    @abc.abstractmethod
    def _visualize_bounding_box(self, img: np.ndarray, detections: Any) -> np.ndarray:
        """
        Abstract method for visualizing the bounding boxes around the detected objects.
        :param img: the input image with the detected objects
        :param detections: the object detection results
        :return: the image with the bounding boxes added
        """

    @abc.abstractmethod
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

            # Calculate the FPS of the video
            fps = 1 / (current_time - start_time)
            start_time = current_time

            img, middle, area = self._predict(img)
            print(middle, area)

            # Add the FPS to the image and display it
            cv2.putText(
                img, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
            )
            cv2.imshow("Face detection", img)

            # Wait for the "q" key to be pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            success, img = cap.read()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

    def _initiate_video_writer(self, video: Union[int, str]) -> cv2.VideoCapture:
        """
        Open a video file or camera stream using the OpenCV library
        and return the VideoCapture instance.
        :param video: the path to the video file or the index of the camera device
        :return: the VideoCapture instance
        """
        self.logger.info("Initiating a video")
        cap = cv2.VideoCapture(video)
        if not cap.isOpened():
            self.logger.error("Cannot open camera")
            raise ValueError("Cannot open camera")

        return cap

    def _predict(self, img: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int], float]:
        """
        Perform object detection on the input image and return the resulting
        :param img: the input image to perform object detection on
        :return: the resulting image with the bounding boxes added
        """
        # Set the image to read-only mode to improve performance
        img.flags.writeable = False

        results = self._model_process(self._preprocess_image(img))

        # Set the image back to writeable mode
        img.flags.writeable = True

        img, middle, area = self._visualize_bounding_box(img, results)
        return img, middle, area
