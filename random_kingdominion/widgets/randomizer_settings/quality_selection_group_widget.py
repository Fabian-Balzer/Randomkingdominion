
import PyQt5.QtWidgets as QW

from random_kingdominion import CustomConfigParser
from random_kingdominion.constants import QUALITIES_AVAILABLE

from ..basic_widgets import CollapsibleBox, CustomButton
from .single_quality_selection_widget import SingleQualitySelectionWidget


class QualitySelectionGroupWidget(CollapsibleBox):
    """Hosts the group from which one can """
    def __init__(self, config: CustomConfigParser):
        super().__init__(title="Quality parameters", initially_collapsed=False)

        lay = QW.QVBoxLayout()
        self.wid_dict: dict[str, SingleQualitySelectionWidget] = {}
        for qual in QUALITIES_AVAILABLE:
            wid = SingleQualitySelectionWidget(qual, config)
            self.wid_dict[qual] = wid
            lay.addWidget(wid)
        self.reset_button = self.init_reset_button()
        lay.addWidget(self.reset_button)
        self.setContentLayout(lay)

    def init_reset_button(self) -> QW.QWidget:
        """Create a button to click on for resetting all values."""
        # TODO: Maybe implement a master slider to change everything at once?
        button = CustomButton(text="Reset preferences", width=200)
        button.clicked.connect(self.on_reset_clicked)
        return button

    # @QC.pyqtSlot()
    def on_reset_clicked(self):
        """Reset all the QualitySelection widgets."""
        for wid in self.wid_dict.values():
            wid.reset_state()
