"""Main module of the application."""

import datetime
import logging
import os

from kivy.logger import Logger
from kivymd.app import MDApp

from helpers import SettingsHandler, ModelsHandler, ModelScraper, ModelScraperError

from components import (
    DebugUI,
    LandingUI,
    LogsUI,
    MainUI,
    ModelsDownloadUI,
    ParametersUI,
    SettingsUI
)

if not os.path.exists('logs'):
    os.makedirs('logs')

log_file_name = datetime.datetime.now().strftime("session_%Y-%m-%d_%H-%M-%S.log")
log_file_path = os.path.join('logs', log_file_name)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

Logger.addHandler(file_handler)

DATA_PATH = "data"


class MainApp(MDApp):
    """
    MainApp class is the main application class that is used to run the application.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_layout = None
        self.data_path = DATA_PATH
        self.settings_handler = SettingsHandler(DATA_PATH)
        self.models_handler = ModelsHandler(DATA_PATH)
        self._scrape_models()

    def build(self) -> LandingUI:
        """
        Build the application.

        Returns:
            LandingUI: The landing page of the application.
        """
        self.current_layout = LandingUI()
        return self.current_layout

    def switch_layout_to_main(self):
        """
        Switch the layout to the main layout.
        """
        Logger.info("Switching UI: MainUI")
        new_layout = MainUI(self.settings_handler)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_download(self):
        """
        Switch the layout to the models download layout.
        """
        Logger.info("Switching UI: ModelsDownloadUI")
        new_layout = ModelsDownloadUI(self.models_handler, self.data_path)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_settings(self):
        """
        Switch the layout to the settings layout.
        """
        Logger.info("Switching UI: SettingsUI")
        new_layout = SettingsUI()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_parameters(self):
        """
        Switch the layout to the parameters layout.
        """
        Logger.info("Switching UI: ParametersUI")
        new_layout = ParametersUI(self)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_debug(self):
        """
        Switch the layout to the debug layout.
        """
        Logger.info("Switching UI: DebugUI")
        new_layout = DebugUI(self.settings_handler)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_logs(self):
        """
        Switch the layout to the logs layout.
        """
        Logger.info("Switching UI: LogsUI")
        new_layout = LogsUI()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def get_logs_text(self) -> str:
        """
        Return the logs text.
        """
        with open(log_file_path, 'r', encoding="utf-8") as log_file:
            log_data = log_file.read()
        return log_data

    def _scrape_models(self):
        """
        Scrape the models from the github file and save them to the models.json file.
        """
        scraper = ModelScraper(DATA_PATH, self.settings_handler, self.models_handler)
        if scraper.should_scrape():
            try:
                models = scraper.scrape()
                scraper.save(models)
            except ModelScraperError as exc:
                Logger.error("An error occurred while using the ModelScraper: %s", str(exc))


if __name__ == "__main__":
    MainApp().run()
