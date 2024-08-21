import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from ...constants import COLOR_PALETTE


class CardAmountLabel(QW.QLabel):
    """Label to display the amount of cards."""

    def __init__(self, amount: str | int, parent: QW.QWidget):
        super().__init__(str(amount), parent)
        self.setStyleSheet(
            f"""
                            background-color: {COLOR_PALETTE.selected_green};
                            border-radius:4;
                            border-color: black; 
                            border-width:1px; border-style: outset"""
        )
        self.setMargin(2)
        self.setScaledContents(True)
        self.setAlignment(QC.Qt.AlignCenter)
        font = self.font()
        font.setPointSize(8)
        self.setFont(font)
