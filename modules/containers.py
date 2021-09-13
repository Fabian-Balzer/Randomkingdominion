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
        self.layouts = LayoutContainer(self._main)
        self.buttons = ButtonContainer()
        self.labels = LabelContainer()
        self.checkboxes = CheckBoxContainer(all_sets=set(data_container.all_cards["Set"]),
            all_attack_types=set(data_container.get_attack_types()), params=data_container.params)
        self.spinners = SpinnerContainer()
        self.arrange_widgets()

    def arrange_widgets(self):
        self.layouts.settings.addWidget(self.checkboxes.set_group)
        self.layouts.settings.addWidget(self.spinners.quality_group)
        self.layouts.settings.addWidget(self.checkboxes.attack_type_group)
        self.layouts.settings.addStretch()
        self.layouts.settings.addWidget(self.buttons.randomize)

    def update_card_display(self):
        for i in reversed(range(self.layouts.kingdomdisplay.count())): 
            self.layouts.kingdomdisplay.itemAt(i).widget().setParent(None)
        for i in range(len(self.labels.kingdom_labels)):
            row = 0 if i < 5 else 1
            col = i if i < 5 else i-5
            wid = QW.QWidget()
            wid.setFixedSize(150, 300)
            lay = QW.QVBoxLayout(wid)
            lay.setContentsMargins(1, 1, 1, 1)
            pic, label = self.labels.kingdom_labels[i]
            lay.addWidget(pic)
            lay.addWidget(label)
            self.layouts.kingdomdisplay.addWidget(wid, row, col)
        for i in reversed(range(self.layouts.csodisplay.count())): 
            self.layouts.csodisplay.itemAt(i).widget().setParent(None)
        for i in range(len(self.labels.cso_labels)):
            wid = QW.QWidget()
            wid.setFixedSize(250, 150)
            lay = QW.QVBoxLayout(wid)
            lay.setContentsMargins(1, 1, 1, 1)
            pic, label = self.labels.cso_labels[i]
            lay.addWidget(pic)
            lay.addWidget(label)
            self.layouts.csodisplay.addWidget(wid, 2, i)


class CheckBoxContainer:
    def __init__(self, all_sets, all_attack_types, params):
        self.sets = {}
        self.set_group = self.create_set_group(all_sets, params)
        self.attack_types = {}
        self.attack_type_group = self.create_attack_type_group(all_attack_types, params)
    
    def create_set_group(self, all_sets, params):
        sets = [set_ for set_ in all_sets if set_ not in ["Intrigue", "Base"]]
        tooltips = [f"Randomize cards from the {set_} expansion." for set_ in sets]
        for set_, tooltip in zip(sets, tooltips):
            checked = set_ in params.sets
            checkbox = coolCheckBox(set_, tooltip, checked=checked)
            self.sets[set_] = checkbox
        set_list = [self.sets[key] for key in sorted(self.sets.keys())]
        return group_widgets(set_list, "Sets used for randomization", num_rows=6)

    def create_attack_type_group(self, all_attack_types, params):
        tooltips = [f"Require attack of {type_} in selection." for type_ in all_attack_types]
        for type_, tooltip in zip(all_attack_types, tooltips):
            checked = type_ in params.attack_types
            checkbox = coolCheckBox(type_, tooltip, checked=checked)
            self.attack_types[type_] = checkbox
        attack_list = [self.attack_types[key] for key in sorted(self.attack_types.keys())]
        return group_widgets(attack_list, "Attack types required", num_rows=6)


class ButtonContainer:
    def __init__(self):
        self.randomize = coolButton(text="Randomize")


class SpinnerContainer:
    def __init__(self):
        self.quality_spinners = {}
        self.quality_group = self.create_spinner_group()

    def create_spinner_group(self):
        spin_dict = {"DrawQuality": {"Range": (0, 30), "Text": "Draw Quality (max 30):",
            "Default": 5, "Tooltip": "What shall be the overall draw quality of the kingdom?",}}
        group_list = []
        for spin_name, vals in spin_dict.items():
            label = QW.QLabel(vals["Text"])
            box = coolSpinBox(range_=vals["Range"], value=vals["Default"], tooltip=vals["Tooltip"])
            subgroup = group_widgets([label, box])
            group_list.append(subgroup)
            self.quality_spinners[spin_name] = box
        return group_widgets(group_list, "Parameters used for randomization", num_rows=1)


class ComboBoxContainer:
    def __init__(self):
        self.parameter_boxes = {}
        self.parameter_group = self.create_parameter_group()

    def create_parameter_group(self, attack_types):
        spin_dict = {"Attack Types": {"Items": attack_types,
            "Tooltip": "Which Attack types should the kingdom contain?"}}



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


class LabelContainer:
    def __init__(self):
        self.kingdom_labels = []
        self.cso_labels = []

    def create_labels_from_supply(self, kingdom, csos):
        self.kingdom_labels = create_kingdom_labels(kingdom)
        self.cso_labels = create_kingdom_labels(csos)


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