from functools import partial
from math import ceil, floor

import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from .base_widgets import (CollapsibleBox, CoolButton, CoolCheckBox,
                           CustomRangeSlider, CustomSlider,
                           HorizontalBarWidget, PictureCheckBox, QualityIcon)
from .config import CustomConfigParser
from .constants import PATH_ASSETS, QUALITIES_AVAILABLE, RENEWED_EXPANSIONS
from .utils import override


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
        self.toggle_all_button = CoolButton(text="Select all", fontsize="10px")
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

class ExpansionNumSlider(QW.QWidget):
    def __init__(self, config: CustomConfigParser):
        super().__init__()
        self.config = config

        # The maximum of the slider
        self.limiting_num = 5

        self._init_slider_with_labels()

        overarching_layout = QW.QHBoxLayout(self)
        overarching_layout.setContentsMargins(0, 0, 0, 0)
        
        self.display_label = QW.QLabel("")
        self.display_label.setAlignment(QC.Qt.AlignTop)
        self.display_label.setFixedWidth(200)
        overarching_layout.addWidget(self.display_label)
        overarching_layout.addWidget(self.slider_wid)
        overarching_layout.addStretch()
        self._set_initial_value()

    def _set_initial_value(self):
        num_exp_val =self.config.getint("General", "max_num_expansions")
        self.slider.setValue(num_exp_val)
        self.set_max_expansion_num()

    def _init_slider_with_labels(self):
        self.slider_wid = QW.QWidget()
        layout = QW.QVBoxLayout(self.slider_wid)
        layout.setContentsMargins(0, 0, 0, 0)

        self.slider = CustomSlider(0, self.limiting_num)
        self.slider.setFixedWidth(300)
        self.slider.valueChanged.connect(self.set_max_expansion_num)
        self.slider.setTickPosition(QW.QSlider.TicksBelow)


        self.labels_widget = QW.QWidget()
        lay = QW.QHBoxLayout(self.labels_widget)
        lay.setContentsMargins(0, 0, 3, 0)
        for tick in range(0, self.limiting_num+1):
            label_text = str(tick) if tick != 0 else "all"
            label = QW.QLabel(label_text)
            label.setAlignment(QC.Qt.AlignCenter)
            lay.addWidget(label)
            if tick < self.limiting_num:
                lay.addItem(
                    QW.QSpacerItem(
                        0, 0, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
                    )
                )
        lay.setAlignment(QC.Qt.AlignTop)
        layout.addWidget(self.slider)
        layout.addWidget(self.labels_widget)

    def set_max_expansion_num(self):
        value = self.slider.value()
        self.config.set("General", "max_num_expansions", str(value))
        if value == 0:
            text = "Pick from all expansions"
        else:
            text = f"Pick from at max {value} expansions."
        self.display_label.setText("<b>Maximum expansion number:</b><br>" + text)

class ExpansionGroupWidget(GroupCheckboxButtonContainer):
    """Container for the expansion group."""

    def __init__(self, all_expansions: list[str], config: CustomConfigParser):
        self.config = config
        names = [exp for exp in all_expansions if exp not in RENEWED_EXPANSIONS]
        tooltips = [f"Randomize cards from the {exp} expansion." for exp in names]
        super().__init__(names, "Expansions", tooltips, initially_collapsed=False)
        self.max_expansion_slider = ExpansionNumSlider(config)
        self.content_layout.addWidget(self.max_expansion_slider)

        self._set_initial_values()
        self.connect_to_change_func(self.update_config_for_expansions)

    def update_config_for_expansions(self):
        """Reads out the currently selected expansions and saves them. Also changes the selection."""
        selected_exps = self.get_names_of_selected()
        self.config.set_expansions(selected_exps)

    def _set_initial_values(self):
        for exp in self.config.get_expansions(add_renewed_bases=False):
            self.widget_dict[exp].setChecked(True)
        self.set_toggle_button_text()
    

    @override
    def get_icon_path(self, name: str) -> str:
        """Returns the image path for the given expansion icon."""
        base = PATH_ASSETS.joinpath("icons/expansions/")
        conversion_dict = {}
        for outdated_exp in RENEWED_EXPANSIONS:
            conversion_dict[outdated_exp + ", 1E"] = outdated_exp + "_old"
            conversion_dict[outdated_exp + ", 2E"] = outdated_exp
        if name in conversion_dict:
            name = conversion_dict[name]
        return str(base.joinpath(name.replace(" ", "_") + ".png"))


class AttackTypeGroupWidget(GroupCheckboxButtonContainer):
    """Container for selecting the AttackTypes"""

    def __init__(self, all_attack_types: list[str], config: CustomConfigParser):
        self.config = config
        tooltips = [
            f"Toggle exclusion of the {type_} attack type."
            for type_ in all_attack_types
        ]
        super().__init__(all_attack_types, "Allowed attack types", tooltips)

        self._set_initial_values()
        self.connect_to_change_func(self.update_config_for_attack_types)

    def update_config_for_attack_types(self):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        selected_types = self.get_names_of_selected()
        self.config.set_special_list("attack_types", selected_types)

    def _set_initial_values(self):
        for exp in self.config.get_special_list("attack_types"):
            self.widget_dict[exp].setChecked(True)
        self.set_toggle_button_text()

    @override
    def get_icon_path(self, name: str) -> str:
        """Returns the image path for the given attack icon."""
        fpath = PATH_ASSETS.joinpath(f"icons/attack_types/{name}.png")
        return str(fpath)


class GeneralRandomizerSettingsWidget(CollapsibleBox):
    def __init__(self, config: CustomConfigParser):
        super().__init__(title="General settings", initially_collapsed=False)
        self.config = config

        lay = QW.QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)

        self._init_landscape_slider()
        lay.addWidget(self.landscape_widget)
        self.setContentLayout(lay)
        self._set_initial_values()

    def _init_landscape_slider(self):
        self.landscape_widget = QW.QWidget()
        lay = QW.QHBoxLayout(self.landscape_widget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.num_landscapes_range_slider = CustomRangeSlider()
        self.num_landscapes_range_slider.setFixedWidth(300)
        self.num_landscapes_label = QW.QLabel("")
        self.num_landscapes_label.setAlignment(QC.Qt.AlignTop)
        self.num_landscapes_label.setFixedWidth(200)
        self.num_landscapes_range_slider.value_changed.connect(
            self.register_num_landscape_change
        )
        lay.addWidget(self.num_landscapes_label)
        lay.addWidget(self.num_landscapes_range_slider)
        lay.addStretch()
        lay.setAlignment(QC.Qt.AlignTop)

    def _set_initial_values(self):
        """Set the initial state given the state of the config."""
        min_val = self.config.getint("General", "min_num_landscapes")
        max_val = self.config.getint("General", "max_num_landscapes")
        self.num_landscapes_range_slider.set_values(min_val, max_val)

    def register_num_landscape_change(self):
        """Displays the values of the range-slider in the text label
        and saves them to config"""
        min_val, max_val = self.num_landscapes_range_slider.get_values()
        self.config.set("General", "min_num_landscapes", str(min_val))
        self.config.set("General", "max_num_landscapes", str(max_val))
        if min_val == max_val:
            text = f"Allow exactly {min_val} landscapes."
        else:
            text = f"Allow between {min_val} and {max_val} landscapes."
        self.num_landscapes_label.setText("<b>Landscape amount:</b><br>" + text)


class SingleQualitySelectionWidget(QW.QWidget):
    """One row to set the requested value of the quality, including
    a slider for flexibility, and a checkbox to exclude the given
    quality completely.

    Parameters
    ----------
    qual : str
        The quality to display
    config : CustomConfigParser
        The ConfigParser to store the data at.
    """

    def __init__(self, qual: str, config: CustomConfigParser):
        super().__init__()
        self.config = config
        self.qual_name = qual

        self.icon = QualityIcon(qual)

        self.label = QW.QLabel(
            f"{qual.capitalize()}:\nDesired minimum {qual} quality of the kingdom."
        )
        # The slider to select the requested quality:
        tooltip = f"Upon randomization, we will try to achieve at least this amount of {qual} quality in the kingdom."
        self.selection_box = HorizontalBarWidget(clickable=True)
        self.selection_box.setToolTip(tooltip)
        self.selection_box.setFixedSize(80, 20)
        self.selection_box.clicked.connect(self.set_quality)

        # The checkbox to exclude this quality:
        self.forbid_this_box = CoolCheckBox(
            f"No {qual}",
            "Completely exclude any card that shows this quality from the draw pool",
        )
        self.forbid_this_box.clicked.connect(self.toggle_forbid_quality)

        lay = QW.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.icon)
        lay.addWidget(self.selection_box)
        lay.addWidget(self.label)
        lay.addWidget(self.forbid_this_box)

        self._set_initial_state()

    def _set_initial_state(self):
        self.selection_box.setValue(self.config.get_requested_quality(self.qual_name))
        is_disabled = self.config.get_forbidden_quality(self.qual_name)
        self.forbid_this_box.setChecked(is_disabled)
        self.selection_box.setDisabled(is_disabled)
        self.icon.set_overlay_cross(is_disabled)
        self.label.setDisabled(is_disabled)

    @QC.pyqtSlot()
    def set_quality(self):
        """Set the desired quality."""
        value = self.selection_box.getValue()
        self.config.set_requested_quality(self.qual_name, value)

    @QC.pyqtSlot()
    def toggle_forbid_quality(self):
        """Handle the toggling of the checkbox and save its value to the config.
        If it is checked, the selection box is disabled."""
        new_state = self.forbid_this_box.isChecked()
        self.selection_box.setDisabled(new_state)
        self.label.setDisabled(new_state)
        self.icon.set_overlay_cross(new_state)
        self.config.set_forbidden_quality(self.qual_name, new_state)

    def reset_state(self):
        """Reset this widget's state to default values."""
        self.selection_box.setValue(0)
        self.forbid_this_box.setChecked(False)
        self.forbid_this_box.clicked.emit(False)


class QualitySelectionGroupWidget(CollapsibleBox):
    def __init__(self, config: CustomConfigParser):
        super().__init__(title="Quality parameters", initially_collapsed=False)

        lay = QW.QVBoxLayout()
        self.wid_dict: dict[str, SingleQualitySelectionWidget] = {}
        for qual in QUALITIES_AVAILABLE:
            wid = SingleQualitySelectionWidget(qual, config)
            self.wid_dict[qual] = wid
            lay.addWidget(wid)
        self.reset_button = self.init_reset_button()
        lay.addWidget(self.reset_button)
        self.setContentLayout(lay)

    def init_reset_button(self) -> QW.QWidget:
        """Create a button to click on for resetting all values."""
        # TODO: Maybe implement a master slider to change everything at once?
        button = CoolButton(text="Reset preferences", width=200)
        button.clicked.connect(self.on_reset_clicked)
        return button

    # @QC.pyqtSlot()
    def on_reset_clicked(self):
        """Reset all the QualitySelection widgets."""
        for wid in self.wid_dict.values():
            wid.reset_state()


def create_buttons():
    button_dict = {}
    button_dict["Randomize"] = CoolButton(text="Randomize")
    button_dict["PrintKingdom"] = CoolButton(text="Print the kingdom")
    button_dict["Previous"] = CoolButton(text="Previous")
    button_dict["Next"] = CoolButton(text="Next")
    return button_dict
