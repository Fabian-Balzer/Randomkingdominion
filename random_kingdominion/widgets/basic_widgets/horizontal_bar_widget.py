
from typing import Literal

import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from random_kingdominion.constants import COLOR_PALETTE
from random_kingdominion.utils import override


class HorizontalBarWidget(QW.QFrame):
    """A widget to display a horizontal bar with 5 different levels of being 'filled'."""

    clicked = QC.pyqtSignal(int)

    def __init__(self, parent=None, clickable=False):
        super().__init__(parent)
        self._width = 0
        self._color = QC.Qt.black
        self.is_disabled = False

        self.setFrameStyle(QW.QFrame.Box | QW.QFrame.Plain)
        self.setLineWidth(10)
        if clickable:
            self.clicked.connect(self.handle_click)

    def setValue(self, value: Literal[0, 1, 2, 3, 4]):
        """Set the value of the bar widget.
        """
        # pylint: disable=invalid-name
        if value == -1:
            value = 0
        rgba_tuple = COLOR_PALETTE.get_bar_level_color(value)  # Get RGBA values from the colormap
        self._color = (
            QG.QColor.fromRgbF(*rgba_tuple) if not self.is_disabled else QC.Qt.gray
        )
        self._width = value
        self.update()

    def getValue(self) -> int:
        """Get the value that the slider currently has.
        """
        # pylint: disable=invalid-name
        return self._width

    @override
    def paintEvent(self, event):
        # pylint: disable=unused-argument,invalid-name,missing-function-docstring
        painter = QG.QPainter(self)
        painter.setRenderHint(QG.QPainter.Antialiasing)

        # Draw the outer rectangular frame
        painter.drawRect(0, 0, self.width(), self.height())

        painter.setBrush(self._color)
        width = int(self._width / 4 * self.width())
        painter.drawRect(1, 1, width - 2, self.height() - 2)

        # Draw the scale
        scale_height = 5
        scale_width = int(self.width() / 4)
        scale_start_y = self.height() - scale_height
        for i in range(5):
            x = i * scale_width
            painter.drawLine(x, scale_start_y, x, self.height())

    @override
    def mousePressEvent(self, event: QG.QMouseEvent):
        # pylint: disable=unused-argument,invalid-name,missing-function-docstring
        # Calculate the clicked value based on the click position
        click_value = int((event.x() + self.width() / 8) / (self.width() / 4))
        self.clicked.emit(click_value)  # Emit the signal with the clicked value

    @override
    def mouseMoveEvent(self, event: QG.QMouseEvent):
        # pylint: disable=unused-argument,invalid-name,missing-function-docstring
        click_value = int((event.x() + self.width() / 8) / (self.width() / 4))
        self.clicked.emit(click_value)  # Emit the signal with the clicked value

    def handle_click(self, value):
        """Handles the click of the mouse on the widget by calling the setValue
        function in a safe way.
        """
        if value >= 5:
            value = 4
        elif value < 0:
            value = 0
        self.setValue(value)

    @override
    def setDisabled(self, disabled: bool):
        """Ensure that everything is grayed out properly."""
        # pylint: disable=unused-argument,invalid-name
        self.is_disabled = disabled
        self.setValue(self.getValue())

        # Call the original setDisabled method to perform the actual disabling
        super(QW.QFrame, self).setDisabled(disabled)


