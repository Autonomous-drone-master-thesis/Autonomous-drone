"""This module contains the MainUI class, which is responsible for displaying the main UI."""

import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.floatlayout import FloatLayout

# import backend
from handlers import TelloHandler

# import utilities
from helpers import load_kv_file_for_class
from helpers import SettingsHandler, SettingsKeys

# import components
from .start_tracking_selection import StartTrackingSelectionDialog
from .tracker_selection import TrackerSelectionDialog
from .video_selection import VideoSelectionDialog

load_kv_file_for_class("index.kv")


# pylint: disable=E1101
class MainUI(FloatLayout):
    """MainUI class is a FloatLayout that displays the main UI of the application."""

    def __init__(self, settings: SettingsHandler, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings
        self.running = False
        self.drone = TelloHandler()
        self.detector = None
        self.tracker = None
        self.detected = False

        # Start listening to the drone
        Clock.schedule_interval(self._update_battery, 1)
        Clock.schedule_interval(self._update_temperature, 1)

    def button_handler(self) -> None:
        """
        Handles the main button press event.
        """
        if self.running:
            self._stop()
        else:
            self._show_tracker_selection_dialog()

        # Clock.schedule_interval(self._update_video_feed, 1 / 60)

    def _stop(self) -> None:
        """
        Private method that stops the drone and the video feed.
        """
        self._update_running_status()
        Clock.unschedule(self._update_video_feed)
        self.drone.disconnect()

    def _show_tracker_selection_dialog(self) -> None:
        """
        Private method that shows the tracker selection dialog.
        """

        def set_tracker(tracker: str) -> None:
            model_path = None
            if tracker == 'human_tracker':
                model_path = self.settings.get_value(
                    SettingsKeys.SELECTED_OBJECT_DETECTION_MODEL
                    )["downloaded_path"]
            self.drone.set_detector_and_tracker(tracker, model_path)

        TrackerSelectionDialog(set_tracker).open()

    def _show_video_selection_dialog(self) -> None:
        """
        Private method that shows the video selection dialog.
        """

        def set_video_record(record: bool) -> None:
            if record:
                self.drone.record_video = True
            else:
                self.drone.record_video = False
            Clock.schedule_interval(self._update_video_feed, 1 / 60)

        VideoSelectionDialog(set_video_record).open()

    # dt argument is required by Clock.schedule_interval
    def _update_video_feed(self, dt):# pylint: disable=[C0103,W0613]
        detected, img = self.drone.detect_and_track(self.detected)

        if not self.detected and detected:
            StartTrackingSelectionDialog(self._set_detected).open()

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.video.texture = texture

    def _set_detected(self, detected: bool) -> None:
        self.detected = detected

    def _update_battery(self, dt: float) -> None:# pylint: disable=[C0103,W0613]
        battery = self.drone.get_battery()
        self.battery.text = f"Battery: {battery}%"

    def _update_temperature(self, dt: float) -> None:# pylint: disable=[C0103,W0613]
        self.temperature.text = f"Temperature: {self.drone.get_temperature()}"

    def _modify_status(self, new_status: str) -> None:
        """Modifies the status of the application.

        Args:
            new_status (str): The new status of the application.
        """
        self.status.text = f"Status: {new_status}"

    def _update_running_status(self):
        """
        Private method that updates the running status.
        """
        if self.running:
            self.running = False
            self.action_button.icon = "play"
            self._modify_status("Landing")
        else:
            self.running = True
            self.action_button.icon = "pause"
            self._modify_status("Flying")
