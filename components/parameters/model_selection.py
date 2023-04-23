"""This module contains the ModelSelectionDialog and ItemConfirm classes, which are responsible for 
displaying model selection dialog."""

from typing import Callable, List

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem


class ItemConfirm(TwoLineAvatarIconListItem):
    """ItemConfirm class is a TwoLineAvatarIconListItem that generates a new list item."""

    divider = None

    def __init__(
        self,
        model: dict,
        parameters: "ParametersUI",
        active: bool,
        **kwargs
        ):
        super().__init__(**kwargs)
        self.model = model
        self.text = model["model_name"]
        self.secondary_text = (
            f"Size: {model['size']} "
            f"Speed: {model['speed']} ms "
            f"Output: {model['output']} "
            f"CocoMap: {model['coco_map']}"
        )
        self._no_ripple_effect = True
        self.parameters = parameters
        if active:
            self.set_icon(self.ids.check)

    def set_icon(self, instance_check) -> None:
        """
        Set the icon for the selected model in the list.

        :param instance_check: The instance of the checkbox that is selected."""
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False
        self.parameters.selected_model = self.model


class ModelSelectionDialog(MDDialog):
    """ModelSelectionDialog class is a MDDialog that displays model selection dialog
    to the application."""

    def __init__(self, items: List[ItemConfirm], callback: Callable, **kwargs):
        super().__init__(
            title="Model Selection",
            type="confirmation",
            items=items,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.dismiss()),
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (callback(), self.dismiss()),
                ),
            ],
            **kwargs,
        )
