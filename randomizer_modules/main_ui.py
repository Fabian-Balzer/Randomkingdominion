from functools import partial

from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from .config import get_randomizer_config_options
from .constants import PATH_ASSETS
from .containers import WidgetContainer
from .data_handling import DataContainer


class UIMainWindow(QW.QMainWindow):
    """The main window to host all widgets and data of the GUI."""

    def __init__(self):
        super().__init__()
        self._main = QW.QWidget()
        self.setCentralWidget(self._main)
        self.config = get_randomizer_config_options()
        self.data_container = DataContainer(config=self.config)
        self.init_ui()
        self.randomize()  # Start with a random selection

    # - Initialization methods
    def init_ui(self):
        """Contains all the actions needed for intitializing the interface."""
        self.setWindowIcon(QG.QIcon(str(PATH_ASSETS.joinpath("CoverIcon.png"))))
        self.setWindowTitle("Random Kingdominon")
        height = int(QW.QDesktopWidget().screenGeometry(-1).height() * 0.85)
        width = int(QW.QDesktopWidget().screenGeometry(-1).width() * 0.7)
        self.setGeometry(0, 0, width, height)
        self.move(20, 20)
        self.widgets = WidgetContainer(self._main, self.data_container, self.config)
        self.connect_buttons()

    def connect_buttons(self):
        self.widgets.buttons["Randomize"].clicked.connect(self.randomize)
        self.widgets.buttons["Previous"].clicked.connect(self.select_previous)
        self.widgets.buttons["Next"].clicked.connect(self.select_next)
        self.widgets.buttons["PrintKingdom"].clicked.connect(
            self.copy_kingdom_to_clipboard
        )

    def copy_kingdom_to_clipboard(self):
        """Copy the current kingdom to clipboard"""
        clipboard = QW.QApplication.clipboard()
        clipboard.setText(str(self.data_container.kingdom))

    def randomize(self):
        self.data_container.randomize()
        self.display_kingdom()

    def display_kingdom(self):
        """Updates the kingdom cards"""
        self.widgets.update_card_display(self.data_container.kingdom)
        button_dict = self.widgets.kingdom_display.reroll_button_dict
        for card_name, button in button_dict.items():
            button.clicked.connect(partial(self.reroll_card, card_name))

    def reroll_card(self, card_name: str):
        self.data_container.reroll_card(card_name)
        self.display_kingdom()

    def select_previous(self):
        self.data_container.select_previous()
        self.display_kingdom()

    def select_next(self):
        self.data_container.select_next()
        self.display_kingdom()

    def closeEvent(self, event):
        self.config.save_to_disk()
        event.accept()
