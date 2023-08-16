"""File containing some convenience widgets."""
from math import ceil, floor
from typing import Literal

import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW
from matplotlib import cm

from .constants import (COLOR_PALETTE, PATH_ASSETS, PATH_MAIN,
                        QUALITIES_AVAILABLE)
from .utils import override


class CollapsibleBox(QW.QWidget):
    """A collapsible box with content that can be hidden if desired."""

    def __init__(self, title="", parent=None, initially_collapsed=True):
        super().__init__(parent)

        self.toggle_button = self.init_toggle_button(title)
        self.content_area = QW.QWidget()
        self.content_layout = QW.QVBoxLayout(self.content_area)

        outer_layout = QW.QVBoxLayout(self)
        outer_layout.addWidget(self.toggle_button)
        outer_layout.addWidget(self.content_area)
        outer_layout.setSpacing(0)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_button.setChecked(initially_collapsed)
        self.set_collapsed(initially_collapsed)

    def init_toggle_button(self, title: str):
        button = QW.QToolButton(text=title, checkable=True)
        button.setStyleSheet("QToolButton { border: none; }")
        button.setToolButtonStyle(QC.Qt.ToolButtonTextBesideIcon)
        button.setArrowType(QC.Qt.RightArrow)
        button.clicked.connect(self.on_button_clicked)
        return button

    def set_collapsed(self, collapsed: bool):
        self.toggle_button.setArrowType(
            QC.Qt.RightArrow if collapsed else QC.Qt.DownArrow
        )
        self.content_area.setVisible(not collapsed)

    @QC.pyqtSlot()
    def on_button_clicked(self):
        self.set_collapsed(self.toggle_button.isChecked())

    def setContentLayout(self, layout: QW.QWidget):
        # Clear the existing content layout and add the provided layout
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.content_layout.addLayout(layout)


def createHorLayout(widList, stretch=False, spacing=0):
    """Create horizontal box layout widget containing widgets in widList"""
    wid = QW.QWidget()
    wid.setStyleSheet(
        """QWidget {border: 0px solid gray;
                           border-radius: 0px; padding: 0, 0, 0, 0}"""
    )
    layout = QW.QHBoxLayout(wid)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for widget in widList:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch(1)
    return wid


class CoolButton(QW.QPushButton):
    def __init__(self, width=None, text="", tooltip="", enabled=True, fontsize="14px"):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setEnabled(enabled)
        if width is not None:
            self.setFixedWidth(width)
        self.setButtonStyle(fontsize=fontsize)

    def setButtonStyle(
        self,
        backStart="#f6f7fa",
        backStop="#dadbde",
        borderColor="100, 100, 100",
        bold="",
        fontsize="14px",
        height=20,
    ):
        """Sets the background and border color of the button and turns its
        text bold if requested."""
        self.setStyleSheet(
            f"""
            QPushButton {{height: {height}px; background-color: 
                qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {backStart}, stop: 1 {backStop});
                border-style: outset; border-width: 2px; border-radius: 5px; 
                border-color: rgb({borderColor}); font: {bold} {fontsize}; padding: 6px}}
                QPushButton:hover {{background-color:
                qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
                0 rgb(240, 240, 255), stop: 1 rgb(200, 200, 200))}}
                QPushButton:pressed {{background-color:
                qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
                0 rgb(200, 200, 200), stop: 1 rgb(140, 140, 140))}}
    """
        )

    def makeTextBold(self, height=20):
        self.setButtonStyle(bold="bold", height=height)

    def makeButtonRed(self):
        self.setButtonStyle(borderColor="255, 0, 0", bold="bold")


class CoolRadioButton(QW.QRadioButton):
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
        self.setStyleSheet(
            """QRadioButton {padding: 1px 1px;
                           color: black; background-color:
                           qlineargradient(x1: 0, y1: 0, 
                           2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
                           font: bold 14px} 
                           QRadioButton:checked {color: rgb(0, 0, 150)}
                           """
        )


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
        RadioButton = CoolRadioButton(name, tooltips[i])
        group.addButton(RadioButton)
        buttons.append(RadioButton)
    button_dict = dict(zip(names, buttons))
    return button_dict


def group_widgets(
    wid_list, text="", num_rows=1, num_cols=None, collapsible=True
) -> QW.QWidget:
    """
    Takes a list of widgets and group them in their own GridLayout with an according number of rows
    params:
        wid_list: list of widgets
        text: In case the group is supposed to have an outline and heading
    returns:
        wid: widget in QGridLayout"""
    layout = QW.QGridLayout()
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
    if collapsible:
        wid = CollapsibleBox(text)
        wid.setLayout(layout)
    else:
        wid = QW.QGroupBox(text)
        wid.setLayout(layout)
    return wid


class CoolCheckBox(QW.QCheckBox):
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


class PictureCheckBox(QW.QPushButton):
    """A custom checkbox with a picture in front."""

    def __init__(self, text, icon_path: str, tooltip=None, checked=False):
        super().__init__()
        self.setFlat(True)

        self.setIcon(QG.QIcon(icon_path))
        self.setIconSize(QC.QSize(30, 30))
        self.setText(text)
        self.setFixedSize(130, 40)
        self.setToolTip(tooltip)
        self.setChecked(checked)
        # self.icon().actualSize(QC.QSize(30, 30).width)

        self.set_style()

    def setChecked(self, check=True):
        self.checked = not check
        self.toggle()

    def toggle(self):
        self.checked = not self.checked
        self.set_style()

    def set_style(self):
        color = COLOR_PALETTE.selected_green if self.checked else "lightGray"

        self.setStyleSheet(
            "QPushButton {"
            "    text-align: left; /* Align text to the left */"
            "    padding-left: 5px; /* Adjust the padding to move text to the right */"
            "    padding-right: 5px; /* Reset padding on the right */"
            f"background-color:{color}; border-radius:4px; border:1px solid black;"
            "}"
            "QPushButton::menu-indicator {"
            "    image: none; /* Hide the menu indicator */"
            "}"
            "QPushButton::icon {"
            "    position: absolute; /* Position the icon absolutely */"
            "    left: 0px; /* Adjust the left position of the icon */"
            "}"
        )

    def isChecked(self, check=True):
        return self.checked


class CoolSpinBox(QW.QSpinBox):
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
        self.setStyleSheet(
            """QSpinBox {color: rgb(0,0,0); height: 18px;
                            background: transparent; padding-right: 5px;
                            /* make room for the arrows */}"""
        )


class CoolComboBox(QW.QComboBox):
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
        self.setStyleSheet(
            """QSpinBox {color: rgb(0,0,0); height: 18px;
                            background: transparent; padding-right: 5px;
                            /* make room for the arrows */}"""
        )


class ImageCutoutWidget(QW.QWidget):
    def __init__(
        self,
        impath: str,
        bottom_frac: float,
        top_frac: float,
        width: int,
        round_edges=True,
    ):
        super().__init__()
        self.image_path = impath
        self.initUI()
        pixmap = self.get_cutout_pixmap(bottom_frac, top_frac, width)
        if pixmap is None:
            return
        if round_edges:
            pixmap = self.round_pixmap(pixmap)
        self.label.setPixmap(pixmap)
        self.setContentsMargins(0, 0, 0, 0)

    def initUI(self):
        """Init.... well... most of the UI. This is a descriptive docstring."""
        layout = QW.QVBoxLayout()
        self.label = QW.QLabel(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

    def get_cutout_pixmap(self, bottom: float, top: float, width: float) -> QG.QPixmap:
        """Generate the cutout pixmap, first rescaling it and then selecting the proper
        section."""
        image = QG.QImage(self.image_path)
        if image.isNull():
            return

        aspect_ratio = image.width() / image.height()
        new_height = int(width / aspect_ratio)
        resized_image = image.scaled(
            width, new_height, QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation
        )

        full_height = resized_image.height()
        cutout_bottom = int(full_height * bottom)
        cutout_top = int(full_height * top)
        cutout_height = cutout_top - cutout_bottom
        cutout = resized_image.copy(0, full_height - cutout_top, width, cutout_height)

        return QG.QPixmap.fromImage(cutout)

    def round_pixmap(self, pixmap):
        """Create a mask to round the edges of the given pixmap."""
        if pixmap is None:
            return
        rounded_mask = QG.QPixmap(pixmap.size())
        rounded_mask.fill(QC.Qt.transparent)

        mask_painter = QG.QPainter(rounded_mask)
        mask_path = QG.QPainterPath()
        rect = QC.QRectF(0, 0, pixmap.width(), pixmap.height())
        mask_path.addRoundedRect(rect, 10, 10)
        mask_painter.setRenderHint(QG.QPainter.Antialiasing)
        mask_painter.fillPath(mask_path, QC.Qt.white)
        mask_painter.end()

        rounded_pixmap = QG.QPixmap(pixmap.size())
        rounded_pixmap.fill(QC.Qt.transparent)

        pixmap_painter = QG.QPainter(rounded_pixmap)
        pixmap_painter.setRenderHint(QG.QPainter.Antialiasing)
        pixmap_painter.setClipPath(mask_path)
        pixmap_painter.drawPixmap(0, 0, pixmap)
        pixmap_painter.end()

        return rounded_pixmap


class RerollButton(QW.QLabel):
    clicked = QC.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = str(PATH_ASSETS.joinpath("icons/114px-Prince_icon.png"))
        style_sheet = """
            QLabel {
                background-color: white;  /* Change to your desired background color */
                border: 1px solid gray;
                border-radius: 10px;
                padding: 2px;
            }
        """
        self.setStyleSheet(style_sheet)
        self.setPixmap(QG.QPixmap(icon_path))
        self.setAlignment(QC.Qt.AlignCenter)
        self.setScaledContents(True)
        self.setFixedSize(QC.QSize(32, 32))
        self.setCursor(QC.Qt.PointingHandCursor)
        self.clicked.connect(self.on_image_clicked)

    def mousePressEvent(self, event):
        self.clicked.emit()

    def on_image_clicked(self):
        pass


class KingdomCardImageWidget(QW.QWidget):
    """Display Name, Picture and Image for the given kingdom card"""

    def __init__(self, card: pd.Series, width=180, special_text=None, detailed=False):
        super().__init__()
        self.is_landscape = card.IsLandscape
        self.card = card
        self.real_width = width * 2 if self.is_landscape else width
        self.is_detailed = detailed
        self.impath = str(PATH_MAIN.joinpath(card["ImagePath"]))
        self.name = card.Name
        self.box_layout = QW.QVBoxLayout(self)
        if self.is_landscape:
            self.real_height = self.display_landscape()
        else:
            self.real_height = self.display_card()
            if special_text:
                self.overlay_text(special_text)
        # Adjust the layout
        self.box_layout.setSpacing(0)
        self.box_layout.setAlignment(QC.Qt.AlignTop)
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.box_layout.setSizeConstraint(QW.QVBoxLayout.SetMinimumSize)
        self.setSizePolicy(QW.QSizePolicy.Fixed, QW.QSizePolicy.Fixed)

        self.reroll_button = self.add_reroll_button()

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QC.Qt.black)
        self.setPalette(palette)
        self._set_tooltip_text()

    def _set_tooltip_text(self):
        """Display the qualities that are > 0 for the given card"""
        card_quals = {
            qual: qualval
            for qual in QUALITIES_AVAILABLE
            if (qualval := self.card[qual + "_quality"]) > 0
        }
        qual_strings = [
            f"{qual.capitalize()}: {val}" for qual, val in card_quals.items()
        ]
        ttstring = self.card.Expansion + "\n"
        ttstring += "\n".join(qual_strings)
        self.setToolTip(ttstring)

    def _get_display_text(self) -> str:
        card = self.card
        coststring = f" ({card['Cost']})" if pd.notna(card["Cost"]) else ""
        return f"{card['Name']}{coststring}\n({card['Expansion']})"

    def display_card(self) -> int:
        """Display the card that this class is based on."""
        if self.is_detailed:
            pic = QW.QLabel()
            pic.setAlignment(QC.Qt.AlignHCenter)
            pic.setWordWrap(True)
            pixmap = QG.QPixmap(self.impath)
            self.real_width -= 80
            w = self.real_width
            pixmap = pixmap.scaledToWidth(w, QC.Qt.SmoothTransformation)
            pic.setPixmap(pixmap)
            pic.setFixedSize(w, pixmap.height())
            label = QW.QLabel(self._get_display_text())
            label.setAlignment(QC.Qt.AlignHCenter)
            label.setWordWrap(True)
            label.setFixedSize(w, 20)
            self.box_layout.addWidget(pic)
            self.box_layout.addWidget(label)
            return pixmap.height() + 20

        top_part = ImageCutoutWidget(self.impath, 0.47, 1, self.real_width)
        bottom_part = ImageCutoutWidget(self.impath, 0.03, 0.11, self.real_width)
        self.box_layout.addWidget(top_part)
        self.box_layout.addWidget(bottom_part)
        top_height = top_part.label.pixmap().height()
        height = top_height + bottom_part.label.pixmap().height()

        # Display the card amount:
        label = QW.QLabel(str(self.card.CardAmount), self)
        label.setStyleSheet(f"""
                            background-color: {COLOR_PALETTE.selected_green};
                            border-radius:4;
                            border-color: black; 
                            border-width:1px; border-style: outset"""
        )
        label.setMargin(2)
        label.setScaledContents(True)
        label.setAlignment(QC.Qt.AlignCenter)
        font = label.font()
        font.setPointSize(8)
        label.setFont(font)
        label.setGeometry(8, 33, 28, 22)
        return height

    def display_landscape(self) -> int:
        """Display the landscape by adding a label to it, displaying the text in a bigger font"""
        image_wid = ImageCutoutWidget(self.impath, 0.05, 1, self.real_width)
        self.box_layout.addWidget(image_wid)
        height = image_wid.label.pixmap().height()
        if self.is_detailed:
            label = QW.QLabel(self.name + self.card.Expansion)
            self.box_layout.addWidget(label)
            return height
        color = COLOR_PALETTE.get_color_for_type(self.card.Types[0])
        label = QW.QLabel(self.name, self)
        label.setStyleSheet(
            f"border-image: url('demo.jpg');\
                            background-color: {color}; \
                            border-radius:50"
        )
        label.setMargin(8)
        label.setScaledContents(True)
        label.setAlignment(QC.Qt.AlignCenter)
        font = label.font()
        font.setPointSize(16)
        label.setFont(font)
        label.setGeometry(12, height - 50, self.real_width - 24, 50)
        self.label = label
        return height

    def add_reroll_button(self) -> RerollButton:
        # Create a button and add it to a widget
        button = RerollButton(self)
        if self.is_landscape:
            button.move(20, self.real_height - 50 + 12)
        else:
            button.move(self.real_width - 10 - button.width(), 33)
        return button

    def overlay_text(self, text: Literal["Bane", "Obelisk"]):
        color_dict = {"Bane": "gray", "Obelisk": "olivegreen"}
        color = "gray"  # color_dict[text]
        label = QW.QLabel(text, self)
        label.setStyleSheet(
            f"border-image: url('demo.jpg');\
                            background-color: {color}; \
                            border-radius:25"
        )
        label.setMargin(2)
        label.setScaledContents(True)
        label.setAlignment(QC.Qt.AlignCenter)

        font = label.font()
        font.setPointSize(10)
        label.setFont(font)
        label.setGeometry(12, self.real_height - 40, self.real_width - 24, 20)


class QualityIcon(QW.QLabel):
    """A small icon to display the image for the requested kingdom quality"""

    def __init__(self, qual_name: str, size=40):
        super().__init__()
        icon_path = PATH_ASSETS.joinpath(f"icons/qualities/{qual_name}.jpg")
        assert icon_path.is_file(), f"Couldn't find {qual_name} asset."
        self.setAlignment(QC.Qt.AlignHCenter)
        pixmap = QG.QPixmap(str(icon_path))
        pixmap = pixmap.scaled(
            QC.QSize(size, size), QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation
        )
        self.pixmap = pixmap
        self.setPixmap(pixmap)
        self.setFixedSize(size, size)
        self.overlay_cross = True  # Initialize overlay status

    def set_overlay_cross(self, overlay: bool):
        self.overlay_cross = overlay
        self.update()

    def paintEvent(self, event):
        painter = QG.QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        if self.overlay_cross:
            painter.setRenderHint(QG.QPainter.Antialiasing)

            # Draw a red "x" over the pixmap
            pen = QG.QPen(QG.QColor(QC.Qt.white))
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.width(), self.height())
            painter.drawLine(0, self.height(), self.width(), 0)
            pen = QG.QPen(QG.QColor(QC.Qt.darkRed))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.width(), self.height())
            painter.drawLine(0, self.height(), self.width(), 0)


class HorizontalBarWidget(QW.QFrame):
    """A widget to display a horizontal bar with 5 different levels of being 'filled'."""

    clicked = QC.pyqtSignal(int)

    def __init__(self, parent=None, clickable=False):
        super().__init__(parent)
        self._width = 0
        self._color = QC.Qt.black
        self.is_disabled = False

        self.setFrameStyle(QW.QFrame.Box | QW.QFrame.Plain)
        self.setLineWidth(10)
        if clickable:
            self.clicked.connect(self.handle_click)

    def setValue(self, value: Literal[0, 1, 2, 3, 4]):
        if value == -1:
            value = 0
        rgba_tuple = COLOR_PALETTE.get_bar_level_color(value)  # Get RGBA values from the colormap
        self._color = (
            QG.QColor.fromRgbF(*rgba_tuple) if not self.is_disabled else QC.Qt.gray
        )
        self._width = value
        self.update()

    def getValue(self) -> int:
        return self._width

    def paintEvent(self, event):
        painter = QG.QPainter(self)
        painter.setRenderHint(QG.QPainter.Antialiasing)

        # Draw the outer rectangular frame
        painter.drawRect(0, 0, self.width(), self.height())

        painter.setBrush(self._color)
        width = int(self._width / 4 * self.width())
        painter.drawRect(1, 1, width - 2, self.height() - 2)

        # Draw the scale
        scale_height = 5
        scale_width = int(self.width() / 4)
        scale_start_y = self.height() - scale_height
        for i in range(5):
            x = i * scale_width
            painter.drawLine(x, scale_start_y, x, self.height())

    def mousePressEvent(self, event: QG.QMouseEvent):
        # Calculate the clicked value based on the click position
        click_value = int((event.x() + self.width() / 8) / (self.width() / 4))
        self.clicked.emit(click_value)  # Emit the signal with the clicked value

    def mouseMoveEvent(self, event: QG.QMouseEvent):
        click_value = int((event.x() + self.width() / 8) / (self.width() / 4))
        self.clicked.emit(click_value)  # Emit the signal with the clicked value

    def handle_click(self, value):
        if value >= 5:
            value = 4
        elif value < 0:
            value = 0
        self.setValue(value)

    @override
    def setDisabled(self, disabled: bool):
        """Ensure that everything is grayed out properly."""
        self.is_disabled = disabled
        self.setValue(self.getValue())

        # Call the original setDisabled method to perform the actual disabling
        super(QW.QFrame, self).setDisabled(disabled)



class CustomSlider(QW.QSlider):
    """Simple horizontal slider going from the min to the max val (including both)."""
    def __init__(self, min_val: int = 0, max_val: int = 5):
        super().__init__(QC.Qt.Horizontal)
        self.setRange(min_val, max_val)
        self.setFixedHeight(20)
        self.setTickInterval(1)
        self.setStyleSheet(
            """
            QSlider::handle:horizontal {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 gray, stop:1 darkGreen);
                border: .5px solid;
                width: 10px;
                }
            QSlider::handle:vertical { 
                height: 15px; 
            }
    
            QSlider::handle:horizontal:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 darkGreen, stop:1 gray);
            }
            """
        )
    @override
    def wheelEvent(self, event):
        # Do nothing to prevent scrolling from changing the value
        pass

class CustomRangeSlider(QW.QWidget):
    """A range slider that allows the user to set two values where the
    second one is larger than the first."""

    value_changed = QC.pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QW.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.slider_max_value = 4
        self.slider_min = CustomSlider(0, self.slider_max_value)
        self.slider_min.valueChanged.connect(self.update_values)
        layout.addWidget(self.slider_min)

        self.slider_max = CustomSlider(0, self.slider_max_value)
        self.slider_max.valueChanged.connect(self.update_values)
        self.slider_max.setTickPosition(QW.QSlider.TicksBelow)
        layout.addWidget(self.slider_max)

        self.labels_widget = QW.QWidget()
        lay = QW.QHBoxLayout(self.labels_widget)
        lay.setContentsMargins(3, 0, 3, 0)
        for tick in range(self.slider_max_value + 1):
            label = QW.QLabel(str(tick))
            label.setAlignment(QC.Qt.AlignCenter)
            lay.addWidget(label)
            if tick < self.slider_max_value:
                lay.addItem(
                    QW.QSpacerItem(
                        0, 0, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
                    )
                )

        layout.addWidget(self.labels_widget)
        layout.addStretch()
        self.setLayout(layout)


    def set_values(self, min_val: int, max_val: int):
        """Set the values of the range and update the UI."""
        assert min_val <= max_val
        self.slider_max.setValue(max_val)
        self.slider_min.setValue(min_val)
        self.update_values()

    def update_values(self):
        min_val = self.slider_min.value()
        max_val = self.slider_max.value()
        if min_val >= max_val:
            self.slider_max.setValue(min_val)
        if max_val <= min_val:
            self.slider_min.setValue(max_val)
        self.update()  # necessary to have nice painting of the area in between
        self.value_changed.emit()

    def get_values(self) -> tuple[int, int]:
        """Get the current values of the sliders as a range of ints"""
        return self.slider_min.value(), self.slider_max.value()

    def paintEvent(self, event):
        # Create a painter to highlight the area in between the sliders
        painter = QG.QPainter(self)
        painter.setRenderHint(QG.QPainter.Antialiasing)

        # Calculate the positions of the slider handles:
        s1 = self.slider_min
        min_pos = s1.pos().x() + int(s1.value() * s1.width() / self.slider_max_value)
        y1 = int(s1.pos().y() + s1.height() / 2)
        h1 = int(s1.height() / 2)

        s2 = self.slider_max
        max_pos = s2.pos().x() + int(s2.value() * s2.width() / self.slider_max_value)

        color_range_rect = min_pos, y1 + 2, max_pos - min_pos, h1 * 2 - 4

        # Draw color range
        painter.fillRect(*color_range_rect, QC.Qt.darkGreen)
