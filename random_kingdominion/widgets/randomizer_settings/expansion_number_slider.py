import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from random_kingdominion import CustomConfigParser

from ..basic_widgets import CustomSlider


class ExpansionNumSlider(QW.QWidget):
    def __init__(self, config: CustomConfigParser):
        super().__init__()
        self.config = config

        # The maximum of the slider
        self.limiting_num = 5

        self._init_slider_with_labels()

        overarching_layout = QW.QHBoxLayout(self)
        overarching_layout.setContentsMargins(0, 0, 0, 0)

        self.display_label = QW.QLabel("")
        self.display_label.setAlignment(QC.Qt.AlignTop)
        self.display_label.setFixedWidth(200)
        overarching_layout.addWidget(self.display_label)
        overarching_layout.addWidget(self.slider_wid)
        overarching_layout.addStretch()
        self._set_initial_value()

    def _set_initial_value(self):
        num_exp_val = self.config.getint("Expansions", "max_num_expansions")
        self.slider.setValue(num_exp_val)
        self.set_max_expansion_num()

    def _init_slider_with_labels(self):
        self.slider_wid = QW.QWidget()
        layout = QW.QVBoxLayout(self.slider_wid)
        layout.setContentsMargins(0, 0, 0, 0)

        self.slider = CustomSlider(0, self.limiting_num)
        self.slider.setFixedWidth(300)
        self.slider.valueChanged.connect(self.set_max_expansion_num)
        self.slider.setTickPosition(QW.QSlider.TicksBelow)

        self.labels_widget = QW.QWidget()
        lay = QW.QHBoxLayout(self.labels_widget)
        lay.setContentsMargins(0, 0, 3, 0)
        for tick in range(0, self.limiting_num + 1):
            label_text = str(tick) if tick != 0 else "all"
            label = QW.QLabel(label_text)
            label.setAlignment(QC.Qt.AlignCenter)
            lay.addWidget(label)
            if tick < self.limiting_num:
                lay.addItem(
                    QW.QSpacerItem(
                        0, 0, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum
                    )
                )
        lay.setAlignment(QC.Qt.AlignTop)
        layout.addWidget(self.slider)
        layout.addWidget(self.labels_widget)

    def set_max_expansion_num(self):
        """Set the number of expansions maximally allowed to the current value of
        the slider, and handle the UI updates.
        """
        value = self.slider.value()
        self.config.set("Expansions", "max_num_expansions", str(value))
        if value == 0:
            text = "Pick from all expansions"
        else:
            text = f"Pick from at max {value} expansions."
        self.display_label.setText("<b>Maximum expansion number:</b><br>" + text)
