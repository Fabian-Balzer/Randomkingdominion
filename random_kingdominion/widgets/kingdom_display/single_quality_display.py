
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion.kingdom import Kingdom

from ..basic_widgets import HorizontalBarWidget, QualityIcon


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
