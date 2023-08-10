from functools import partial

from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from .config import get_randomizer_config_options
from .constants import PATH_ASSETS
from .containers import WidgetContainer
from .data_handling import DataContainer


class UIMainWindow(QW.QMainWindow):
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
        self.widgets = WidgetContainer(self._main, self.data_container)
        self.connect_buttons()
        self.set_values()

    def connect_buttons(self):
        self.widgets.buttons["Randomize"].clicked.connect(self.randomize)
        self.widgets.buttons["Previous"].clicked.connect(self.select_previous)
        self.widgets.buttons["Next"].clicked.connect(self.select_next)
        self.widgets.buttons["PrintKingdom"].clicked.connect(
            self.copy_kingdom_to_clipboard
        )
        for checkbox in self.widgets.checkboxes["ExpansionDict"].values():
            # The partial function must be used as lambda functions don't work with iterators
            checkbox.clicked.connect(checkbox.toggle)
            checkbox.clicked.connect(
                partial(
                    self.data_container.read_expansions,
                    self.widgets.checkboxes["ExpansionDict"],
                    self.widgets.buttons["ExpansionToggle"],
                )
            )
        self.widgets.buttons["ExpansionToggle"].clicked.connect(
            lambda: self.data_container.toggle_all_expansions(
                self.widgets.checkboxes["ExpansionDict"],
                self.widgets.buttons["ExpansionToggle"],
            )
        )
        for checkbox in self.widgets.checkboxes["AttackTypeDict"].values():
            # The partial function must be used as lambda functions don't work with iterators
            checkbox.clicked.connect(checkbox.toggle)
            checkbox.clicked.connect(
                partial(
                    self.data_container.read_attack_types,
                    self.widgets.checkboxes["AttackTypeDict"],
                    self.widgets.buttons["AttackTypeToggle"],
                )
            )
        self.widgets.buttons["AttackTypeToggle"].clicked.connect(
            lambda: self.data_container.toggle_all_attack_types(
                self.widgets.checkboxes["AttackTypeDict"],
                self.widgets.buttons["AttackTypeToggle"],
            )
        )
        # for type_, checkbox in self.widgets.checkboxes["AttackTypeDict"].items():
        #     checkbox.toggled.connect(partial(self.data_container.params.toggle_attack_type, type_))
        for qual, combobox in self.widgets.comboboxes["QualityDict"].items():
            combobox.currentIndexChanged.connect(
                partial(self.data_container.read_quality, qual)
            )

    def copy_kingdom_to_clipboard(self):
        """Copy the current kingdom to clipboard"""
        clipboard = QW.QApplication.clipboard()
        clipboard.setText(str(self.data_container.kingdom))

    def set_values(self):
        for exp in self.config.get_expansions():
            self.widgets.checkboxes["ExpansionDict"][exp].setChecked(True)
        for att in self.config.get_special_list("attack_types"):
            self.widgets.checkboxes["AttackTypeDict"][att].setChecked(True)
        for qual in self.config["Qualities"]:
            self.widgets.comboboxes["QualityDict"][qual].setCurrentIndex(
                self.config.get_quality(qual)
            )

    def randomize(self):
        self.data_container.randomize()
        self.display_kingdom()

    def display_kingdom(self):
        """Updates the kingdom cards"""
        self.widgets.update_card_display(self.data_container.kingdom)
        for entry in (
            self.widgets.cards["KingdomList"] + self.widgets.cards["LandscapeList"]
        ):
            if isinstance(entry, dict):
                button = entry["Button"]
                name = entry["Name"]
            else:
                button = entry.reroll_button
                name = entry.name
            button.clicked.connect(partial(self.reroll_card, name))

    def reroll_card(self, card_name):
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
