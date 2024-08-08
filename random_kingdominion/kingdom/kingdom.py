"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from functools import reduce
from typing import Any
from uuid import uuid4

import numpy as np
import pandas as pd

from random_kingdominion.constants import (
    ALL_CSOS,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
)
from random_kingdominion.utils.utils import copy_to_clipboard

from .kingdom_helper_funcs import (
    _dict_factory_func,
    _get_total_quality,
    sanitize_cso_list,
    sanitize_cso_name,
    sort_kingdom,
)


@dataclass(order=True)
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
            Which card is the Way of the Mouse target,
            should not be contained in the cards list (optional)
        druid_boons : list[str], by default []
            An array of boons, 3 max (optional)
        traits : list[tuple[str, str]], by default []
            An array containing a comma separated list with pairs of cards,
            a trait first then the card it applies to next,
            both should already be in the cards and landscapes lists (optional)
        notes : str
            Any extra notes (optional)
        expansions : list[str]
            The expansions needed to recreate this kingdom
    """

    cards: list[str]
    landscapes: list[str] = field(default_factory=list)
    expansions: list[str] = field(default_factory=list)
    use_colonies: bool = False
    use_shelters: bool = False
    extras: list[str] = field(default_factory=list)
    obelisk_pile: str = ""
    bane_pile: str = ""
    ferryman_pile: str = ""
    mouse_card: str = ""
    druid_boons: list[str] = field(default_factory=list)
    traits: list[list[str]] = field(default_factory=list)

    name: str = ""
    notes: str = ""
    idx: int = field(default_factory=lambda: int(uuid4()), compare=False)

    # TODO: Find a more lightweight way to do this as it causes load times > 1 sec for > 100 kingdoms
    full_kingdom_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    """All components of the kingdom except for boons, loot etc., but including colonies and shelters."""
    kingdom_card_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    kingdom_landscape_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    total_qualities: dict[str, int] = field(default_factory=dict, compare=False)

    __yaml_ignore__ = {
        "full_kingdom_df",
        "kingdom_card_df",
        "kingdom_landscape_df",
        "expansions",
        "extras",
        "total_qualities",
    }

    @classmethod
    def from_dombot_csv_string(cls, csv_string: str) -> Kingdom:
        """Try to initialize the kingdom from a given comma-separated value string similar to
        the one that DomBot produces using the !kingdom -r -l command.
        """
        # Search for all single entries (we can't just split by "," because of druid boons)
        pattern = r"\s*,\s*(?![^()]*\))"
        full_list = re.split(pattern, csv_string)
        full_list = [entry.replace(":", "(") for entry in full_list]
        duplicates = [entry for entry in full_list if full_list.count(entry) > 1]
        full_list = list(set(full_list))
        # Find the instance of Colonies/NoColonies:
        colony_indicator = next(
            filter(lambda entry: "colonies" in entry.lower(), full_list), "no"
        )
        use_colonies = "no" not in colony_indicator.lower()
        shelter_indicator = next(
            filter(lambda entry: "shelters" in entry.lower(), full_list), "no"
        )
        use_shelters = "no" not in shelter_indicator.lower()
        # Handle the CSOs and recognize special values:
        cso_list = [
            entry
            for entry in full_list
            if not ("colonies" in entry.lower() or "shelters" in entry.lower())
        ]
        cso_list = [sanitize_cso_name(entry.split("(")[0]) for entry in cso_list]
        special_ones = [entry for entry in full_list if "(" in entry or ":" in entry]
        special_tuples = [tupstr.split("(") for tupstr in special_ones]
        special_dict = {
            sanitize_cso_name(cso): inside.strip(") ") for cso, inside in special_tuples
        }
        special_dict = defaultdict(lambda: "", special_dict)
        druid_boons = (
            [sanitize_cso_name(boon) for boon in special_dict["druid"].split(",")]
            if "druid" in special_dict
            else []
        )
        bane_pile = sanitize_cso_name(special_dict["young_witch"])
        if bane_pile != "":
            cso_list += [bane_pile]
        obelisk_pile = sanitize_cso_name(special_dict["obelisk"])
        mouse_card = sanitize_cso_name(special_dict["way_of_the_mouse"])
        ferryman_pile = sanitize_cso_name(special_dict["ferryman"])

        split_piles = [cso for cso in ALL_CSOS.index if "/" in cso]
        # Replace the split pile representation (e.g. gladiator will be replaced by gladiator/fortune)
        cso_list = [
            next(filter(lambda entry: cso in entry.split("/"), split_piles), cso)
            for cso in cso_list
        ]
        avail_csos = [cso for cso in cso_list if cso in ALL_CSOS.index]
        unrecognized_csos = [cso for cso in cso_list if cso not in ALL_CSOS.index]
        avail_csos = np.unique(avail_csos)
        csos = ALL_CSOS.loc[avail_csos]
        # if len(unrecognized_csos) > 0:
        #     print(f"Could not recognize the following terms: {unrecognized_csos}")
        cards = csos[~csos["IsExtendedLandscape"] & csos["IsInSupply"]]
        landscapes = csos[csos["IsExtendedLandscape"]]
        traits = []
        for trait, _ in csos[csos["IsTrait"]].iterrows():
            traits.append([trait, special_dict[trait]])  # type: ignore

        note_str = ""
        if len(unrecognized_csos) > 0:
            note_str += f"Unrecognized: {unrecognized_csos}\n"
        if len(duplicates) > 0:
            dup_counts = {entry: duplicates.count(entry) for entry in duplicates}
            note_str += f"Duplicates: {dup_counts}\n"
        return Kingdom(
            cards.index.to_list(),
            landscapes=landscapes.index.to_list(),
            use_colonies=use_colonies,
            use_shelters=use_shelters,
            bane_pile=bane_pile,
            druid_boons=druid_boons,
            traits=traits,
            obelisk_pile=obelisk_pile,
            mouse_card=mouse_card,
            ferryman_pile=ferryman_pile,
            notes=note_str,
        )

    @classmethod
    def from_dict(cls, kingdom_dict: dict[str, Any]) -> Kingdom:
        """Construct a kingdom from a dictionary."""
        return Kingdom(**kingdom_dict)

    def __post_init__(self):
        self.cards = sanitize_cso_list(self.cards)
        self.landscapes = sanitize_cso_list(self.landscapes)
        self.mouse_card = sanitize_cso_name(self.mouse_card)
        self.bane_pile = sanitize_cso_name(self.bane_pile)
        self.druid_boons = sanitize_cso_list(self.druid_boons)
        self.obelisk_pile = sanitize_cso_name(self.obelisk_pile)
        self.ferryman_pile = sanitize_cso_name(self.ferryman_pile)
        self.traits = sorted(
            [sanitize_cso_list(trait_tup, sort=False) for trait_tup in self.traits]
        )
        if self.ferryman_pile in self.cards:
            self.cards.remove(self.ferryman_pile)
        if self.mouse_card in self.cards:
            self.cards.remove(self.mouse_card)
        assert all([trait_tup[0] in self.landscapes for trait_tup in self.traits])
        key_list = self.cards + self.landscapes
        if self.mouse_card != "":
            key_list.append(self.mouse_card)
        if self.ferryman_pile != "":
            key_list.append(self.ferryman_pile)
        if self.use_colonies:
            key_list.append("colony")
            key_list.append("platinum")
        if self.use_shelters:
            key_list += ["necropolis", "hovel", "overgrown_estate"]
        key_list = np.unique(key_list)
        full_kingdom_df = ALL_CSOS.loc[key_list]
        self.full_kingdom_df = sort_kingdom(full_kingdom_df)

        self.kingdom_card_df = sort_kingdom(self.full_kingdom_df.loc[self.cards])
        self.kingdom_landscape_df = sort_kingdom(
            self.full_kingdom_df.loc[self.landscapes]
        )
        self._set_quality_values()

        # TODO: Calculate extra piles necessary for the kingdom.
        # Also don't forgot to add a df for it?
        unique_expansions = np.unique(full_kingdom_df["Expansion"])
        exps_to_remove = []
        exps_to_add = []
        for exp in unique_expansions:
            if exp in RENEWED_EXPANSIONS:
                if (
                    not f"{exp}, 1E" in unique_expansions
                    and not f"{exp}, 2E" in unique_expansions
                ):
                    added_exp = (
                        f"{exp}, 2E"
                        if exp not in ["Cornucopia", "Guilds"]
                        else "Cornucopia & Guilds, 2E"
                    )
                    exps_to_add.append(added_exp)
                exps_to_remove.append(exp)
        self.expansions = [
            exp
            for exp in np.unique(unique_expansions.tolist() + exps_to_add)
            if exp not in exps_to_remove
        ]

    @property
    def is_empty(self) -> bool:
        """Check whether this kingdom is empty."""
        return len(self.expansions) == 0

    @property
    def ferryman_obj(self) -> pd.Series | None:
        """Return the ferryman card as a pandas series."""
        if self.ferryman_pile == "":
            return None
        return ALL_CSOS.loc[self.ferryman_pile]

    @property
    def bane_obj(self) -> pd.Series | None:
        """Return the ferryman card as a pandas series."""
        if self.bane_pile == "":
            return None
        return ALL_CSOS.loc[self.bane_pile]

    @property
    def mouse_obj(self) -> pd.Series | None:
        """Return the ferryman card as a pandas series."""
        if self.mouse_card == "":
            return None
        return ALL_CSOS.loc[self.mouse_card]

    def get_dombot_csv_string(self) -> str:
        """Construct a comma-separated string that can be fed to DomBot to generate
        the kingdom.
        """
        # Remove the / for split piles:
        cards = [card.split("/")[0] for card in self.cards]
        special_dict = {}
        if self.bane_pile:
            special_dict["young_witch"] = ALL_CSOS.loc[self.bane_pile].Name
            cards.remove(self.bane_pile)
        if self.druid_boons:
            boon_str = ", ".join([ALL_CSOS.loc[boon].Name for boon in self.druid_boons])
            special_dict["druid"] = boon_str
        if self.obelisk_pile:
            special_dict["obelisk"] = ALL_CSOS.loc[self.obelisk_pile].Name
        if self.ferryman_pile:
            special_dict["ferryman"] = ALL_CSOS.loc[self.ferryman_pile].Name
        if self.mouse_card:
            special_dict["way_of_the_mouse"] = ALL_CSOS.loc[self.mouse_card].Name
        for trait, target in self.traits:
            special_dict[trait] = ALL_CSOS.loc[target].Name
        special_dict = defaultdict(
            lambda: "", {key: f" ({val})" for key, val in special_dict.items()}
        )
        proper_strings = [
            ALL_CSOS.loc[cso].Name + special_dict[cso]
            for cso in cards + self.landscapes
        ]
        proper_strings.append("Shelters" if self.use_shelters else "No Shelters")
        proper_strings.append("Colonies" if self.use_colonies else "No Colonies")
        sep_string = ", ".join(sorted(proper_strings))
        return sep_string

    def contains_ally(self) -> bool:
        """Checks whether this kingdom contains an ally"""
        return np.sum(self.kingdom_landscape_df["IsAlly"]) > 0

    def contains_prophecy(self) -> bool:
        """Checks whether this kingdom contains a prophecy"""
        return np.sum(self.kingdom_landscape_df["IsProphecy"]) > 0

    def pretty_print(self) -> str:
        """Return a string describing the most important things about this kingdom"""
        text = self.full_kingdom_df.to_string(
            columns=["Name", "Cost", "Expansion"], index=False
        )
        quality_summary = "\n".join(
            f"Total {qual.capitalize() + ' quality:':20}\t{val}"
            for qual, val in self.total_qualities.items()
        )
        text += "\n" + quality_summary + "\n"
        text += "CSV representation:\n\n" + self.get_csv_repr()
        return text

    def get_dict_repr(self) -> dict[str, Any]:
        """Return the dictionary representation of the kingdom,
        using only the properties that should be exposed.
        """
        return asdict(
            self, dict_factory=lambda x: _dict_factory_func(x, self.__yaml_ignore__)
        )

    def get_csv_repr(self) -> str:
        """TODO: proper Bane/Trait/Mouse/Druid Boons representation, currently you should use the dombot str"""
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
        # TODO: Equivalent to get string for combined qualities!
        qual_name += "_quality"
        df = self.full_kingdom_df
        sub_df = df[df[qual_name] > 0].sort_values(qual_name)
        return ", ".join(
            [f"{card.Name} ({card[qual_name]})" for _, card in sub_df.iterrows()]
        )

    def get_unique_qualtypes(self, type_name: str) -> str:
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
        """Get text for cards that are somewhat special."""
        text_list = []
        if card_name == self.bane_pile:
            text_list.append("Bane")
        if card_name == self.obelisk_pile:
            text_list.append("Obelisk")
        if card_name == self.ferryman_pile:
            text_list.append("Ferryman")
        if card_name == self.mouse_card:
            text_list.append("Mouse")
        for tup in self.traits:
            if card_name == tup[1]:
                text_list.append(tup[0])
        return ",\n".join(text_list)

    def get_actual_expansions(self):
        """Returns the actual expansions used; e.g., if Base, 1E and Base, 2E are both present, they will both be
        returned, but if there is only Base and Base 1E, only Base 1E will be returned, and if there's only
        Base, just Base 2E will be returned."""

    def copy_to_clipboard(self):
        """Copies the kingdom to the clipboard."""

        copy_to_clipboard(self.get_dombot_csv_string())
