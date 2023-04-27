"""This module contains the VideoSelectionDialog class, which is responsible for 
displaying the video selection dialog for selecting if a video should be recorded."""

from typing import Callable

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class VideoSelectionDialog(MDDialog):
    """VideoSelectionDialog class is a MDDialog that displays the video selection dialog
    to the application."""

    def __init__(self, callback: Callable, **kwargs):
        super().__init__(
            title="Record video?",
            text="Do you wish to record a video?",
            type="custom",
            buttons=[
                MDFlatButton(
                    text="No", on_release=lambda x: (callback(False), self.dismiss())
                ),
                MDFlatButton(
                    text="Yes", on_release=lambda x: (callback(True), self.dismiss())
                )
            ],
            **kwargs
        )
