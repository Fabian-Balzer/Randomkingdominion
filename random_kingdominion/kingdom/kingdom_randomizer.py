"""File to contain the KingdomQualities and the Kingdom classes"""
from __future__ import annotations

import random

from random_kingdominion.utils.config import CustomConfigParser

from .kingdom import Kingdom
from .pool_container import PoolContainer
from .randomized_kingdom import RandomizedKingdom


class KingdomRandomizer:
    """A class that can be used to randomize a kingdom based on the current config settings."""

    def __init__(self, config: CustomConfigParser):
        self.config = config
        self.rerolled_csos: list[str] = []
        self.pool_con = PoolContainer(self.config)

    def pick_next_card(self, random_kingdom: RandomizedKingdom):
        """Picks the next card and makes sure that the Young Witch target and
        Allies are taken care of.
        """
        pick = self.pool_con.pick_next_card(random_kingdom.quality_of_selection)
        random_kingdom.add_card(pick)
        if pick == "Young Witch":
            self.pick_bane_card(random_kingdom)
        # TODO: Druid boons
        # Pick an Ally if one of the cards in the Kingdom is a liaison:
        if random_kingdom.contains_liaison() and not random_kingdom.contains_ally():
            pick = self.pool_con.pick_ally(random_kingdom.quality_of_selection)
            # An ally is not different from other landscapes, only picked under different conditions
            random_kingdom.add_landscape(pick)

    def pick_bane_card(self, random_kingdom: RandomizedKingdom):
        """Pick the bane card."""
        pick = self.pool_con.pick_next_card(random_kingdom.quality_of_selection, True)
        random_kingdom.add_card(pick)
        random_kingdom.set_bane_card(pick)

    def pick_new_landscape(self, random_kingdom: RandomizedKingdom):
        """Picks the next landscape and makes sure that WotMouse is taken care of."""
        pick = self.pool_con.pick_next_landscape(
            random_kingdom.quality_of_selection, random_kingdom.contains_way()
        )
        random_kingdom.add_landscape(pick)
        if pick == "Way of the Mouse":
            pick = self.pool_con.pick_next_card(
                random_kingdom.quality_of_selection, True
            )
            random_kingdom.set_mouse_card(pick)

    def randomize_new_kingdom(self) -> Kingdom:
        """Create a completely fresh randomized kingdom."""
        excluded_csos = self.rerolled_csos
        self.pool_con = PoolContainer(self.config, excluded_csos)
        if len(self.config.get_expansions(False)) == 0:
            return

        num_cards = self.config.getint("General", "num_cards")
        num_landscapes = self._determine_landscape_number()
        random_kingdom = RandomizedKingdom(num_landscapes=num_landscapes)

        for _ in range(num_cards):
            self.pick_next_card(random_kingdom)
        for _ in range(num_landscapes):
            current_qual = random_kingdom.quality_of_selection
            pick = self.pool_con.pick_next_landscape(
                current_qual, random_kingdom.contains_way()
            )
            random_kingdom.add_landscape(pick)
        # Pick Ally in case a Liaison is in the kingdom
        # Pick a mouse card in case Way of the Mouse is amongst the picks:
        return random_kingdom.get_kingdom()

    def _determine_landscape_number(self) -> int:
        min_num = self.config.getint("General", "min_num_landscapes")
        max_num = self.config.getint("General", "max_num_landscapes")
        return random.randint(min_num, max_num)

    def reroll_single_cso(self, old_kingdom: Kingdom, cso_name: str) -> Kingdom:
        """Take the old kingdom, reroll one cso, and return the new one with
        that card rerolled."""
        self.rerolled_csos.append(cso_name)
        random_kingdom = RandomizedKingdom.from_kingdom(old_kingdom)
        if random_kingdom.contains_card(cso_name):
            is_bane = random_kingdom.remove_card(cso_name)
            if is_bane:
                self.pick_bane_card(random_kingdom)
            else:
                self.pick_next_card(random_kingdom)
        elif random_kingdom.contains_landscape(cso_name):
            random_kingdom.remove_landscape(cso_name)
            self.pick_new_landscape(random_kingdom)
        return random_kingdom.get_kingdom()
