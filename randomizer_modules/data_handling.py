# %%

from functools import reduce
from typing import Optional

from .config import CustomConfigParser, get_randomizer_config_options
from .constants import FPATH_CARD_DATA
from .kingdom import Kingdom
from .utils import read_dataframe_from_file


class DataContainer:
    def __init__(self, config: Optional[CustomConfigParser] = None):
        self.config = config if config is not None else get_randomizer_config_options()
        self.all_cards = read_dataframe_from_file(FPATH_CARD_DATA, eval_lists=True)
        self.all_expansions = list(set(self.all_cards["Expansion"]))
        self.all_attack_types = self.get_attack_types()
        self.rerolled_cards = []
        self.parameter_dict = {"RequireReaction": False, "attack_types": None}
        self.kingdom = None

    def randomize(self):
        self.rerolled_cards = []
        self.kingdom = Kingdom(self.all_cards, config=self.config)
        self.kingdom.randomize(self.rerolled_cards)

    def reroll_card(self, old_card):
        """Creates a new card with the old card removed and tries a reroll."""
        kept_cards = [card for card in self.kingdom.kingdom_cards if card != old_card]
        if old_card == "Young Witch":
            kept_cards = [
                card
                for card in kept_cards
                if card != self.kingdom.special_targets["Bane"]
            ]
        kept_landscapes = [card for card in self.kingdom.landscapes if card != old_card]
        kept_ally = self.kingdom.ally if old_card != self.kingdom.ally else ""
        if (
            len(
                self.kingdom.get_kingdom_df()[
                    self.kingdom.get_kingdom_df()["Types"].apply(
                        lambda x: "Liaison" in x
                    )
                ]
            )
            == 0
        ):
            kept_ally = ""
        self.kingdom = Kingdom(
            self.all_cards,
            config=self.config,
            kingdom_cards=kept_cards,
            landscapes=kept_landscapes,
            ally=kept_ally,
        )
        self.rerolled_cards.append(old_card)
        self.kingdom.randomize(self.rerolled_cards)

    def get_attack_types(self):
        all_types = reduce(lambda x, y: x + y, self.all_cards["attack_types"])
        set_ = set(all_types)
        set_.discard("")
        return sorted(list(set_))

    def select_or_deselect(self, checkbox_dict, button):
        pass
        # if len(self.selected_sets) == 0:
        #     for checkbox in

    def select_previous(self):
        index = self.kingdom.history.index(self.kingdom)
        if index > 0:
            self.kingdom = self.kingdom.history[index - 1]

    def select_next(self):
        index = self.kingdom.history.index(self.kingdom)
        if index < len(self.kingdom.history) - 1:
            self.kingdom = self.kingdom.history[index + 1]


def create_supply(kingdom, landscapes):
    supply = kingdom.append(landscapes, sort=False)
    supply = supply.sort_values(
        by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"],
        ascending=[False, True, True, True, True],
    )
    return supply


def give_card(df, name):
    return df[df["Name"] == name]


if __name__ == "__main__":
    a = DataContainer()
    a.randomize()
    print(a.kingdom)
    c = a.all_cards
