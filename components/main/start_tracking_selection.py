"""This module contains the StartTrackingSelectionDialog class, which is responsible for 
displaying the start tracking selection dialog for starting the tracking process."""

from typing import Callable

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class StartTrackingSelectionDialog(MDDialog):
    """StartTrackingSelectionDialog class is a MDDialog that displays the start tracking dialog
    to the application."""

    def __init__(self, callback: Callable, **kwargs):
        super().__init__(
            title="Start tracking?",
            text="Do you wish to start drone tracking?",
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
