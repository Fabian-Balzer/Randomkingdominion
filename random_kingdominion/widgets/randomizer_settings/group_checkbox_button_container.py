
from math import floor

import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from ..basic_widgets import CollapsibleBox, CustomButton, PictureCheckBox


class GroupCheckboxButtonContainer(CollapsibleBox):
    """A widget containing a grouped Checkbox buttons."""

    def __init__(
        self,
        names: list[str],
        description: str,
        tooltips: list[str] | None = None,
        num_cols=4,
        initially_collapsed: bool = True,
    ):
        super().__init__(title=description, initially_collapsed=initially_collapsed)
        self.description = description
        names = sorted(names)

        widget_dict: dict[str, PictureCheckBox] = {}
        for name, tooltip in zip(names, tooltips):
            icon_path = self.get_icon_path(name)
            checkbox = PictureCheckBox(name, icon_path=icon_path, tooltip=tooltip)
            widget_dict[name] = checkbox

        self.widget_dict = widget_dict
        self.toggle_all_button = CustomButton(text="Select all", fontsize="10px")
        self.toggle_all_button.clicked.connect(self.toggle_all_checkbox_buttons)

        self._init_layout(num_cols)

    def get_icon_path(self, name: str):
        """To be overridden"""
        return str(name)

    def _init_layout(self, num_cols):
        layout = QW.QGridLayout(self)
        layout.setContentsMargins(5, 0, 5, 5)
        # num_items = len(self.widget_dict) + 1
        # num_rows = ceil(num_items / num_cols)
        widget_list = list(self.widget_dict.values()) + [self.toggle_all_button]
        for i, widget in enumerate(widget_list):
            row = floor(i / num_cols)
            col = i - row * num_cols
            layout.addWidget(widget, row, col)
        layout.setAlignment(QC.Qt.AlignTop | QC.Qt.AlignLeft)
        super().setContentLayout(layout)

    def connect_to_change_func(self, func: callable):
        """Connect all of the buttons to the functions toggling them."""
        for widget in self.widget_dict.values():
            widget.clicked.connect(widget.toggle)
            widget.clicked.connect(func)
        self.toggle_all_button.clicked.connect(self.set_toggle_button_text)
        self.toggle_all_button.clicked.connect(func)

    def _are_all_boxes_checked(self) -> bool:
        return all(checkbox.isChecked() for checkbox in self.widget_dict.values())

    def toggle_all_checkbox_buttons(self):
        """Collectively toggle all checkbox_buttons in the group."""
        new_check_value = not self._are_all_boxes_checked()
        for checkbox in self.widget_dict.values():
            checkbox.setChecked(new_check_value)
        self.set_toggle_button_text()

    def set_toggle_button_text(self):
        """Have the button represent whether to select or deselect everything"""
        if self._are_all_boxes_checked():
            self.toggle_all_button.setText("Deslect all")
        else:
            self.toggle_all_button.setText("Select all")

    def get_names_of_selected(self) -> list[str]:
        """Get the names of all checkbox_buttons that are currently selected."""
        selected_names = [
            name for name, checkbox in self.widget_dict.items() if checkbox.isChecked()
        ]
        return selected_names
