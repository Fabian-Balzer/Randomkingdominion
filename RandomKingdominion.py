# -*- coding: utf-8 -*-
import sys
import pandas as pd
from modules.containers import WidgetContainer
from modules.data_handling import DataContainer
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG


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
        self.setWindowIcon(QG.QIcon('../Assets/CoverIcon.png'))
        self.setWindowTitle("Random Kingdominon")
        height = int(QW.QDesktopWidget().screenGeometry(-1).height()*0.85)
        width = int(QW.QDesktopWidget().screenGeometry(-1).width()*0.7)
        self.setGeometry(0, 0, width, height)
        self.move(20, 20)
        self.widgets = WidgetContainer(self._main)
        self.connect_buttons()

    def connect_buttons(self):
        self.widgets.buttons.randomize.clicked.connect(self.randomize)

    def randomize(self):
        self.data_container.randomize()
        self.display_kingdom()

    def display_kingdom(self):
        """Updates the kingdom cards"""
        self.widgets.labels.create_labels_from_supply(self.data_container.kingdom, self.data_container.csos)
        self.widgets.update_card_display()


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