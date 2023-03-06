from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import cv2

from handlers import TelloHandler
from detectors import FaceDetector
from trackers import FaceTracker

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
        # self.drone.send_rc_control(0, 0, 25, 0)
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
        img = self.drone.get_frame_read().frame

        img, middle, area = self.detector.predict(img)
        self.previous_error = self.tracker.track(area, middle, self.previous_error)

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.video.texture = texture
        
    def update_battery(self, dt):
        batery = self.drone.get_battery()
        if batery > 50:
            self.battery.source = "icons/Battery-high.png"
        else:
            self.battery.source = "icons/Battery-low.png"
        
    def _update_buttons(self):
        if self.start_button.size_hint == (0, 0):
            self.start_button.size_hint = (0.1, 0.1) 
            self.stop_button.size_hint = (0, 0)
        else:
            self.start_button.size_hint = (0, 0)
            self.stop_button.size_hint = (0.1, 0.1)


class MainApp(App):
    def build(self):
        return MyUI()


if __name__ == "__main__":
    MainApp().run()
