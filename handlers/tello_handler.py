"""Module for the TelloHandler class."""
from datetime import datetime
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

    def set_detector_and_tracker(self, tracker: str, settings: Optional[dict]) -> None:
        """Sets the detector and tracker to use.
        :param tracker: The tracker to use.
        :param settings: A dictionary containing the settings for the application.
        """
        if tracker == "face_tracker":
            self.detector = FaceDetector()
            self.tracker = FaceTracker(self)
            self.previous_error = (0, 0)
        elif tracker == "human_tracker":
            if settings is None:
                raise ValueError(
                    "A settings dictionary must be provided when using the human tracker."
                    )
            selected_model_information = settings["selected_object_detection_model"]
            model_path = selected_model_information["downloaded_path"]
            model_width, model_height = map(int, selected_model_information["size"].split("x"))
            self.detector = HumanDetector(model_path, model_height, model_width)

            target_distance = settings["tracking_distance"]
            target_height = settings["tracking_height"]
            tracking_human_height = settings["person_height"]
            self.tracker = HumanTracker(self, target_distance, target_height, tracking_human_height)
            self.previous_error = (0, 0, 0)
        else:
            raise NotImplementedError("Tracker not implemented yet.")

    def initiate_video_stream(self) -> None:
        """Initiates the video stream and video recording if enabled."""
        self.streamon()
        if self.record_video:
            self._start_recording()

    def detect_and_track(self, track: bool, debug: bool=False) -> Tuple[bool, np.ndarray]:
        """Detects and tracks the object.
        :param track: Whether to track the object or not.
        :param debug: Whether to return the debug image or not."""
        img = self.get_frame_read().frame
        if isinstance(self.tracker, FaceTracker):
            detected, debug_img, center, area = self.detector.predict(img)
            self.previous_error = self.tracker.track(center, self.previous_error, area, track)

        elif isinstance(self.tracker, HumanTracker):
            detected, debug_img, center, bbox_height = self.detector.predict(img)
            self.previous_error = self.tracker.track(
                center,
                self.previous_error,
                bbox_height,
                track
                )

        else:
            raise NotImplementedError("Tracker not implemented yet.")
        return detected, debug_img if debug else img

    def takeoff_and_hover(self) -> None:
        """Takes off and hover"""
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
        file_name = f"videos/video_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.avi"
        self.video = cv2.VideoWriter(
            file_name,
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
