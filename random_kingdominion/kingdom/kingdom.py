"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from functools import reduce
from typing import Any, Literal
from uuid import uuid4

import numpy as np
import pandas as pd

from ..constants import (
    ALL_CSOS,
    ALL_INTERACTIONS,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
)
from ..utils.utils import copy_to_clipboard
from .kingdom_helper_funcs import (
    _dict_factory_func,
    _get_total_quality,
    sanitize_cso_list,
    sanitize_cso_name,
    sort_kingdom,
)


def remove_deep_nested_parentheses(s: str) -> str:
    """Remove all parentheses and stuff in them that are nested deeper than one layer,
    e.g. "Nearby(Druid(_boons_))" -> "Nearby(Druid)".
    """
    stack = []
    result = []

    for char in s:
        if char == "(":
            stack.append(char)
            if len(stack) == 1:
                result.append(char)
        elif char == ")":
            if len(stack) == 1:
                result.append(char)
            if stack:
                stack.pop()
        else:
            if not stack or len(stack) == 1:
                result.append(char)

    return "".join(result)


def get_cso_name(cso_key: str) -> str:
    return ALL_CSOS["Name"].to_dict().get(cso_key, "NOT FOUND")


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
            Which card costing $2 or $3 is the bane, should already be listed in the cards list (optional)
        ferryman_pile : str, by default ""
            Which card costing $3 or $4 is chosen by Ferryman
            (optional)
        riverboat_card : str, by default ""
            Which Non-Duration Action is chosen to be the Riverboat card
            (optional)
        mouse_card : str, by default ""
            Which card is the Way of the Mouse target,
            should not be contained in the cards list (optional)
        army_pile : str, by default ""
            Which card is the target for the Approaching Army pile (optional)
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
    riverboat_card: str = ""
    mouse_card: str = ""
    army_pile: str = ""
    druid_boons: list[str] = field(default_factory=list)
    traits: list[list[str]] = field(default_factory=list)

    name: str = ""
    notes: str = field(default="", compare=False)
    idx: int = field(default_factory=lambda: int(uuid4()), compare=False)

    # TODO: Find a more lightweight way to do this as it causes load times > 1 sec for > 100 kingdoms
    full_kingdom_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    """All components of the kingdom except for boons, loot etc., but including colonies, shelters, and ruins plus the special cards."""
    kingdom_card_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    kingdom_landscape_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    total_qualities: dict[str, int] = field(default_factory=dict, compare=False)

    __yaml_ignore__ = {
        "full_kingdom_df",
        "kingdom_card_df",
        "kingdom_landscape_df",
        "extras",
        "total_qualities",
    }

    @classmethod
    def from_dombot_csv_string(
        cls,
        csv_string: str,
        name: str = "",
        add_unrecognized_notes=True,
        add_invalidity_notes=True,
    ) -> Kingdom:
        """Try to initialize the kingdom from a given comma-separated value string similar to
        the one that DomBot produces using the !kingdom -r -l command.
        Does not support deep nesting (e.g. Nearby(Druid(_boons_)) would be ignored).
        """
        note_str = ""
        # remove the -m parameter sometimes present in TGG kingdoms
        csv_string = csv_string.replace("-m ", ", ").replace(". ", ", ")
        # Remove all parentheses and stuff in them that are nested deeper than one layer
        new_string = remove_deep_nested_parentheses(csv_string)
        if new_string != csv_string:
            note_str += "Removed nested parentheses, they currently aren't supported.\n"
        for col_str in ["colony", "colony/platinum", "platinum"]:
            new_string = (
                new_string.lower()
                .replace(col_str, "colonies")
                .replace("landscapes: ", ", ")
            )
        # Search for all single entries (we can't just split by "," because of druid boons)
        pattern = r"\s*,\s*(?![^()]*\))"
        full_list = re.split(pattern, new_string)
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
        special_ones = [entry for entry in full_list if "(" in entry]
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
        bane_pile = (
            sanitize_cso_name(special_dict["young_witch"])
            if "young_witch" in special_dict
            else sanitize_cso_name(special_dict["bane"])
        )
        if bane_pile != "":
            cso_list += [bane_pile]
        obelisk_pile = sanitize_cso_name(special_dict["obelisk"])
        ferryman_pile = sanitize_cso_name(special_dict["ferryman"])
        riverboat_card = sanitize_cso_name(special_dict["riverboat"])
        army_pile = sanitize_cso_name(special_dict["approaching_army"])
        if army_pile != "":
            cso_list += [army_pile]
        mouse_card = sanitize_cso_name(special_dict["way_of_the_mouse"])

        # Replace the split pile thingies:
        avail_csos = [cso for cso in cso_list if cso in ALL_CSOS.index]
        avail_csos += [
            sanitize_cso_name(cso["ParentPile"])  # type: ignore
            for cso_key in avail_csos
            if (cso := ALL_CSOS.loc[cso_key])["IsPartOfSplitPile"]
        ]
        unrecognized_csos = [cso for cso in cso_list if cso not in ALL_CSOS.index]
        avail_csos = np.unique(avail_csos)
        csos = ALL_CSOS.loc[avail_csos]
        # if len(unrecognized_csos) > 0:
        #     print(f"Could not recognize the following terms: {unrecognized_csos}")
        cards = csos[csos["IsInSupply"]]
        landscapes = csos[csos["IsExtendedLandscape"]]
        traits = []
        for trait, _ in landscapes[landscapes["IsTrait"]].iterrows():
            target: str = sanitize_cso_name(special_dict[trait])  # type: ignore
            if target not in ALL_CSOS[ALL_CSOS["IsInSupply"]].index:
                unrecognized_csos.append(target)
            else:
                traits.append([trait, target])
        if len(traits) > 0:
            cards = pd.concat(
                [cards, ALL_CSOS.loc[[t[1] for t in traits if t[1] not in cards.index]]]
            )
        if "" in unrecognized_csos:
            unrecognized_csos.remove("")
        if "bane" in unrecognized_csos:
            unrecognized_csos.remove("bane")
        if add_unrecognized_notes and len(unrecognized_csos) > 0:
            note_str += f"Unrecognized: {unrecognized_csos}\n"
        if add_unrecognized_notes and len(duplicates) > 0:
            dup_counts = {entry: duplicates.count(entry) for entry in duplicates}
            note_str += f"Duplicates: {dup_counts}\n"
        k = Kingdom(
            cards.index.to_list(),
            landscapes=landscapes.index.to_list(),
            use_colonies=use_colonies,
            use_shelters=use_shelters,
            bane_pile=bane_pile,
            obelisk_pile=obelisk_pile,
            ferryman_pile=ferryman_pile,
            riverboat_card=riverboat_card,
            mouse_card=mouse_card,
            druid_boons=druid_boons,
            army_pile=army_pile,
            traits=traits,
            notes=note_str,
            name=name,
        )
        if (
            add_invalidity_notes
            and len(invalid_reasons := k.get_reasons_for_invalidity()) > 0
        ):
            k.notes += f"This is only a partial kingdom, reason(s): {invalid_reasons}"
        return k

    @classmethod
    def from_dict(cls, kingdom_dict: dict[str, Any]) -> Kingdom:
        """Construct a kingdom from a dictionary."""
        sanitized_dict = {
            k: v for k, v in kingdom_dict.items() if k in cls.__dataclass_fields__
        }
        return Kingdom(**sanitized_dict)

    def __post_init__(self):
        self.cards = sanitize_cso_list(self.cards)
        self.landscapes = sanitize_cso_list(self.landscapes)
        self.mouse_card = sanitize_cso_name(self.mouse_card)
        self.bane_pile = sanitize_cso_name(self.bane_pile)
        self.druid_boons = sanitize_cso_list(self.druid_boons)
        self.army_pile = sanitize_cso_name(self.army_pile)
        self.obelisk_pile = sanitize_cso_name(self.obelisk_pile)
        self.ferryman_pile = sanitize_cso_name(self.ferryman_pile)
        self.riverboat_card = sanitize_cso_name(self.riverboat_card)
        self.traits = (
            []
            if isinstance(self.traits, float)
            else sorted(
                [sanitize_cso_list(trait_tup, sort=False) for trait_tup in self.traits]
            )
        )
        # The following three are non-supply
        if self.ferryman_pile in self.cards:
            self.cards.remove(self.ferryman_pile)
        if self.riverboat_card in self.cards:
            self.cards.remove(self.riverboat_card)
        if self.mouse_card in self.cards:
            self.cards.remove(self.mouse_card)
        assert all([trait_tup[0] in self.landscapes for trait_tup in self.traits])
        key_list = self.cards + self.landscapes
        if self.ferryman_pile != "":
            key_list.append(self.ferryman_pile)
        if self.riverboat_card != "":
            key_list.append(self.riverboat_card)
        if self.mouse_card != "":
            key_list.append(self.mouse_card)
        if self.use_colonies:
            key_list.append("colony")
            key_list.append("platinum")
        if self.use_shelters:
            key_list += ["necropolis", "hovel", "overgrown_estate"]
        if ["marauder", "death_cart", "cultist"] in self.cards:
            key_list += ["ruins"]
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
            str(exp)
            for exp in np.unique(unique_expansions.tolist() + exps_to_add)
            if exp not in exps_to_remove
        ]

    def __len__(self) -> int:
        return len(self.cards) + len(self.landscapes)

    @property
    def is_empty(self) -> bool:
        """Check whether this kingdom is empty."""
        return len(self.expansions) == 0

    @property
    def trait_dict(self) -> dict[str, str]:
        """Mapping of traits to their targets"""
        return {t[0]: t[1] for t in self.traits}

    @property
    def card_and_landscape_text(self) -> str:
        """A description of all cards and landscapes in this kingdom."""
        card_names = [self.get_cso_name_with_extra(c) for c in self.cards]
        landscape_names = [self.get_cso_name_with_extra(c) for c in self.landscapes]
        card_text = "Cards:\n\t" + "\n\t".join(card_names)
        if len(self.landscapes) > 0:
            card_text += "\nLandscapes:\n\t" + "\n\t".join(landscape_names)
        if self.use_shelters:
            card_text += "\nUse Shelters"
        if self.use_colonies:
            card_text += "\nUse Colonies/Platinum"
        return card_text.replace("\t", "  ")

    @property
    def is_valid(self) -> bool:
        """Check whether this kingdom is valid."""
        return len(self.get_reasons_for_invalidity()) == 0

    def _get_reasons_young_witch(self) -> list[str]:
        reasons = []
        bane = self.bane_pile
        if bane != "" and "young_witch" not in self.cards:
            reasons.append("no_young_witch_but_bane")
        if bane == "" and "young_witch" in self.cards:
            reasons.append("young_witch_but_no_bane")
        if bane != "" and bane not in self.cards:
            reasons.append(f"bane_{bane}_not_in_cards")
        return reasons

    def _get_reasons_army(self) -> list[str]:
        reasons = []
        army = self.army_pile
        if army != "" and "approaching_army" not in self.landscapes:
            reasons.append("no_approaching_army_but_army_pile")
        if army == "" and "approaching_army" in self.landscapes:
            reasons.append("approaching_army_but_no_army")
        if army != "" and army not in self.cards:
            reasons.append(f"army_{army}_not_in_cards")
        return reasons

    def _get_reasons_ally_prophecy(self) -> list[str]:
        reasons = []
        contains_liaison = self.check_cards_for_type("IsLiaison")
        contains_omen = self.check_cards_for_type("IsOmen")
        if contains_liaison and not self.contains_ally():
            reasons.append("no_ally")
        if contains_omen and not self.contains_prophecy():
            reasons.append("no_prophecy")
        if self.contains_ally() and not contains_liaison:
            reasons.append("no_liaison")
        if self.contains_prophecy() and not contains_omen:
            reasons.append("no_omen")
        return reasons

    def _get_reasons_traits(self) -> list[str]:
        reasons = []
        trait_dict = self.trait_dict
        ls = self.kingdom_landscape_df
        traits = ls[ls["IsTrait"]].index.tolist()
        for trait in traits:
            if trait not in trait_dict:
                reasons.append(f"no_trait_{trait}_target")
            if (target := trait_dict.get(trait, "")) not in self.cards:
                reasons.append(f"trait_{trait}_target_{target}_not_in_cards")
        for trait in trait_dict:
            if trait not in traits:
                reasons.append(f"trait_{trait}_not_in_landscapes")
        return reasons

    def _get_reasons_extras(self) -> list[str]:
        reasons = []
        if self.ferryman_pile != "" and "ferryman" not in self.cards:
            reasons.append("no_ferryman_but_target")
        if "ferrymen" in self.cards and self.ferryman_pile == "":
            reasons.append("no_ferryman_target")
        if self.riverboat_card != "" and "riverboat" not in self.cards:
            reasons.append("no_riverboat_but_target")
        if "riverboat" in self.cards and self.riverboat_card == "":
            reasons.append("no_riverboat_target")
        if self.mouse_card != "" and "way_of_the_mouse" not in self.landscapes:
            reasons.append("no_mouse_but_target")
        if "way_of_the_mouse" in self.landscapes and self.mouse_card == "":
            reasons.append("no_mouse_target")
        if self.obelisk_pile != "" and "obelisk" not in self.landscapes:
            reasons.append("obelisk_but_no_ob")
        if "obelisk" in self.landscapes and self.obelisk_pile == "":
            reasons.append("no_obelisk_target")
        if "druid" in self.cards and len(self.druid_boons) != 3:
            reasons.append("no_druid_boons")
        if "druid" not in self.cards and len(self.druid_boons) > 0:
            reasons.append("no_druid_but_boons")
        return reasons

    def get_reasons_for_invalidity(self) -> list[str]:
        """Check whether this kingdom represents a valid kingdom."""
        cards = self.cards
        reasons = []
        expected_card_num = 10
        if self.bane_pile != "":
            expected_card_num += 1
        if self.army_pile != "":
            expected_card_num += 1
        if len(cards) != expected_card_num:
            reasons.append(f"wrong_card_num_of_{len(cards)}")
        if len(self.landscapes) > 4:
            reasons.append("too_many_landscapes")
        reason_funcs = [
            self._get_reasons_ally_prophecy,
            self._get_reasons_traits,
            self._get_reasons_extras,
            self._get_reasons_young_witch,
            self._get_reasons_army,
        ]
        return reasons + [reason for func in reason_funcs for reason in func()]

    def get_cso_name_with_extra(self, cso_key: str) -> str:
        """Get the name of the card or landscape with the extra information."""
        return get_cso_name(cso_key) + self._get_cso_extras(cso_key)

    def _get_cso_extras(self, cso_key: str) -> str:
        """Provides the cso text for the given card key and adds special information
        provided by the kingdom (like bane, mouse, etc...)."""
        text = ""
        if cso_key == "ferryman":
            text += f" (Extra: {get_cso_name(self.ferryman_pile)})"
        elif cso_key == "young_witch":
            text += f" (Bane: {get_cso_name(self.bane_pile)})"
        elif cso_key == "approaching_army":
            text += f" (Attack: {get_cso_name(self.army_pile)})"
        elif cso_key == "riverboat":
            text += f" (As: {get_cso_name(self.riverboat_card)})"
        elif cso_key == "way_of_the_mouse":
            text += f"/{get_cso_name(self.mouse_card)}"
        elif cso_key == "obelisk":
            text += f" (On: {get_cso_name(self.obelisk_pile)})"
        elif cso_key == "druid":
            text += (
                f" (With: {', '.join(get_cso_name(boon) for boon in self.druid_boons)})"
            )
        if cso_key in [t[0] for t in self.traits]:
            target = [t[1] for t in self.traits if t[0] == cso_key][0]
            text += f" (On: {get_cso_name(target)})"
        # Do the same thing the other way round:
        if cso_key == self.bane_pile:
            text += f" >>>Bane<<<"
        if cso_key == self.army_pile:
            text += f" >>>For Approaching Army<<<"
        if cso_key == self.obelisk_pile:
            text += f" >>>Obelisk<<<"
        if cso_key in [t[1] for t in self.traits]:
            trait = [t[0] for t in self.traits if t[1] == cso_key][0]
            text += f" >>>{get_cso_name(trait)}<<<"
        return text

    def get_dombot_csv_string(self) -> str:
        """Construct a comma-separated string that can be fed to DomBot to generate
        the kingdom.
        """
        # Remove the / for split piles:
        cards = [card.split("/")[0] for card in self.cards]
        special_dict = {}
        if self.bane_pile:
            special_dict["young_witch"] = get_cso_name(self.bane_pile)
        if self.army_pile:
            special_dict["approaching_army"] = get_cso_name(self.army_pile)
        if self.druid_boons:
            boon_str = ", ".join([ALL_CSOS.loc[boon].Name for boon in self.druid_boons])
            special_dict["druid"] = boon_str
        if self.obelisk_pile:
            special_dict["obelisk"] = get_cso_name(self.obelisk_pile)
        if self.ferryman_pile:
            special_dict["ferryman"] = get_cso_name(self.ferryman_pile)
        if self.riverboat_card:
            special_dict["riverboat"] = get_cso_name(self.riverboat_card)
        if self.mouse_card:
            special_dict["way_of_the_mouse"] = get_cso_name(self.mouse_card)
        for trait, target in self.traits:
            special_dict[trait] = get_cso_name(target)
        special_dict = defaultdict(
            lambda: "", {key: f" ({val})" for key, val in special_dict.items()}
        )
        proper_strings = [
            get_cso_name(cso) + special_dict[cso] for cso in cards + self.landscapes
        ]
        proper_strings.append("Shelters" if self.use_shelters else "No Shelters")
        proper_strings.append("Colonies" if self.use_colonies else "No Colonies")
        sep_string = ", ".join(sorted(proper_strings))
        return sep_string

    def check_cards_for_type(self, key: Literal["IsLiaison", "IsOmen"]) -> bool:
        """Check whether this kingdom contains a card of the given type."""
        # Deliberately check full kingdom df as omen or liaison might be hidden in ferryman/riverboat/mouse stuff
        return np.sum(self.full_kingdom_df[key]) > 0

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

    def get_unique_qualtypes(self, qual: str) -> dict[str, int]:
        """For the given quality name, return all of the unique types
        that are part of the kingdom (e.g. all gain types, which might be a list
        of [Buys, Workshop] etc.)
        """
        qual += "_types"
        if not qual in self.full_kingdom_df.columns:
            return {}
        df = self.full_kingdom_df
        avail_types = reduce(lambda x, y: x + y, df[qual])
        if len(avail_types) == 0:
            return {}
        unique_types, counts = np.unique(avail_types, return_counts=True)
        return {t: c for t, c in zip(unique_types, counts)}

    def get_qualtype_string(self, qual: str) -> str:
        text = f"{qual.capitalize() + ':':10s}"
        if len((types := self.get_unique_qualtypes(qual))) > 0:
            types = [
                k if types[k] == 1 else f"{k} [x{types[k]}]"
                for k in sorted(types.keys())
            ]
            text += ", ".join(sorted(types))
        else:
            text += "-"
        return text

    def get_component_string(self) -> str:
        """Retrieve the string describing the extra components and csos needed for this kingdom."""
        comp = self.full_kingdom_df["Extra Components"].tolist()
        excluded = ["Trash mat", "-"]
        unzipped = [cso for cso_list in comp for cso in cso_list if cso not in excluded]
        uni_comp = list(np.unique(unzipped))
        if self.use_shelters:
            uni_comp.append("Shelters")
        if self.use_colonies:
            uni_comp.append("Colonies/Platinum")
        text = "EXTRAS:   "
        return text + (", ".join(uni_comp) if len(uni_comp) > 0 else "None needed")

    def get_special_card_text(self, card_name: str):
        """Get text for cards that are somewhat special."""
        text_list = []
        if card_name == self.bane_pile:
            text_list.append("Bane")
        if card_name == self.army_pile:
            text_list.append("Army attack")
        if card_name == self.obelisk_pile:
            text_list.append("Obelisk")
        if card_name == self.ferryman_pile:
            text_list.append("Ferryman")
        if card_name == self.riverboat_card:
            text_list.append("Riverboat")
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

    def get_interactions(self) -> pd.DataFrame:
        """Get all interactions between the cards in this kingdom."""
        combinations = []
        keys = self.full_kingdom_df.index.tolist()
        for key1 in keys:
            for key2 in keys:
                if key1 >= key2:
                    continue
                combinations.append(f"{key1}___{key2}")
        combinations = [c for c in combinations if c in ALL_INTERACTIONS.index]
        interactions = ALL_INTERACTIONS.loc[combinations]
        return interactions
