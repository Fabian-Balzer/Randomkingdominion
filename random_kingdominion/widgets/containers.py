from PyQt5 import QtWidgets as QW

from random_kingdominion.kingdom import Kingdom, KingdomRandomizer
from random_kingdominion.utils.config import CustomConfigParser

from .basic_widgets import CustomButton, ScrollableGroupBox
from .kingdom_display import FullKingdomDisplay, KingdomStatsDisplay
from .randomizer_settings import (
    AttackTypeGroupWidget,
    ExpansionGroupWidget,
    GeneralSettingsWidget,
    QualitySelectionGroupWidget,
)


def create_buttons():
    button_dict = {}
    button_dict["Randomize"] = CustomButton(text="Randomize")
    button_dict["PrintKingdom"] = CustomButton(text="Print the kingdom")
    button_dict["Previous"] = CustomButton(text="Previous")
    button_dict["Next"] = CustomButton(text="Next")
    return button_dict


class WidgetContainer:
    """Contains the main widgets of the GUI."""

    def __init__(
        self,
        _main: QW.QWidget,
        config: CustomConfigParser,
    ):
        self._main = _main
        self.buttons = create_buttons()
        self.expansion_group = ExpansionGroupWidget(config)
        self.attack_type_group = AttackTypeGroupWidget(config)
        self.general_settings_group = GeneralSettingsWidget(config)
        self.quality_selection_group = QualitySelectionGroupWidget(config)
        self.main_layout = QW.QHBoxLayout()

        # Create widgets that will be aligned on the left side...
        self.settings_widget = self._init_settings_widget()
        self.navigation_widget = self._init_navigation_widget()
        self.leftside_widget = self._init_leftside_widget()

        # ...and now widgets that will be aligned on the right side...
        self.kingdom_display = FullKingdomDisplay()
        self.stats_display = KingdomStatsDisplay()

        self.rightside_widget = self._init_rightside_widget()
        self._init_main_widget()

    def _init_settings_widget(self) -> QW.QVBoxLayout:
        scroll_content_wid = ScrollableGroupBox("Settings")
        scroll_content_wid.addWidget(self.expansion_group)
        scroll_content_wid.addWidget(self.general_settings_group)
        scroll_content_wid.addWidget(self.quality_selection_group)
        scroll_content_wid.addWidget(self.attack_type_group)
        scroll_content_wid.content_layout.addStretch()
        scroll_content_wid.setMinimumWidth(600)
        return scroll_content_wid

    def _init_navigation_widget(self) -> QW.QHBoxLayout:
        wid = QW.QWidget()
        lay = QW.QHBoxLayout(wid)
        lay.addWidget(self.buttons["Previous"])
        lay.addWidget(self.buttons["Randomize"])
        lay.addWidget(self.buttons["Next"])
        return wid

    def _init_leftside_widget(self) -> QW.QVBoxLayout:
        wid = QW.QWidget()
        lay = QW.QVBoxLayout(wid)
        lay.addWidget(self.settings_widget)
        lay.addWidget(self.navigation_widget)
        return wid

    def _init_rightside_widget(self) -> QW.QVBoxLayout:
        wid = QW.QWidget()
        lay = QW.QVBoxLayout(wid)

        lay.addWidget(self.kingdom_display)
        lay.addWidget(self.stats_display)
        return wid

    def _init_main_widget(self):
        lay = QW.QHBoxLayout(self._main)
        lay.addWidget(self.leftside_widget)
        lay.addWidget(self.rightside_widget)

    def update_card_display(self, kingdom: Kingdom, reroll_func: callable):
        self.kingdom_display.replace_images(kingdom, reroll_func)
        self.stats_display.display_kingdom_stats(kingdom)
