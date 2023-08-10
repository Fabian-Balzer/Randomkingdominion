import numpy as np
import pandas as pd
from numpy.lib.function_base import disp

from .creator_functions import (
    create_buttons,
    create_cards,
    create_checkboxes,
    create_comboboxes,
    create_labels,
    create_layouts,
)
from .kingdom import Kingdom
from .utils import display_cards


class WidgetContainer:
    def __init__(self, _main, data_container):
        self._main = _main
        self.buttons = create_buttons()
        self.checkboxes = create_checkboxes(
            data_container.all_sets, data_container.all_attack_types, self.buttons
        )
        self.comboboxes = create_comboboxes()
        self.layouts = create_layouts(self._main)
        self.labels = create_labels()
        self.arrange_widgets()

    def arrange_widgets(self):
        self.layouts["Settings"].addWidget(self.checkboxes["ExpansionGroup"])
        self.layouts["Settings"].addWidget(self.comboboxes["QualityGroup"])
        self.layouts["Settings"].addWidget(self.checkboxes["AttackTypeGroup"])
        # self.layouts["Settings"].addWidget(self.checkboxes["AttackTypeGroup"])
        self.layouts["Settings"].addStretch()
        self.layouts["Settings"].addWidget(self.layouts["RandomizeNavigationWid"])
        self.layouts["RandomizeNavigation"].addWidget(self.buttons["Previous"])
        self.layouts["RandomizeNavigation"].addWidget(self.buttons["Randomize"])
        self.layouts["RandomizeNavigation"].addWidget(self.buttons["Next"])
        self.layouts["Settings"].addWidget(self.buttons["PrintKingdom"])
        for label in self.labels.values():
            self.layouts["Stats"].addWidget(label)

    def update_card_display(self, kingdom: Kingdom):
        self.cards = create_cards(kingdom)
        display_cards(self.cards, self.layouts, "Kingdom", num_rows=2)
        display_cards(
            self.cards, self.layouts, "Landscape", num_rows=1, size=(250, 170)
        )
        self.labels["qualities"].setText(kingdom.qualities.prettify())
