"""File to contain the KingdomQualities and the Kingdom classes"""
import random
import time
from functools import reduce

import numpy as np
import pandas as pd

from .config import CustomConfigParser, add_renewed_base_expansions
from .constants import ALL_CARDS, QUALITIES_AVAILABLE
from .utils import filter_column, get_mask_for_listlike_col_to_contain_any


def _calculate_total_quality(values: list[int]) -> int:
    # Initialize array with zeros representing 0, 1, 2, 3, 4
    counts = np.zeros(5)

    # If there are 5-i values of the same thing, increment the value count of the next one
    # e.g. a list of [1, 1, 1, 1, 2] should be counted as two 2s. because there are four
    # ones, three 2s will be counted as a single 3, and two 3s will yield a 4.
    for i in range(4):
        counts[i] += values.count(i)
        if i == 0:
            continue
        counts[i + 1] += counts[i] // (5 - i)

    # Look where the first nonzero value sits.
    total_quality_value = np.nonzero(counts)[0][-1]

    return total_quality_value


def _get_total_quality(qual_name: str, kingdom_df: pd.DataFrame) -> int:
    value_list = kingdom_df[qual_name + "_quality"].to_list()
    return _calculate_total_quality(value_list)


def _sort_kingdom(df: pd.DataFrame) -> pd.DataFrame:
    """Sort the kingdom such that the supply cards come first, then the landscapes,
    then it is sorted by cost, then by name.
    """
    return df.sort_values(
        by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"],
        ascending=[False, False, False, True, True],
    )


class Kingdom:
    """Represents a single static Kingdom."""

    history = []

    def __init__(self, kingdom_df: pd.DataFrame):
        self.id = time.time_ns()

        kingdom_df = _sort_kingdom(kingdom_df)

        self.full_kingdom_df = kingdom_df
        is_ally = kingdom_df.Types.apply(lambda x: "Ally" in x)
        self.kingdom_card_df = kingdom_df[~kingdom_df["IsLandscape"] & ~is_ally]
        self.landscape_df = kingdom_df[kingdom_df["IsLandscape"] & ~is_ally]
        self.ally_df = kingdom_df[is_ally]

        self.non_supply: list[str] = []
        self.total_qualities: dict[str, int] = {qual: 0 for qual in QUALITIES_AVAILABLE}
        self.set_quality_values()
        self.history.append(self)

        self.special_targets = {
            "Bane": None,
            "Obelisk": None,
            "Mouse": None,
            "Druid Boons": None,
        }

    def __str__(self):
        s = self.full_kingdom_df.to_string(
            columns=["Name", "Cost", "Expansion"], index=False
        )
        quality_summary = "\n".join(
            f"Total {qual.capitalize() + ' quality:':20}\t{val}"
            for qual, val in self.total_qualities.items()
        )
        s += "\n" + quality_summary + "\n"
        s += "CSV representation:\n\n" + self.get_csv_representation()
        return s

    def get_csv_representation(self):
        """TODO: proper Bane/Trait/Mouse/Druid Boons representation"""
        return ", ".join(card for card in self.full_kingdom_df["Name"])

    def set_quality_values(self):
        """Update the quality values for this kingdom by summing them up."""
        for qual in QUALITIES_AVAILABLE:
            val = _get_total_quality(qual, self.full_kingdom_df)
            self.total_qualities[qual] = val

    def get_card_string_for_quality(self, qual_name: str) -> str:
        """Get a string to describe which cards contribute to the given
        quality, and how much they do that.

        Parameters
        ----------
        qual_name : str
            The name of the quality.

        Returns
        -------
        str
            The description containing the cards.
        """
        qual_name += "_quality"
        df = self.full_kingdom_df
        sub_df = df[df[qual_name] > 0].sort_values(qual_name)
        return ", ".join(
            [f"{card.Name} ({card[qual_name]})" for _, card in sub_df.iterrows()]
        )

    def get_unique_types(self, type_name: str) -> str:
        """For the given quality name, return all of the unique types
        that are part of the kingdom (e.g. all gain types, which might be a list
        of [Buys, Workshop] etc.)
        """
        type_name += "_types"
        if not type_name in self.full_kingdom_df.columns:
            return ""
        df = self.full_kingdom_df
        avail_types = reduce(lambda x, y: x + y, df[type_name])
        if len(avail_types) == 0:
            return ""
        unique_types = np.unique(avail_types)
        return str(sorted(unique_types))


class KingdomRandomizer:
    """A class that can be used to randomize a kingdom based on the current config settings."""

    def __init__(self, config: CustomConfigParser):
        self.config = config
        self.rerolled_cards: list[str] = []
        # A DataFrame to contain all cards that have already been selected:
        self.already_selected_df: pd.DataFrame = ALL_CARDS[:0]
        self.initial_draw_pool = self.get_initial_draw_pool()

        self.quality_of_selection: dict[str, int] = {
            qual: 0 for qual in QUALITIES_AVAILABLE
        }

    def reset(self):
        self.rerolled_cards: list[str] = []
        self.already_selected_df = self.already_selected_df[:0]

    def get_initial_draw_pool(self) -> pd.DataFrame:
        """Create the initial draw pool for the kingdom.
        This is the overarching one that is used for all of the draws,
        so here we filter for requested expansions, allowed attack types,
        cards that are in the supply, and remove all cards with forbidden
        qualities.
        """
        pool = ALL_CARDS.copy()
        # Reduce the pool to the requested expansions:
        eligible_expansions = self._determine_eligible_expansions()
        pool = filter_column(pool, "Expansion", eligible_expansions)

        # Reduce the pool to exclude any attacks that are not wanted
        _allowed_attack_types = self.config.get_special_list("attack_types")
        mask = get_mask_for_listlike_col_to_contain_any(
            pool.attack_types, _allowed_attack_types, empty_too=True
        )
        pool = pool[mask]

        pool = self._exclude_forbidden_qualities(pool)

        # Discard all non-supply-non-landscape cards as we don't need them to draw from
        is_ally = pool.Types.apply(lambda x: "Ally" in x)
        pool = pool[pool["IsInSupply"] | pool["IsLandscape"] | is_ally]

        pool = pool.set_index("Name", drop=False)
        pool = pool.drop(self.rerolled_cards, errors="ignore")
        pool = pool.drop(self.already_selected_df.Name, errors="ignore")
        return pool

    def _determine_eligible_expansions(self) -> list[str]:
        """From all of the expansions the user has selected, sub-select a number
        that corresponds to the one the user has chosen."""
        user_expansions = self.config.get_expansions(add_renewed_bases=False)
        max_num_expansions = self.config.getint("General", "max_num_expansions")
        if max_num_expansions == 0:
            return add_renewed_base_expansions(user_expansions)
        sampled_expansions = random.sample(user_expansions, k=max_num_expansions)
        return add_renewed_base_expansions(sampled_expansions)

    def _exclude_forbidden_qualities(self, pool: pd.DataFrame) -> pd.DataFrame:
        """Filter the pool to exclude any quality that is not wanted."""
        for qual in QUALITIES_AVAILABLE:
            if self.config.get_forbidden_quality(qual):
                pool = pool[pool[qual + "_quality"] == 0]
        return pool

    def _set_quality_values(self):
        """Update the quality values for the selected dataframe by summing them up."""
        for qual in QUALITIES_AVAILABLE:
            val = _get_total_quality(qual, self.already_selected_df)
            self.quality_of_selection[qual] = val

    def randomize_new_kingdom(self) -> Kingdom:
        self.reset()
        if len(self.config.get_expansions()) == 0:
            return

        self.initial_draw_pool = self.get_initial_draw_pool()

        num_cards = self.config.getint("General", "num_cards")
        num_landscapes = self._determine_landscape_number()

        for _ in range(num_cards):
            narrowed_pool = self._get_draw_pool_for_card()
            self.savely_pick_from_pool(narrowed_pool)
        for _ in range(num_landscapes):
            narrowed_pool = self._get_draw_pool_for_landscape()
            self.savely_pick_from_pool(narrowed_pool)

        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Young Witch" in self.already_selected_df.Name:
            narrowed_pool = self._get_draw_pool_for_card(for_bane=True)
            bane = self.savely_pick_from_pool(narrowed_pool)

        # Pick a Mouse card in case the Young Witch is amongst the picks:
        if "Way of the Mouse" in self.already_selected_df.Name:
            narrowed_pool = self._get_draw_pool_for_card(for_bane=True)
            mouse_card = self.savely_pick_from_pool(narrowed_pool)

        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Obelisk" in self.already_selected_df.Name:
            pool = self.already_selected_df
            pool = pool[pool.Types.apply(lambda x: "Action" in x)]
            obelisk_card = self.savely_pick_from_pool(pool)

        # Pick an Ally if necessary:
        if self.does_selection_contain_type("Liaison"):
            narrowed_pool = self._get_draw_pool_for_ally()
            ally = self.savely_pick_from_pool(narrowed_pool)

        # Pick a Trait target if necessary:
        if self.does_selection_contain_type("Trait"):
            pool = self.already_selected_df
            pool = pool[pool.Types.apply(lambda x: "Action" in x or "Treasure" in x)]
            trait_target = self.savely_pick_from_pool(pool)

        return Kingdom(self.already_selected_df)

    def _determine_landscape_number(self) -> int:
        min_num = self.config.getint("General", "min_num_landscapes")
        max_num = self.config.getint("General", "max_num_landscapes")
        return random.randint(min_num, max_num)

    def _get_draw_pool_for_card(self, for_bane=False) -> pd.DataFrame:
        pool = self.initial_draw_pool
        pool = pool[~pool["IsLandscape"] & pool["IsInSupply"]]
        pool = self._narrow_pool_for_parameters(pool)
        if for_bane:
            pool = self._reduce_pool_for_cost(pool, ["$2", "$3"])
        return pool

    def _reduce_pool_for_cost(
        self, pool: pd.DataFrame, cost_limits: list[str]
    ) -> pd.DataFrame:
        return pool[pool.Cost.isin(cost_limits)]

    def _get_draw_pool_for_landscape(self) -> pd.DataFrame:
        pool = self.initial_draw_pool
        pool = pool[pool["IsLandscape"]]
        if self.does_selection_contain_type("Way"):
            pool = pool[pool["Types"].apply(lambda x: "Way" not in x)]
        pool = self._narrow_pool_for_parameters(pool)
        return pool

    def _get_draw_pool_for_ally(self) -> pd.DataFrame:
        pool = self.initial_draw_pool
        is_ally = pool.Types.apply(lambda x: "Ally" in x)
        pool = pool[is_ally]
        pool = self._narrow_pool_for_parameters(pool)
        return pool

    def savely_pick_from_pool(self, pool: pd.DataFrame):
        """Add the given pick to the already selected cards."""
        if len(pool) == 0:
            return
        pick = pool.sample(n=1)
        self.already_selected_df = pd.concat([self.already_selected_df, pick])
        self._set_quality_values()
        self.initial_draw_pool = self.initial_draw_pool.drop(pick.Name, errors="ignore")
        return pick

    def _narrow_pool_for_parameters(self, pool: pd.DataFrame) -> pd.DataFrame:
        # Create a dictionary for args that still require fulfilment (i. e. VQ is set to 4-2 if the kingdom already contains a VQ of 4)
        quals_to_pick_from: dict[str, int] = {}
        for qual, diff_to_desired in self.quality_of_selection.items():
            if self.config.get_forbidden_quality(qual):
                continue  # We should not try to access forbidden qualities here.
            diff_to_desired = self.config.get_requested_quality(qual) - diff_to_desired
            if diff_to_desired > 0:
                # Set the difference as the weight for this quality to be picked
                quals_to_pick_from[qual] = diff_to_desired
        # Pick a quality that should define the next pick:
        if len(quals_to_pick_from) > 0:
            # weighting the choices by urgency
            qual = random.choice(
                [k for k, weight in quals_to_pick_from.items() for _ in range(weight)]
            )
            min_qual_val = random.randint(1, min(3, quals_to_pick_from[qual]))
            defining_quality = qual + "_quality"
            before_narrowing = pool
            pool = pool[pool[defining_quality] >= min_qual_val]
            # If the constraints are too much, do not constrain it.
            if len(pool) == 0:
                pool = before_narrowing
        return pool

    def does_selection_contain_type(self, card_type: str) -> bool:
        """Returns wether the selection already contains at least one card
        with the given type."""
        df = self.already_selected_df
        return len(df[df["Types"].apply(lambda x: card_type in x)]) > 0

    def reroll_single_card(self, old_kingdom: Kingdom, card_name: str) -> Kingdom:
        """Take the old kingdom, reroll one card, and return the new one with
        that card rerolled."""
        self.already_selected_df = old_kingdom.full_kingdom_df
        self.rerolled_cards.append(card_name)
        card = self.already_selected_df.loc[card_name]

        self.already_selected_df = self.already_selected_df.drop(card_name)
        # TODO: Reroll Ally, Bane, or other reroll!
        self.initial_draw_pool = self.get_initial_draw_pool()
        if card.IsLandscape:
            narrowed_pool = self._get_draw_pool_for_landscape()
            self.savely_pick_from_pool(narrowed_pool)
        else:
            narrowed_pool = self._get_draw_pool_for_card()
            self.savely_pick_from_pool(narrowed_pool)
        return Kingdom(self.already_selected_df)

        # kept_cards = [card for card in self.kingdom.kingdom_cards if card != old_card]
        # if old_card == "Young Witch":
        #     kept_cards = [
        #         card
        #         for card in kept_cards
        #         if card != self.kingdom.special_targets["Bane"]
        #     ]
        # kept_landscapes = [card for card in self.kingdom.landscapes if card != old_card]
        # kept_ally = self.kingdom.ally if old_card != self.kingdom.ally else ""
        # if (
        #     len(
        #         self.kingdom.get_kingdom_df()[
        #             self.kingdom.get_kingdom_df()["Types"].apply(
        #                 lambda x: "Liaison" in x
        #             )
        #         ]
        #     )
        #     == 0
        # ):
        #     kept_ally = ""
        # self.kingdom = Kingdom(
        #     self.all_cards,
        #     config=self.config,
        #     kingdom_cards=kept_cards,
        #     landscapes=kept_landscapes,
        #     ally=kept_ally,
        # )
        # self.rerolled_cards.append(old_card)
        # self.kingdom.randomize(self.rerolled_cards)
