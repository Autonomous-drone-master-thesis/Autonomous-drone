"""This module defines the BaseHandler class for handling file-based data storage."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Union


class BaseHandler(ABC):
    """
    The BaseHandler class is an abstract base class for handling file-based data storage.
    """
    default_values = {}

    def __init__(self, data_directory: str, file_name: str):
        """
        Initialize the BaseHandler object with the specified file path.

        :param data_directory: The directory where the data files are stored.
        :param file_name: The name of the file to be managed.
        """
        self.file_path = os.path.join(data_directory, file_name)

        if not os.path.exists(data_directory):
            os.mkdir(data_directory)

        if not os.path.exists(self.file_path):
            self._create_file()

    @abstractmethod
    def set_value(self, key: Union[str, "SettingsKeys"], value: Any) -> None:
        """
        Set the specified value for the given key in the data file.
        """

    @abstractmethod
    def get_value(self, key: Union[str, "SettingsKeys"]) -> Any:
        """
        Get the value associated with the given key from the data file.
        """

    def _create_file(self) -> None:
        """
        Create the file with default values.
        """
        self.write_data(self.default_values)

    def read_data(self) -> Dict[str, Any]:
        """
        Read the data from the file.

        :return: The data dictionary.
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def write_data(self, new_data: Dict[str, Any]) -> None:
        """
        Write the data to the file.

        :param data: New data dictionary.
        """
        with open(self.file_path, "w+", encoding="utf-8") as file:
            json.dump(new_data, file, indent=4)
