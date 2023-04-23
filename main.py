"""Main module of the application."""
import logging

from kivymd.app import MDApp

from helpers import SettingsHandler, ModelsHandler, ModelScraper, ModelScraperError

from components import LandingUI, MainUI, ModelsDownloadUI, ParametersUI, SettingsUI

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
        new_layout = MainUI()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_download(self):
        """
        Switch the layout to the models download layout.
        """
        new_layout = ModelsDownloadUI(self.models_handler, self.data_path)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_settings(self):
        """
        Switch the layout to the settings layout.
        """
        new_layout = SettingsUI()
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

    def switch_layout_to_parameters(self):
        """
        Switch the layout to the parameters layout.
        """
        print("Switching to parameters layout")
        new_layout = ParametersUI(main_app=self)
        self.root.clear_widgets()
        self.root.add_widget(new_layout)
        self.current_layout = new_layout

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
                logging.error("An error occurred while using the ModelScraper: %s", str(exc))


if __name__ == "__main__":
    MainApp().run()
