"""This module contains the LandingUI class, which is responsible for 
displaying the landing page."""

from kivy.uix.boxlayout import BoxLayout

from helpers import load_kv_file_for_class

load_kv_file_for_class("index.kv")

class LandingUI(BoxLayout):
    """LandingUI class is a BoxLayout that displays the landing page of the application."""
