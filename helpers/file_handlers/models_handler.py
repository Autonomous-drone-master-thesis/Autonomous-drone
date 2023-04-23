from typing import Any

from .base_handler import BaseHandler


class ModelsHandler(BaseHandler):
    def __init__(self, data_directory: str):
        self.DEFAULT_VALUES = {}
        super().__init__(data_directory, "models.json")
    
    def set_value(self, model_name: str, value: Any) -> None:
        """
        Set the specified model in the models file.

        :param model_name: the name of the model to be updated
        :param value: the new value for the setting.
        """

        models = self.read_data()
        models[model_name] = value
        self.write_data(models)

    def get_value(self, model_name: str) -> Any:
        """
        Get the value of the specified model from the models file.

        :param model_name: the name of the model to be get
        :return: the value of the setting.
        """

        settings = self.read_data()
        return settings.get(model_name)
