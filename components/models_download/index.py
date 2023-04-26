"""This module contains the ModelsDownloadUI class, which is responsible for 
displaying the models download UI."""

from typing import Callable

# pylint: disable=E0611
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import IRightBodyTouch, TwoLineAvatarIconListItem

from helpers import load_kv_file_for_class, ModelDownloader, ModelsHandler

load_kv_file_for_class("index.kv")


class ModelListItem(TwoLineAvatarIconListItem):
    """
    Item for the list of models to download.
    """

    def __init__(self, model: dict, **kwargs):
        super().__init__(**kwargs)
        self.download_link = model["download_link"]
        self.text = model["model_name"]
        self.secondary_text = (
            f"Size: {model['size']} "
            f"Speed: {model['speed']} ms "
            f"Output: {model['output']} "
            f"CocoMap: {model['coco_map']} "
        )
        self._no_ripple_effect = True


class ModelListItemRight(IRightBodyTouch, MDCheckbox):
    """
    Right side of the list item, contains the checkbox.
    """

    def __init__(self, model: dict, on_check: Callable, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.on_check = on_check

    # pylint: disable=[W0221, W0613]
    def on_active(self, checkbox, value: bool) -> None:
        """Runs when the checkbox is checked or unchecked.

        Args:
            checkbox: Checkbox instance.
            value (bool): True if the checkbox is checked, False otherwise.
        """
        self.on_check(self.model, value)


class ModelsDownloadUI(BoxLayout):
    """
    ModelsDownloadUI class is a BoxLayout that displays the models download page
    of the application.
    """

    selection_list = ObjectProperty(None)

    def __init__(self, model_handler: ModelsHandler, data_path: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model_handler = model_handler
        self.data_path = data_path
        self.selected_models = {}
        self._populate_list()

    def download_selected_models(self):
        """
        Downloads the selected models.
        """

        # TODO: Add notification call instead of print
        def on_complete(model_name):
            print(f"Downloaded {model_name}")

        downloader = ModelDownloader(self.data_path, self.model_handler, callback=on_complete)
        downloader.download_models_threaded(self.selected_models.values())

    def _populate_list(self) -> None:
        """
        Private method that populates the list of models to download from the models.json file.
        """
        data = self.model_handler.read_data()
        for model in data.values():
            if not model["downloaded"]:
                list_item = ModelListItem(model)
                list_item.add_widget(ModelListItemRight(model, self._on_model_check))
                self.selection_list.add_widget(list_item)

    # TODO: Unify doc-strings
    def _on_model_check(self, model: dict, is_checked: bool) -> None:
        """Callback for when a model is checked or unchecked.

        Args:
            model (dict): Model dictionary.
            is_checked (bool): True if the model is checked, False otherwise.
        """
        if is_checked:
            self.selected_models[model["model_name"]] = model
        else:
            self.selected_models.pop(model["model_name"], None)
