"""This module contains the TrackingInputDialog class, which is responsible for 
displaying the height and distance input for tracking."""

from typing import Callable

from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout

class TrackingInputDialog(MDDialog):
    """TrackingInputDialog class is a MDDialog that displays the height and distance input
    dialog to the application."""

    def __init__(self, callback: Callable, **kwargs):
        tracking_height_input = MDTextField(
            hint_text="Enter tracking height (in cm)",
            mode="rectangle"
            )
        tracking_distance_input = MDTextField(
            hint_text="Enter tracking distance (in cm)",
            mode="rectangle"
            )

        super().__init__(
            title="Tracking Height and Distance",
            type="custom",
            content_cls=MDBoxLayout(
                tracking_height_input,
                tracking_distance_input,
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="120dp",
            ),
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dismiss()),
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (
                        callback(tracking_height_input.text, tracking_distance_input.text),
                        self.dismiss(),
                    ),
                ),
            ],
            **kwargs
        )
