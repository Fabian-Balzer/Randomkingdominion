from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from .base_widgets import QualityIcon, HorizontalBarWidget
from .config import CustomConfigParser
from .constants import QUALITIES_AVAILABLE
from .creator_functions import (
    AttackTypeGroupWidget,
    ExpansionGroupWidget,
    QualitySelectionGroupWidget,
    create_buttons,
)
from .data_handling import DataContainer
from .kingdom import Kingdom, KingdomDisplayWidget


class ScrollableGroupBox(QW.QGroupBox):
    """A group box that is scrollable in the vertical direction.
    Refer to the content_layout attribute to add widgets."""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)

        layout = QW.QVBoxLayout(self)

        scroll_area = QW.QScrollArea(self)
        layout.addWidget(scroll_area)

        scroll_content = QW.QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)

        lay = QW.QVBoxLayout(scroll_content)
        lay.setSpacing(5)
        lay.setContentsMargins(3, 3, 3, 3)
        self.content_layout = lay

        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QC.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QC.Qt.ScrollBarAlwaysOff)

    def addWidget(self, widget: QW.QWidget, stretch: int = 0):
        self.content_layout.addWidget(widget, stretch)


class SingleQualityDisplay(QW.QWidget):
    """Hosts a picture and a small graph to display the
    given qualities' value for the kingdom."""

    quality_name_dict = {
        0: "Nonexistent",
        1: "Weak",
        2: "Sufficient",
        3: "Really good",
        4: "Fantastic",
    }

    def __init__(self, qual: str):
        super().__init__()
        self.name = qual
        self.descriptor_image = QualityIcon(self.name)
        self.descriptor_label = QW.QLabel(qual.capitalize())
        self.descriptor_label.setFixedSize(80, 40)
        self.bar_wid = HorizontalBarWidget()
        self.bar_wid.setFixedSize(150, 30)
        self.value_name_label = QW.QLabel("-")

        lay = QW.QHBoxLayout(self)
        lay.setAlignment(QC.Qt.AlignLeft)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addWidget(self.descriptor_image)
        lay.addWidget(self.descriptor_label)
        lay.addWidget(self.bar_wid)
        lay.addWidget(self.value_name_label)

    def set_total_quality_value(self, value: int):
        """Manipulate the state of this widget to set the quality value"""
        self.value_name_label.setText(self.quality_name_dict[value])
        self.bar_wid.setValue(value)


class KingdomStatsDisplay(QW.QGroupBox):
    """Contains a grid with a total display for each of the qualities."""

    def __init__(self):
        super().__init__(title="Stat summary")
        lay = QW.QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setSpacing(0)
        self.wid_dict: dict[str, SingleQualityDisplay] = {}
        for qual in QUALITIES_AVAILABLE:
            qual_display = SingleQualityDisplay(qual)
            lay.addWidget(qual_display)
            self.wid_dict[qual] = qual_display

    def display_kingdom_stats(self, kingdom: Kingdom):
        """Update the display given the new kingdom"""
        for qual, val in kingdom.total_qualities.items():
            self.wid_dict[qual].set_total_quality_value(val)


class WidgetContainer:
    """Contains the main widgets of the GUI."""

    def __init__(
        self,
        _main: QW.QWidget,
        data_container: DataContainer,
        config: CustomConfigParser,
    ):
        self._main = _main
        self.buttons = create_buttons()
        self.expansion_group = ExpansionGroupWidget(
            data_container.all_expansions, config
        )
        self.attack_type_group = AttackTypeGroupWidget(
            data_container.all_attack_types, config
        )
        self.quality_selection_group = QualitySelectionGroupWidget(config)
        self.main_layout = QW.QHBoxLayout()

        # Create widgets that will be aligned on the left side...
        self.settings_widget = self._init_settings_widget()
        self.navigation_widget = self._init_navigation_widget()
        self.leftside_widget = self._init_leftside_widget()

        # ...and now widgets that will be aligned on the right side...
        self.kingdom_display = KingdomDisplayWidget()
        self.stats_display = KingdomStatsDisplay()

        self.rightside_widget = self._init_rightside_widget()
        self._init_main_widget()

    def _init_settings_widget(self) -> QW.QVBoxLayout:
        scroll_content_wid = ScrollableGroupBox("Settings")
        scroll_content_wid.addWidget(self.expansion_group)
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

    def update_card_display(self, kingdom: Kingdom):
        self.kingdom_display.replace_images(kingdom)
        self.stats_display.display_kingdom_stats(kingdom)
