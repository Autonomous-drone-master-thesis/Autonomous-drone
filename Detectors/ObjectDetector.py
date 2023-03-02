import os
from typing import Dict, Tuple, Any

from .BaseDetector import BaseDetector

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.utils.data_utils import get_file


class ObjectDetector(BaseDetector):
    def __init__(self, threshold: float = 0.5, human: bool = False) -> None:
        """
        Initialize the ObjectDetector object with the given threshold.
        :param threshold: the minimum confidence score for a detected object to be considered valid
        :param human: whether to detect only humans or not
        """
        super().__init__(threshold)
        self.human = human
        self.classes_list, self.color_list = self._read_classes()

    def download_model(self, model_url: str) -> None:
        """
        Download the object detection model from the given URL.
        :param model_url: the URL of the object detection model
        """
        self.logger.info("Downloading model")
        file_name = os.path.basename(model_url)
        self.model_name = file_name[: file_name.index(".")]

        self.cache_dir = "./models/"
        os.makedirs(self.cache_dir, exist_ok=True)
        get_file(fname=file_name, origin=model_url, cache_dir=self.cache_dir, cache_subdir="checkpoints", extract=True)
        self.logger.info("Model downloaded")

    def load_model(self) -> None:
        """
        Load the object detection model from the checkpoint directory.
        """
        self.logger.info("Loading model")
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cache_dir, "checkpoints", self.model_name, "saved_model"))
        self.logger.info("Model loaded")

    def _read_classes(self) -> Tuple[list[str], np.ndarray[Any, np.dtype[np.float64]]]:
        """
        Read the object classes from the COCO dataset and initialize the color list.
        :return: a tuple with the list of object classes and the color list
        """
        path = "utils/coco.names"
        with open(path, "rt") as f:
            classes_list = f.read().rstrip("\n").split("\n")

        color_list = np.random.uniform(low=0, high=255, size=(len(classes_list), 3))

        return classes_list, color_list

    def _model_process(self, img):
        """
        Perform object detection on the input image using the loaded model.
        :param img: the preprocessed input image
        :return: the object detection results
        """
        return self.model(img)

    def _preprocess_image(self, img: np.ndarray) -> tf.Tensor:
        """
        Preprocess the input image by converting it to a tensor in the correct format for the model.
        :param img: the input image to be preprocessed
        :return: the preprocessed image tensor
        """
        img.flags.writeable = False
        input_tensor = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
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

        H, W, C = img.shape

        img = self._draw_bounding_boxes(img, bbox_idx, bboxs, class_indexes, class_scores, H, W)

        return img

    def _get_bounding_boxes(self, detections: dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract the bounding boxes, class indexes, and class scores from the object detection results.
        :param detections: the object detection results
        :return: a tuple with the indices of the selected bounding boxes, the bounding boxes themselves,
                 the class indexes, and the class scores
        """
        bboxs = detections["detection_boxes"][0].numpy()
        class_indexes = detections["detection_classes"][0].numpy().astype(np.int32)
        class_scores = detections["detection_scores"][0].numpy()

        bbox_idx = tf.image.non_max_suppression(
            bboxs, class_scores, max_output_size=30, iou_threshold=self.threshold, score_threshold=self.threshold
        )

        return bbox_idx, bboxs, class_indexes, class_scores

    def _draw_bounding_boxes(
        self,
        img: np.ndarray,
        bbox_idx: np.ndarray,
        bboxs: np.ndarray,
        class_indexes: np.ndarray,
        class_scores: np.ndarray,
        H: int,
        W: int,
    ) -> np.ndarray:
        """
        Draw the bounding boxes around the detected objects and add the class names and confidence scores as text.
        :param img: the input image with the detected objects
        :param bbox_idx: the indices of the selected bounding boxes
        :param bboxs: the bounding boxes themselves
        :param class_indexes: the class indexes
        :param class_scores: the class scores
        :param H: the height of the input image
        :param W: the width of the input image
        :return: the image with the bounding boxes and class names added
        """
        if len(bbox_idx) != 0:
            for i in bbox_idx:
                index = class_indexes[i]
                class_name = self.classes_list[index]
                if not self.human or class_name == "person":
                    bbox = tuple(bboxs[i].tolist())
                    confidence = round(100 * class_scores[i], 2)
                    
                    label = f"{class_name} {confidence}%".upper()
                    color = self.color_list[index]

                    ymin, xmin, ymax, xmax = bbox

                    ymin, xmin, ymax, xmax = int(ymin * H), int(xmin * W), int(ymax * H), int(xmax * W)

                    cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
                    cv2.putText(img, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return img
