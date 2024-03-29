"""This module defines the SettingsHandler class for managing application settings data."""

import enum
from typing import Any

from kivy.logger import Logger

from .base_handler import BaseHandler


class SettingsKeys(enum.Enum):
    """
    The SettingsKeys enum defines the keys used for managing application settings in the
    SettingsHandler.
    """

    MODELS_LAST_SCRAPE_TIME = "models_last_scrape_time"
    PERSON_HEIGHT = "person_height"
    TRACKING_HEIGHT = "tracking_height"
    TRACKING_DISTANCE = "tracking_distance"
    DEBUG_MODE = "debug_mode"
    SELECTED_OBJECT_DETECTION_MODEL = "selected_object_detection_model"


class SettingsHandler(BaseHandler):
    """
    The SettingsHandler class manages application settings data in a JSON file.
    """

    def __init__(self, data_directory: str) -> None:
        self.default_values = {
            "models_last_scrape_time": 0,
            "person_height": None,
            "tracking_height": None,
            "tracking_distance": None,
            "debug_mode": False,
            "selected_object_detection_model": None
        }
        super().__init__(data_directory, "settings.json")

    def set_value(self, key: SettingsKeys, value: Any) -> None:
        """
        Set the specified setting in the settings file.

        :param key: the key of the setting to be updated.
        :param value: the new value for the setting.
        """
        if key not in SettingsKeys:
            Logger.error("Settings Handler: Invalid setting key %s", key)
            raise ValueError(f"Invalid setting key: {key}")

        Logger.info("Settings Handler: Setting a setting %s to %s", key.value, value)
        settings = self.read_data()
        settings[key.value] = value
        self.write_data(settings)

    def get_value(self, key: SettingsKeys) -> Any:
        """
        Get the value of the specified setting from the settings file.

        :param key: the key of the setting to get.
        :return: the value of the setting.
        """
        if key not in SettingsKeys:
            Logger.error("Settings Handler: Invalid setting key - %s", key)
            raise ValueError(f"Invalid setting key - {key}")

        Logger.info("Settings Handler: Getting a setting value for %s", key.value)
        settings = self.read_data()
        return settings.get(key.value)
