from typing import List, Dict, Optional, Union
import requests
import re
import json
import logging
from io import TextIOWrapper


class ModelScraperError(Exception):
    """
    A custom exception class for errors that occur while using the ModelScraper class.

    This exception is raised when there is a connection error or any other error
    while fetching the file from the given URL.
    """
    pass


class ModelScraper:
    def __init__(self, directory_path: str, logger: Optional[logging.Logger] = None):
        """
        Initializes the ModelScraper class.

        
        :param logger: A logger instance to use for logging messages.
        """
        self._directory_path = directory_path
        self._models_url = "https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/g3doc/tf2_detection_zoo.md"
        self._logger = logger or logging.getLogger(__name__)

    def get_and_save_models_list(self) -> None:
        """
        Retrieves and saves the list of models from the GitHub URL.

        :raises ModelScraperError: If there's a connection error or an error fetching the file.
        """
        self._logger.info("Fetching model data from GitHub...")
        data = self._get_md_file_from_github(self._models_url)
        self._logger.info("Extracting models information...")
        models = self._extract_models(data)
        try:
            models_file = open(f"{self._directory_path}/models.json", 'r+')
            existing_models = json.load(models_file)
        except FileNotFoundError:
            models_file = open(f"{self._directory_path}/models.json", 'w+')
            existing_models = {}
        self._save(models, models_file, existing_models)

        
    def _save(self, models: List[Dict[str, str]], models_file: TextIOWrapper, existing_models: dict) -> None:
        """
        Saves the list of models to a file and closes the file.

        :param models: The list of dictionaries containing model information.
        :param models_file: The file object to save the models to.
        :param existing_models: The existing models in the file.
        """
        self._logger.info(f"Saving models to {self._directory_path}...")
        merged_models = {**models, **existing_models}
        models_file.seek(0)
        models_file.truncate(0)
        json.dump(merged_models, models_file, indent=2)
        self._logger.info(f"Models saved successfully to {self._directory_path}")
        models_file.close()

    def _get_md_file_from_github(self, url: str) -> str:
        """
        Fetches the file from the given URL.
        """
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            self._logger.error(
                f"Connection error while fetching the file: {str(e)}")
            raise ModelScraperError(
                "Connection error while fetching the file.") from e

        if response.status_code == 200:
            return response.text
        else:
            self._logger.error(
                f"Error fetching the file: {response.status_code} - {response.reason}")
            raise ModelScraperError(
                f"Error fetching the file: {response.status_code} - {response.reason}")

    def _extract_models(self, data: str) -> Dict[str, Dict[str, Union[str, int]]]:
        """
        Extracts the models information from the given data.
        """
        models = {}
        pattern = re.compile(r'(.+?)\s+(\d+x\d+)')
        for line in data[data.find('Model name'):].splitlines():
            if line.startswith('['):
                model_name_with_size = line[1:line.find(']')]

                match = pattern.match(model_name_with_size)
                if match:
                    model_name, size = match.groups()
                    download_link = line[line.find('(')+1:line.find(')')]
                    speed, coco_map, output = line.split('|')[1:]

                    if output.strip() == 'Boxes':
                       
                        models[model_name] = {
                            "model_name": model_name,
                            "size": size,
                            "download_link": download_link,
                            "speed": int(speed.strip()),
                            "coco_map": coco_map.strip(),
                            "output": output.strip(),
                            "downloaded": False,
                            "downloaded_path": None
                        }
                    
        return models
