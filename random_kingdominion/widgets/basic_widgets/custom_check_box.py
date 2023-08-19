
import PyQt5.QtWidgets as QW


class CustomCheckBox(QW.QCheckBox):
    """Modified version of QCheckBoxes.
    Creates a QCheckBox with a given text and tooltip.
    params:
        text: Text to be shown
        tooltip: optionally create a tooltip for the edit
        checked: Bool set to false by default.
    """

    def __init__(self, text=None, tooltip=None, checked=False, width=150):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setChecked(checked)
        if width is not None:
            self.setFixedWidth(width)
        self.setStyleSheet("QCheckBox {color: rgb(0, 0, 0); height: 18 px}")
