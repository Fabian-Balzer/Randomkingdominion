import PyQt5.QtWidgets as QW

from random_kingdominion.kingdom import Kingdom, KingdomRandomizer

from .grouped_card_display import GroupedCardDisplay
from .grouped_landscape_display import GroupedLandscapeDisplay


class FullKingdomDisplay(QW.QWidget):
    """Display all the kingdom cards in
    an array similar to how DomBot provides it.
    Also hosts the buttons for rerolling which need to be
    reconnected externally
    """

    def __init__(self):
        super().__init__()
        main_lay = QW.QVBoxLayout(self)
        main_lay.setContentsMargins(3, 3, 3, 3)
        main_lay.setSpacing(3)
        self.card_display = GroupedCardDisplay()
        main_lay.addWidget(self.card_display)
        self.landscape_display = GroupedLandscapeDisplay()
        main_lay.addWidget(self.landscape_display)

    def replace_images(self, kingdom: Kingdom, reroll_func: callable):
        """Resets the widget by clearing the grid layout and displaying
        the kingdom"""
        self.card_display.set_kingdom_cards(kingdom, reroll_func)
        self.landscape_display.set_landscapes(kingdom, reroll_func)
