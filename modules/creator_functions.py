import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
from modules.utils import coolButton, coolCheckBox, group_widgets, coolSpinBox
import pandas as pd


def create_checkboxes(all_sets, all_attack_types, button_dict):
    checkbox_dict = {}
    checkbox_dict["SetDict"], checkbox_dict["SetGroup"] = create_checkbox_group(all_sets, "Sets", button_dict)
    checkbox_dict["AttackTypeDict"], checkbox_dict["AttackTypeGroup"] = create_checkbox_group(all_attack_types, "Attack Types", button_dict)
    return checkbox_dict


def create_checkbox_group(names, kind, button_dict):
    """Creates a dictionary containing all checkboxes for set selection and a group
    widget containing all of them for display."""
    box_dict = {}
    if kind == "Sets":
        names = [set_ for set_ in names if set_ not in ["Intrigue", "Base"]]
        tooltips = [f"Randomize cards from the {set_} expansion." for set_ in names]
    elif kind == "Attack Types":
        tooltips = [f"Require attack of {type_} in selection." for type_ in names]
    for name, tooltip in zip(names, tooltips):
        checkbox = coolCheckBox(name, tooltip)
        box_dict[name] = checkbox
    select_all_button = coolButton(text=f"Select all {kind}")
    button_dict[f"{kind}SelectionButton"] = select_all_button
    set_list = [box_dict[key] for key in sorted(box_dict.keys())] + [select_all_button]
    return box_dict, group_widgets(set_list, f"{kind} used for randomization", num_rows=6)




def create_buttons():
    button_dict = {}
    button_dict["Randomize"] = coolButton(text="Randomize")
    return button_dict


def create_spinners():
    spinner_dict = {}
    spinner_dict["QualityDict"], spinner_dict["QualityGroup"] = create_spinner_group()
    return spinner_dict

def create_spinner_group():
    qual_dict = {}
    spin_dict = {"DrawQuality": {"Range": (0, 30), "Text": "Draw Quality (max 30):",
        "Default": 5, "Tooltip": "What shall be the overall draw quality of the kingdom?",},
        "VillageQuality": {"Range": (0, 30), "Text": "Village Quality (max 30):",
        "Default": 5, "Tooltip": "What shall be the overall village quality of the kingdom?",},
        "TrashingQuality": {"Range": (0, 20), "Text": "Trashing Quality (max 20):",
        "Default": 5, "Tooltip": "What shall be the overall trashing quality of the kingdom?"}
        }
    group_list = []
    for spin_name, vals in spin_dict.items():
        label = QW.QLabel(vals["Text"])
        box = coolSpinBox(range_=vals["Range"], value=vals["Default"], tooltip=vals["Tooltip"], width=50)
        subgroup = group_widgets([label, box])
        group_list.append(subgroup)
        qual_dict[spin_name] = box
    return qual_dict, group_widgets(group_list, "Parameters used for randomization", num_rows=len(group_list))


def create_layouts(_main):
    layout_dict = {}
    main = create_main_layout(_main)
    layout_dict["Settings"] = create_vboxlayout("Settings", main, 0, 0)
    layout_dict["Stats"] = create_vboxlayout("Kingdom stats", main, 1, 0)
    layout_dict["Display"] = create_vboxlayout("Kingdom overview", main, 0, 1, 2, 1)
    layout_dict["Kingdomdisplay"] = create_gridlayout(layout_dict["Display"])
    layout_dict["Landscapedisplay"] = create_gridlayout(layout_dict["Display"])
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


def create_cards(kingdom, landscapes):
    card_dict = {}
    card_dict["KingdomList"] = create_kingdom_cards(kingdom)
    card_dict["LandscapeList"] = create_kingdom_cards(landscapes)
    return card_dict


def create_kingdom_cards(cards):
    kingdom = []
    for i, card in cards.iterrows():
        kingdom.append(create_card_group(card, 150, 250))
    return kingdom


def create_cso_cards(cards):
    csos = []
    for i, card in cards.iterrows():
        csos.append(create_card_group(card, 250, 100))
    return csos


def create_card_group(card, width, pic_height):
    display_text = get_display_text(card)
    tooltip = get_tooltip_text(card)
    pic = QW.QLabel()
    pic.setAlignment(QC.Qt.AlignHCenter)
    pic.setWordWrap(True)
    pic.setToolTip(tooltip)
    pixmap = QG.QPixmap(card["ImagePath"])
    w = min(pixmap.width(),  width)
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
    attrdict = {"Pic": pic, "Label": label, "Button": button, "Name": card["Name"]}
    return attrdict


def get_display_text(card):
    coststring =  f" ({card['Cost']})" if pd.notna(card['Cost']) else ""
    return f"{card['Name']}{coststring}\n({card['Set']})"

def get_tooltip_text(card):
    qualities = ["Draw", "Village", "Trashing"]
    ttstring = "\n".join([f"{qual} quality: {card[qual +'Quality']}" for qual in qualities])
    return ttstring

def create_labels(qualities):
    label_dict = {}
    for qual, val in qualities.items():
        label_dict[qual] = QW.QLabel(f"Total {qual} Quality:\t{val}")
    return label_dict