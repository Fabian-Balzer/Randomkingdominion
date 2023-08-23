from math import ceil

import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
from random_kingdominion.kingdom import Kingdom, KingdomRandomizer
from random_kingdominion.utils import clear_layout, get_row_and_col

from .single_card_display import SingleCardImageWidget


class GroupedCardDisplay(QW.QWidget):
    """Display all cards of a given kingdom."""

    def __init__(self):
        super().__init__()
        self.grid_layout = QW.QGridLayout(self)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QC.Qt.black)
        self.setPalette(palette)
        self.widget_list: list[SingleCardImageWidget] = []
        self.setSizePolicy(QW.QSizePolicy.Minimum, QW.QSizePolicy.Minimum)
        self.grid_layout.setSizeConstraint(QW.QGridLayout.SetMinimumSize)

    def set_kingdom_cards(self, kingdom: Kingdom, reroll_func: callable):
        self._reset_layout()
        card_df = kingdom.kingdom_card_df
        num_cols = ceil(len(card_df) / 2)
        for i, (_, card) in enumerate(card_df.iterrows()):
            row, col = get_row_and_col(i, num_cols)
            # Invert the rows such that the lower cost cards are on the bottom
            row = 1 - row
            special_text = kingdom.get_special_card_text(card.name)
            wid = SingleCardImageWidget(card, reroll_func, special_text=special_text)
            self.grid_layout.addWidget(wid, row, col)
            self.widget_list.append(wid)

    def _reset_layout(self):
        self.widget_list = []
        clear_layout(self.grid_layout)
        # while self.grid_layout.count():
        #     item = self.grid_layout.itemAt(0)
        #     self.grid_layout.removeItem(item)
        #     widget = item.widget()
        #     if widget:
        #         widget.deleteLater()
