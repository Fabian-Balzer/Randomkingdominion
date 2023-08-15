# %%

from functools import reduce
from typing import Optional

import numpy as np

from .config import CustomConfigParser, get_randomizer_config_options
from .constants import FPATH_CARD_DATA
from .kingdom import Kingdom, KingdomRandomizer
from .utils import read_dataframe_from_file


class DataContainer:
    def __init__(self, config: Optional[CustomConfigParser] = None):
        self.config = config if config is not None else get_randomizer_config_options()
        self.all_cards = read_dataframe_from_file(FPATH_CARD_DATA, eval_lists=True)
        self.all_expansions = list(set(self.all_cards["Expansion"]))
        self.all_attack_types = self.get_attack_types()

        self.kingdom_randomizer = KingdomRandomizer(self.all_cards, self.config)
        self.kingdom: Kingdom | None = None

    def randomize(self):
        self.kingdom = self.kingdom_randomizer.randomize_new_kingdom()

    def reroll_card(self, old_card: str):
        """Creates a new card with the old card removed and tries a reroll."""
        self.kingdom = self.kingdom_randomizer.reroll_single_card(
            self.kingdom, old_card
        )

    def get_attack_types(self):
        all_types = reduce(lambda x, y: x + y, self.all_cards["attack_types"])
        return sorted(list(np.unique(all_types)))

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
