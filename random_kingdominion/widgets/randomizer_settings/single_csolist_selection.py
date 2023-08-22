from functools import partial

import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW

from random_kingdominion.constants import ALL_CSOS
from random_kingdominion.utils import CustomConfigParser, clear_layout, get_row_and_col
from random_kingdominion.widgets.basic_widgets import (
    CustomButton,
    TextValidationSubmissionWidget,
)


class CSOSelectionDisplay(QW.QWidget):
    removeButtonPressed = QC.pyqtSignal(str)

    def __init__(self, initial_list: list[str]):
        super().__init__()
        self.grid_layout = QW.QGridLayout(self)
        self.grid_layout.setAlignment(QC.Qt.AlignTop | QC.Qt.AlignLeading)
        self.grid_layout.setContentsMargins(1, 1, 1, 1)
        self.remove_button_dict = {}
        self.set_displayed_csos(initial_list)

    def set_displayed_csos(self, cso_list: list[str]):
        clear_layout(self.grid_layout)
        num_cols = 5
        for i, cso_name in enumerate(cso_list):
            row, col = get_row_and_col(i, num_cols)
            # TODO: Make this a picture with an x to remove
            button = CustomButton(width=100, text=cso_name)
            clickfunc = partial(self.removeButtonPressed.emit, cso_name)
            button.clicked.connect(clickfunc)
            self.remove_button_dict[cso_name] = button
            self.grid_layout.addWidget(button, row, col)


class SingleCSOListSelectionWidget(QW.QGroupBox):
    def __init__(self, selection_type: str, config: CustomConfigParser):
        super().__init__(selection_type)
        self.config = config
        self.selection_key = selection_type.lower().replace(" ", "_")
        lay = QW.QVBoxLayout(self)
        lay.setContentsMargins(1, 1, 1, 1)

        self.current_selection = self.config.getlist("General", self.selection_key)
        self.selection_textbox = TextValidationSubmissionWidget()
        self.selection_textbox.set_allowed_terms(self._get_allowed_terms())
        self.selection_textbox.submitPressed.connect(self.on_new_csos_submitted)
        lay.addWidget(self.selection_textbox)

        self.cso_display = CSOSelectionDisplay(self.current_selection)
        self.cso_display.removeButtonPressed.connect(self.on_cso_removed)
        lay.addWidget(self.cso_display)

    def on_new_csos_submitted(self, cso_list: list[str]):
        self.current_selection = sorted(set(cso_list).union(self.current_selection))
        self.config.setlist("General", self.selection_key, self.current_selection)
        self.cso_display.set_displayed_csos(self.current_selection)
        self.selection_textbox.set_allowed_terms(self._get_allowed_terms())

    def on_cso_removed(self, cso_name: str):
        self.current_selection.remove(cso_name)
        self.config.setlist("General", self.selection_key, self.current_selection)
        self.cso_display.set_displayed_csos(self.current_selection)
        self.selection_textbox.set_allowed_terms(self._get_allowed_terms())

    def _get_allowed_terms(self) -> list[str]:
        mask = ALL_CSOS.IsInSupply | ALL_CSOS.IsAlly | ALL_CSOS.IsLandscape
        all_names = set(ALL_CSOS[mask].Name)
        allowed_terms = all_names.difference(set(self.current_selection))
        return allowed_terms
