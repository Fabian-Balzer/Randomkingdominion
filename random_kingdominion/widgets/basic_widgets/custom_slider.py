"""Contains a Slider used in the UI"""

import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion.utils.utils import override


class CustomSlider(QW.QSlider):
    """Simple horizontal slider going from the min to the max val (including both)."""
    def __init__(self, min_val: int = 0, max_val: int = 5):
        super().__init__(QC.Qt.Horizontal)
        self.setRange(min_val, max_val)
        self.setFixedHeight(20)
        self.setTickInterval(1)
        self.setStyleSheet(
            """
            QSlider::handle:horizontal {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 gray, stop:1 darkGreen);
                border: .5px solid;
                width: 10px;
                }
            QSlider::handle:vertical { 
                height: 15px; 
            }
    
            QSlider::handle:horizontal:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 darkGreen, stop:1 gray);
            }
            """
        )
    @override
    def wheelEvent(self, event):
        # Do nothing to prevent scrolling from changing the value
        pass