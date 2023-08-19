import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion.kingdom import Kingdom
from random_kingdominion.utils import get_row_and_col

from .single_landscape_display import SingleLandscapeImageWidget


class GroupedLandscapeDisplay(QW.QWidget):
    """Display all cards of a given kingdom."""

    def __init__(self):
        super().__init__()
        self.grid_layout = QW.QGridLayout(self)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QC.Qt.black)
        self.setPalette(palette)
        self.reroll_button_dict = {}

    def set_landscapes(self, kingdom: Kingdom, reroll_func):
        self._reset_layout()
        landscape_df = kingdom.kingdom_landscape_df
        num_cols = 2 if len(landscape_df) < 5 else 3
        for i, landscape in landscape_df.reset_index(drop=True).iterrows():
            row, col = get_row_and_col(i, num_cols)
            # TODO: Mouse text
            wid = SingleLandscapeImageWidget(landscape, reroll_func)
            self.reroll_button_dict[landscape.Name] = wid.reroll_button
            self.grid_layout.addWidget(wid, row, col)

    def _reset_layout(self):
        self.reroll_button_dict = {}
        while self.grid_layout.count():
            item = self.grid_layout.itemAt(0)
            self.grid_layout.removeItem(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()
