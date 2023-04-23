import os
import asyncio
import aiohttp
import json
import threading
from typing import Optional, Callable
from tensorflow.python.keras.utils.data_utils import get_file


class ModelDownloader:
    def __init__(self, data_path: str, cache_dir: Optional[str] = None, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Initialize the ModelDownloader object with the specified cache directory and callback.

        :param data_path: The path to the data directory.
        :param cache_dir: Optional; the directory where the downloaded models will be stored.
                          If not provided, defaults to './models/'.
        :param callback: Optional; a function to be called with the path of each downloaded model.
        """
        self._data_path = data_path
        self.cache_dir = cache_dir or "./models/"
        self.callback = callback
        self.downloaded_models = []

    def download_models_threaded(self, model_urls: list) -> None:
        """
        Download the models from the given URLs concurrently on a separate thread.

        :param model_urls: A list of URLs of the models to download.
        """
        threading.Thread(target=self._download_models_async,
                         args=(model_urls,)).start()

    def _download_models_async(self, model_urls: list) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.download_models(model_urls))
        loop.close()

        self._save_path_to_models()

    async def download_models(self, model: dict) -> list:
        """
        Download the models from the given URLs concurrently.

        :param model: A dictionary with model information.
        :return: A list of paths to the downloaded model directories.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self._download_model(model_url)
                     for model_url in model]
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

        os.makedirs(self.cache_dir, exist_ok=True)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._get_file_wrapper, file_name, download_link, self.cache_dir)

        model_name = model["model_name"]

        if self.callback is not None:
            self.callback(model_name)

        self.downloaded_models.append(
            [model_name, f"{self.cache_dir}/checkpoints/{model_name}/saved_model"])

    def _save_path_to_models(self) -> None:
        """
        Save the downloaded model paths to models.json.
        """

        models_file = os.path.join(self._data_path, "models.json")
        data = {}

        with open(models_file, 'r+') as f:
            data = json.load(f)
            for downloaded_model in self.downloaded_models:
                model = data[downloaded_model[0]]
                model["downloaded_path"] = downloaded_model[1]
                model["downloaded"] = True
            f.seek(0)
            f.truncate(0)
            json.dump(data, f, indent=2)

