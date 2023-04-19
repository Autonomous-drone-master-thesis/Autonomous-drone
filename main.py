from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.lang import Builder

from kivymd.app import MDApp


import cv2
import math

from handlers import TelloHandler
from detectors import FaceDetector
from trackers import FaceTracker


class LandingUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MainUI(FloatLayout):
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

    
    def button_handler(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        #self.drone.takeoff_and_hover()
        self._update_running_status()
        # Clock.schedule_interval(self._update_video_feed, 1 / 60)
        # Clock.schedule_interval(self._update_flight_time, 1 / 100)

    def _stop(self):
        self._update_running_status()
        #Clock.unschedule(self._update_video_feed)
        #Clock.unschedule(self._update_flight_time)
        #self.drone.disconnect()

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
        self.status.text = f"Status: {new_status}"
        
    def _update_running_status(self):
        if self.running:
            self.running = False
            self.action_button.icon = "play"
            self._modify_status("Landing")
        else:
            self.running = True
            self.action_button.icon = "pause"
            self._modify_status("Flying")


class MainApp(MDApp):
    def build(self):
        self.current_layout = LandingUI()
        return self.current_layout

    def switch_layout(self):
        new_layout = MainUI()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

if __name__ == "__main__":
    MainApp().run()
