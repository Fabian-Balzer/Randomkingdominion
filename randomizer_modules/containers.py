from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from .base_widgets import HorizontalBarWidget, QualityIcon
from .config import CustomConfigParser
from .constants import COLOR_PALETTE, QUALITIES_AVAILABLE
from .creator_functions import (AttackTypeGroupWidget, ExpansionGroupWidget,
                                GeneralRandomizerSettingsWidget,
                                QualitySelectionGroupWidget, create_buttons)
from .kingdom import Kingdom
from .kingdom_display_widget import KingdomDisplayWidget
from .utils import get_expansion_icon_path, get_row_and_col


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
        self.descriptor_icon = QualityIcon(self.name)
        self.descriptor_label = QW.QLabel(qual.capitalize())
        self.descriptor_label.setFixedSize(80, 40)
        self.bar_wid = HorizontalBarWidget()
        self.bar_wid.setFixedSize(150, 30)
        self.value_name_label = QW.QLabel("-")
        self.unique_types_label = QW.QLabel("-")

        lay = QW.QHBoxLayout(self)
        lay.setAlignment(QC.Qt.AlignLeft)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lay.addWidget(self.descriptor_icon)
        lay.addWidget(self.descriptor_label)
        lay.addWidget(self.bar_wid)
        lay.addWidget(self.value_name_label)
        lay.addWidget(self.unique_types_label)

    def set_total_quality_value(self, kingdom: Kingdom):
        """Manipulate the state of this widget to set the quality value"""
        self.setToolTip(kingdom.get_card_string_for_quality(self.name))
        value = kingdom.total_qualities[self.name]
        self.value_name_label.setText(self.quality_name_dict[value])
        self.bar_wid.setValue(value)
        self.descriptor_icon.set_overlay_cross(value == 0)
        self.unique_types_label.setText(kingdom.get_unique_types(self.name))

class ExpansionIcon(QW.QWidget):
    def __init__(self, expansion_name: str):
        super().__init__()
        icon_path = get_expansion_icon_path(expansion_name)
        container = QW.QFrame(self)
        container.setObjectName("bordered-container")

        layout = QW.QHBoxLayout(container)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(1)
        pixmap = QG.QPixmap(icon_path)
        aspect_ratio = pixmap.width() / pixmap.height()
        target_width = 30
        target_height = int(target_width / aspect_ratio)
        pixmap = pixmap.scaled(target_width, target_height, QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation)
        self.icon = QW.QLabel()
        self.icon.setPixmap(pixmap)
        self.text = QW.QLabel(expansion_name)
        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        layout.addStretch()
        
        # Set the container as the main layout of the widget
        main_layout = QW.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        self.setFixedSize(135, 40)
        color = COLOR_PALETTE.selected_green
        border_style = f"""
            #bordered-container {{
                border: 1px solid black;
                border-radius: 4px; /* Make the border round */
                padding-left: 5px; /* Adjust the padding to move text to the right */
                padding-right: 5px; /* Reset padding on the right */
                background-color: {color}; /* Set the background color */
            }}
        """
        container.setStyleSheet(border_style)

class KingdomExpansionGroupWidget(QW.QGroupBox):
    def __init__(self):
        super().__init__(title="Used expansions")
        self.main_layout = QW.QGridLayout(self)
        self.setSizePolicy(
            QW.QSizePolicy.Preferred,  # Horizontal size policy
            QW.QSizePolicy.Preferred   # Vertical size policy
            )
    
    def set_expansions(self, kingdom: Kingdom):
        """Set the expansion display to the ones of the current kingdom"""
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for i, expansion in enumerate(sorted(kingdom.expansions)):
            row, col = get_row_and_col(i, max_columns=2)
            wid = ExpansionIcon(expansion)
            self.main_layout.addWidget(wid, row, col)
        spacer = QW.QSpacerItem(0, 0, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum)
        self.main_layout.addItem(spacer, 0, 2)

class KingdomStatsDisplay(QW.QGroupBox):
    """Contains a grid with a total display for each of the qualities."""

    def __init__(self):
        super().__init__(title="Stat summary")
        main_layout = QW.QHBoxLayout(self)

        left_part_widget = QW.QWidget()
        lay = QW.QVBoxLayout(left_part_widget)
        lay.setContentsMargins(1, 1, 1, 1)
        lay.setSpacing(0)
        self.quality_wid_dict: dict[str, SingleQualityDisplay] = {}
        for qual in QUALITIES_AVAILABLE:
            qual_display = SingleQualityDisplay(qual)
            lay.addWidget(qual_display)
            self.quality_wid_dict[qual] = qual_display
        lay.addStretch()

        right_part_widget = QW.QWidget()
        lay = QW.QVBoxLayout(right_part_widget)
        lay.setContentsMargins(1, 1, 1, 1)
        self.expansion_widget = KingdomExpansionGroupWidget()
        lay.addWidget(self.expansion_widget)
        lay.addStretch()
        main_layout.addWidget(left_part_widget)
        main_layout.addWidget(right_part_widget)

    def display_kingdom_stats(self, kingdom: Kingdom):
        """Update the display given the new kingdom"""
        for qual in QUALITIES_AVAILABLE:
            self.quality_wid_dict[qual].set_total_quality_value(kingdom)
        self.expansion_widget.set_expansions(kingdom)


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
        self.general_settings_group = GeneralRandomizerSettingsWidget(config)
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

    def update_card_display(self, kingdom: Kingdom):
        self.kingdom_display.replace_images(kingdom)
        self.stats_display.display_kingdom_stats(kingdom)
