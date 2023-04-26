"""This module defines the ModelScraper class for scraping and managing model data."""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

from kivy.logger import Logger
import requests

from .file_handlers import SettingsHandler, SettingsKeys, ModelsHandler


class ModelScraperError(Exception):
    """
    A custom exception class for errors that occur while using the ModelScraper class.

    This exception is raised when there is a connection error or any other error
    while fetching the file from the given URL.
    """


class ModelScraper:
    """
    The ModelScraper class fetches model data from a GitHub URL and extracts relevant information.
    """

    MODELS_URL = (
        "https://raw.githubusercontent.com/tensorflow/models/master/"
        "research/object_detection/g3doc/tf2_detection_zoo.md"
    )

    def __init__(
        self,
        directory_path: str,
        settings_handler: SettingsHandler,
        models_handler: ModelsHandler,
    ):
        """
        Initializes the ModelScraper class.

        :param directory_path: The path to the directory where the models.json file is stored.
        :param settings_handler: The SettingsHandler object.
        :param models_handler: The ModelsHandler object.
        """
        self._directory_path = directory_path
        self._settings_handler = settings_handler
        self._models_handler = models_handler
        self._current_datetime = datetime.now()

    def should_scrape(self) -> bool:
        """
        Determines if the scraper should perform a new scrape based on the last scrape time.

        :return: True if the scraper should perform a new scrape, otherwise False.
        """
        last_scrape_time = self._settings_handler.get_value(SettingsKeys.MODELS_LAST_SCRAPE_TIME)

        last_scrape_datetime = datetime.fromtimestamp(last_scrape_time)
        time_difference = self._current_datetime - last_scrape_datetime

        return time_difference > timedelta(days=1)

    def scrape(self) -> None:
        """
        Retrieves the list of models from the GitHub URL.

        :raises ModelScraperError: If there's a connection error or an error fetching the file.
        """
        Logger.info("Model Scraper: Fetching model data from GitHub...")
        data = self._get_md_file_from_github()
        Logger.info("Model Scraper: Extracting models information...")
        models = self._extract_models(data)
        return models

    def save(self, models: List[Dict[str, str]]) -> None:
        """
        Saves the list of models to a file and closes the file.

        :param models: The list of dictionaries containing model information.
        """
        existing_models = self._models_handler.read_data()
        Logger.info("Model Scraper: Saving models")
        merged_models = {**models, **existing_models}
        self._models_handler.write_data(merged_models)
        Logger.info("Model Scraper: Models saved successfully")
        self._settings_handler.set_value(
            SettingsKeys.MODELS_LAST_SCRAPE_TIME,
            self._current_datetime.timestamp()
        )

    def _get_md_file_from_github(self) -> str:
        """
        Fetches the file from github and returns the data.

        :return: The content of the fetched file as a string.
        """
        try:
            response = requests.get(ModelScraper.MODELS_URL, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            raise ModelScraperError(
                f"Connection error while fetching the file: {str(exc)}"
                ) from exc

        if response.status_code == 200:
            return response.text

        raise ModelScraperError(
            f"Error fetching the file: {response.status_code} - {response.reason}"
            )

    def _extract_models(self, data: str) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Extracts the models information from the given data.

        :param data: The content of the fetched file as a string.
        :return: A dictionary containing model information.
        """
        models = {}
        for line in data[data.find("Model name") :].splitlines():
            if line.startswith("["):
                model_info = self._parse_model_line(line)
                if model_info:
                    models[model_info["model_name"]] = model_info

        return models

    def _parse_model_line(self, line: str) -> Optional[Dict[str, Union[str, int]]]:
        """
        Parses a single line from the model data and extracts model information.

        :param line: A string representing a line from the model data.
        :return: A dictionary containing model information if the line contains a valid model,
            otherwise None.
        """
        pattern = re.compile(r"(.+?)\s+(\d+x\d+)")
        model_name_with_size = line[1 : line.find("]")]

        match = pattern.match(model_name_with_size)
        if match:
            model_name, size = match.groups()
            download_link = line[line.find("(") + 1 : line.find(")")]
            speed, coco_map, output = line.split("|")[1:]

            if output.strip() == "Boxes":
                return {
                    "model_name": model_name,
                    "size": size,
                    "download_link": download_link,
                    "speed": int(speed.strip()),
                    "coco_map": coco_map.strip(),
                    "output": output.strip(),
                    "downloaded": False,
                    "downloaded_path": None,
                }
        return None
