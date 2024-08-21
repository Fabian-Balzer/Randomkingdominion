import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from ...constants import PATH_ASSETS
from ...utils import override


class CustomRerollButton(QW.QLabel):
    """A button used for rerolling a single card."""

    clicked = QC.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = str(PATH_ASSETS.joinpath("icons/114px-Prince_icon.png"))
        style_sheet = """
            QLabel {
                background-color: white;  /* Change to your desired background color */
                border: 1px solid gray;
                border-radius: 10px;
                padding: 2px;
            }
        """
        self.setStyleSheet(style_sheet)
        self.setPixmap(QG.QPixmap(icon_path))
        self.setAlignment(QC.Qt.AlignCenter)
        self.setScaledContents(True)
        self.setFixedSize(QC.QSize(28, 28))
        self.setCursor(QC.Qt.PointingHandCursor)

    @override
    def mousePressEvent(self, event):
        # pylint: disable=unused-argument,invalid-name,missing-function-docstring
        self.clicked.emit()
