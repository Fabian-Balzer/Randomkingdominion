from functools import partial
from math import ceil, floor

import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from .base_widgets import (
    CollapsibleBox,
    CoolButton,
    CoolCheckBox,
    CoolComboBox,
    CoolSpinBox,
    PictureCheckBox,
    group_widgets,
)
from .constants import PATH_MAIN, QUALITIES_AVAILABLE, RENEWED_EXPANSIONS
from .kingdom import KingdomDisplayWidget
from .utils import get_attack_icon, get_expansion_icon


class GroupCheckboxButtonContainer(CollapsibleBox):
    """A widget containing a grouped Checkbox buttons."""

    def __init__(
        self,
        names: list[str],
        description: str,
        tooltips: list[str] | None = None,
        num_cols=4,
    ):
        super().__init__(title=description)
        self.description = description
        names = sorted(names)

        widget_dict: dict[str, PictureCheckBox] = {}
        for name, tooltip in zip(names, tooltips):
            icon = get_expansion_icon(name)
            checkbox = PictureCheckBox(name, icon=icon, tooltip=tooltip)
            widget_dict[name] = checkbox

        self.widget_dict = widget_dict
        self.toggle_all_button = CoolButton(text="Select all", fontsize="10px")
        self.toggle_all_button.clicked.connect(self.toggle_all_checkbox_buttons)

        self._init_layout(num_cols)

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


class ExpansionGroupWidget(GroupCheckboxButtonContainer):
    """Container for the expansion group."""

    def __init__(self, all_expansions: list[str]):
        names = [exp for exp in all_expansions if exp not in RENEWED_EXPANSIONS]
        tooltips = [f"Randomize cards from the {exp} expansion." for exp in names]
        super().__init__(names, "Expansions", tooltips)
        self.on_button_pressed()


def create_checkboxes(all_attack_types, button_dict):
    checkbox_dict = {}

    box_dict = {}
    tooltips = [
        f"Require attack of {type_} in selection." for type_ in all_attack_types
    ]
    for name, tooltip in zip(all_attack_types, tooltips):
        icon = get_attack_icon(name)
        checkbox = PictureCheckBox(name, icon=icon, tooltip=tooltip)
        box_dict[name] = checkbox
    button_dict["AttackTypeToggle"] = CoolButton(
        text="Select all attack types", fontsize="10px"
    )
    checkbox_dict["AttackTypeDict"] = box_dict
    explist = [box_dict[key] for key in sorted(box_dict.keys())] + [
        button_dict["AttackTypeToggle"]
    ]
    checkbox_dict["AttackTypeGroup"] = group_widgets(
        explist, "Allowed attack types for randomization", num_cols=4
    )
    return checkbox_dict


def create_checkbox_group(names, kind, button_dict):
    """Creates a dictionary containing all checkboxes for set selection and a group
    widget containing all of them for display."""
    box_dict = {}
    if kind == "Expansions":
        names = [exp for exp in names if exp not in RENEWED_EXPANSIONS]
        tooltips = [f"Randomize cards from the {exp} expansion." for exp in names]
    elif kind == "Attack Types":
        tooltips = [f"Require attack of {type_} in selection." for type_ in names]
    select_all_button = CoolButton(text=f"Select all {kind}", fontsize="10px")
    refname = "AttackType" if kind == "Attack Types" else kind
    button_dict[f"{refname}Toggle"] = select_all_button
    num_rows = 6 if kind == "Expansions" else 2
    explist = [box_dict[key] for key in sorted(box_dict.keys())] + [select_all_button]
    return box_dict, group_widgets(
        explist, f"{kind} used for randomization", num_rows=num_rows
    )


def create_buttons():
    button_dict = {}
    button_dict["Randomize"] = CoolButton(text="Randomize")
    button_dict["PrintKingdom"] = CoolButton(text="Print the kingdom")
    button_dict["Previous"] = CoolButton(text="Previous")
    button_dict["Next"] = CoolButton(text="Next")
    return button_dict


def create_comboboxes():
    box_dict = {}
    box_dict["QualityDict"], box_dict["QualityGroup"] = create_combobox_group()
    return box_dict


def create_combobox_group():
    qual_dict = {}
    possibilities = ["None", "Weak", "Medium", "Strong", "Extra strong"]
    group_list = []
    for qual in QUALITIES_AVAILABLE:
        qual = qual.lower()
        label = QW.QLabel(f"Minimum {qual} quality of the kingdom:")
        tooltip = f"Set the minimum {qual} quality for the randomized kingdom"
        box = CoolComboBox(possibilities, 1, tooltip=tooltip, width=100)
        subgroup = group_widgets([label, box], collapsible=False)
        group_list.append(subgroup)
        qual_dict["min_" + qual] = box
    # for other, val in {"AttackStrength": "attack strength", "InteractivityValue": "interactivity value"}.items():
    #     label = QW.QLabel(f"Minimum {val} of the kingdom:")
    #     tooltip = f"Set the minimum {val} for the randomized kingdom"
    #     box = coolComboBox(possibilities, 1, tooltip=tooltip, width=100)
    #     subgroup = group_widgets([label, box])
    #     group_list.append(subgroup)
    #     qual_dict[other] = box
    return qual_dict, group_widgets(
        group_list, "Parameters used for randomization", num_rows=len(group_list)
    )


def create_vboxlayout(name, parent, row, col, rowstretch=1, colstretch=1):
    wid = QW.QGroupBox(name)
    lay = QW.QVBoxLayout(wid)
    lay.setSpacing(5)
    lay.setContentsMargins(3, 3, 3, 3)
    parent.addWidget(wid, row, col, rowstretch, colstretch)
    return lay


def create_gridlayout(parent):
    wid = QW.QWidget()
    lay = QW.QGridLayout(wid)
    lay.setSpacing(20)
    lay.setContentsMargins(3, 3, 3, 3)
    parent.addWidget(wid)
    return lay


def create_cards(kingdom):
    card_dict = {}
    card_dict["KingdomList"] = create_kingdom_cards(kingdom.get_kingdom_card_df())
    card_dict["LandscapeList"] = create_kingdom_cards(kingdom.get_landscape_df())
    card_dict["LandscapeList"] += create_kingdom_cards(kingdom.get_ally_df())
    return card_dict


def create_kingdom_cards(cards):
    kingdom = []
    for _, card in cards.iterrows():
        kingdom.append(create_card_group(card, 150, 250))
    return kingdom


def create_card_group(card, width, pic_height):
    display_text = get_display_text(card)
    tooltip = get_tooltip_text(card)
    pic = QW.QLabel()
    pic.setAlignment(QC.Qt.AlignHCenter)
    pic.setWordWrap(True)
    pic.setToolTip(tooltip)
    pixmap = QG.QPixmap(str(PATH_MAIN.joinpath(card["ImagePath"])))
    w = min(pixmap.width(), width)
    h = min(pixmap.height(), pic_height)
    pixmap = pixmap.scaled(
        QC.QSize(w, h), QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation
    )
    pic.setPixmap(pixmap)
    pic.setFixedSize(width, pic_height)
    label = QW.QLabel(display_text)
    label.setAlignment(QC.Qt.AlignHCenter)
    label.setWordWrap(True)
    label.setFixedSize(width, 50)
    button = QW.QPushButton(f"Reroll {card['Name']}")
    button.setFixedSize(width, 20)
    attrdict = {"Pic": pic, "Label": label, "Button": button, "Name": card["Name"]}
    return attrdict


def get_display_text(card):
    coststring = f" ({card['Cost']})" if pd.notna(card["Cost"]) else ""
    return f"{card['Name']}{coststring}\n({card['Expansion']})"


def get_tooltip_text(card):
    """Display the qualities that are > 0 for the given card"""
    card_quals = {
        qual: qualval
        for qual in QUALITIES_AVAILABLE
        if (qualval := card[qual + "_quality"]) > 0
    }
    ttstring = "\n".join(
        [f"{qual.capitalize()}: {val}" for qual, val in card_quals.items()]
    )
    return ttstring
