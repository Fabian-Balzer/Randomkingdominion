
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW


class ImageCutoutWidget(QW.QWidget):
    """A widget displaying a rounded, cut-out version of the image
    supplied by impath.
    Parameters
    ----------
    impath : str
        The path of the image to display
    bottom_frac : float
        Set which part of the bottom to cut out, expected to be between 0 and 1
    top_frac : float
        Set which part of the bottom to cut out, expected to be between 0 and 1
    width : int
        The desired width of the image
    round_edges : bool, optional
        whether the edges of the image should be rounded, by default True
    """
    def __init__(
        self,
        impath: str,
        bottom_frac: float,
        top_frac: float,
        width: int,
        round_edges=True,
    ):
        super().__init__()
        self.image_path = impath
        self.init_ui()
        pixmap = self.get_cutout_pixmap(bottom_frac, top_frac, width)
        if pixmap is None:
            return
        if round_edges:
            pixmap = self.round_pixmap(pixmap)
        self.label.setPixmap(pixmap)
        self.setContentsMargins(0, 0, 0, 0)

    def init_ui(self):
        """Init.... well... most of the UI. This is a descriptive docstring."""
        layout = QW.QVBoxLayout()
        self.label = QW.QLabel(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

    def get_cutout_pixmap(self, bottom: float, top: float, width: float) -> QG.QPixmap:
        """Generate the cutout pixmap, first rescaling it and then selecting the proper
        section."""
        image = QG.QImage(self.image_path)
        if image.isNull():
            return

        aspect_ratio = image.width() / image.height()
        new_height = int(width / aspect_ratio)
        resized_image = image.scaled(
            width, new_height, QC.Qt.KeepAspectRatio, QC.Qt.SmoothTransformation
        )

        full_height = resized_image.height()
        cutout_bottom = int(full_height * bottom)
        cutout_top = int(full_height * top)
        cutout_height = cutout_top - cutout_bottom
        cutout = resized_image.copy(0, full_height - cutout_top, width, cutout_height)

        return QG.QPixmap.fromImage(cutout)

    def round_pixmap(self, pixmap):
        """Create a mask to round the edges of the given pixmap."""
        if pixmap is None:
            return
        rounded_mask = QG.QPixmap(pixmap.size())
        rounded_mask.fill(QC.Qt.transparent)

        mask_painter = QG.QPainter(rounded_mask)
        mask_path = QG.QPainterPath()
        rect = QC.QRectF(0, 0, pixmap.width(), pixmap.height())
        mask_path.addRoundedRect(rect, 10, 10)
        mask_painter.setRenderHint(QG.QPainter.Antialiasing)
        mask_painter.fillPath(mask_path, QC.Qt.white)
        mask_painter.end()

        rounded_pixmap = QG.QPixmap(pixmap.size())
        rounded_pixmap.fill(QC.Qt.transparent)

        pixmap_painter = QG.QPainter(rounded_pixmap)
        pixmap_painter.setRenderHint(QG.QPainter.Antialiasing)
        pixmap_painter.setClipPath(mask_path)
        pixmap_painter.drawPixmap(0, 0, pixmap)
        pixmap_painter.end()

        return rounded_pixmap
