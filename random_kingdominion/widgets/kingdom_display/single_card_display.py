from functools import partial
from typing import Literal

import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion.constants import COLOR_PALETTE, PATH_MAIN, QUALITIES_AVAILABLE

from ..basic_widgets import ImageCutoutWidget
from .card_amount_label import CardAmountLabel
from .custom_reroll_button import CustomRerollButton


class SingleCardImageWidget(QW.QWidget):
    """Display Name, Picture and Image for the given kingdom card"""

    def __init__(self, card: pd.Series, reroll_func: callable, special_text=None):
        super().__init__()
        self.impath = str(PATH_MAIN.joinpath(card["ImagePath"]))
        self.name = card.Name
        self.box_layout = QW.QVBoxLayout(self)
        self.box_layout.setSpacing(0)
        self.box_layout.setAlignment(QC.Qt.AlignTop)
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.box_layout.setSizeConstraint(QW.QVBoxLayout.SetMinimumSize)
        self.setFixedWidth(130)
        self.setSizePolicy(QW.QSizePolicy.Minimum, QW.QSizePolicy.Minimum)

        self.im_height = self.display_card()

        # - Add additional labels and buttons:
        amount_label = CardAmountLabel(card.CardAmount, self)
        amount_label.setGeometry(8, 25, 28, 22)
        if special_text:
            self.overlay_text(special_text)

        self.reroll_button = CustomRerollButton(self)
        self.reroll_button.move(self.width() - 5 - self.reroll_button.width(), 25)
        self.reroll_button.clicked.connect(partial(reroll_func, self.name))

        # self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), QC.Qt.black)
        # self.setPalette(palette)
        # self._set_tooltip_text()

    # TODO: Do this differently, e.g. in a card container.
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
        top_part = ImageCutoutWidget(self.impath, 0.47, 1, self.width())
        bottom_part = ImageCutoutWidget(self.impath, 0.03, 0.11, self.width())
        self.box_layout.addWidget(top_part)
        self.box_layout.addWidget(bottom_part)
        top_height = top_part.label.pixmap().height()
        height = top_height + bottom_part.label.pixmap().height()
        return height

    def overlay_text(self, text: Literal["Bane", "Obelisk"]):
        # color_dict = {"Bane": "gray", "Obelisk": "olivegreen"}
        color = COLOR_PALETTE.trait
        label = QW.QLabel(text, self)
        label.setStyleSheet(
            f"border-image: url('demo.jpg');\
                            background-color: {color}; \
                            border-radius:5"
        )
        label.setMargin(1)
        label.setScaledContents(True)
        label.setAlignment(QC.Qt.AlignCenter)

        font = label.font()
        font.setPointSize(8)
        label.setFont(font)
        label_height = 20 * (text.count("\n") + 1)
        label.setGeometry(
            12, self.im_height - 20 - label_height, self.width() - 24, label_height
        )
