from numpy.lib.function_base import disp
import pandas as pd
import numpy as np
import modules.creator_functions as cf
import modules.utils as utils


class WidgetContainer:
    def __init__(self, _main, data_container):
        self._main = _main
        self.buttons = cf.create_buttons()
        all_sets = set(data_container.all_cards["Set"])
        all_attack_types = set(data_container.get_attack_types())
        params = params=data_container.params
        self.checkboxes = cf.create_checkboxes(all_sets,
            all_attack_types, params)
        self.spinners = cf.create_spinners()
        self.layouts = cf.create_layouts(self._main)
        self.arrange_widgets()

    def arrange_widgets(self):
        self.layouts["Settings"].addWidget(self.checkboxes["SetGroup"])
        self.layouts["Settings"].addWidget(self.spinners["QualityGroup"])
        self.layouts["Settings"].addWidget(self.checkboxes["AttackTypeGroup"])
        self.layouts["Settings"].addStretch()
        self.layouts["Settings"].addWidget(self.buttons["Randomize"])

    def update_card_display(self, kingdom, landscapes):
        self.labels = cf.create_labels(kingdom, landscapes)
        utils.display_labels(self.labels, self.layouts, "Kingdom", num_rows=2)
        utils.display_labels(self.labels, self.layouts, "Landscape", num_rows=1, size=(250, 150))


