
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from random_kingdominion.constants import PATH_ASSETS
from random_kingdominion.utils import override


class QualityIcon(QW.QLabel):
    """A small icon to display the image for the requested kingdom quality.

    Parameters
    ----------
    qual_name : str
        The quality name
    size : int, optional
        The size of the icon, by default 40
    """

    def __init__(self, qual_name: str, size=40):
        super().__init__()
        icon_path = PATH_ASSETS.joinpath(f"icons/qualities/{qual_name}.jpg")
        assert icon_path.is_file(), f"Couldn't find {qual_name} asset."
        self.setAlignment(QC.Qt.AlignHCenter)
        pixmap = QG.QPixmap(str(icon_path))
        pixmap = pixmap.scaled(
            QC.QSize(size, size), QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation
        )
        self.pixmap = pixmap
        self.setPixmap(pixmap)
        self.setFixedSize(size, size)
        self.overlay_cross = True  # Initialize overlay status

    def set_overlay_cross(self, overlay: bool):
        self.overlay_cross = overlay
        self.update()

    @override
    def paintEvent(self, event):
        # pylint: disable=unused-argument,invalid-name,missing-function-docstring
        painter = QG.QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        if self.overlay_cross:
            painter.setRenderHint(QG.QPainter.Antialiasing)

            # Draw a red "x" over the pixmap
            pen = QG.QPen(QG.QColor(QC.Qt.white))
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.width(), self.height())
            painter.drawLine(0, self.height(), self.width(), 0)
            pen = QG.QPen(QG.QColor(QC.Qt.darkRed))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.width(), self.height())
            painter.drawLine(0, self.height(), self.width(), 0)
