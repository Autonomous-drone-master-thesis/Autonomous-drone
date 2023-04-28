"""This module contains the MainUI class, which is responsible for displaying the main UI."""

import threading

import cv2

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout

# import backend
from handlers import TelloHandler

# import utilities
from helpers import load_kv_file_for_class, SettingsHandler, SettingsKeys

# import components
from .connection_dialog import DroneConnectionDialog
from .connection_error_dialog import DroneConnectionErrorDialog
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
        self.drone = None
        self.detector = None
        self.tracker = None
        self.detected = False
        self.pop_up = None

    def button_handler(self) -> None:
        """
        Handles the main button press event.
        """
        if self.running:
            self._stop()
        else:
            self._connect_to_drone()

    def _stop(self) -> None:
        """
        Private method that stops the drone and the video feed.
        """
        self._update_running_status()
        Clock.unschedule(self._update_video_feed)
        self.drone.disconnect()

    def _connect_to_drone(self) -> None:
        """
        Connects to the drone and shows the tracker selection dialog if the connection is successful
        else shows the error dialog.
        """
        self.pop_up = Factory.DroneConnectionDialog()
        self.pop_up.open()

        my_thread = threading.Thread(target=self._init_drone)
        my_thread.start()

    def _init_drone(self):
        """
        Private method that initializes the drone. Needed as needs to be run in a separate thread.
        """
        try:
            self.drone = TelloHandler()
            Clock.schedule_once(lambda dt: self._modify_status("Connected."))

            # Start listening to the drone
            Clock.schedule_interval(self._update_battery, 1)
            Clock.schedule_interval(self._update_temperature, 1)
            Clock.schedule_once(self._show_tracker_selection_dialog)
        except Exception:#pylint: disable=W0703
            Clock.schedule_once(lambda dt: self._modify_status("Connection failed."))
            Clock.schedule_once(lambda dt: DroneConnectionErrorDialog().open())
        finally:
            Clock.schedule_once(lambda dt: self.pop_up.dismiss())

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
            self._show_video_selection_dialog()

        tracker_dialog = TrackerSelectionDialog(set_tracker)
        tracker_dialog.open()

    def _show_video_selection_dialog(self) -> None:
        """
        Private method that shows the video selection dialog.
        """

        def set_video_record(record: bool) -> None:
            if record:
                self.drone.record_video = True
            else:
                self.drone.record_video = False
            self.drone.connect_and_initiate()
            self._update_running_status()
            self.drone.takeoff_and_hover()
            Clock.schedule_interval(self._update_video_feed, 1 / 60)

        video_dialog = VideoSelectionDialog(set_video_record)
        video_dialog.open()

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
        self.battery.text = f"Battery: {self.drone.get_battery()}%"

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
