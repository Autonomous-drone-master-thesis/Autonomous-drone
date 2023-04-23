"""TThis module contains the MainUI class, which is responsible for displaying the main UI."""

from kivy.uix.floatlayout import FloatLayout

from helpers import load_kv_file_for_class

load_kv_file_for_class("index.kv")

# pylint: disable=E1101
class MainUI(FloatLayout):
    """MainUI class is a FloatLayout that displays the main UI of the application."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.running = False
        # self.drone = TelloHandler()
        # self.drone.connect_and_initiate()
        # self.detector = FaceDetector()
        # self.tracker = FaceTracker(self.drone)
        # self.previous_error = 0

        # Clock.schedule_interval(self._update_battery, 1)
        # Clock.schedule_interval(self._update_current_speed, 1 / 2)
        # Clock.schedule_interval(self._update_temperature, 1 / 2)

    def button_handler(self) -> None:
        """
        Handles the main button press event.
        """
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self) -> None:
        """
        Private method that starts the drone and the video feed.
        """
        # self.drone.takeoff_and_hover()
        self._update_running_status()
        # Clock.schedule_interval(self._update_video_feed, 1 / 60)
        # Clock.schedule_interval(self._update_flight_time, 1 / 100)

    def _stop(self) -> None:
        """
        Private method that stops the drone and the video feed.
        """
        self._update_running_status()
        # Clock.unschedule(self._update_video_feed)
        # Clock.unschedule(self._update_flight_time)
        # self.drone.disconnect()

    # def _update_video_feed(self, dt):
    #     img = self.drone.get_frame_read().frame

    #     img, middle, area = self.detector.predict(img)
    #     self.previous_error = self.tracker.track(area, middle, self.previous_error)

    #     buf1 = cv2.flip(img, 0)
    #     buf = buf1.tostring()
    #     texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
    #     texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
    #     self.video.texture = texture

    # def _update_battery(self, dt):
    #     batery = self.drone.get_battery()
    #     self.battery.text = f"Battery: {batery}%"

    # def _update_flight_time(self, dt):
    #     self.flight_time.text = f"Flight time: {self.drone.get_flight_time()}"

    # def _update_temperature(self, dt):
    #     self.temperature.text = f"Temperature: {self.drone.get_temperature()}"

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
