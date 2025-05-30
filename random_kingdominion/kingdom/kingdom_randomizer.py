"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

import random

from ..constants import ALL_CSOS
from ..logger import LOGGER
from ..single_cso_utils import (is_card, is_cso_in_expansions,
                                is_extended_landscape)
from ..utils.config import CustomConfigParser
from .kingdom import Kingdom
from .kingdom_helper_funcs import sanitize_cso_list
from .pool_container import PoolContainer
from .randomized_kingdom import RandomizedKingdom


class KingdomRandomizer:
    """A class that can be used to randomize a kingdom based on the current config settings,
    keeping track of the rerolled cards."""

    def __init__(self, config: CustomConfigParser | None = None):
        self.config = (
            config if config is not None else CustomConfigParser(load_default=True)
        )
        self.rerolled_csos: list[str] = []
        self.pool_con = PoolContainer(self.config)

    def pick_next_card(
        self,
        random_kingdom: RandomizedKingdom,
        pick: str | None = None,
        add_to_cards=True,
    ) -> bool:
        """Picks the next card and makes sure that the Young Witch target and
        Allies are taken care of.

        If not specified, the card is picked randomly from the current pool.
        If add_to_cards is False, the card is not added to the kingdom cards (relevant for Ferryman and Riverboat)
        """
        was_added = False
        if pick is None:
            pick = self.pool_con.pick_next_card(random_kingdom.quality_of_selection)
        if add_to_cards:
            was_added = random_kingdom.add_card(pick)
        if pick == "young_witch":
            self.pick_bane_pile(random_kingdom)
        elif pick == "ferryman":
            self.pick_ferryman_pile(random_kingdom)
        elif pick == "riverboat":
            self.pick_riverboat_card(random_kingdom)
        elif pick == "druid":
            self.pick_druid_boons(random_kingdom)
        # Pick an Ally if one of the cards in the Kingdom is a liaison:
        if random_kingdom.contains_liaison() and not random_kingdom.contains_ally():
            pick = self.pool_con.pick_ally(random_kingdom.quality_of_selection)
            # An ally is not different from other landscapes, only picked under different conditions,
            # Except that it doesn't count towards the landscape number.
            random_kingdom.add_landscape(pick)
        if random_kingdom.contains_omen() and not random_kingdom.contains_prophecy():
            pick = self.pool_con.pick_prophecy(random_kingdom.quality_of_selection)
            if pick == "approaching_army":
                self.pick_army_pile(random_kingdom)
            # A prophecy is not different from other landscapes, only picked under different conditions,
            # Except that it doesn't count towards the landscape number.
            random_kingdom.add_landscape(pick)
        return was_added

    def pick_bane_pile(self, random_kingdom: RandomizedKingdom, repick=True):
        """Pick the bane card."""
        if random_kingdom.bane_pile != "" and not repick:
            return
        bane = self.pool_con.pick_next_card(
            random_kingdom.quality_of_selection, "young_witch"
        )
        self.pick_next_card(random_kingdom, bane)
        random_kingdom.set_bane_pile(bane)

    def pick_army_pile(self, random_kingdom: RandomizedKingdom, repick=True):
        """Pick the army pile."""
        if random_kingdom.army_pile != "" and not repick:
            return
        army = self.pool_con.pick_next_card(
            random_kingdom.quality_of_selection, "approaching_army"
        )
        self.pick_next_card(random_kingdom, army)
        random_kingdom.set_army_pile(army)

    def pick_ferryman_pile(self, random_kingdom: RandomizedKingdom, repick=True):
        """Pick the ferryman pile."""
        if random_kingdom.ferryman_pile != "" and not repick:
            return
        ferryman = self.pool_con.pick_next_card(
            random_kingdom.quality_of_selection, "ferryman"
        )
        self.pick_next_card(random_kingdom, ferryman, add_to_cards=False)
        random_kingdom.set_ferryman_pile(ferryman)

    def pick_riverboat_card(self, random_kingdom: RandomizedKingdom, repick=True):
        """Pick the card associated with riverboat."""
        if random_kingdom.riverboat_card != "" and not repick:
            return
        riverboat = self.pool_con.pick_next_card(
            random_kingdom.quality_of_selection, "riverboat"
        )
        self.pick_next_card(random_kingdom, riverboat, add_to_cards=False)
        random_kingdom.set_riverboat_card(riverboat)

    def pick_druid_boons(self, random_kingdom: RandomizedKingdom, repick=True):
        """Pick the card associated with riverboat."""
        if random_kingdom.druid_boons != [] and not repick:
            return
        boons = ALL_CSOS[ALL_CSOS["IsBoon"]].index.to_list()
        selected_boons = random.sample(boons, 3)
        random_kingdom.set_druid_boons(selected_boons)

    def pick_mouse_card(self, random_kingdom: RandomizedKingdom, repick=True):
        """Pick the card for Way of the Mouse."""
        if random_kingdom.mouse_card != "" and not repick:
            return
        mouse = self.pool_con.pick_next_card(
            random_kingdom.quality_of_selection, "way_of_the_mouse"
        )
        self.pick_next_card(random_kingdom, mouse, add_to_cards=False)
        random_kingdom.set_mouse_card(mouse)

    def pick_next_landscape(
        self, random_kingdom: RandomizedKingdom, pick: str | None = None
    ) -> bool:
        """Picks the next landscape and makes sure that WotMouse is taken care of."""
        was_added = False
        if pick is None:
            pick = self.pool_con.pick_next_landscape(
                random_kingdom.quality_of_selection, random_kingdom.contains_way()
            )
        was_added = random_kingdom.add_landscape(pick)
        if pick == "way_of_the_mouse":
            self.pick_mouse_card(random_kingdom)
        elif pick == "approaching_army":
            self.pick_army_pile(random_kingdom)
        if pick == "":
            return False
        cso = ALL_CSOS.loc[pick]
        # If an ally is picked, pick a liaison if there is none in the kingdom.
        # Should only happen if the ally is directly set.
        if cso["IsAlly"]:  # type: ignore
            pick = self.pool_con.pick_liaison(random_kingdom.quality_of_selection)
            was_added = self.pick_next_card(random_kingdom, pick)
        # If a prophecy is picked, pick an omen if there is none in the kingdom.
        # Should only happen if the prophecy is directly set.
        if cso["IsProphecy"]:  # type: ignore
            pick = self.pool_con.pick_omen(random_kingdom.quality_of_selection)
            was_added = self.pick_next_card(random_kingdom, pick)
        return was_added

    def randomize_new_kingdom(self) -> Kingdom:
        """Create a completely fresh randomized kingdom."""
        self.pool_con = PoolContainer(self.config, self.rerolled_csos)

        num_cards = self.config.getint("General", "num_cards")
        num_landscapes = self._determine_landscape_number()
        if (partial_str := self.config.get("General", "partial_random_kingdom")) != "":
            try:
                _partial_kingdom = Kingdom.from_dombot_csv_string(
                    partial_str,
                    check_validity=False,
                    add_unrecognized_notes=False,
                )
            except ValueError:
                _partial_kingdom = Kingdom([], notes="Invalid partial kingdom input.")
            random_kingdom = RandomizedKingdom.from_kingdom(_partial_kingdom)
            random_kingdom.num_desired_landscapes = num_landscapes
            if random_kingdom.contains_ally() and not random_kingdom.contains_liaison():
                pick = self.pool_con.pick_liaison(random_kingdom.quality_of_selection)
                random_kingdom.add_card(pick)
            if (
                random_kingdom.contains_prophecy()
                and not random_kingdom.contains_omen()
            ):
                pick = self.pool_con.pick_omen(random_kingdom.quality_of_selection)
                random_kingdom.add_card(pick)
        else:
            random_kingdom = RandomizedKingdom(num_desired_landscapes=num_landscapes)
        random_kingdom = self.add_required_csos(random_kingdom)
        if len(self.config.get_expansions(False)) == 0:
            return random_kingdom.get_kingdom()
        num_cards -= random_kingdom.num_selected_cards
        bane_incl = random_kingdom.contains_card(
            "young_witch"
        ) and random_kingdom.contains_card(random_kingdom.bane_pile)
        if bane_incl:
            num_cards += 1
        num_landscapes -= random_kingdom.num_selected_landscapes
        army_incl = random_kingdom.contains_landscape(
            "approaching_army"
        ) and random_kingdom.contains_card(random_kingdom.army_pile)
        if army_incl:
            num_cards += 1

        for _ in range(max(num_cards, 0)):
            self.pick_next_card(random_kingdom)
        for _ in range(max(num_landscapes, 0)):
            current_qual = random_kingdom.quality_of_selection
            pick = self.pool_con.pick_next_landscape(
                current_qual, random_kingdom.contains_way()
            )
            random_kingdom.add_landscape(pick)
        # try to pick targets if they haven't been set
        for special, func in {
            "young_witch": self.pick_bane_pile,
            "ferryman": self.pick_ferryman_pile,
            "riverboat": self.pick_riverboat_card,
            "druid": self.pick_druid_boons,
            "approaching_army": self.pick_army_pile,
            "way_of_the_mouse": self.pick_mouse_card,
        }.items():
            if random_kingdom.contains_card(
                special
            ) or random_kingdom.contains_landscape(special):
                func(random_kingdom, repick=False)
        random_kingdom.finish_randomization(self.config)
        return random_kingdom.get_kingdom()

    def add_required_csos(self, random_kingdom: RandomizedKingdom) -> RandomizedKingdom:
        """Adds the required csos to the random kingdom"""
        required_csos = self.config.getlist("General", "required_csos")
        expansions = self.config.get_expansions()
        allow_required_csos_of_other_exps = self.config.getboolean(
            "General", "allow_required_csos_of_other_exps"
        )
        added_cards, added_landscapes = 0, 0
        for cso in sanitize_cso_list(required_csos):
            if not allow_required_csos_of_other_exps and not is_cso_in_expansions(
                cso, expansions
            ):
                continue
            if is_card(cso):
                if self.pick_next_card(random_kingdom, cso):
                    added_cards += 1
            elif is_extended_landscape(cso):
                if self.pick_next_landscape(random_kingdom, cso):
                    added_landscapes += 1
            else:
                LOGGER.warning(f"Couldn't find {cso} in cards or landscapes")
        return random_kingdom

    def _determine_landscape_number(self) -> int:
        min_num = self.config.getint("Landscapes", "min_num_landscapes")
        max_num = self.config.getint("Landscapes", "max_num_landscapes")
        return random.randint(min_num, max_num)

    def reroll_single_cso(self, old_kingdom: Kingdom, cso_name: str) -> Kingdom:
        """Take the old kingdom, reroll one cso, and return the new one with
        that card rerolled."""
        self.rerolled_csos.append(cso_name)
        random_kingdom = RandomizedKingdom.from_kingdom(old_kingdom)
        if random_kingdom.contains_card(cso_name):
            bane_army = random_kingdom.remove_card_and_test_bane_army(cso_name)
            if bane_army["bane"]:
                self.pick_bane_pile(random_kingdom)
            elif bane_army["army"]:
                self.pick_army_pile(random_kingdom)
            else:
                self.pick_next_card(random_kingdom)
        elif random_kingdom.contains_landscape(cso_name):
            removed_types = random_kingdom.remove_landscape_and_return_types(cso_name)
            if "Ally" in removed_types:
                pick = self.pool_con.pick_ally(random_kingdom.quality_of_selection)
                random_kingdom.add_landscape(pick)
            elif "Prophecy" in removed_types:
                pick = self.pool_con.pick_prophecy(random_kingdom.quality_of_selection)
                if pick == "approaching_army":
                    self.pick_army_pile(random_kingdom)
                random_kingdom.add_landscape(pick)
            else:
                self.pick_next_landscape(random_kingdom)
        elif random_kingdom.riverboat_card == cso_name:
            random_kingdom.remove_card_and_test_bane_army(cso_name)
            self.pick_riverboat_card(random_kingdom)
        elif random_kingdom.ferryman_pile == cso_name:
            random_kingdom.remove_card_and_test_bane_army(cso_name)
            self.pick_ferryman_pile(random_kingdom)
        elif random_kingdom.mouse_card == cso_name:
            random_kingdom.remove_card_and_test_bane_army(cso_name)
            self.pick_mouse_card(random_kingdom)
        else:
            LOGGER.error(
                f"Something went wrong on the reroll: Couldn't find {cso_name} in the old kingdom."
            )

        return random_kingdom.get_kingdom()
        return random_kingdom.get_kingdom()
