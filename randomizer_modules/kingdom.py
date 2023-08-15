"""File to contain the KingdomQualities and the Kingdom classes"""
import random
import time
from dataclasses import asdict, dataclass, field
from functools import reduce
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
import yaml

from .config import CustomConfigParser, add_renewed_base_expansions
from .constants import (
    ALL_CARDS,
    FPATH_KINGDOMS_LAST100,
    FPATH_KINGDOMS_RECOMMENDED,
    QUALITIES_AVAILABLE,
)
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
        by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost"],
        ascending=[False, False, False, True],
    )


def _is_value_not_empty_or_true(val: any) -> bool:
    """Check whether the given value is not empty, or true if it's a boolean."""
    if isinstance(val, bool):
        return val  # If it's false, we want
    if val is None:
        return False
    if isinstance(val, (str, list)):
        return len(val) != 0
    return True


def _dict_factory_func(attrs: list[tuple[str, str]], ignore_keys: set) -> dict:
    """Custom dictionary factory function to make sure no unnecessary empty
    values are saved.
    This includes all booleans since they are false by default."""
    return {
        k: v
        for (k, v) in attrs
        if _is_value_not_empty_or_true(v) and k not in ignore_keys
    }


@dataclass
class Kingdom:
    """Kingdom model similar to Kieranmillar's sets.
    It has the following attributes:
        idx : UUID
            An identifier (random python uuid4)
        name : str, by default ""
            The kingdom name, if any
        cards : list[str]
            A list of card names
        use_colonies : bool, by default False
            A boolean to include Colony and Platinum (optional)
        use_shelters : bool, by default False
            A boolean to include Shelters (optional)
        extras : list[str], by default []
            An array of extra component names (optional)
        landscapes : list[str], by default []
            An array of landscape names (optional)
        obelisk_pile : str, by default ""
            The obelisk target, should already be listed in the cards list (optional)
        bane_pile : str, by default ""
            Which card is the bane, should already be listed in the cards list (optional)
        mouse_card : str, by default ""
            Which card is the Way of the Mouse target, should not be listed in the cards list (optional)
        druid_boons : list[str], by default []
            An array of boons, 3 max (optional)
        traits : list[tuple[str, str]], by default []
            An array containing a comma separated list with pairs of cards, a trait first then the card it applies to next, both should already be in the cards and landscapes lists (optional)
        notes : str
            Any extra notes (optional)
        expansions : list[str]
            The expansions needed to recreate this kingdom
    """

    cards: list[str]
    name: str = ""
    landscapes: list[str] = field(default_factory=lambda: [])
    expansions: list[str] = field(default_factory=lambda: [])
    use_colonies: bool = False
    use_shelters: bool = False
    extras: list[str] = field(default_factory=lambda: [])
    obelisk_pile: str = ""
    bane_pile: str = ""
    mouse_card: str = ""
    druid_boons: list[str] = field(default_factory=lambda: [])
    traits: list[list[str, str]] = field(default_factory=lambda: [])
    notes: str = ""
    idx: int = field(default_factory=lambda: int(uuid4()))

    full_kingdom_df: pd.DataFrame = None
    kingdom_card_df: pd.DataFrame = None
    kingdom_landscape_df: pd.DataFrame = None
    total_qualities: dict[str, int] = field(default_factory=lambda: {})

    __yaml_ignore__ = {
        "full_kingdom_df",
        "kingdom_card_df",
        "kingdom_landscape_df",
        "expansions",
        "extras",
        "total_qualities",
    }

    def __post_init__(self):
        key_list = self.cards + self.landscapes
        if self.mouse_card != "":
            key_list += [self.mouse_card]
        full_kingdom_df = ALL_CARDS.set_index("Name", drop=False).loc[key_list]
        self.full_kingdom_df = _sort_kingdom(full_kingdom_df)

        self.kingdom_card_df = self.full_kingdom_df[
            self.full_kingdom_df.Name.apply(lambda x: x in self.cards)
        ]
        self.kingdom_landscape_df = self.full_kingdom_df[
            self.full_kingdom_df.Name.apply(lambda x: x in self.landscapes)
        ]
        self._set_quality_values()

        # TODO: Calculate extra piles necessary for the kingdom.
        # Also don't forgot to add a df for it?
        self.expansions = list(np.unique(full_kingdom_df["Expansion"]))

    def pretty_print(self) -> str:
        """Return a string describing the most important things about this kingdom"""
        s = self.full_kingdom_df.to_string(
            columns=["Name", "Cost", "Expansion"], index=False
        )
        quality_summary = "\n".join(
            f"Total {qual.capitalize() + ' quality:':20}\t{val}"
            for qual, val in self.total_qualities.items()
        )
        s += "\n" + quality_summary + "\n"
        s += "CSV representation:\n\n" + self.get_csv_repr()
        return s

    def get_dict_repr(self) -> dict[str, any]:
        return asdict(
            self, dict_factory=lambda x: _dict_factory_func(x, self.__yaml_ignore__)
        )

    def get_csv_repr(self) -> str:
        """TODO: proper Bane/Trait/Mouse/Druid Boons representation"""
        return ", ".join(card for card in self.full_kingdom_df["Name"])

    def _set_quality_values(self):
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


class KingdomManager:
    def __init__(self):
        self.kingdoms: list[Kingdom] = []
        self.load_last_100_kingdoms()
        # self.load_recommended_kingdoms()

    def add_kingdom(self, kingdom: Kingdom):
        self.kingdoms.append(kingdom)
        self.save_last_100_kingdoms()

    def load_last_100_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_LAST100)

    def load_recommended_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_RECOMMENDED)

    def save_last_100_kingdoms(self):
        self.save_kingdoms_to_yaml(FPATH_KINGDOMS_LAST100)

    def load_kingdoms_from_yaml(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)
            if data is not None:
                self.kingdoms = [Kingdom(**kingdom_data) for kingdom_data in data]

    def save_kingdoms_to_yaml(self, file_path: str):
        data = [kingdom.get_dict_repr() for kingdom in self.kingdoms]
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml.safe_dump(data, yaml_file)


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

        extra_arg_dict = {}

        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Young Witch" in self.already_selected_df.Name:
            narrowed_pool = self._get_draw_pool_for_card(for_bane=True)
            bane_pile = self.savely_pick_from_pool(narrowed_pool).Name
            extra_arg_dict["bane_pile"] = bane_pile

        # Pick a Mouse card in case the Young Witch is amongst the picks:
        if "Way of the Mouse" in self.already_selected_df.Name:
            narrowed_pool = self._get_draw_pool_for_card(for_bane=True)
            mouse_card = self.savely_pick_from_pool(narrowed_pool).Name
            extra_arg_dict["mouse_card"] = mouse_card

        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Obelisk" in self.already_selected_df.Name:
            pool = self.already_selected_df
            pool = pool[pool.Types.apply(lambda x: "Action" in x)]
            obelisk_pile = self.savely_pick_from_pool(pool)
            extra_arg_dict["obelisk_pile"] = obelisk_pile

        # Pick an Ally if necessary:
        if self.does_selection_contain_type("Liaison"):
            narrowed_pool = self._get_draw_pool_for_ally()
            ally = self.savely_pick_from_pool(narrowed_pool)

        # Pick Trait targets if necessary:
        if self.does_selection_contain_type("Trait"):
            pool = self.already_selected_df
            extra_arg_dict["trait_list"] = []
            for _, trait in self.get_selection_of_certain_type("Trait").iterrows():
                pool = pool[
                    pool.Types.apply(lambda x: "Action" in x or "Treasure" in x)
                ]
                trait_target_name = self.savely_pick_from_pool(pool).Name
                extra_arg_dict["obelisk_pile"].append([trait.Name, trait_target_name])

        return Kingdom(
            cards=self.get_card_subset(), landscapes=self.get_landscape_subset()
        )

    def get_card_subset(self) -> list[str]:
        df = self.already_selected_df
        return df[~df["IsLandscape"]].Name.to_list()

    def get_landscape_subset(self) -> list[str]:
        df = self.already_selected_df
        return df[df["IsLandscape"]].Name.to_list()

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

    def get_selection_of_certain_type(self, card_type: str) -> pd.DataFrame:
        df = self.already_selected_df
        return df[df["Types"].apply(lambda x: card_type in x)]

    def does_selection_contain_type(self, card_type: str) -> bool:
        """Returns wether the selection already contains at least one card
        with the given type."""
        return len(self.get_selection_of_certain_type(card_type)) > 0

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
        return Kingdom(self.already_selected_df.Name)

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
