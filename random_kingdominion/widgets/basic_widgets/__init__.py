from .collapsible_box import CollapsibleBox
from .custom_button import CustomButton
from .custom_check_box import CustomCheckBox
from .custom_range_slider import CustomRangeSlider
from .custom_slider import CustomSlider
from .horizontal_bar_widget import HorizontalBarWidget
from .image_cutout_widget import ImageCutoutWidget
from .picture_check_box import PictureCheckBox
from .quality_icon import QualityIcon
from .scrollable_group_box import ScrollableGroupBox

__all__ = ["CollapsibleBox", "CustomButton",
           "CustomCheckBox", "CustomRangeSlider",
           "CustomSlider", "HorizontalBarWidget",
           "ImageCutoutWidget", "PictureCheckBox",
           "QualityIcon", "ScrollableGroupBox"]

# Some unused subclasses which might be handy later:

# class CoolRadioButton(QW.QRadioButton):
#     """Modified version of QRadioButtons.
#     Creates a QRadioButton with a given placeholder and tooltip.
#     params:
#         lineText: Text to be already entered. Overrides placeholder.
#         placeholder: Text to be displayed by default
#         tooltip: optionally create a tooltip for the edit"""

#     def __init__(self, text=None, tooltip=None, width=50):
#         super().__init__()
#         self.setText(text)
#         self.setToolTip(tooltip)
#         self.setMinimumWidth(width)
#         self.setStyleSheet(
#             """QRadioButton {padding: 1px 1px;
#                            color: black; background-color:
#                            qlineargradient(x1: 0, y1: 0, 
#                            2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
#                            font: bold 14px} 
#                            QRadioButton:checked {color: rgb(0, 0, 150)}
#                            """
#         )


# def create_radio_buttons(group, names, tooltips=None):
#     """
#     Creates QRadioButtons with the names passed through 'names' and adds them
#     to a RadioButton group.
#     params:
#         group: QButtonGroup object
#         names: List of Strings for the radio button names
#         tooltip: optionally create a tooltip for the buttons
#     returns:
#         button_dict: Dictionary of QRadioButtonObjects with their names
#     """
#     tooltips = tooltips if tooltips is not None else [None for name in names]
#     buttons = []
#     for i, name in enumerate(names):
#         RadioButton = CoolRadioButton(name, tooltips[i])
#         group.addButton(RadioButton)
#         buttons.append(RadioButton)
#     button_dict = dict(zip(names, buttons))
#     return button_dict


# class CoolSpinBox(QW.QSpinBox):
#     """Modified version of QSpinBox
#     Creates a QSpinBox with a given range and start value
#     params:
#         range_: range for the Box
#         value: start value. Needs to be in range.
#         tooltip: optionally create a tooltip for the edit
#     """

#     def __init__(self, range_=(0, 100), value=50, tooltip=None, width=250):
#         super().__init__()
#         self.setRange(*range_)
#         self.setValue(value)
#         self.setToolTip(tooltip)
#         if width:
#             self.setFixedWidth(width)
#         self.setStyleSheet(
#             """QSpinBox {color: rgb(0,0,0); height: 18px;
#                             background: transparent; padding-right: 5px;
#                             /* make room for the arrows */}"""
#         )

# class CoolComboBox(QW.QComboBox):
#     """Modified version of QSpinBox
#     Creates a QSpinBox with a given range and start value
#     params:
#         range_: range for the Box
#         value: start value. Needs to be in range.
#         tooltip: optionally create a tooltip for the edit
#     """

#     def __init__(self, possibilities, index, tooltip=None, width=250):
#         super().__init__()
#         self.addItems(possibilities)
#         self.setCurrentIndex(index)
#         self.setToolTip(tooltip)
#         if width:
#             self.setFixedWidth(width)
#         self.setStyleSheet(
#             """QSpinBox {color: rgb(0,0,0); height: 18px;
#                             background: transparent; padding-right: 5px;
#                             /* make room for the arrows */}"""
#         )
