import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
from numpy.lib.function_base import disp
from modules.utils import coolButton, coolCheckBox, group_widgets
import pandas as pd
import numpy as np


class WidgetContainer:
    def __init__(self, _main, df):
        self._main = _main
        self.layouts = LayoutContainer(self._main)
        self.buttons = ButtonContainer()
        self.labels = LabelContainer()
        self.checkboxes = CheckBoxContainer()
        self.checkboxes.create_set_group(set(df["Set"]))
        self.arrange_widgets()

    def arrange_widgets(self):
        self.layouts.settings.addWidget(self.checkboxes.set_group)
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
    def __init__(self):
        self.sets = {}
    
    def create_set_group(self, all_sets):
        sets = [set_ for set_ in all_sets if set_ not in ["Intrigue", "Base"]]
        tooltips = [f"Randomize cards from the {set_} expansion." for set_ in sets]
        for set_, tooltip in zip(sets, tooltips):
            checkbox = coolCheckBox(set_, tooltip)
            self.sets[set_] = checkbox
        set_list = [self.sets[key] for key in sorted(self.sets.keys())]
        self.set_group = group_widgets(set_list, "Sets used for randomization", num_rows=6)


class ButtonContainer:
    def __init__(self):
        self.randomize = coolButton(text="Randomize")


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