import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion import CustomConfigParser

from ..basic_widgets import CollapsibleBox, CustomRangeSlider
from .single_csolist_selection import SingleCSOListSelectionWidget


class GeneralSettingsWidget(CollapsibleBox):
    """A widget to display the general settings, which includes
    tweaking the number of landscapes
    """

    def __init__(self, config: CustomConfigParser):
        super().__init__(title="General settings", initially_collapsed=False)
        self.config = config

        lay = QW.QVBoxLayout()
        lay.setContentsMargins(0, 0, 10, 0)

        self._init_landscape_slider()
        lay.addWidget(self.landscape_widget)
        self.banned_selection_widget = SingleCSOListSelectionWidget(
            "Banned CSOs", config
        )
        self.disliked_selection_widget = SingleCSOListSelectionWidget(
            "Disliked CSOs", config
        )
        self.liked_selection_widget = SingleCSOListSelectionWidget("Liked CSOs", config)
        self.required_selection_widget = SingleCSOListSelectionWidget(
            "Required CSOs", config
        )
        lay.addWidget(self.banned_selection_widget)
        lay.addWidget(self.disliked_selection_widget)
        lay.addWidget(self.liked_selection_widget)
        lay.addWidget(self.required_selection_widget)
        self.setContentLayout(lay)
        self._set_initial_values()

    def _init_landscape_slider(self):
        self.landscape_widget = QW.QWidget()
        lay = QW.QHBoxLayout(self.landscape_widget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.num_landscapes_range_slider = CustomRangeSlider()
        self.num_landscapes_range_slider.setFixedWidth(300)
        self.num_landscapes_label = QW.QLabel("")
        self.num_landscapes_label.setAlignment(QC.Qt.AlignTop)
        self.num_landscapes_label.setFixedWidth(200)
        self.num_landscapes_range_slider.value_changed.connect(
            self.register_num_landscape_change
        )
        lay.addWidget(self.num_landscapes_label)
        lay.addWidget(self.num_landscapes_range_slider)
        lay.addStretch()
        lay.setAlignment(QC.Qt.AlignTop)

    def _set_initial_values(self):
        """Set the initial state given the state of the config."""
        min_val = self.config.getint("General", "min_num_landscapes")
        max_val = self.config.getint("General", "max_num_landscapes")
        self.num_landscapes_range_slider.set_values(min_val, max_val)

    def register_num_landscape_change(self):
        """Displays the values of the range-slider in the text label
        and saves them to config"""
        min_val, max_val = self.num_landscapes_range_slider.get_values()
        self.config.set("General", "min_num_landscapes", str(min_val))
        self.config.set("General", "max_num_landscapes", str(max_val))
        if min_val == max_val:
            text = f"Allow exactly {min_val} landscapes."
        else:
            text = f"Allow between {min_val} and {max_val} landscapes."
        self.num_landscapes_label.setText("<b>Landscape amount:</b><br>" + text)
