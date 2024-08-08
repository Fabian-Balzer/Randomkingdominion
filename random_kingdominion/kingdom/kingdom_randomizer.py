"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

import random

from random_kingdominion.single_cso_utils import (
    is_card,
    is_cso_in_expansions,
    is_landscape_or_ally,
)
from random_kingdominion.utils.config import CustomConfigParser

from .kingdom import Kingdom
from .pool_container import PoolContainer
from .randomized_kingdom import RandomizedKingdom


class KingdomRandomizer:
    """A class that can be used to randomize a kingdom based on the current config settings,
    keeping track of the rerolled cards."""

    def __init__(self, config: CustomConfigParser):
        self.config = config
        self.rerolled_csos: list[str] = []
        self.pool_con = PoolContainer(self.config)

    def pick_next_card(
        self, random_kingdom: RandomizedKingdom, pick: str | None = None
    ):
        """Picks the next card and makes sure that the Young Witch target and
        Allies are taken care of.
        """
        if pick is None:
            pick = self.pool_con.pick_next_card(random_kingdom.quality_of_selection)
        random_kingdom.add_card(pick)
        if pick == "young_witch":
            self.pick_bane_card(random_kingdom)
        if pick == "ferryman":
            self.pick_ferryman_card(random_kingdom)
        # TODO: Druid boons
        # Pick an Ally if one of the cards in the Kingdom is a liaison:
        if random_kingdom.contains_liaison() and not random_kingdom.contains_ally():
            pick = self.pool_con.pick_ally(random_kingdom.quality_of_selection)
            # An ally is not different from other landscapes, only picked under different conditions,
            # Except that it doesn't count towards the landscape number.
            random_kingdom.add_landscape(pick)
        if random_kingdom.contains_omen() and not random_kingdom.contains_prophecy():
            pick = self.pool_con.pick_prophecy(random_kingdom.quality_of_selection)
            # An ally is not different from other landscapes, only picked under different conditions,
            # Except that it doesn't count towards the landscape number.
            random_kingdom.add_landscape(pick)

    def pick_bane_card(self, random_kingdom: RandomizedKingdom):
        """Pick the bane card."""
        pick = self.pool_con.pick_next_card(random_kingdom.quality_of_selection, True)
        random_kingdom.add_card(pick)
        random_kingdom.set_bane_card(pick)
        print("selected bane card", pick)

    def pick_ferryman_card(self, random_kingdom: RandomizedKingdom):
        """Pick the bane card."""
        pick = self.pool_con.pick_next_card(random_kingdom.quality_of_selection, True)
        random_kingdom.set_ferryman_card(pick)

    def pick_next_landscape(
        self, random_kingdom: RandomizedKingdom, pick: str | None = None
    ):
        """Picks the next landscape and makes sure that WotMouse is taken care of."""
        if pick is None:
            pick = self.pool_con.pick_next_landscape(
                random_kingdom.quality_of_selection, random_kingdom.contains_way()
            )
        random_kingdom.add_landscape(pick)
        if pick == "way_of_the_mouse":
            pick = self.pool_con.pick_next_card(
                random_kingdom.quality_of_selection, True
            )
            random_kingdom.set_mouse_card(pick)

    def randomize_new_kingdom(self) -> Kingdom:
        """Create a completely fresh randomized kingdom."""
        self.pool_con = PoolContainer(self.config, self.rerolled_csos)
        if len(self.config.get_expansions(False)) == 0:
            return Kingdom([])

        num_cards = self.config.getint("General", "num_cards")
        num_landscapes = self._determine_landscape_number()
        random_kingdom = RandomizedKingdom(num_landscapes=num_landscapes)
        random_kingdom, used_cards, used_lscapes = self.add_required_csos(
            random_kingdom
        )
        num_cards -= used_cards
        num_landscapes -= used_lscapes

        for _ in range(max(num_cards, 0)):
            self.pick_next_card(random_kingdom)
        for _ in range(max(num_landscapes, 0)):
            current_qual = random_kingdom.quality_of_selection
            pick = self.pool_con.pick_next_landscape(
                current_qual, random_kingdom.contains_way()
            )
            random_kingdom.add_landscape(pick)
        random_kingdom.finish_randomization()
        # Pick Ally in case a Liaison is in the kingdom
        # Pick a mouse card in case Way of the Mouse is amongst the picks:
        return random_kingdom.get_kingdom()

    def add_required_csos(
        self, random_kingdom: RandomizedKingdom
    ) -> tuple[RandomizedKingdom, int, int]:
        """Adds the required csos to the random kingdom"""
        required_csos = self.config.getlist("General", "required_csos")
        expansions = self.config.get_expansions()
        allow_required_csos_of_other_exps = self.config.getboolean(
            "General", "allow_required_csos_of_other_exps"
        )
        added_cards, added_landscapes = 0, 0
        for cso in required_csos:
            if not allow_required_csos_of_other_exps and not is_cso_in_expansions(
                cso, expansions
            ):
                continue
            if is_card(cso):
                self.pick_next_card(random_kingdom, cso)
                added_cards += 1
            elif is_landscape_or_ally(cso):
                self.pick_next_landscape(random_kingdom, cso)
                added_landscapes += 1
            else:
                print(f"Couldn't find {cso} in cards or landscapes")
        return random_kingdom, added_cards, added_landscapes

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
            is_bane = random_kingdom.remove_card_and_test_if_bane(cso_name)
            if is_bane:
                self.pick_bane_card(random_kingdom)
            else:
                self.pick_next_card(random_kingdom)
        elif random_kingdom.contains_landscape(cso_name):
            if "Ally" in random_kingdom.remove_landscape_and_return_types(cso_name):
                pick = self.pool_con.pick_ally(random_kingdom.quality_of_selection)
                random_kingdom.add_landscape(pick)
            if "Prophecy" in random_kingdom.remove_landscape_and_return_types(cso_name):
                pick = self.pool_con.pick_prophecy(random_kingdom.quality_of_selection)
                random_kingdom.add_landscape(pick)
            else:
                self.pick_next_landscape(random_kingdom)
        else:
            print(
                f"Something went wrong on the reroll: Couldn't find {cso_name} in the old kingdom."
            )

        return random_kingdom.get_kingdom()
