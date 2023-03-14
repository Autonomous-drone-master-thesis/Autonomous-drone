from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import cv2
import math

from handlers import TelloHandler
from detectors import FaceDetector
from trackers import FaceTracker

class MyUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.drone = TelloHandler()
        self.drone.connect_and_initiate()
        self.detector = FaceDetector()
        self.tracker = FaceTracker(self.drone)
        self.previous_error = 0

        Clock.schedule_interval(self._update_battery, 1)
        Clock.schedule_interval(self._update_current_speed, 1 / 2)
        Clock.schedule_interval(self._update_temperature, 1 / 2)

    
    def button_handler(self):
        if self.button.text == "Start":
            self._start()
        elif self.button.text == "Stop":
            self._stop()
        else:
            print("Unknown button pressed")

    def _start(self):
        print("Start button pressed")
        self.drone.takeoff_and_hover()
        self._update_buttons()

        Clock.schedule_interval(self._update_video_feed, 1 / 60)
        Clock.schedule_interval(self._update_flight_time, 1 / 100)

    def _stop(self):
        self._update_buttons()
        print("Stop button pressed")
        Clock.unschedule(self._update_video_feed)
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
        self.battery.text = f"Battery: {batery}%"
        
    def _update_flight_time(self, dt):
        self.flight_time.text = f"Flight time: {self.drone.get_flight_time()}"

    def _update_current_speed(self, dt):
        speed_x = self.drone.get_speed_x()
        speed_y = self.drone.get_speed_y()
        speed_z = self.drone.get_speed_z()
        total_speed = math.sqrt(speed_x**2 + speed_y**2 + speed_z**2)
        self.current_speed.text = f"Current speed: {total_speed}"
    
    def _update_temperature(self, dt):
        self.temperature.text = f"Temperature: {self.drone.get_temperature()}"
    
    def _modify_status(self, new_status):
        self.status.text = new_status
        
    def _update_buttons(self):
        if self.button.text == "Start":
            self.button.text = "Stop"
        else:
            self.button.text = "Start"


class MainApp(App):
    def build(self):
        return MyUI()


if __name__ == "__main__":
    MainApp().run()
