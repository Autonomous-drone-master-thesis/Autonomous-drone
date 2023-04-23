import enum
from typing import Any

from .base_handler import BaseHandler

class SettingsKeys(enum.Enum):
    MODELS_LAST_SCRAPE_TIME = "models_last_scrape_time"
    PERSON_HEIGHT = "person_height"
    TRACKING_HEIGHT = "tracking_height"
    TRACKING_DISTANCE = "tracking_distance"
    MODEL_PATH = "model_path"


class SettingsHandler(BaseHandler):

    def __init__(self, data_directory: str):
        self.DEFAULT_VALUES = {
            "models_last_scrape_time": 0,
            "person_height": None,
            "tracking_height": None,
            "tracking_distance": None
        }
        super().__init__(data_directory, "settings.json")
    
    def set_value(self, setting_key: SettingsKeys, value: Any) -> None:
        """
        Set the specified setting in the settings file.

        :param setting_key: the key of the setting to be updated.
        :param value: the new value for the setting.
        """
        if setting_key not in SettingsKeys:
            raise ValueError(f"Invalid setting key: {setting_key}")

        settings = self.read_data()
        settings[setting_key.value] = value
        self.write_data(settings)

    def get_value(self, setting_key: SettingsKeys) -> Any:
        """
        Get the value of the specified setting from the settings file.

        :param setting_key: the key of the setting to get.
        :return: the value of the setting.
        """
        if setting_key not in SettingsKeys:
            raise ValueError(f"Invalid setting key: {setting_key}")

        settings = self.read_data()
        return settings.get(setting_key.value)
