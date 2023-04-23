from datetime import datetime, timedelta
import logging
import json


from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from kivymd.app import MDApp


import cv2

# from handlers import TelloHandler
# from detectors import FaceDetector
# from trackers import FaceTracker
from helpers import SettingsHandler, SettingsKeys, ModelDownloader, ModelsHandler, ModelScraper, ModelScraperError


DATA_PATH = "data"


class LandingUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ModelListItem(TwoLineAvatarIconListItem):

    def __init__(self, model: dict, **kwargs):
        super().__init__(**kwargs)
        self.download_link = model['download_link']
        self.text = model['model_name']
        self.secondary_text = f"Size: {model['size']} Speed: {model['speed']} ms Output: {model['output']} CocoMap: {model['coco_map']}"
        self._no_ripple_effect = True


class ModelListItemRight(IRightBodyTouch, MDCheckbox):
    def __init__(self, model, on_check, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.on_check = on_check

    def on_active(self, checkbox, value):
        self.on_check(self.model, value)


class DownloadModels(BoxLayout):
    selection_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_models = {}
        self._populate_list()

    def download_selected_models(self):
        def on_complete(model_name):
            print(f"Downloaded {model_name}")
        downloader = ModelDownloader(DATA_PATH, callback=on_complete)
        downloader.download_models_threaded(self.selected_models.values())

    def _populate_list(self) -> None:
        folder_path = f"{DATA_PATH}/models.json"
        try:
            with open(folder_path, "r") as f:
                data = json.load(f)
                for model in data.values():
                    if not model['downloaded']:
                        list_item = ModelListItem(model)
                        list_item.add_widget(ModelListItemRight(
                            model, self._on_model_check))
                        self.selection_list.add_widget(list_item)
        except FileNotFoundError:
            logging.error(f"Models file not found at {folder_path}")
            # TODO: Add error message to UI

    def _on_model_check(self, model, is_checked):
        if is_checked:
            self.selected_models[model['model_name']] = model
        else:
            self.selected_models.pop(model['model'], None)


class Settings(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Parameters(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.selected_model = None

    def show_height_input(self):
        height_input = MDTextField(
            hint_text="Enter height (in cm)", mode="rectangle")
        dialog = MDDialog(
            title="Person Height",
            type="custom",
            content_cls=height_input,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (self.save_height(
                        height_input.text), dialog.dismiss())
                )
            ]
        )
        dialog.open()

    def save_height(self, height):
        self.main_app.settings.set_value(
            SettingsKeys.PERSON_HEIGHT, height)

    def show_tracking_input(self):
        tracking_height_input = MDTextField(
            hint_text="Enter tracking height (in cm)", mode="rectangle")
        tracking_distance_input = MDTextField(
            hint_text="Enter tracking distance (in cm)", mode="rectangle")

        dialog = MDDialog(
            title="Tracking Height and Distance",
            type="custom",
            content_cls=MDBoxLayout(
                tracking_height_input,
                tracking_distance_input,
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="120dp",
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (self.save_tracking(
                        tracking_height_input.text, tracking_distance_input.text), dialog.dismiss())
                )
            ]
        )
        dialog.open()

    def save_tracking(self, height, distance):
        self.main_app.settings.set_value(
            SettingsKeys.TRACKING_HEIGHT, height)
        self.main_app.settings.set_value(
            SettingsKeys.TRACKING_DISTANCE, distance)

    def show_model_selection_select(self):
        items = [
            ItemConfirm(self),
            ItemConfirm(self),
            ItemConfirm(self),
            ItemConfirm(self),
            # Add more models as needed
        ]

        dialog = MDDialog(
            title="Model Selection",
            type="confirmation",
            items=items,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (
                        self.save_model_selection(), dialog.dismiss()),
                ),
            ],
        )
        dialog.open()

    def save_model_selection(self):
        if self.selected_item is not None:
            selected_model = self.selected_item.text
            print("Selected model:", selected_model)
        else:
            print("No model selected")


class ItemConfirm(TwoLineAvatarIconListItem):
    divider = None

    def __init__(self, model: dict, parameters: Parameters, **kwargs):
        super().__init__(**kwargs)
        self.text = model['model_name']
        self.secondary_text = f"Size: {model['size']} Speed: {model['speed']} ms Output: {model['output']} CocoMap: {model['coco_map']}"
        self._no_ripple_effect = True
        self.parameters = parameters

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False
        self.parameters.selected_item = self


class ModelSelection(BoxLayout):
    pass


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
        # self.drone.takeoff_and_hover()
        self._update_running_status()
        # Clock.schedule_interval(self._update_video_feed, 1 / 60)
        # Clock.schedule_interval(self._update_flight_time, 1 / 100)

    def _stop(self):
        self._update_running_status()
        # Clock.unschedule(self._update_video_feed)
        # Clock.unschedule(self._update_flight_time)
        # self.drone.disconnect()

    def _update_video_feed(self, dt):
        img = self.drone.get_frame_read().frame

        img, middle, area = self.detector.predict(img)
        self.previous_error = self.tracker.track(
            area, middle, self.previous_error)

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(
            size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.video.texture = texture

    def _update_battery(self, dt):
        batery = self.drone.get_battery()
        self.battery.text = f"Battery: {batery}%"

    def _update_flight_time(self, dt):
        self.flight_time.text = f"Flight time: {self.drone.get_flight_time()}"

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_layout = None
        self.settings = SettingsHandler(DATA_PATH)
        self.models = ModelsHandler(DATA_PATH)
        self._scrape_models()

    def build(self):
        self.current_layout = LandingUI()
        return self.current_layout

    def switch_layout_to_main(self):
        print("Switching to main layout")
        new_layout = MainUI()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_download(self):
        print("Switching to download layout")
        new_layout = DownloadModels()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_settings(self):
        print("Switching to settings layout")
        new_layout = Settings()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_parameters(self):
        print("Switching to parameters layout")
        new_layout = Parameters(main_app=self)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def _scrape_models(self):
        scraper = ModelScraper(DATA_PATH)
        last_scrape_time = self.settings.get_value(
            SettingsKeys.MODELS_LAST_SCRAPE_TIME)

        last_scrape_datetime = datetime.fromtimestamp(last_scrape_time)
        current_datetime = datetime.now()
        time_difference = current_datetime - last_scrape_datetime

        if time_difference > timedelta(days=1):
            scraper = ModelScraper(DATA_PATH)
            try:
                scraper.get_and_save_models_list()
                self.settings.set_value(
                    SettingsKeys.MODELS_LAST_SCRAPE_TIME, current_datetime.timestamp())

            except ModelScraperError as e:
                logging.error(
                    f"An error occurred while using the ModelScraper: {str(e)}")


if __name__ == "__main__":
    MainApp().run()
