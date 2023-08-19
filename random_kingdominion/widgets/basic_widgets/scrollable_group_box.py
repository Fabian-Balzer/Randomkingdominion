
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW


class ScrollableGroupBox(QW.QGroupBox):
    """A group box that is scrollable in the vertical direction.
    Refer to the content_layout attribute to add widgets.
    Parameters
    ----------
    title : str
        The title for the GroupBox
    parent : QWidget, optional
        The parent widget, by default None
    """

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)

        layout = QW.QVBoxLayout(self)

        scroll_area = QW.QScrollArea(self)
        layout.addWidget(scroll_area)

        scroll_content = QW.QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)

        lay = QW.QVBoxLayout(scroll_content)
        lay.setSpacing(5)
        lay.setContentsMargins(3, 3, 3, 3)
        self.content_layout = lay

        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(QC.Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(QC.Qt.ScrollBarAlwaysOff)

    def addWidget(self, widget: QW.QWidget, stretch: int = 0):
        """Convenience function to add a widget to the main layout of the box.

        Parameters
        ----------
        widget : QW.QWidget
            The widget to add
        stretch : int, optional
            Whether the added widget should make up a certain stretch, by default 0
        """
        # pylint: disable=invalid-name
        self.content_layout.addWidget(widget, stretch)
