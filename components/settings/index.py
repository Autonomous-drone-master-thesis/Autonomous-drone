"""This module contains the SettingsUI class, which is responsible for 
displaying the settings page."""

from kivy.uix.boxlayout import BoxLayout

from helpers import load_kv_file_for_class

load_kv_file_for_class("index.kv")


class SettingsUI(BoxLayout):
    """SettingsUI class is a BoxLayout that displays the settings page of the application."""
