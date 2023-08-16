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
from .constants import (ALL_CARDS, FPATH_KINGDOMS_LAST100,
                        FPATH_KINGDOMS_RECOMMENDED, QUALITIES_AVAILABLE,
                        RENEWED_EXPANSIONS)
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
    df["CostSort"] = df["Cost"].str.replace("$", "Z")  # To ensure Potion and Debt Cost will be ranked first
    df["NameSort"] = df["Name"]
    df = df.sort_values(
        by=["IsInSupply", "IsLandscape", "IsOtherThing", "CostSort", "NameSort"],
        ascending=[False, False, False, True, True]
    )
    return df.drop(["NameSort", "CostSort"], axis=1)


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


def _get_draw_pool_for_landscape(initial_pool: pd.DataFrame, exclude_ways=False) -> pd.DataFrame:
    pool = initial_pool[initial_pool["IsLandscape"]]
    if exclude_ways:
        pool = pool[pool["Types"].apply(lambda x: "Way" not in x)]
    return pool
    
def _get_draw_pool_for_card(initial_pool: pd.DataFrame, for_bane_or_mouse=False) -> pd.DataFrame:
    pool = initial_pool[~initial_pool["IsLandscape"] & initial_pool["IsInSupply"]]
    if for_bane_or_mouse:
        pool = _reduce_pool_for_cost(pool, ["$2", "$3"])
    return pool

def _reduce_pool_for_cost(pool: pd.DataFrame, cost_limits: list[str]) -> pd.DataFrame:
    return pool[pool.Cost.isin(cost_limits)]


def _sample_card_from_dataframe(df: pd.DataFrame) -> str:
    if len(df) == 0:
        return ""
    return df.sample(1).iloc[0].Name
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
        full_kingdom_df = ALL_CARDS.loc[key_list]
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
        self.expansions = [exp for exp in np.unique(full_kingdom_df["Expansion"]) if exp not in RENEWED_EXPANSIONS]

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

    def get_special_card_text(self, card_name: str):
        """Generate additional attributes for this card."""
        text_list = []
        if card_name == self.bane_pile:
            text_list.append("Bane")
        if card_name == self.obelisk_pile:
            text_list.append("Obelisk")
        for tup in self.traits:
            if card_name == tup[1]:
                text_list.append(tup[0])
        return ",\n".join(text_list)


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
        yaml_stream = yaml.safe_dump(data)
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(yaml_stream)

@dataclass
class RandomizedKingdom:
    """A Kingdom that has yet to be completed for randomization"""
    num_landscapes: int
    num_cards: int = 10
    selected_cards: list[str] = field(default_factory=list)
    selected_landscapes: list[str] = field(default_factory=list)
    quality_of_selection: dict[str, int] = field(default_factory=lambda:{qual: 0 for qual in QUALITIES_AVAILABLE})
    obelisk_pile: str = ""
    bane_pile: str = ""
    mouse_card: str = ""
    druid_boons: list[str] = field(default_factory=lambda: [])
    traits: list[list[str, str]] = field(default_factory=lambda: [])
    all_cards_picked = False  # Turned to true once the cards meet the requirement
    all_landscapes_picked = False  # Turned to true once the num landscapes meet the requirement
    
    def _get_full_df(self) -> pd.DataFrame:
        combined_list = self.selected_cards + self.selected_landscapes
        if self.mouse_card:
            combined_list += [self.mouse_card]
        return ALL_CARDS.loc[combined_list].copy()

    def _get_card_df(self)-> pd.DataFrame:
        return ALL_CARDS.loc[self.selected_cards].copy()
    
    def _get_landscape_df(self)-> pd.DataFrame:
        return ALL_CARDS.loc[self.selected_landscapes].copy()
        
    def _set_quality_values(self):
        """Update the quality values for the selected dataframe by summing them up."""
        df = self._get_full_df()
        for qual in QUALITIES_AVAILABLE:
            val = _get_total_quality(qual, df)
            self.quality_of_selection[qual] = val
    
    def contains_way(self) -> bool:
        """Checks whether the current selection contains a way."""
        return np.sum(self._get_landscape_df()["Types"].apply(lambda x: "Way" in x))

    def does_selection_contain_type(self, card_type: str) -> bool:
        """Returns wether the selection already contains at least one card
        with the given type."""
        return len(self.get_selection_of_certain_type(card_type)) > 0

    def get_selection_of_certain_type(self, card_type: str) -> pd.DataFrame:
        df = self._get_full_df()
        return df[df["Types"].apply(lambda x: card_type in x)]

    def add_card(self, card_name: str):
        if card_name == "":
            return
        self.selected_cards.append(card_name)
        self.all_cards_picked = len(self.selected_cards) >= self.num_cards
        self._set_quality_values()

    def add_landscape(self, landscape_name: str):
        if landscape_name == "":
            return
        self.selected_landscapes.append(landscape_name)
        self.all_landscapes_picked = len(self.selected_landscapes) >= self.num_landscapes
        self._set_quality_values()

    def set_bane_card(self, bane_name: str):
        """Removes any existing old bane card and sets the new one"""
        if self.bane_pile != "":
            if bane_name in self.selected_cards:
                self.selected_cards.remove(bane_name)
        if bane_name == "":
            return
        if bane_name not in self.selected_cards:
            self.add_card(bane_name)
        self.bane_pile = bane_name

    def set_mouse_card(self, mouse_name: str):
        """Removes any existing old mouse card and sets the new one"""
        if mouse_name == "":
            return
        self.mouse_card = mouse_name
        self._set_quality_values()
    
    def pick_traits(self):
        """Since the cards should all be included in the kingdom already, the
        traits may be picked."""
        df = self._get_landscape_df()
        traits = df[df.Types.apply(lambda x: "Trait" in x)]
        # Make sure no card is picked by more than one Trait
        excluded = [trait_tuple[1] for trait_tuple in self.traits]
        for trait, _ in traits.iterrows():
            counterpart = self._pick_action_or_treasure(excluded)
            if counterpart:
                self.traits.append([trait, counterpart])
                excluded.append(counterpart)

    def pick_obelisk(self):
        """Since the cards should all be included in the kingdom already, the
        obelisk may be picked."""
        if "Obelisk" in self.selected_landscapes:
            self.obelisk_pile = self._pick_action()

    def _pick_action_or_treasure(self, excluded: list[str] | None = None) -> str:
        df = self._get_card_df()
        subset = df[df.Types.apply(lambda x: "Action" in x or "Treasure" in x)]
        if excluded:
            subset = subset[~np.isin(list(subset.Name), excluded)]
        return _sample_card_from_dataframe(subset)

    def _pick_action(self) -> str:
        """For the obelisk pile, an Action supply pile must be picked"""
        df = self._get_card_df()
        subset = df[df.Types.apply(lambda x: "Action" in x)]
        return _sample_card_from_dataframe(subset)

    def get_kingdom(self) -> Kingdom:
        """Construct a proper kingdom out of this one"""
        return Kingdom(cards=self.selected_cards, 
                       landscapes=self.selected_landscapes, 
                       bane_pile=self.bane_pile,
                       traits=self.traits,
                       obelisk_pile=self.obelisk_pile,
                       mouse_card=self.mouse_card)

class PoolContainer:
    """A class to set up a draw pool from which one can pick new cards.
    The pool needs to be set up freshly for each new randomization.
    On a basic level, it containts an initial pool which is a pandas
    DataFrame"""
    def __init__(self, config: CustomConfigParser, excluded_csos: list[str] | None = None):
        self.config = config
        self.eligible_expansions = self._determine_eligible_expansions()
        self.main_pool: pd.DataFrame = self.get_initial_draw_pool()
        if excluded_csos:
            self.main_pool = self.main_pool.drop(excluded_csos, errors="ignore")

    def get_initial_draw_pool(self) -> pd.DataFrame:
        """Create the initial draw pool for the kingdom.
        This is the overarching one that is used for all of the draws,
        so here we filter for requested expansions, allowed attack types,
        cards that are in the supply, and remove all cards with forbidden
        qualities.
        """
        pool = ALL_CARDS.copy()
        # Reduce the pool to the requested expansions:
        pool = filter_column(pool, "Expansion", self.eligible_expansions)

        # Reduce the pool to exclude any attacks that are not wanted
        _allowed_attack_types = self.config.getlist("Specialization", "attack_types")
        mask = get_mask_for_listlike_col_to_contain_any(
            pool.attack_types, _allowed_attack_types, empty_too=True
        )
        pool = pool[mask]

        pool = self._exclude_forbidden_qualities(pool)

        # Discard all non-supply-non-landscape-non-ally cards as we don't need them to draw from
        pool = pool[pool["IsInSupply"] | pool["IsLandscape"] | pool["IsAlly"]]
        return pool

    def _exclude_forbidden_qualities(self, pool: pd.DataFrame) -> pd.DataFrame:
        """Filter the pool to exclude any quality that is not wanted."""
        for qual in QUALITIES_AVAILABLE:
            if self.config.get_forbidden_quality(qual):
                pool = pool[pool[qual + "_quality"] == 0]
        return pool

    def _determine_eligible_expansions(self) -> list[str]:
        """From all of the expansions the user has selected, sub-select a number
        that corresponds to the one the user has chosen."""
        user_expansions = self.config.get_expansions(add_renewed_bases=False)
        max_num_expansions = self.config.getint("General", "max_num_expansions")
        if max_num_expansions == 0 or max_num_expansions >= len(user_expansions):
            return add_renewed_base_expansions(user_expansions)
        sampled_expansions = random.sample(user_expansions, k=max_num_expansions)
        return add_renewed_base_expansions(sampled_expansions)

    def _narrow_pool_for_quality(self, pool: pd.DataFrame, qualities_so_far: dict[str, int]):
        """Pick out the most urgent of the qualities and lower the pool size, as long as cards
        remain afterwards.
        Otherwise try to reduce for the next most urgent quality, and so on.
        """
        unfulfilled_qualities = self._determine_unfulfilled_qualities(qualities_so_far)
        for qual, diff in unfulfilled_qualities:
            # If the difference is big, try to sometimes also pick only cards with higher
            # values in that category
            minimum_requirement = random.randint(1, min(diff, 3))
            mask = pool[qual + "_quality"] >= minimum_requirement
            if np.sum(mask) > 0:
                return pool[mask]
        return pool

    def _determine_unfulfilled_qualities(self, qualities_so_far: dict[str, int]) -> list[tuple[str,str]]:
        """Determine which qualities are needed the most, and return a dictionary
        that maps the quality names to the amount they are needed.

        Parameters
        ----------
        qualities_so_far : dict[str, int]
            The qualities that are making up the currently randomized kingdom

        Returns
        -------
        list[str]
            A list of the qualities that still need to fulfil their requirements,
            sorted by their urgency
        """
        # Calculate the difference to the required kingdom quality
        diffs = {qual: self.config.get_requested_quality(qual) - val for qual, val in qualities_so_far.items()}
        # Exclude all values where the difference is <= 0, because in these cases we do not want to pick for them.
        # Also, exclude the 
        diffs = {qual: val for qual, val in diffs.items() if val > 0 and not self.config.get_forbidden_quality(qual)}
        sorted_quals = sorted(diffs, key=lambda x: diffs[x], reverse=True)
        return [(qual, diffs[qual]) for qual in sorted_quals]

    def pick_next_card(self, qualities_so_far: dict[str, int], for_bane_or_mouse=False) -> str:
        pool = _get_draw_pool_for_card(self.main_pool, for_bane_or_mouse)
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = _sample_card_from_dataframe(pool)
        self.main_pool = self.main_pool.drop(pick)
        return pick
    
    def pick_next_landscape(self, qualities_so_far: dict[str, int], exclude_ways: bool) -> str:
        pool = _get_draw_pool_for_landscape(self.main_pool, exclude_ways)
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = _sample_card_from_dataframe(pool)
        self.main_pool = self.main_pool.drop(pick)
        return pick
    

class KingdomRandomizer:
    """A class that can be used to randomize a kingdom based on the current config settings."""

    def __init__(self, config: CustomConfigParser):
        self.config = config
        self.rerolled_csos: list[str] = []
        self.pc = PoolContainer(self.config)

    def randomize_new_kingdom(self) -> Kingdom:
        excluded_csos = self.rerolled_csos
        self.pc = PoolContainer(self.config, excluded_csos)
        if len(self.config.get_expansions(False)) == 0:
            return

        num_cards = self.config.getint("General", "num_cards")
        num_landscapes = self._determine_landscape_number()
        random_kingdom = RandomizedKingdom(num_landscapes=num_landscapes)

        for _ in range(num_cards):
            pick = self.pc.pick_next_card(random_kingdom.quality_of_selection)
            random_kingdom.add_card(pick)
            if random_kingdom.all_cards_picked:
                break
        for _ in range(num_landscapes):
            pick = self.pc.pick_next_landscape(random_kingdom.quality_of_selection, random_kingdom.contains_way())
            random_kingdom.add_landscape(pick)
            if random_kingdom.all_landscapes_picked:
                break
        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Young Witch" in random_kingdom.selected_cards:
            pick = self.pc.pick_next_card(random_kingdom.quality_of_selection, True)
            random_kingdom.set_bane_card(pick)
        # Pick a mouse card in case Way of the Mouse is amongst the picks:
        if "Way of the Mouse" in random_kingdom.selected_landscapes:
            pick = self.pc.pick_next_card(random_kingdom.quality_of_selection, True)
            random_kingdom.set_mouse_card(pick)
        random_kingdom.pick_traits()
        random_kingdom.pick_obelisk()
        return random_kingdom.get_kingdom()

        extra_arg_dict = {}

        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Young Witch" in self.already_selected_df.Name:
            bane_pool = self._get_draw_pool_for_card(for_bane=True)
            bane_pile = self.savely_pick_from_pool(bane_pool)
            extra_arg_dict["bane_pile"] = bane_pile

        # Pick a Mouse card in case the Young Witch is amongst the picks:
        if "Way of the Mouse" in self.already_selected_df.Name:
            mouse_pool = self._get_draw_pool_for_card(for_bane=True)
            if len(mouse_pool) > 0:
                mouse_card = mouse_pool.sample(n=1).iloc[0].Name
                extra_arg_dict["mouse_card"] = mouse_card

        # Pick a bane card in case the Young Witch is amongst the picks:
        if "Obelisk" in self.already_selected_df.Name:
            obelisk_pool = self.already_selected_df
            obelisk_pool = obelisk_pool[obelisk_pool.Types.apply(lambda x: "Action" in x)]
            if len(obelisk_pool) > 0:
                obelisk_pile = obelisk_pool.sample(n=1).iloc[0].Name
                extra_arg_dict["obelisk_pile"] = obelisk_pile

        # Pick an Ally if necessary:
        if self.does_selection_contain_type("Liaison"):
            narrowed_pool = self._get_draw_pool_for_ally()
            self.savely_pick_from_pool(narrowed_pool)

        # Pick Trait targets if necessary:
        if self.does_selection_contain_type("Trait"):
            pool = self.already_selected_df
            extra_arg_dict["traits"] = []
            for _, trait in self.get_selection_of_certain_type("Trait").iterrows():
                pool = pool[
                    pool.Types.apply(lambda x: "Action" in x or "Treasure" in x)
                ]
                trait_target_name = pool.sample(n=1).iloc[0].Name
                extra_arg_dict["traits"].append([trait.Name, trait_target_name])
                pool = pool.drop(trait_target_name)

        return Kingdom(
            cards=self.get_card_subset(), landscapes=self.get_landscape_subset(), **extra_arg_dict
        )

    def _determine_landscape_number(self) -> int:
        min_num = self.config.getint("General", "min_num_landscapes")
        max_num = self.config.getint("General", "max_num_landscapes")
        return random.randint(min_num, max_num)

    def _get_draw_pool_for_ally(self) -> pd.DataFrame:
        pool = self.initial_draw_pool
        pool = pool[pool["IsAlly"]]
        pool = self._narrow_pool_for_parameters(pool)
        return pool

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
