import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from ...utils import clear_layout


class CollapsibleBox(QW.QWidget):
    """A collapsible box with content that can be hidden if desired."""

    def __init__(self, title="", parent=None, initially_collapsed=True):
        super().__init__(parent)

        self.toggle_button = self.init_toggle_button(title)
        self.content_area = QW.QWidget()
        self.content_layout = QW.QVBoxLayout(self.content_area)

        outer_layout = QW.QVBoxLayout(self)
        outer_layout.addWidget(self.toggle_button)
        outer_layout.addWidget(self.content_area)
        outer_layout.setSpacing(0)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_button.setChecked(initially_collapsed)
        self.set_collapsed(initially_collapsed)

    def init_toggle_button(self, title: str):
        button = QW.QToolButton(text=title, checkable=True)
        button.setStyleSheet("QToolButton { border: none; }")
        button.setToolButtonStyle(QC.Qt.ToolButtonTextBesideIcon)
        button.setArrowType(QC.Qt.RightArrow)
        button.clicked.connect(self.on_button_clicked)
        return button

    def set_collapsed(self, collapsed: bool):
        self.toggle_button.setArrowType(
            QC.Qt.RightArrow if collapsed else QC.Qt.DownArrow
        )
        self.content_area.setVisible(not collapsed)

    @QC.pyqtSlot()
    def on_button_clicked(self):
        self.set_collapsed(self.toggle_button.isChecked())

    def setContentLayout(self, layout: QW.QWidget):
        # Clear the existing content layout and add the provided layout
        clear_layout(self.content_layout)
        self.content_layout.addLayout(layout)
