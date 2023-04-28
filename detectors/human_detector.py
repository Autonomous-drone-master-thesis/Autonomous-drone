"""Module for performing human detection."""

from typing import Dict, Tuple

import cv2
import numpy as np
import tensorflow as tf

from .base_detector import BaseDetector


class HumanDetector(BaseDetector):
    """Class for performing object detection on videos."""

    def __init__(
        self,
        model_path: str,
        model_height: int,
        model_width: int,
        threshold: float = 0.5) -> None:
        """
        Initialize the HumanDetector object with the given threshold.
        :param model_path: the path to the model to use for object detection
        :param model_height: the height of the input image for the model
        :param model_width: the width of the input image for the model
        :param threshold: the minimum confidence score for a detected object to be considered valid
        """
        self.model_path = model_path
        self.classes_list = self._read_classes()
        self.model_height = model_height
        self.model_width = model_width
        super().__init__(threshold)

    def predict(self, img: np.ndarray) -> Tuple[bool, np.ndarray, Tuple[int, int], float]:
        """
        Perform object detection on the input image and return the resulting
        :param img: the input image to perform object detection on
        :return: a boolean value indicating whether a human was detected,
        the resulting image with the bounding boxes added,
        the center of the bounding box, and the height of the bounding box
        """
        img.flags.writeable = False # Set the image to read-only mode to improve performance

        results = self._model_process(self._preprocess_image(img))

        img.flags.writeable = True # Set the image back to writeable mode

        detected, img, center, bbox_height = self._visualize_bounding_box(img, results)
        return detected, img, center, bbox_height

    def _read_classes(self) -> list[str]:
        """
        Read the object classes from the COCO dataset
        :return: list of object classes
        """
        path = "utils/coco.names"
        with open(path, "rt", encoding="utf-8") as file:
            classes_list = file.read().rstrip("\n").split("\n")

        return classes_list

    def _load_model(self) -> None:
        """
        Load the object detection model from the checkpoint directory.
        """
        self.logger.info("Loading model")
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(self.model_path)
        self.logger.info("Model loaded")

    def _model_process(self, img: np.ndarray):
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
        input_tensor = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        input_tensor = cv2.resize(input_tensor, (self.model_height, self.model_width))

        input_tensor = tf.convert_to_tensor(input_tensor, dtype=tf.uint8)
        input_tensor = input_tensor[tf.newaxis, ...]
        return input_tensor

    def _visualize_bounding_box(self, img: np.ndarray, detections: Dict[str, tf.Tensor]) -> np.ndarray:
        """
        Visualize the bounding boxes around the detected objects.
        :param img: the input image with the detected objects
        :param detections: the object detection results
        :return: the image with the bounding boxes added
        """
        bbox_idx, bboxs, class_indexes, class_scores = self._get_bounding_boxes(detections)

        height, width, _ = img.shape

        person_index = self.classes_list.index("person")
        human_boxes = False
        if tf.size(bbox_idx) > 0:
            human_boxes = [(box, class_scores[box]) for box in bbox_idx if class_indexes[box] == person_index]

        human_found = bool(human_boxes)

        img, center, bbox_height = self._draw_bounding_boxes(
            img, human_boxes, bboxs, height, width
        )

        return human_found, img, center, bbox_height

    def _get_bounding_boxes(self, detections: dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
        human_boxes: list,
        bboxs: np.ndarray,
        height: int,
        width: int,
    ) -> Tuple[np.ndarray, Tuple[int, int], float]:
        """
        Draw the bounding boxes around the detected objects
        and add the class names and confidence scores as text.
        :param img: the input image with the detected objects
        :param human_boxes: the human bounding box indices and their confidence scores
        :param bboxs: the bounding boxes themselves
        :param height: the height of the input image
        :param width: the width of the input image
        :return: the image with the bounding boxes and class names added
        """
        center = (0, 0)
        bbox_height = 0

        if human_boxes:
            most_confident_human_box, confidence = max(human_boxes, key=lambda x: x[1])

            bbox = tuple(bboxs[most_confident_human_box].tolist())

            label = f"person {confidence * 100:.2f}%".upper()
            color = (0, 255, 0)

            ymin, xmin, ymax, xmax = bbox

            ymin, xmin, ymax, xmax = (
                int(ymin * height),
                int(xmin * width),
                int(ymax * height),
                int(xmax * width),
            )

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(img, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            center = (int((xmin + xmax) / 2), int((ymin + ymax) / 2))
            bbox_height = ymax - ymin

        return img, center, bbox_height
