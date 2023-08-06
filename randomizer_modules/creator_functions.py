import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW
from modules.constants import RENEWED_EXPANSIONS
from modules.utils import (coolButton, coolCheckBox, coolComboBox, coolSpinBox,
                           group_widgets, pictureCheckBox)


def create_checkboxes(all_expansions, all_attack_types, button_dict):
    checkbox_dict = {}
    box_dict = {}
    names = [exp for exp in all_expansions if exp not in RENEWED_EXPANSIONS]
    tooltips = [f"Randomize cards from the {exp} expansion." for exp in names]
    for name, tooltip in zip(names, tooltips):
        checkbox = pictureCheckBox(name, tooltip, expansion=True)
        box_dict[name] = checkbox
    button_dict["ExpansionToggle"] = coolButton(text=f"Select all expansions", fontsize="10px")
    checkbox_dict["ExpansionDict"] = box_dict
    explist = [box_dict[key] for key in sorted(box_dict.keys())] + [button_dict["ExpansionToggle"]]
    checkbox_dict["ExpansionGroup"] = group_widgets(explist, f"Expansions used for randomization", num_cols=4)
    
    box_dict = {}
    tooltips = [f"Require attack of {type_} in selection." for type_ in all_attack_types]
    for name, tooltip in zip(all_attack_types, tooltips):
        checkbox = pictureCheckBox(name, tooltip, expansion=False)
        box_dict[name] = checkbox
    button_dict["AttackTypeToggle"] = coolButton(text=f"Select all attack types", fontsize="10px")
    checkbox_dict["AttackTypeDict"] = box_dict
    explist = [box_dict[key] for key in sorted(box_dict.keys())] + [button_dict["AttackTypeToggle"]]
    checkbox_dict["AttackTypeGroup"] = group_widgets(explist, f"Allowed attack types for randomization", num_cols=4)
    return checkbox_dict


def create_checkbox_group(names, kind, button_dict):
    """Creates a dictionary containing all checkboxes for set selection and a group
    widget containing all of them for display."""
    box_dict = {}
    if kind == "Expansions":
        names = [exp for exp in names if exp not in RENEWED_EXPANSIONS]
        tooltips = [
            f"Randomize cards from the {exp} expansion." for exp in names]
    elif kind == "Attack Types":
        tooltips = [
            f"Require attack of {type_} in selection." for type_ in names]
    select_all_button = coolButton(text=f"Select all {kind}", fontsize="10px")
    refname = "AttackType" if kind == "Attack Types" else kind
    button_dict[f"{refname}Toggle"] = select_all_button
    num_rows = 6 if kind == "Expansions" else 2
    explist = [box_dict[key]
               for key in sorted(box_dict.keys())] + [select_all_button]
    return box_dict, group_widgets(explist, f"{kind} used for randomization", num_rows=num_rows)


def create_buttons():
    button_dict = {}
    button_dict["Randomize"] = coolButton(text="Randomize")
    button_dict["PrintKingdom"] = coolButton(text="Print the kingdom")
    button_dict["Previous"] = coolButton(text="Previous")
    button_dict["Next"] = coolButton(text="Next")
    return button_dict

def create_comboboxes():
    box_dict = {}
    box_dict["QualityDict"], box_dict["QualityGroup"] = create_combobox_group()
    return box_dict


def create_combobox_group():
    qual_dict = {}
    possibilities = ["None", "Weak", "Medium", "Strong", "Extra strong"]
    group_list = []
    for qual in ["Draw", "Village", "Thinning", "Attack", "Interactivity"]:
        label = QW.QLabel(f"Minimum {qual.lower()} quality of the kingdom:")
        tooltip = f"Set the minimum {qual.lower()} quality for the randomized kingdom"
        box = coolComboBox(possibilities, 1, tooltip=tooltip, width=100)
        subgroup = group_widgets([label, box])
        group_list.append(subgroup)
        qual_dict[qual] = box
    # for other, val in {"AttackStrength": "attack strength", "InteractivityValue": "interactivity value"}.items():
    #     label = QW.QLabel(f"Minimum {val} of the kingdom:")
    #     tooltip = f"Set the minimum {val} for the randomized kingdom"
    #     box = coolComboBox(possibilities, 1, tooltip=tooltip, width=100)
    #     subgroup = group_widgets([label, box])
    #     group_list.append(subgroup)
    #     qual_dict[other] = box
    return qual_dict, group_widgets(group_list, "Parameters used for randomization", num_rows=len(group_list))


def create_layouts(_main):
    layout_dict = {}
    main = create_main_layout(_main)
    layout_dict["Settings"] = create_vboxlayout("Settings", main, 0, 0)
    layout_dict["Stats"] = create_vboxlayout("Kingdom stats", main, 1, 0)
    layout_dict["Display"] = create_vboxlayout(
        "Kingdom overview", main, 0, 1, 2, 1)
    layout_dict["Kingdomdisplay"] = create_gridlayout(layout_dict["Display"])
    layout_dict["Landscapedisplay"] = create_gridlayout(layout_dict["Display"])
    layout_dict["RandomizeNavigationWid"] = QW.QWidget()
    layout_dict["RandomizeNavigation"] = QW.QHBoxLayout(
        layout_dict["RandomizeNavigationWid"])
    layout_dict["Main"] = main
    return layout_dict


def create_main_layout(_main):
    lay = QW.QGridLayout(_main)
    wid = QW.QWidget()
    lay.setContentsMargins(1, 1, 1, 1)
    lay.addWidget(wid, 0, 0)
    return lay


def create_vboxlayout(name, parent, row, col, rowstretch=1, colstretch=1):
    wid = QW.QGroupBox(name)
    lay = QW.QVBoxLayout(wid)
    lay.setSpacing(20)
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
    card_dict["KingdomList"] = create_kingdom_cards(
        kingdom.get_kingdom_card_df())
    card_dict["LandscapeList"] = create_kingdom_cards(
        kingdom.get_landscape_df())
    card_dict["LandscapeList"] += create_kingdom_cards(
        kingdom.get_ally_df())
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
    pixmap = QG.QPixmap(card["ImagePath"])
    w = min(pixmap.width(), width)
    h = min(pixmap.height(), pic_height)
    pixmap = pixmap.scaled(QC.QSize(w, h),
                           QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation)
    pic.setPixmap(pixmap)
    pic.setFixedSize(width, pic_height)
    label = QW.QLabel(display_text)
    label.setAlignment(QC.Qt.AlignHCenter)
    label.setWordWrap(True)
    label.setFixedSize(width, 50)
    button = QW.QPushButton(f"Reroll {card['Name']}")
    button.setFixedSize(width, 20)
    attrdict = {"Pic": pic, "Label": label,
                "Button": button, "Name": card["Name"]}
    return attrdict


def get_display_text(card):
    coststring = f" ({card['Cost']})" if pd.notna(card['Cost']) else ""
    return f"{card['Name']}{coststring}\n({card['Expansion']})"


def get_tooltip_text(card):
    qualities = ["Draw", "Village", "Thinning", "Attack", "Interactivity"]
    ttstring = "\n".join(
        [f"{qual} quality: {card[qual +'Quality']}" for qual in qualities])
    return ttstring


def create_labels():
    label_dict = {}
    label_dict["qualities"] = QW.QLabel("")
    return label_dict
