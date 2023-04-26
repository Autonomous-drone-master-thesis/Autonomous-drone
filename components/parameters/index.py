"""This module contains the ParametersUI class, which is responsible for 
displaying the parameters settings page."""

from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout

from helpers import load_kv_file_for_class, SettingsKeys

from .height_input import HeightInputDialog
from .tracking_input import TrackingInputDialog
from .model_selection import ModelSelectionDialog, ItemConfirm

load_kv_file_for_class("index.kv")


class ParametersUI(BoxLayout):
    """ParametersUI class is a BoxLayout that displays the parameters settings page 
    of the application."""

    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.selected_model = None

    def show_height_input(self) -> None:
        """Show the height input dialog for entering the person's height."""
        Logger.info("Parameters Component: Showing height input dialog")
        dialog = HeightInputDialog(self.save_height)
        dialog.open()

    def save_height(self, height: int) -> None:
        """
        Save the entered person's height.
        
        :param height: The person's height.
        """
        Logger.info("Parameters Component: Saving height: %s", height)
        self.main_app.settings_handler.set_value(SettingsKeys.PERSON_HEIGHT, height)

    def show_tracking_input(self) -> None:
        """Show the tracking input dialog for entering the tracking height and distance."""
        Logger.info("Parameters Component: Showing tracking input dialog")
        dialog = TrackingInputDialog(self.save_tracking)
        dialog.open()

    def save_tracking(self, height: int, distance: int) -> None:
        """
        Save the entered tracking height and distance.
        
        :param height: The tracking height.
        :param distance: The tracking distance.
        """
        Logger.info(
            "Parameters Component: Saving tracking height: %s and distance: %s",
            height,
            distance
            )
        self.main_app.settings_handler.set_value(SettingsKeys.TRACKING_HEIGHT, height)
        self.main_app.settings_handler.set_value(SettingsKeys.TRACKING_DISTANCE, distance)

    def show_model_selection_select(self) -> None:
        """Show the model selection dialog for choosing a human tracker model."""
        Logger.info("Parameters Component: Showing model selection dialog")
        current_settings = self.main_app.settings_handler.get_value(
            SettingsKeys.SELECTED_OBJECT_DETECTION_MODEL
            )

        items = []
        index = 0
        for model in self.main_app.models_handler.read_data().values():
            if model["downloaded"]:
                active = model == current_settings if current_settings else index == 0
                items.append(ItemConfirm(model, self, active))
                index += 1

        dialog = ModelSelectionDialog(items, self.save_model_selection)
        dialog.open()

    def save_model_selection(self) -> None:
        """Save the selected human tracker model."""
        Logger.info("Parameters Component: Saving model selection: %s", self.selected_model)
        self.main_app.settings_handler.set_value(
            SettingsKeys.SELECTED_OBJECT_DETECTION_MODEL,
            self.selected_model
        )
