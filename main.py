import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import cv2

from handlers import TelloHandler
from detectors import FaceDetector
from trackers import FaceTracker

kivy.require("2.1.0")

class MyUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.drone = None
        self.detector = None
        self.tracker = None
        self.previous_error = 0
        self.flight_start = 0

    def start(self):
        self.drone = TelloHandler()
        self.drone.connect_and_initiate()
        self._update_buttons()
        self.detector = FaceDetector()
        self.tracker = FaceTracker(self.drone)

        Clock.schedule_interval(self.update_video_feed, 1 / 60)
        Clock.schedule_interval(self.update_battery, 1)
        # Clock.schedule_interval(self.update_flight_time, 1)

    def stop(self):
        self._update_buttons()
        self.drone.disconnect()

    def update_video_feed(self, dt):
        frame = self.drone.get_frame_read().frame
        img = cv2.resize(frame, (360, 240))

        img, middle, area = self.detector._predict(img)
        self.previous_error = self.tracker.track(area, middle, self.previous_error)

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.video.texture = texture
        
    def update_battery(self, dt):
        self.battery.text = f"Battery: {self.drone.get_battery()}"
        
    def _update_buttons(self):
        self.start_button.disabled = not self.start_button.disabled
        self.stop_button.disabled = not self.stop_button.disabled


class MainApp(App):
    def build(self):
        return MyUI()


if __name__ == "__main__":
    MainApp().run()
