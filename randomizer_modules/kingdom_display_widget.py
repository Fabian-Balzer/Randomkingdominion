from math import ceil

import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from .base_widgets import CoolButton, KingdomCardImageWidget
from .kingdom import Kingdom


class KingdomDisplayWidget(QW.QWidget):
    """Display all the kingdom cards (but not the landscapes) in
    an array similar to how DomBot provides it.
    Also hosts the buttons for rerolling which need to be
    reconnected externally."""

    def __init__(self):
        super().__init__()
        main_lay = QW.QVBoxLayout(self)
        main_lay.setContentsMargins(3, 3, 3, 3)
        main_lay.setSpacing(3)
        kingdom_display = QW.QWidget()
        lay = QW.QGridLayout(kingdom_display)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setSpacing(0)
        lay.setAlignment(QC.Qt.AlignTop | QC.Qt.AlignLeft)
        self.grid_layout = lay
        self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), QC.Qt.black)
        # self.setPalette(palette)
        main_lay.addWidget(kingdom_display)

        # Dictionary to contain buttons to be connected for the rerolling
        self.reroll_button_dict: dict[str, QW.QPushButton] = {}

        self.is_detailed = False
        self.kingdom = None
        self.switch_detailed_view_button = CoolButton(text="Toggle detailed view")
        self.switch_detailed_view_button.clicked.connect(self.toggle_detailed_view)
        main_lay.addWidget(self.switch_detailed_view_button)

    # @QC.pyqtSlot()
    def toggle_detailed_view(self):
        self.is_detailed = not self.is_detailed
        self.replace_images(self.kingdom)

    def replace_images(
        self,
        kingdom: Kingdom,
    ):
        """Resets the widget by clearing the grid layout and displaying
        the kingdom"""
        while self.grid_layout.count():
            item = self.grid_layout.itemAt(0)
            self.grid_layout.removeItem(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.reroll_button_dict = {}

        self.kingdom = kingdom
        # Recreate the image grid
        self.display_kingdom_cards(kingdom)
        self.display_kingdom_landscapes(kingdom)

    def display_kingdom_cards(self, kingdom: Kingdom):
        kingdom_df = kingdom.kingdom_card_df
        num_rows = 2
        num_cols = ceil(len(kingdom_df) / num_rows)
        for row in range(num_rows):
            for col in range(num_cols):
                index = row * num_cols + col
                if index >= len(kingdom_df):
                    continue
                card = kingdom_df.iloc[index]
                special_text = "Bane" if card.Name == kingdom.bane_pile else ""
                wid = KingdomCardImageWidget(
                    card, special_text=special_text, detailed=self.is_detailed
                )
                self.reroll_button_dict[card.Name] = wid.reroll_button
                self.grid_layout.addWidget(wid, row, col)

    def display_kingdom_landscapes(self, kingdom: Kingdom):
        kingdom_df = kingdom.kingdom_landscape_df

        num_cols = len(kingdom_df)
        for col in range(num_cols):
            landscape = kingdom_df.iloc[col]
            wid = KingdomCardImageWidget(landscape, detailed=self.is_detailed)
            self.reroll_button_dict[landscape.Name] = wid.reroll_button
            self.grid_layout.addWidget(wid, 2, col * 2, 1, 2)
