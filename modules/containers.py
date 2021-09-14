import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
from numpy.lib.function_base import disp
from modules.utils import coolButton, coolCheckBox, group_widgets, coolSpinBox
import pandas as pd
import numpy as np


class WidgetContainer:
    def __init__(self, _main, data_container):
        self._main = _main
        self.buttons = create_buttons()
        all_sets = set(data_container.all_cards["Set"])
        all_attack_types = set(data_container.get_attack_types())
        params = params=data_container.params
        self.checkboxes = create_checkboxes(all_sets,
            all_attack_types, params)
        self.spinners = create_spinners()
        self.layouts = LayoutContainer(self._main)
        self.arrange_widgets()

    def arrange_widgets(self):
        self.layouts.settings.addWidget(self.checkboxes["SetGroup"])
        self.layouts.settings.addWidget(self.spinners["QualityGroup"])
        self.layouts.settings.addWidget(self.checkboxes["AttackTypeGroup"])
        self.layouts.settings.addStretch()
        self.layouts.settings.addWidget(self.buttons["Randomize"])

    def update_card_display(self, kingdom, landscapes):
        self.labels = create_labels(kingdom, landscapes)
        for i in reversed(range(self.layouts.kingdomdisplay.count())): 
            self.layouts.kingdomdisplay.itemAt(i).widget().setParent(None)
        for i in range(len(self.labels["KingdomList"])):
            row = 0 if i < 5 else 1
            col = i if i < 5 else i-5
            wid = QW.QWidget()
            wid.setFixedSize(150, 300)
            lay = QW.QVBoxLayout(wid)
            lay.setContentsMargins(1, 1, 1, 1)
            pic, label = self.labels["KingdomList"][i]
            lay.addWidget(pic)
            lay.addWidget(label)
            self.layouts.kingdomdisplay.addWidget(wid, row, col)
        for i in reversed(range(self.layouts.csodisplay.count())): 
            self.layouts.csodisplay.itemAt(i).widget().setParent(None)
        for i in range(len(self.labels["LandscapeList"])):
            wid = QW.QWidget()
            wid.setFixedSize(250, 150)
            lay = QW.QVBoxLayout(wid)
            lay.setContentsMargins(1, 1, 1, 1)
            pic, label = self.labels["LandscapeList"][i]
            lay.addWidget(pic)
            lay.addWidget(label)
            self.layouts.csodisplay.addWidget(wid, 2, i)


def create_checkboxes(all_sets, all_attack_types, params):
    checkbox_dict = {}
    checkbox_dict["SetDict"], checkbox_dict["SetGroup"] = create_checkbox_group(all_sets, params, "Sets")
    checkbox_dict["AttackTypeDict"], checkbox_dict["AttackTypeGroup"] = create_checkbox_group(all_attack_types, params, "Attack Types")
    return checkbox_dict


def create_checkbox_group(names, params, kind):
    """Creates a dictionary containing all checkboxes for set selection and a group
    widget containing all of them for display."""
    box_dict = {}
    if kind == "Sets":
        names = [set_ for set_ in names if set_ not in ["Intrigue", "Base"]]
        tooltips = [f"Randomize cards from the {set_} expansion." for set_ in names]
        checked_check = params.sets
    elif kind == "Attack Types":
        tooltips = [f"Require attack of {type_} in selection." for type_ in names]
        checked_check = params.attack_types
    for name, tooltip in zip(names, tooltips):
        checked = name in checked_check
        checkbox = coolCheckBox(name, tooltip, checked=checked)
        box_dict[name] = checkbox
    set_list = [box_dict[key] for key in sorted(box_dict.keys())]
    return box_dict, group_widgets(set_list, "{kind} used for randomization", num_rows=6)


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
        "Default": 5, "Tooltip": "What shall be the overall draw quality of the kingdom?",}}
    group_list = []
    for spin_name, vals in spin_dict.items():
        label = QW.QLabel(vals["Text"])
        box = coolSpinBox(range_=vals["Range"], value=vals["Default"], tooltip=vals["Tooltip"])
        subgroup = group_widgets([label, box])
        group_list.append(subgroup)
        qual_dict[spin_name] = box
    return qual_dict, group_widgets(group_list, "Parameters used for randomization", num_rows=1)


class LayoutContainer:
    def __init__(self, _main):
        self.main_widget = QW.QWidget()
        self._main = _main
        self.main = self.create_main()
        self.settings = self.create_settings()
        self.display = self.create_display()
        self.kingdomdisplay = self.create_kingdomdisplay()
        self.csodisplay = self.create_csodisplay()

    def create_main(self):
        lay = QW.QGridLayout(self._main)
        lay.setContentsMargins(1, 1, 1, 1)
        # A top one to contain plotting and plot mode
        lay.addWidget(self.main_widget, 0, 0)
        return lay

    def create_settings(self):
        wid = QW.QGroupBox("Settings")
        wid.setFixedWidth(500)
        lay = QW.QVBoxLayout(wid)
        lay.setSpacing(20)
        lay.setContentsMargins(3, 3, 3, 3)
        self.main.addWidget(wid, 0, 0)
        return lay

    def create_display(self):
        wid = QW.QGroupBox("Kingdom Overview")
        lay = QW.QGridLayout(wid)
        lay.setSpacing(0)
        lay.setContentsMargins(3, 3, 3, 3)
        self.main.addWidget(wid, 0, 1)
        return lay

    def create_kingdomdisplay(self):
        wid = QW.QWidget()
        lay = QW.QGridLayout(wid)
        lay.setSpacing(10)
        lay.setContentsMargins(3, 3, 3, 3)
        self.display.addWidget(wid, 0, 0)
        return lay

    def create_csodisplay(self):
        wid = QW.QWidget()
        lay = QW.QGridLayout(wid)
        lay.setSpacing(10)
        lay.setContentsMargins(3, 3, 3, 3)
        self.display.addWidget(wid, 1, 0)
        return lay


def create_labels(kingdom, landscapes):
    label_dict = {}
    label_dict["KingdomList"] = create_kingdom_labels(kingdom)
    label_dict["LandscapeList"] = create_kingdom_labels(landscapes)
    return label_dict


def create_kingdom_labels(cards):
    kingdom = []
    for i, card in cards.iterrows():
        kingdom.append(create_label_pair(card, 150, 250))
    return kingdom


def create_cso_labels(cards):
    csos = []
    for i, card in cards.iterrows():
        csos.append(create_label_pair(card, 250, 100))
    return csos


def create_label_pair(card, width, height):
    display_text = get_display_text(card)
    pic = QW.QLabel()
    pic.setAlignment(QC.Qt.AlignHCenter)
    pic.setWordWrap(True)
    pixmap = QG.QPixmap(card["ImagePath"])
    w = min(pixmap.width(),  width)
    h = min(pixmap.height(), height)
    pixmap = pixmap.scaled(QC.QSize(w, h),
        QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation)
    pic.setPixmap(pixmap)
    pic.setFixedSize(width, height)
    label = QW.QLabel(display_text)
    label.setAlignment(QC.Qt.AlignHCenter)
    label.setWordWrap(True)
    label.setFixedSize(width, 50)
    return pic, label


def get_display_text(card):
    coststring =  f" ({card['Cost']})" if pd.notna(card['Cost']) else ""
    return f"{card['Name']}{coststring}\n({card['Set']})"