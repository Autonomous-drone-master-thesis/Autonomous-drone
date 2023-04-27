"""This module contains the TrackerSelectionDialog class, which is responsible for 
displaying the tracker selection dialog for selecting the tracker mode."""

from typing import Callable

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class TrackerSelectionDialog(MDDialog):
    """TrackerSelectionDialog class is a MDDialog that displays the tracker selection dialog
    to the application."""

    def __init__(self, callback: Callable, **kwargs):
        super().__init__(
            title="Select Tracker Mode",
            text="Choose between Face Tracker Mode or Human Tracker Mode:",
            type="custom",
            buttons=[
                MDFlatButton(
                    text="Face Tracker", on_release=lambda x: (callback("face_tracker"), self.dismiss())
                ),
                MDFlatButton(
                    text="Human Tracker", on_release=lambda x: (callback("human_tracker"), self.dismiss())
                )
            ],
            **kwargs
        )
