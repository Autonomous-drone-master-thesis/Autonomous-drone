"""Module for the TelloHandler class."""
import os
import time
from threading import Thread
from typing import Optional, Tuple

import cv2
from djitellopy import Tello
import numpy as np

from detectors import FaceDetector, HumanDetector
from trackers import FaceTracker, HumanTracker

VIDEOS_PATH = "videos"


class TelloHandler(Tello):
    """TelloHandler class is a wrapper class for the Tello class from the djitellopy library."""

    def __init__(self) -> None:
        super().__init__()
        self.connect()
        # Video recording attributes
        self.video = None
        self.recording = False
        self.recorder_thread = None
        self.record_video = False

        # Backend attributes
        self.detector = None
        self.tracker = None
        self.previous_error = None

        if not os.path.exists(VIDEOS_PATH):
            os.mkdir(VIDEOS_PATH)

    def set_detector_and_tracker(self, tracker: str, model_path: Optional[str]) -> None:
        """Sets the detector and tracker to use.
        :param tracker: The tracker to use.
        :param model_path: The path to the model to use. Only used if the tracker is 
        human_tracker."""
        if tracker == "face_tracker":
            self.detector = FaceDetector()
            self.tracker = FaceTracker(self)
            self.previous_error = (0, 0)
        elif tracker == "human_tracker":
            if model_path is None:
                raise ValueError("A model path must be provided when using the human tracker.")
            self.detector = HumanDetector(model_path)
            self.tracker = HumanTracker(self)
            self.previous_error = (0, 0, 0)
        else:
            raise NotImplementedError("Tracker not implemented yet.")

    def connect_and_initiate(self) -> None:
        """Connects to the drone and initiates the drone to takeoff and hover at 25cm."""
        self.streamon()
        if self.record_video:
            self._start_recording()

    def detect_and_track(self, track: bool, debug: bool=False) -> Tuple[bool, np.ndarray]:
        """Detects and tracks the object.
        :param track: Whether to track the object or not.
        :param debug: Whether to return the debug image or not."""
        img = self.get_frame_read().frame
        if isinstance(self.tracker, FaceTracker):
            detected, debug_img, middle, area = self.detector.predict(img)
            if track:
                self.previous_error = self.tracker.track(area, middle, self.previous_error)

        elif isinstance(self.tracker, HumanTracker):
            detected, debug_img, center, bbox_height = self.detector.predict(img)
            if track:
                self.previous_error = self.tracker.track(bbox_height, center, self.previous_error)

        else:
            raise NotImplementedError("Tracker not implemented yet.")
        return detected, debug_img if debug else img

    def takeoff_and_hover(self) -> None:
        """Takes off and hovers at 35cm."""
        self.takeoff()
        self.send_rc_control(0, 0, 35, 0)

    def disconnect(self) -> None:
        """Disconnects from the drone and lands it."""
        self.send_rc_control(0, 0, 0, 0)
        self._stop_recording()
        self.streamoff()
        self.land()

    def _start_recording(self):
        """Starts recording the video feed from the drone."""
        height, width, _ = self.get_frame_read().frame.shape
        self.video = cv2.VideoWriter(
            "videos/video.avi",
            cv2.VideoWriter_fourcc(*"XVID"),
            30,
            (width, height)
            )
        self.recording = True
        self.recorder_thread = Thread(target=self._keep_recording)
        self.recorder_thread.start()

    def _keep_recording(self) -> None:
        while self.recording:
            self.video.write(self.get_frame_read().frame)
            time.sleep(1 / 30)
        self.video.release()

    def _stop_recording(self) -> None:
        """Stops recording the video feed from the drone."""
        self.recording = False
        self.recorder_thread.join()
