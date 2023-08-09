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
# %%

import sys

import PyQt5.QtWidgets as QW
from randomizer_modules.main_ui import UIMainWindow


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
