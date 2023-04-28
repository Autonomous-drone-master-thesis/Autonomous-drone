"""This module contains the DroneConnectionDialog class, which is responsible for 
displaying the drone connection dialog."""

from kivymd.uix.dialog import MDDialog

class DroneConnectionDialog(MDDialog):
    """DroneConnectionDialog class is a MDDialog that displays the tracker drone 
    connection dialog to the application."""

    def __init__(self, **kwargs):
        super().__init__(
            title="Connecting",
            text="Connecting to drone. Please wait...",
            type="custom",
            **kwargs
        )