import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from random_kingdominion.constants import COLOR_PALETTE, QUALITIES_AVAILABLE
from random_kingdominion.kingdom import Kingdom
from random_kingdominion.utils import get_expansion_icon_path, get_row_and_col
from random_kingdominion.utils import clear_layout

from .single_quality_display import SingleQualityDisplay


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
        pixmap = pixmap.scaled(
            target_width,
            target_height,
            QC.Qt.KeepAspectRatio,
            QC.Qt.SmoothTransformation,
        )
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
            QW.QSizePolicy.Preferred,  # Vertical size policy
        )

    def set_expansions(self, kingdom: Kingdom):
        """Set the expansion display to the ones of the current kingdom"""
        clear_layout(self.main_layout)
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
