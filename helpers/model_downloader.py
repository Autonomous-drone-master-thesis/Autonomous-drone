"""
Module for downloading models concurrently using asyncio and aiohttp.
"""

import asyncio
import logging
import os
import threading
from typing import Callable, Optional

import aiohttp

# pylint: disable=E0611
from tensorflow.python.keras.utils.data_utils import get_file

from .file_handlers import ModelsHandler

#TODO: Remove this
os.environ['http_proxy'] = 'http://10.246.170.130:3128'
os.environ['https_proxy'] = 'https://10.246.170.130:3128'

class ModelDownloader:
    """
    A class for downloading models concurrently using asyncio and aiohttp.
    """

    def __init__(
        self,
        data_path: str,
        models_handler: ModelsHandler,
        cache_dir: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize the ModelDownloader object with the specified cache directory and callback.

        :param data_path: The path to the data directory.
        :param models_handler: The ModelsHandler object.
        :param cache_dir: Optional; the directory where the downloaded models will be stored.
                          If not provided, defaults to './models/'.
        :param callback: Optional; a function to be called with the path of each downloaded model.
        :param logger: A logger instance to use for logging messages.
        """
        self._data_path = data_path
        self._models_handler = models_handler
        self._cache_dir = cache_dir or "./models/"
        self._callback = callback
        self._logger = logger or logging.getLogger(__name__)
        self._downloaded_models = []

    def download_models_threaded(self, model_urls: list) -> None:
        """
        Download the models from the given URLs concurrently on a separate thread.

        :param model_urls: A list of URLs of the models to download.
        """
        threading.Thread(target=self._download_models_async, args=(model_urls,)).start()

    def _download_models_async(self, model_urls: list) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.download_models(model_urls))
        loop.close()

        self._remove_archive_files()
        self._save_path_to_models()

    async def download_models(self, model: dict) -> list:
        """
        Download the models from the given URLs concurrently.

        :param model: A dictionary with model information.
        :return: A list of paths to the downloaded model directories.
        """
        async with aiohttp.ClientSession():
            tasks = [self._download_model(model_url) for model_url in model]
            return await asyncio.gather(*tasks)

    def _get_file_wrapper(self, file_name, download_link, cache_dir) -> None:
        return get_file(
            fname=file_name,
            origin=download_link,
            cache_dir=cache_dir,
            cache_subdir="checkpoints",
            extract=True,
        )

    async def _download_model(self, model: dict) -> None:
        """
        Download a single model from the given URL.

        :param model: A dictionary with model information.
        """
        download_link = model["download_link"]

        file_name = os.path.basename(download_link)

        os.makedirs(self._cache_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._get_file_wrapper,
            file_name,
            download_link,
            self._cache_dir
            )

        model_name = model["model_name"]

        if self._callback is not None:
            self._callback(model_name)

        file_name = file_name.split(".")[0]

        self._downloaded_models.append(
            [model_name, f"{self._cache_dir}checkpoints/{file_name}/saved_model"]
            )

    def _remove_archive_files(self) -> None:
        """
        Remove the downloaded archive files.
        """
        folder_path = f"{self._cache_dir}checkpoints/"

        for file in os.listdir(folder_path):
            if file.endswith(".tar.gz") and os.path.isfile(os.path.join(folder_path, file)):
                os.remove(os.path.join(folder_path, file))
                self._logger.info(f"Removed file:{file}")

    def _save_path_to_models(self) -> None:
        """
        Save the downloaded model paths to models.json.
        """
        existing_models = self._models_handler.read_data()

        self._logger.info("Saving path models")
        for downloaded_model in self._downloaded_models:
            model = existing_models[downloaded_model[0]]
            model["downloaded_path"] = downloaded_model[1]
            model["downloaded"] = True
        self._models_handler.write_data(existing_models)
        self._logger.info("Models modified successfully")
