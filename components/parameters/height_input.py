"""This module contains the HeightInputDialog class, which is responsible for 
displaying the height input dialog for entering the person's height."""

from typing import Callable

from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton


class HeightInputDialog(MDDialog):
    """HeightInputDialog class is a MDDialog that displays the height input dialog 
    to the application."""

    def __init__(self, callback: Callable, **kwargs):
        height_input = MDTextField(hint_text="Enter height (in cm)", mode="rectangle")
        super().__init__(
            title="Person Height",
            type="custom",
            content_cls=height_input,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dismiss()),
                MDFlatButton(text="OK", on_release=lambda x: (
                                callback(height_input.text),
                                self.dismiss()
                                )
                             ),
            ],
            **kwargs
        )
