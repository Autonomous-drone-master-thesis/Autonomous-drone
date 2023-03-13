from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import cv2
import datetime

import random

from handlers import TelloHandler
from detectors import FaceDetector
from trackers import FaceTracker

class MyUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.drone = TelloHandler()
        self.drone.connect_and_initiate()
        self.detector = None
        self.tracker = None
        self.previous_error = 0
        self.flight_start = 0
    
    def button_handler(self):
        if self.button.text == "Start":
            self._start()
        elif self.button.text == "Stop":
            self._stop()
        else:
            print("Unknown button pressed")

    def _start(self):
        print("Start button pressed")
        self.drone.takeoff()
        self.drone.send_rc_control(0, 0, 25, 0)
        self._update_buttons()
        self.detector = FaceDetector()
        self.tracker = FaceTracker(self.drone)

        self.flight_start = datetime.datetime.now()
        Clock.schedule_interval(self._update_video_feed, 1 / 60)
        Clock.schedule_interval(self._update_battery, 1)
        Clock.schedule_interval(self._update_flight_time, 1 / 100)
        Clock.schedule_interval(self._update_current_speed, 1 / 2)

    def _stop(self):
        self._update_buttons()
        print("Stop button pressed")
        Clock.unschedule(self._update_battery)
        Clock.unschedule(self._update_flight_time)
        self.drone.disconnect()

    def _update_video_feed(self, dt):
        img = self.drone.get_frame_read().frame

        img, middle, area = self.detector.predict(img)
        self.previous_error = self.tracker.track(area, middle, self.previous_error)

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.video.texture = texture
        
    def _update_battery(self, dt):
        batery = self.drone.get_battery()
        self.battery.text = f"Battery: {random.randint(0, 100)}%"
        
    def _update_flight_time(self, dt):
        flight_time = datetime.datetime.now() - self.flight_start
        self.flight_time.text = f"Flight time: {flight_time}"
    
    def _modify_status(self, new_status):
        self.status.text = new_status
        
    def _update_buttons(self):
        if self.button.text == "Start":
            self.button.text = "Stop"
        else:
            self.button.text = "Start"
    
    def _update_current_speed(self):
        self.current_speed.text = f"Current speed: {self.drone.get_current_speed()}"


class MainApp(App):
    def build(self):
        return MyUI()


if __name__ == "__main__":
    MainApp().run()
