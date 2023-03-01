import cv2
import numpy as np
from typing import Tuple
import mediapipe as mp
from mediapipe.python.solutions.face_detection import FaceDetection

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def find_face(img: np.ndarray, face_detection: FaceDetection) -> Tuple[np.ndarray, Tuple[int, int], int]:
    img.flags.writeable = False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_detection.process(gray)
    
    img.flags.writeable = True
    
    if results.detections:
      for detection in results.detections:
        bounding_box = detection.location_data.relative_bounding_box
        width = bounding_box.width
        height = bounding_box.height
        x = bounding_box.xmin + (width / 2)
        y = bounding_box.ymin + (height / 2)
        middle = (int(x * img.shape[1]), int(y * img.shape[0]))
        area = width * height
        mp_drawing.draw_detection(img, detection)
        cv2.circle(img, (int(x * img.shape[1]), int(y * img.shape[0])), 5, (0, 255, 0), -1)

        return img, middle, area
    return img, (0, 0), 0


def main():
    capture = cv2.VideoCapture(0)
    with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5) as face_detection:
        while capture.isOpened():
            success, img = capture.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            img, face, area = find_face(img, face_detection)
            cv2.imshow("Camera", img)
            cv2.waitKey(1)


if __name__ == "__main__":
    main()
