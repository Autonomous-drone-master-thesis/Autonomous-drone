"""This module contains the DebugUI class, which is responsible for 
displaying the debug settings page."""

from kivy.logger import Logger
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from helpers import load_kv_file_for_class, SettingsHandler, SettingsKeys

load_kv_file_for_class("index.kv")

class DebugUI(BoxLayout):
    """DebugUI class is a BoxLayout that displays the debug settings page 
    of the application."""

    debug_mode = BooleanProperty(False)
    debug_mode_text = StringProperty("Debug mode - Not active")

    def __init__(self, settings: SettingsHandler, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings
        self.debug_mode = self.settings.get_value(SettingsKeys.DEBUG_MODE)
        self._update_debug_mode_text()

    def toggle_debug_mode(self) -> None:
        """
        Toggle the debug mode on or off.
        """
        self.debug_mode = not self.debug_mode
        self.settings.set_value(SettingsKeys.DEBUG_MODE, self.debug_mode)
        Logger.info("Debug Component: Debug mode set to %s", self.debug_mode)
        self._update_debug_mode_text()

    def _update_debug_mode_text(self) -> None:
        """
        Update the debug mode text.
        """
        if self.debug_mode:
            self.debug_mode_text = "Debug mode - Active"
        else:
            self.debug_mode_text = "Debug mode - Not active"
