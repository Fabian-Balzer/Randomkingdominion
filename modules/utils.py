import PyQt5.QtWidgets as QW


def createHorLayout(widList, stretch=True, spacing=0):
    """Create horizontal box layout widget containing widgets in widList"""
    wid = QW.QWidget()
    wid.setStyleSheet("""QWidget {border: 0px solid gray;
                           border-radius: 0px; padding: 0, 0, 0, 0}""")
    layout = QW.QHBoxLayout(wid)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for widget in widList:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch(1)
    return wid


class coolButton(QW.QPushButton):
    def __init__(self, width=None, text="", tooltip="", enabled=True):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setEnabled(enabled)
        if width is not None:
            self.setFixedWidth(width)
        self.setButtonStyle()

    def setButtonStyle(self,  backStart="#f6f7fa", backStop="#dadbde",
                       borderColor="100, 100, 100", bold="", height=20):
        """Sets the background and border color of the button and turns its
        text bold if requested."""
        self.setStyleSheet(
f"""QPushButton {{height: {height}px; background-color: 
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {backStart}, stop: 1 {backStop});
border-style: outset; border-width: 2px; border-radius: 5px; 
border-color: rgb({borderColor}); font: {bold} 14px; padding: 6px}}
QPushButton:hover {{background-color:
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
0 rgb(240, 240, 255), stop: 1 rgb(200, 200, 200))}}
QPushButton:pressed {{background-color:
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
0 rgb(200, 200, 200), stop: 1 rgb(140, 140, 140))}}""")

    def makeTextBold(self, height=20):
        self.setButtonStyle(bold="bold", height=height)

    def makeButtonRed(self):
        self.setButtonStyle(borderColor="255, 0, 0", bold="bold")
