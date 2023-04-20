"""Module for performing object detection."""

import os
from typing import Dict, Tuple, Any

try:
    import cv2
    import numpy as np
    import tensorflow as tf
    from tensorflow.python.keras.utils.data_utils import get_file
except ImportError:
    cv2 = None
    np = None
    tf = None
    get_file = None

from .base_detector import BaseDetector


class ObjectDetector(BaseDetector):
    """Class for performing object detection on videos."""

    def __init__(self, model_url: str, threshold: float = 0.5) -> None:
        """
        Initialize the ObjectDetector object with the given threshold.
        :param threshold: the minimum confidence score for a detected object to be considered valid
        """
        super().__init__(threshold)
        self.classes_list, self.color_list = self._read_classes()
        self._download_model(model_url)
        self._load_model()
    
    def predict(self, img: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int], float]:
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

        img, center, bbox_height = self._visualize_bounding_box(img, results)
        return img, center, bbox_height

    def _read_classes(self) -> Tuple[list[str], np.ndarray[Any, np.dtype[np.float64]]]:
        """
        Read the object classes from the COCO dataset and initialize the color list.
        :return: a tuple with the list of object classes and the color list
        """
        path = "utils/coco.names"
        with open(path, "rt", encoding="utf-8") as file:
            classes_list = file.read().rstrip("\n").split("\n")

        color_list = np.random.uniform(low=0, high=255, size=(len(classes_list), 3))

        return classes_list, color_list

    def _download_model(self, model_url: str) -> None:
        """
        Download the object detection model from the given URL.
        :param model_url: the URL of the object detection model
        """
        self.logger.info("Downloading model")
        file_name = os.path.basename(model_url)
        self.model_name = file_name[: file_name.index(".")]

        self.cache_dir = "./models/"
        os.makedirs(self.cache_dir, exist_ok=True)
        get_file(
            fname=file_name,
            origin=model_url,
            cache_dir=self.cache_dir,
            cache_subdir="checkpoints",
            extract=True,
        )
        self.logger.info("Model downloaded")

    def _load_model(self) -> None:
        """
        Load the object detection model from the checkpoint directory.
        """
        self.logger.info("Loading model")
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(
            os.path.join(self.cache_dir, "checkpoints", self.model_name, "saved_model")
        )
        self.logger.info("Model loaded")

    def _model_process(self, img):
        """
        Perform object detection on the input image using the loaded model.
        :param img: the preprocessed input image
        :return: the object detection results
        """
        return self.model(img)

    def _preprocess_image(self, img: np.ndarray) -> tf.Tensor:
        """
        Preprocess the input image by converting it
        to a tensor in the correct format for the model.
        :param img: the input image to be preprocessed
        :return: the preprocessed image tensor
        """
        img.flags.writeable = False
        input_tensor = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(input_tensor, dtype=tf.uint8)
        input_tensor = input_tensor[tf.newaxis, ...]
        return input_tensor

    def _visualize_bounding_box(
        self, img: np.ndarray, detections: Dict[str, tf.Tensor]
    ) -> np.ndarray:
        """
        Visualize the bounding boxes around the detected objects.
        :param img: the input image with the detected objects
        :param detections: the object detection results
        :return: the image with the bounding boxes added
        """
        bbox_idx, bboxs, class_indexes, class_scores = self._get_bounding_boxes(detections)

        height, width, _ = img.shape

        img, center, bbox_height = self._draw_bounding_boxes(
            img, bbox_idx, bboxs, class_indexes, class_scores, height, width
        )

        return img, center, bbox_height

    def _get_bounding_boxes(
        self, detections: dict
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract the bounding boxes, class indexes,
        and class scores from the object detection results.
        :param detections: the object detection results
        :return: a tuple with the indices of the selected bounding boxes,
                 the bounding boxes themselves,
                 the class indexes, and the class scores
        """
        bboxs = detections["detection_boxes"][0].numpy()
        class_indexes = detections["detection_classes"][0].numpy().astype(np.int32)
        class_scores = detections["detection_scores"][0].numpy()

        bbox_idx = tf.image.non_max_suppression(
            bboxs,
            class_scores,
            max_output_size=30,
            iou_threshold=self.threshold,
            score_threshold=self.threshold,
        )

        return bbox_idx, bboxs, class_indexes, class_scores

    # pylint: disable=R0913, R0914
    def _draw_bounding_boxes(
        self,
        img: np.ndarray,
        bbox_idx,
        bboxs: np.ndarray,
        class_indexes: np.ndarray,
        class_scores: np.ndarray,
        height: int,
        width: int,
    ) -> Tuple[np.ndarray, Tuple[int, int], float]:
        """
        Draw the bounding boxes around the detected objects
        and add the class names and confidence scores as text.
        :param img: the input image with the detected objects
        :param bbox_idx: the indices of the selected bounding boxes
        :param bboxs: the bounding boxes themselves
        :param class_indexes: the class indexes
        :param class_scores: the class scores
        :param height: the height of the input image
        :param width: the width of the input image
        :return: the image with the bounding boxes and class names added
        """
        center = (0, 0)
        bbox_height = 0
        person_index = self.classes_list.index("person")

        if tf.size(bbox_idx) > 0:
            human_boxes = [(box, class_scores[box]) for box in bbox_idx if class_indexes[box] == person_index]

            if human_boxes:
                most_confident_human_box, confidence = max(human_boxes, key=lambda x: x[1])

                bbox = tuple(bboxs[most_confident_human_box].tolist())

                label = f"person {confidence * 100:.2f}%".upper()
                color = self.color_list[person_index]

                ymin, xmin, ymax, xmax = bbox

                ymin, xmin, ymax, xmax = (
                    int(ymin * height),
                    int(xmin * width),
                    int(ymax * height),
                    int(xmax * width),
                )

                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
                cv2.putText(
                    img, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )

                center = (int((xmin + xmax) / 2), int((ymin + ymax) / 2))
                bbox_height = ymax - ymin

        return img, center, bbox_height
