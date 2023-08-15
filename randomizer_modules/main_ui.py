from functools import partial

from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from .config import get_randomizer_config_options
from .constants import PATH_ASSETS
from .containers import WidgetContainer
from .kingdom import Kingdom, KingdomManager, KingdomRandomizer


class UIMainWindow(QW.QMainWindow):
    """The main window to host all widgets and data of the GUI."""

    def __init__(self):
        super().__init__()
        self._main = QW.QWidget()
        self.setCentralWidget(self._main)
        self.config = get_randomizer_config_options()
        self.kingdom_randomizer = KingdomRandomizer(self.config)
        self.kingdom_manager = KingdomManager()
        self.current_kingdom: Kingdom = None
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
        self.widgets = WidgetContainer(self._main, self.config)
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
        clipboard.setText(str(self.current_kingdom))

    def randomize(self):
        self.current_kingdom = self.kingdom_randomizer.randomize_new_kingdom()
        self.kingdom_manager.add_kingdom(self.current_kingdom)
        self.display_kingdom()

    def reroll_card(self, old_card: str):
        """Creates a new kingdom with the old card removed and tries a reroll."""
        self.current_kingdom = self.kingdom_randomizer.reroll_single_card(
            self.current_kingdom, old_card
        )
        self.kingdom_manager.add_kingdom(self.current_kingdom)
        self.display_kingdom()

    def display_kingdom(self):
        """Updates the kingdom cards"""
        self.widgets.update_card_display(self.current_kingdom)
        button_dict = self.widgets.kingdom_display.reroll_button_dict
        for card_name, button in button_dict.items():
            button.clicked.connect(partial(self.reroll_card, card_name))

    def select_previous(self):
        index = self.kingdom_manager.kingdoms.index(self.current_kingdom)
        if index > 0:
            self.current_kingdom = self.kingdom_manager.kingdoms[index - 1]
        self.display_kingdom()

    def select_next(self):
        index = self.kingdom_manager.kingdoms.index(self.current_kingdom)
        if index < len(self.kingdom_manager.kingdoms) - 1:
            self.current_kingdom = self.kingdom_manager.kingdoms[index + 1]
        self.display_kingdom()

    def closeEvent(self, event):
        self.config.save_to_disk()
        event.accept()
