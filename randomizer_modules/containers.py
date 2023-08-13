from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from .constants import QUALITIES_AVAILABLE
from .creator_functions import (
    ExpansionGroupWidget,
    create_buttons,
    create_checkboxes,
    create_comboboxes,
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

    def __init__(self, qual: str):
        super().__init__()
        # TODO: Introduce picture and a small bar-chart-like label
        self.name = qual
        self.descriptor_label = QW.QLabel(qual)
        self.value_name_label = QW.QLabel("-")

        lay = QW.QHBoxLayout(self)
        lay.addWidget(self.descriptor_label)
        lay.addWidget(self.value_name_label)

    def set_total_quality_value(self, value: int):
        """Manipulate the state of this widget to set the quality value"""
        # TODO: Introduce dictionary to give more descriptive names to levels,
        # and to manipulate the bar chart
        self.value_name_label.setText(str(value))


class KingdomStatsDisplay(QW.QWidget):
    """Contains a grid with a total display for each of the qualities."""

    def __init__(self):
        super().__init__()
        lay = QW.QGridLayout(self)
        self.wid_dict: dict[str, SingleQualityDisplay] = {}
        for qual in QUALITIES_AVAILABLE:
            qual_display = SingleQualityDisplay(qual)
            lay.addWidget(qual_display)
            self.wid_dict[qual] = qual_display

    def display_kingdom_stats(self, kingdom: Kingdom):
        for qual, val in kingdom.total_qualities.items():
            self.wid_dict[qual].set_total_quality_value(val)


class WidgetContainer:
    """Contains the main widgets of the GUI."""

    def __init__(self, _main: QW.QWidget, data_container: DataContainer):
        self._main = _main
        self.buttons = create_buttons()
        self.expansion_group = ExpansionGroupWidget(data_container.all_expansions)
        self.checkboxes = create_checkboxes(
            data_container.all_attack_types, self.buttons
        )
        self.comboboxes = create_comboboxes()
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
        scroll_content_wid.addWidget(self.comboboxes["QualityGroup"])
        scroll_content_wid.addWidget(self.checkboxes["AttackTypeGroup"])
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
