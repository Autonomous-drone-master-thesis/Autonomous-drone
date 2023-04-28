"""This module contains the DroneConnectionErrorDialog class, which is responsible for 
displaying the drone connection error dialog."""

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class DroneConnectionErrorDialog(MDDialog):
    """DroneConnectionErrorDialog class is a MDDialog that displays the tracker drone 
    connection error dialog to the application."""

    def __init__(self, **kwargs):
        super().__init__(
            title="Connection Error",
            text="The drone is not connected. Please connect to the drone wifi and try again.",
            type="custom",
            buttons=[
                MDFlatButton(
                    text="Dismiss", on_release=lambda x: self.dismiss()
                ),
            ],
            **kwargs
        )
