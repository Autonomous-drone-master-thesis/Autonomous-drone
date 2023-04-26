"""This module defines the ModelsHandler class for managing model-related data."""

import logging
from typing import Any

from kivy.logger import Logger

from .base_handler import BaseHandler


class ModelsHandler(BaseHandler):
    """
    The ModelsHandler class manages model-related data in a JSON file.
    """
    def __init__(self, data_directory: str) -> None:
        self.default_values = {}
        super().__init__(data_directory, "models.json")

    def set_value(self, key: str, value: Any) -> None:
        """
        Set the specified model in the models file.

        :param key: the name of the model to be updated
        :param value: the new value for the setting.
        """

        Logger.info("Models Handler: Setting a model %s to %s", key, value)
        models = self.read_data()
        models[key] = value
        self.write_data(models)

    def get_value(self, key: str) -> Any:
        """
        Get the value of the specified model from the models file.

        :param key: the name of the model to be get
        :return: the value of the setting.
        """

        Logger.info("Models Handler: Getting a model value for %s", key)
        settings = self.read_data()
        return settings.get(key)
