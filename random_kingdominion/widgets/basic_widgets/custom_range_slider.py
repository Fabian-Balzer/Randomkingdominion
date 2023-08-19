
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from random_kingdominion.utils import override

from .custom_slider import CustomSlider


class CustomRangeSlider(QW.QWidget):
    """A range slider that allows the user to set two values where the
    second one is larger than the first."""

    value_changed = QC.pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QW.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.slider_max_value = 4
        self.slider_min = CustomSlider(0, self.slider_max_value)
        self.slider_min.valueChanged.connect(self.update_values)
        layout.addWidget(self.slider_min)

        self.slider_max = CustomSlider(0, self.slider_max_value)
        self.slider_max.valueChanged.connect(self.update_values)
        self.slider_max.setTickPosition(QW.QSlider.TicksBelow)
        layout.addWidget(self.slider_max)

        self.labels_widget = QW.QWidget()
        lay = QW.QHBoxLayout(self.labels_widget)
        lay.setContentsMargins(3, 0, 3, 0)
        for tick in range(self.slider_max_value + 1):
            label = QW.QLabel(str(tick))
            label.setAlignment(QC.Qt.AlignCenter)
            lay.addWidget(label)
            if tick < self.slider_max_value:
                lay.addItem(
                    QW.QSpacerItem(
                        0, 0, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
                    )
                )

        layout.addWidget(self.labels_widget)
        layout.addStretch()
        self.setLayout(layout)


    def set_values(self, min_val: int, max_val: int):
        """Set the values of the range and update the UI."""
        assert min_val <= max_val
        self.slider_max.setValue(max_val)
        self.slider_min.setValue(min_val)
        self.update_values()

    def update_values(self):
        """Safely updates the values of this slider."""
        min_val = self.slider_min.value()
        max_val = self.slider_max.value()
        if min_val >= max_val:
            self.slider_max.setValue(min_val)
        if max_val <= min_val:
            self.slider_min.setValue(max_val)
        self.update()  # necessary to have nice painting of the area in between
        self.value_changed.emit()

    def get_values(self) -> tuple[int, int]:
        """Get the current values of the sliders as a range of ints"""
        return self.slider_min.value(), self.slider_max.value()

    @override
    def paintEvent(self, event):
        # pylint: disable=unused-argument,invalid-name,missing-function-docstring
        # Create a painter to highlight the area in between the sliders
        painter = QG.QPainter(self)
        painter.setRenderHint(QG.QPainter.Antialiasing)

        # Calculate the positions of the slider handles:
        s_1 = self.slider_min
        min_pos = s_1.pos().x() + int(s_1.value() * s_1.width() / self.slider_max_value)
        y_1 = int(s_1.pos().y() + s_1.height() / 2)
        h_1 = int(s_1.height() / 2)

        s_2 = self.slider_max
        max_pos = s_2.pos().x() + int(s_2.value() * s_2.width() / self.slider_max_value)

        color_range_rect = min_pos, y_1 + 2, max_pos - min_pos, h_1 * 2 - 4

        # Draw color range
        painter.fillRect(*color_range_rect, QC.Qt.darkGreen)
