from math import ceil, floor

import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW
from modules.constants import RENEWED_EXPANSIONS


def createHorLayout(widList, stretch=False, spacing=0):
    """Create horizontal box layout widget containing widgets in widList"""
    wid = QW.QWidget()
    wid.setStyleSheet("""QWidget {border: 0px solid gray;
                           border-radius: 0px; padding: 0, 0, 0, 0}""")
    layout = QW.QHBoxLayout(wid)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for widget in widList:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch(1)
    return wid


class coolButton(QW.QPushButton):
    def __init__(self, width=None, text="", tooltip="", enabled=True, fontsize="14px"):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setEnabled(enabled)
        if width is not None:
            self.setFixedWidth(width)
        self.setButtonStyle(fontsize=fontsize)

    def setButtonStyle(self, backStart="#f6f7fa", backStop="#dadbde",
                       borderColor="100, 100, 100", bold="", fontsize="14px", height=20):
        """Sets the background and border color of the button and turns its
        text bold if requested."""
        self.setStyleSheet(
            f"""QPushButton {{height: {height}px; background-color: 
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {backStart}, stop: 1 {backStop});
border-style: outset; border-width: 2px; border-radius: 5px; 
border-color: rgb({borderColor}); font: {bold} {fontsize}; padding: 6px}}
QPushButton:hover {{background-color:
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
0 rgb(240, 240, 255), stop: 1 rgb(200, 200, 200))}}
QPushButton:pressed {{background-color:
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
0 rgb(200, 200, 200), stop: 1 rgb(140, 140, 140))}}""")

    def makeTextBold(self, height=20):
        self.setButtonStyle(bold="bold", height=height)

    def makeButtonRed(self):
        self.setButtonStyle(borderColor="255, 0, 0", bold="bold")


class coolRadioButton(QW.QRadioButton):
    """Modified version of QRadioButtons.
    Creates a QRadioButton with a given placeholder and tooltip.
    params:
        lineText: Text to be already entered. Overrides placeholder.
        placeholder: Text to be displayed by default
        tooltip: optionally create a tooltip for the edit"""

    def __init__(self, text=None, tooltip=None, width=50):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setMinimumWidth(width)
        self.setStyleSheet("""QRadioButton {padding: 1px 1px;
                           color: black; background-color:
                           qlineargradient(x1: 0, y1: 0, 
                           2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
                           font: bold 14px} 
                           QRadioButton:checked {color: rgb(0, 0, 150)}
                           """)


def create_radio_buttons(group, names, tooltips=None):
    """
    Creates QRadioButtons with the names passed through 'names' and adds them
    to a RadioButton group.
    params:
        group: QButtonGroup object
        names: List of Strings for the radio button names
        tooltip: optionally create a tooltip for the buttons
    returns:
        button_dict: Dictionary of QRadioButtonObjects with their names
    """
    tooltips = tooltips if tooltips is not None else [None for name in names]
    buttons = []
    for i, name in enumerate(names):
        RadioButton = coolRadioButton(name, tooltips[i])
        group.addButton(RadioButton)
        buttons.append(RadioButton)
    button_dict = dict(zip(names, buttons))
    return button_dict


def group_widgets(wid_list, text=None, num_rows=1, num_cols=None):
    """
    Takes a list of widgets and group them in their own GridLayout with an according number of rows
    params:
        wid_list: list of widgets
        text: In case the group is supposed to have an outline and heading
    returns:
        wid: widget in QGridLayout"""
    if text is None:
        wid = QW.QWidget()
    else:
        wid = QW.QGroupBox(text)
    layout = QW.QGridLayout(wid)
    layout.setContentsMargins(5, 0, 5, 5)
    num_items = len(wid_list)
    if num_cols is None:
        num_cols = ceil(num_items / num_rows)
    else:
        num_rows = ceil(num_items / num_cols)
    for i, widget in enumerate(wid_list):
        row = floor(i / num_cols)
        col = i - row * num_cols
        layout.addWidget(widget, row, col)
    return wid


def display_cards(label_dict, layout_dict, name, num_rows=2, size=(150, 320)):
    # Delete the old display
    for i in reversed(range(layout_dict[f"{name}display"].count())):
        layout_dict[f"{name}display"].itemAt(i).widget().setParent(None)
    num_items = len(label_dict[f"{name}List"])
    num_cols = ceil(num_items / num_rows)
    for i, widget in enumerate(label_dict[f"{name}List"]):
        row = floor(i / num_cols)
        col = i - row * num_cols
        wid = QW.QWidget()
        wid.setFixedSize(*size)
        lay = QW.QVBoxLayout(wid)
        lay.setContentsMargins(1, 1, 1, 1)
        entry = label_dict[f"{name}List"][i]
        lay.addWidget(entry["Button"])
        lay.addWidget(entry["Pic"])
        lay.addWidget(entry["Label"])
        layout_dict[f"{name}display"].addWidget(wid, row, col)


class coolCheckBox(QW.QCheckBox):
    """Modified version of QCheckBoxes.
    Creates a QCheckBox with a given text and tooltip.
    params:
        text: Text to be shown
        tooltip: optionally create a tooltip for the edit
        checked: Bool set to false by default.
    """

    def __init__(self, text=None, tooltip=None, checked=False, width=150):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setChecked(checked)
        if width is not None:
            self.setFixedWidth(width)
        self.setStyleSheet("QCheckBox {color: rgb(0, 0, 0); height: 18 px}")


class pictureCheckBox(QW.QPushButton):
    """Modified version of QCheckBoxes.
    Creates a QCheckBox with a given text and tooltip.
    params:
        text: Text to be shown
        tooltip: optionally create a tooltip for the edit
        checked: Bool set to false by default.
    """

    def __init__(self, text, tooltip=None, checked=False, expansion=True):
        super().__init__()
        self.setFlat(True)
        icon = get_expansion_icon(text) if expansion else get_attack_icon(text)
        self.setIcon(QG.QIcon(icon))
        self.setIconSize(QC.QSize(30, 30))
        # self.setLayoutDirection(QC.Qt.RightToLeft)
        # self.setLayout(QW.QGridLayout())
        # label = QW.QLabel(expansion)
        # label.setAlignment(QC.Qt.AlignRight | QC.Qt.AlignVCenter)
        # label.setAttribute(QC.Qt.WA_TransparentForMouseEvents)
        # self.layout().addWidget(label)
        self.setText(text)
        self.setFixedSize(130, 40)
        self.setToolTip(tooltip)
        self.setChecked(checked)

    def toggle(self):
        self.checked = not self.checked
        color = "gray" if self.checked else "lightGray"
        self.setStyleSheet(
            f"background-color:{color}; border-radius:4px; border:1px solid black;"
            "QPushButton: {text-align:left}")

    def setChecked(self, check=True):
        self.checked = not check
        self.toggle()
        
    def isChecked(self, check=True):
        return self.checked


def get_expansion_icon(exp):
    """Returns the image path for the given expansion icon."""
    base = "assets/icons/expansions/"
    conversion_dict = {}
    for outdated_exp in RENEWED_EXPANSIONS:
        conversion_dict[outdated_exp + ", 1E"] = outdated_exp + "_old"
        conversion_dict[outdated_exp + ", 2E"] = outdated_exp
    if exp in conversion_dict:
        exp = conversion_dict[exp]
    return base + exp.replace(" ", "_") + ".png"

def get_attack_icon(at):
    """Returns the image path for the given attack icon."""
    base = "assets/icons/attack_types/"
    return base + at + ".png"


# %% The coolSpinBox class and functions for SpinBoxes


class coolSpinBox(QW.QSpinBox):
    """Modified version of QSpinBox
    Creates a QSpinBox with a given range and start value
    params:
        range_: range for the Box
        value: start value. Needs to be in range.
        tooltip: optionally create a tooltip for the edit
    """

    def __init__(self, range_=(0, 100), value=50, tooltip=None, width=250):
        super().__init__()
        self.setRange(*range_)
        self.setValue(value)
        self.setToolTip(tooltip)
        if width:
            self.setFixedWidth(width)
        self.setStyleSheet("""QSpinBox {color: rgb(0,0,0); height: 18px;
                            background: transparent; padding-right: 5px;
                            /* make room for the arrows */}""")
                           

class coolComboBox(QW.QComboBox):
    """Modified version of QSpinBox
    Creates a QSpinBox with a given range and start value
    params:
        range_: range for the Box
        value: start value. Needs to be in range.
        tooltip: optionally create a tooltip for the edit
    """

    def __init__(self, possibilities, index, tooltip=None, width=250):
        super().__init__()
        self.addItems(possibilities)
        self.setCurrentIndex(index)
        self.setToolTip(tooltip)
        if width:
            self.setFixedWidth(width)
        self.setStyleSheet("""QSpinBox {color: rgb(0,0,0); height: 18px;
                            background: transparent; padding-right: 5px;
                            /* make room for the arrows */}""")