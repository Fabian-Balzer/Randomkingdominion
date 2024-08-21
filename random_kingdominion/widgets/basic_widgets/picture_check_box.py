
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from ...constants import COLOR_PALETTE


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
        # pylint: disable=unused-argument
        return self.checked