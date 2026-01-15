import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion import CustomConfigParser

from ..basic_widgets import CustomCheckBox, HorizontalBarWidget, QualityIcon


class SingleQualitySelectionWidget(QW.QWidget):
    """One row to set the requested value of the quality, including
    a slider for flexibility, and a checkbox to exclude the given
    quality completely.

    Parameters
    ----------
    qual : str
        The quality to display
    config : CustomConfigParser
        The ConfigParser to store the data at.
    """

    def __init__(self, qual: str, config: CustomConfigParser):
        super().__init__()
        self.config = config
        self.qual_name = qual

        self.icon = QualityIcon(qual)

        self.label = QW.QLabel(
            f"{qual.capitalize()}:\nDesired minimum {qual} quality of the kingdom."
        )
        # The slider to select the requested quality:
        tooltip = f"Upon randomization, we will try to achieve at least this amount of {qual} quality in the kingdom."
        self.selection_box = HorizontalBarWidget(clickable=True)
        self.selection_box.setToolTip(tooltip)
        self.selection_box.setFixedSize(80, 20)
        self.selection_box.clicked.connect(self.set_quality)

        # The checkbox to exclude this quality:
        self.forbid_this_box = CustomCheckBox(
            f"No {qual}",
            "Completely exclude any card that shows this quality from the draw pool",
        )
        self.forbid_this_box.clicked.connect(self.toggle_forbid_quality)

        lay = QW.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.icon)
        lay.addWidget(self.selection_box)
        lay.addWidget(self.label)
        lay.addWidget(self.forbid_this_box)

        self._set_initial_state()

    def _set_initial_state(self):
        self.selection_box.setValue(
            int(self.config.get_requested_quality(self.qual_name))  # type: ignore
        )
        is_disabled = self.config.get_forbidden_quality(self.qual_name)
        self.forbid_this_box.setChecked(is_disabled)
        self.selection_box.setDisabled(is_disabled)
        self.icon.set_overlay_cross(is_disabled)
        self.label.setDisabled(is_disabled)

    @QC.pyqtSlot()
    def set_quality(self):
        """Set the desired quality."""
        value = self.selection_box.getValue()
        self.config.set_requested_quality(self.qual_name, value)

    @QC.pyqtSlot()
    def toggle_forbid_quality(self):
        """Handle the toggling of the checkbox and save its value to the config.
        If it is checked, the selection box is disabled."""
        new_state = self.forbid_this_box.isChecked()
        self.selection_box.setDisabled(new_state)
        self.label.setDisabled(new_state)
        self.icon.set_overlay_cross(new_state)
        self.config.set_forbidden_quality(self.qual_name, new_state)

    def reset_state(self):
        """Reset this widget's state to default values."""
        self.selection_box.setValue(0)
        self.set_quality()
        self.forbid_this_box.setChecked(False)
        self.forbid_this_box.clicked.emit(False)
