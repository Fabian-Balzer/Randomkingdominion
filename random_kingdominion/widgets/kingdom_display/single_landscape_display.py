from functools import partial
from typing import Literal

import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion.constants import COLOR_PALETTE, PATH_MAIN, QUALITIES_AVAILABLE

from ..basic_widgets import ImageCutoutWidget
from .custom_reroll_button import CustomRerollButton


class SingleLandscapeImageWidget(QW.QWidget):
    """Display Name, Picture and Image for the given kingdom landscape"""

    def __init__(self, landscape: pd.Series, reroll_func: callable, special_text=None):
        super().__init__()
        self.impath = str(PATH_MAIN.joinpath(landscape["ImagePath"]))
        self.name = landscape.Name
        self.landscape = landscape
        self.box_layout = QW.QVBoxLayout(self)
        self.box_layout.setSpacing(0)
        self.box_layout.setAlignment(QC.Qt.AlignTop)
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.box_layout.setSizeConstraint(QW.QVBoxLayout.SetMinimumSize)
        self.setFixedWidth(280)
        pixmap_height = self.display_landscape()
        # Adjust the layout
        self.setSizePolicy(QW.QSizePolicy.Fixed, QW.QSizePolicy.Fixed)

        if special_text:
            self.overlay_text(special_text)

        self.reroll_button = CustomRerollButton(self)
        self.reroll_button.move(
            self.width() - 20 - self.reroll_button.width(), pixmap_height - 30
        )
        self.reroll_button.clicked.connect(partial(reroll_func, self.name))

        # self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), QC.Qt.black)
        # self.setPalette(palette)
        # self._set_tooltip_text()

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

    def display_landscape(self) -> int:
        """Display the landscape by adding a label to it, displaying the text in a bigger font"""
        image_wid = ImageCutoutWidget(self.impath, 0.05, 1, self.width())
        self.box_layout.addWidget(image_wid)
        height = image_wid.label.pixmap().height()
        color = COLOR_PALETTE.get_color_for_type(self.landscape.Types[0])
        label = QW.QLabel(self.name, self)
        label.setStyleSheet(
            f"border-image: url('demo.jpg');\
                            background-color: {color}; \
                            border-radius:50"
        )
        label.setMargin(6)
        label.setScaledContents(True)
        label.setAlignment(QC.Qt.AlignCenter)
        font = label.font()
        font.setPointSize(12)
        label.setFont(font)
        label.setGeometry(12, height - 40, self.width() - 24, 40)
        self.label = label
        return height

    # TODO: Proper mouse text display
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
