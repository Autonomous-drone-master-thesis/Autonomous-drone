import cv2
import numpy as np
import tensorflow as tf
import time
import os
from typing import Dict, Tuple, Union

from tensorflow.python.keras.utils.data_utils import get_file


class Detector:
    def __init__(self) -> None:
        pass

    def read_classes(self, path: str) -> None:
        with open(path, "rt") as f:
            self.classes_list = f.read().rstrip("\n").split("\n")

        self.color_list = np.random.uniform(low=0, high=255, size=(len(self.classes_list), 3))

    def download_model(self, model_url: str) -> None:
        file_name = os.path.basename(model_url)
        self.model_name = file_name[: file_name.index(".")]

        self.cache_dir = "./models/"
        os.makedirs(self.cache_dir, exist_ok=True)

        get_file(fname=file_name, origin=model_url, cache_dir=self.cache_dir, cache_subdir="checkpoints", extract=True)

    def load_model(self) -> None:
        tf.keras.backend.clear_session()
        self.model = tf.saved_model.load(os.path.join(self.cache_dir, "checkpoints", self.model_name, "saved_model"))
        print("Model loaded")

    def predict_video(self, video: Union[int, str], threshold: float = 0.5) -> None:
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
            cv2.imshow("Object Detection", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            success, image = cap.read()

        cv2.destroyAllWindows()

    def _predict(self, image: np.ndarray) -> np.ndarray:
        detections = self.model(self._preprocess_image(image))
        image = self._visualize_bounding_box(detections, image)
        return image

    def _preprocess_image(self, image: np.ndarray) -> tf.Tensor:
        input_tensor = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(input_tensor, dtype=tf.uint8)
        input_tensor = input_tensor[tf.newaxis, ...]
        return input_tensor

    def _visualize_bounding_box(
        self, detections: Dict[str, tf.Tensor], image: np.ndarray, threshold: float = 0.5
    ) -> np.ndarray:
        bbox_idx, bboxs, class_indexes, class_scores = self._get_bounding_boxes(detections, threshold)

        H, W, C = image.shape

        image = self._draw_bounding_boxes(image, bbox_idx, bboxs, class_indexes, class_scores, H, W)

        return image

    def _get_bounding_boxes(
        self, detections: dict, threshold: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        bboxs = detections["detection_boxes"][0].numpy()
        class_indexes = detections["detection_classes"][0].numpy().astype(np.int32)
        class_scores = detections["detection_scores"][0].numpy()

        bbox_idx = tf.image.non_max_suppression(
            bboxs, class_scores, max_output_size=30, iou_threshold=threshold, score_threshold=threshold
        )

        return bbox_idx, bboxs, class_indexes, class_scores

    def _draw_bounding_boxes(
        self,
        image: np.ndarray,
        bbox_idx: np.ndarray,
        bboxs: np.ndarray,
        class_indexes: np.ndarray,
        class_scores: np.ndarray,
        H: int,
        W: int,
    ) -> np.ndarray:
        if len(bbox_idx) != 0:
            for i in bbox_idx:
                bbox = tuple(bboxs[i].tolist())
                confidence = round(100 * class_scores[i], 2)
                index = class_indexes[i]

                label = f"{self.classes_list[index]} {confidence}%".upper()
                color = self.color_list[index]

                ymin, xmin, ymax, xmax = bbox

                ymin, xmin, ymax, xmax = int(ymin * H), int(xmin * W), int(ymax * H), int(xmax * W)

                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
                cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                line_width = min(int((xmax - xmin) * 0.2), int((ymax - ymin) * 0.2))

                for x, y in [(xmin, ymin), (xmin, ymax), (xmax, ymin), (xmax, ymax)]:
                    cv2.line(image, (x, y), (x + line_width, y), color, 6)
                    cv2.line(image, (x, y), (x, y + line_width), color, 6)

        return image
