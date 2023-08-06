import numpy as np
import pandas as pd
from numpy.lib.function_base import disp

import modules.creator_functions as cf
import modules.utils as utils


class WidgetContainer:
    def __init__(self, _main, data_container):
        self._main = _main
        self.buttons = cf.create_buttons()
        self.checkboxes = cf.create_checkboxes(
            data_container.all_sets, data_container.all_attack_types, self.buttons)
        self.comboboxes = cf.create_comboboxes()
        self.layouts = cf.create_layouts(self._main)
        self.labels = cf.create_labels()
        self.arrange_widgets()

    def arrange_widgets(self):
        self.layouts["Settings"].addWidget(self.checkboxes["ExpansionGroup"])
        self.layouts["Settings"].addWidget(self.comboboxes["QualityGroup"])
        self.layouts["Settings"].addWidget(self.checkboxes["AttackTypeGroup"])
        # self.layouts["Settings"].addWidget(self.checkboxes["AttackTypeGroup"])
        self.layouts["Settings"].addStretch()
        self.layouts["Settings"].addWidget(
            self.layouts["RandomizeNavigationWid"])
        self.layouts["RandomizeNavigation"].addWidget(
            self.buttons["Previous"])
        self.layouts["RandomizeNavigation"].addWidget(
            self.buttons["Randomize"])
        self.layouts["RandomizeNavigation"].addWidget(
            self.buttons["Next"])
        self.layouts["Settings"].addWidget(self.buttons["PrintKingdom"])
        for label in self.labels.values():
            self.layouts["Stats"].addWidget(label)

    def update_card_display(self, kingdom):
        self.cards = cf.create_cards(kingdom)
        utils.display_cards(self.cards, self.layouts, "Kingdom", num_rows=2)
        utils.display_cards(self.cards, self.layouts,
                            "Landscape", num_rows=1, size=(250, 170))
        self.labels["qualities"].setText(kingdom.qualities.prettify())
