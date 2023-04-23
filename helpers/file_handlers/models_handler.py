"""This module defines the ModelsHandler class for managing model-related data."""

from typing import Any

from .base_handler import BaseHandler


class ModelsHandler(BaseHandler):
    """
    The ModelsHandler class manages model-related data in a JSON file.
    """
    def __init__(self, data_directory: str):
        self.default_values = {}
        super().__init__(data_directory, "models.json")

    def set_value(self, key: str, value: Any) -> None:
        """
        Set the specified model in the models file.

        :param key: the name of the model to be updated
        :param value: the new value for the setting.
        """

        models = self.read_data()
        models[key] = value
        self.write_data(models)

    def get_value(self, key: str) -> Any:
        """
        Get the value of the specified model from the models file.

        :param key: the name of the model to be get
        :return: the value of the setting.
        """

        settings = self.read_data()
        return settings.get(key)
