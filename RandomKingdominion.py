# -*- coding: utf-8 -*-
"""
@author: Fabian Balzer

***
LICENSE:
    Copyright 2021 Fabian Balzer

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
***

Code to open a GUI Dominion randomizer
"""
import sys
import pandas as pd
from modules.containers import WidgetContainer
from modules.data_handling import DataContainer
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
from functools import partial


class UIMainWindow(QW.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QW.QWidget()
        self.setCentralWidget(self._main)
        self.data_container = DataContainer()
        self.init_ui()
        self.randomize()  # Start with a random selection

    # %% Initialization methods
    def init_ui(self):
        """Contains all the actions needed for intitializing the interface.
        """
        self.setWindowIcon(QG.QIcon('assets/CoverIcon.png'))
        self.setWindowTitle("Random Kingdominon")
        height = int(QW.QDesktopWidget().screenGeometry(-1).height()*0.85)
        width = int(QW.QDesktopWidget().screenGeometry(-1).width()*0.7)
        self.setGeometry(0, 0, width, height)
        self.move(20, 20)
        self.widgets = WidgetContainer(self._main, self.data_container)
        self.connect_buttons()
        self.set_values()

    def connect_buttons(self):
        self.widgets.buttons["Randomize"].clicked.connect(self.randomize)
        for set_, checkbox in self.widgets.checkboxes["SetDict"].items():
            # The partial function must be used as lambda functions don't work with iterators
            checkbox.toggled.connect(partial(self.data_container.get_sets, self.widgets.checkboxes["SetDict"]))
        # for type_, checkbox in self.widgets.checkboxes["AttackTypeDict"].items():
        #     checkbox.toggled.connect(partial(self.data_container.params.toggle_attack_type, type_))
        for quality_name, spinner in self.widgets.spinners["QualityDict"].items():
            spinner.valueChanged.connect(partial(self.data_container.get_quality_arg, quality_name))

    def set_values(self):
        self.data_container.set_sets(self.widgets.checkboxes["SetDict"])
        self.data_container.set_quality_args(self.widgets.spinners["QualityDict"])

    def randomize(self):
        self.data_container.randomize()
        self.display_kingdom()

    def display_kingdom(self):
        """Updates the kingdom cards"""
        self.widgets.update_card_display(self.data_container.kingdom, self.data_container.landscapes)


def start_program():
    """A function to include everything needed to start the application"""
    # Check whether there is already a running QApplication (e.g. if running
    # from an IDE). This setup prevents crashes for the next run:
    qapp = QW.QApplication.instance()
    if not qapp:
        qapp = QW.QApplication(sys.argv)
    app = UIMainWindow()  # creating the instance
    app.show()
    qapp.exec_()  # Start the Qt event loop


if __name__ == "__main__":
    start_program()