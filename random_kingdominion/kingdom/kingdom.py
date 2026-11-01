"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from functools import reduce
from json import JSONDecodeError, dumps, loads
from typing import Any, Callable, Literal
from uuid import uuid4

import numpy as np
import pandas as pd

from ..constants import (
    ALL_CSOS,
    EXPANSION_DICT,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
)
from ..logger import LOGGER
from ..utils import (
    get_cso_name,
    get_total_quality,
    sanitize_cso_list,
    sanitize_cso_name,
    sort_kingdom,
)
from .invalidity_stuff import InvalidityReason


def _is_value_not_empty_or_true(val: Any) -> bool:
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
    This includes all booleans since they are false by default.
    """
    return {
        k: v
        for (k, v) in attrs
        if _is_value_not_empty_or_true(v) and k not in ignore_keys
    }


def _group_targets(pairs: list[list[str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for name, target in pairs:
        grouped[name].append(target)
    return dict(grouped)


def _split_targets(raw_targets: str, replace_parent_pile: bool = False) -> list[str]:
    """Split a comma-separated list of targets (e.g. "silver, estate", or the
    "silver,_estate" older kingdom files contain) into sanitized CSO keys."""
    return [
        sanitize_cso_name(target.strip(" _"), replace_parent_pile)
        for target in raw_targets.split(",")
        if target.strip(" _")
    ]


def _normalize_target_pairs(
    pairs: list[list[str]] | float, remove_duplicates: bool = False
) -> list[list[str]]:
    """Sorted [trait or campaign effect, target] pairs, one per target."""
    if isinstance(pairs, float):  # A missing value in a DataFrame row
        return []
    normalized = []
    for name, raw_targets in pairs:
        for target in _split_targets(raw_targets):
            pair = [sanitize_cso_name(name), target]
            if not (remove_duplicates and pair in normalized):
                normalized.append(pair)
    return sorted(normalized)


def _normalize_divine_wind_str(divine_wind_str: str) -> str:
    """The Divine Wind CSOs as sorted keys, so that a kingdom compares equal however
    they were entered (display names or keys, any order). Special targets inside,
    e.g. a Bane, aren't supported yet (M19)."""
    if not isinstance(divine_wind_str, str) or not divine_wind_str:
        return ""  # Also a missing value (NaN) in a DataFrame row
    entries = re.split(r"\s*,\s*(?![^()]*\))", divine_wind_str)
    return ", ".join(sorted(sanitize_cso_name(e) for e in entries if e.strip()))


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
        divine_wind_cso_str : str, by default ""
            A string describing the csos that replace the original kingdom when
            Divine Wind is triggered (optional)
        traits : list[tuple[str, str]], by default []
            An array containing a comma separated list with pairs of cards,
            a trait first then the card it applies to next,
            both should already be in the cards and landscapes lists (optional)
        stamp_effects: list[tuple[str, str]], by default []
            An array containing a comma separated list with pairs of cards,
            a stamp or setup effect first, then the CSO it applies to next,
            both should already be in the cards and landscapes lists (optional)
        notes : str
            Any extra notes (optional)
        expansions : list[str]
            The expansions needed to recreate this kingdom
    """

    cards: list[str]
    landscapes: list[str] = field(default_factory=list)
    campaign_effects: list[str] = field(default_factory=list)
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
    divine_wind_cso_str: str = ""
    traits: list[list[str]] = field(default_factory=list)
    stamps_and_effects: list[list[str]] = field(default_factory=list)
    is_campaign: bool = False

    name: str = ""
    notes: str = field(default="", compare=False)
    invalidity_reasons: list[InvalidityReason] = field(
        default_factory=list, compare=False
    )
    idx: int = field(default_factory=lambda: int(uuid4()), compare=False)

    # TODO: Find a more lightweight way to do this as it causes load times > 1 sec for > 100 kingdoms
    full_kingdom_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    """All components of the kingdom except for Boons, Loot etc., but including Colonies, Shelters, and Ruins plus the special cards as well as Druid Boons."""
    kingdom_card_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    kingdom_landscape_df: pd.DataFrame = field(init=False, repr=False, compare=False)
    kingdom_campaign_effects_df: pd.DataFrame = field(
        init=False, repr=False, compare=False
    )
    total_qualities: dict[str, float] = field(default_factory=dict, compare=False)

    __yaml_ignore__ = {
        "full_kingdom_df",
        "kingdom_card_df",
        "kingdom_landscape_df",
        "kingdom_campaign_effects_df",
        "extras",
        "total_qualities",
    }

    @classmethod
    def from_dombot_csv_string(
        cls,
        csv_string: str,
        name: str = "",
        add_unrecognized_notes=True,
        check_validity=True,
    ) -> Kingdom:
        """Try to initialize the kingdom from a given comma-separated value string similar to
        the one that DomBot produces using the !kingdom -r -l command.
        Does not support deep nesting (e.g. Nearby(Druid(_boons_)) would be ignored).
        """
        note_str = ""
        # remove the -m parameter sometimes present in TGG kingdoms
        for char in ["-m ", "-x ", ". ", "; "]:
            csv_string = csv_string.replace(char, ", ")
        # Remove all parentheses and stuff in them that are nested deeper than one layer
        new_string = remove_deep_nested_parentheses(csv_string)
        if new_string != csv_string:
            note_str += "Removed nested parentheses, they currently aren't supported. You may list nested stuff separately.\n"
        new_string = (
            new_string.lower()
            .replace("landscapes: ", ", ")
            .replace("city_state", "city-state")
            .replace("will_o_wisp", "will-o-wisp")
        )
        # Search for all single entries (we can't just split by "," because of druid boons)
        pattern = r"\s*,\s*(?![^()]*\))"
        full_list = re.split(pattern, new_string)
        full_list = [entry.replace(":", "(") for entry in full_list]
        # Only standalone entries: "start_double_pile(colony)" targets the Colony pile.
        # Longest spelling first; "colony/platinum" would become "colonies/colonies"
        for i, entry in enumerate(full_list):
            if "(" not in entry:
                for col_str in ["colony/platinum", "colony", "platinum"]:
                    entry = entry.replace(col_str, "colonies")
                full_list[i] = entry
        # Marks a kingdom that may use campaign rules (see `is_campaign`)
        is_campaign = "campaign" in full_list
        full_list = [entry for entry in full_list if entry != "campaign"]
        # Specials are collected from all entries: a campaign effect may appear
        # several times (start_replace_copper(silver) twice replaces two Coppers),
        # and a Trait may have several targets in campaigns
        special_dict: defaultdict[str, list[str]] = defaultdict(list)
        for entry in full_list:
            if "(" in entry:
                cso, inside = entry.split("(", 1)
                special_dict[sanitize_cso_name(cso, True)].append(inside.strip(") "))
        effect_keys = set(ALL_CSOS.index[ALL_CSOS["IsCampaignEffect"]])
        duplicates = [
            entry
            for entry in full_list
            if full_list.count(entry) > 1
            and sanitize_cso_name(entry.split("(")[0], True) not in effect_keys
        ]
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
        cso_list = [sanitize_cso_name(entry.split("(")[0], True) for entry in cso_list]

        def single_special(key: str) -> str:
            """The target of a special that only takes one (e.g. the Bane)."""
            return special_dict[key][0] if special_dict.get(key) else ""

        druid_boons = (
            [sanitize_cso_name(boon) for boon in single_special("druid").split(",")]
            if "druid" in special_dict
            else []
        )
        divine_wind_cso_str = single_special("divine_wind")
        bane_pile = sanitize_cso_name(
            single_special("young_witch") or single_special("bane"), True
        )
        if bane_pile != "":
            cso_list += [bane_pile]
        obelisk_pile = sanitize_cso_name(single_special("obelisk"), True)
        ferryman_pile = sanitize_cso_name(single_special("ferryman"), True)
        riverboat_card = sanitize_cso_name(single_special("riverboat"), True)
        army_pile = sanitize_cso_name(single_special("approaching_army"), True)
        if army_pile != "":
            cso_list += [army_pile]
        mouse_card = sanitize_cso_name(single_special("way_of_the_mouse"), True)

        # Replace the split pile thingies:
        avail_csos = [cso for cso in cso_list if cso in ALL_CSOS.index]
        unrecognized_csos = [cso for cso in cso_list if cso not in ALL_CSOS.index]
        avail_csos = np.unique(avail_csos)
        csos = ALL_CSOS.loc[avail_csos]
        # if len(unrecognized_csos) > 0:
        #     LOGGER.info(f"Could not recognize the following terms: {unrecognized_csos}")
        cards = csos[csos["IsInSupply"]]
        landscapes = csos[csos["IsExtendedLandscape"]]
        campaign_effects = csos[csos["IsCampaignEffect"]]
        # Add Traits plus their targets (if not in there already). Outside of
        # campaigns, a Trait has exactly one supply pile as its target; several
        # targets or non-supply ones (e.g. Gold) are kept, and the validity check
        # marks them as campaign-only.
        traits = []
        for trait, _ in landscapes[landscapes["IsTrait"]].iterrows():
            for raw_target in special_dict.get(str(trait), []):
                target = sanitize_cso_name(raw_target, True)
                if target not in ALL_CSOS.index:
                    unrecognized_csos.append(target)
                elif [trait, target] not in traits:
                    traits.append([trait, target])
        supply_targets = [
            t[1] for t in traits if ALL_CSOS.loc[t[1], "IsInSupply"]
        ]
        if len(supply_targets) > 0:
            cards = pd.concat(
                [cards, ALL_CSOS.loc[[t for t in supply_targets if t not in cards.index]]]
            )
        # Add Stamps plus their targets (if not in there already), one pair per
        # target; several targets of one effect may also come comma-separated
        stamps_and_effects = []
        for campaign_effect, _ in campaign_effects.iterrows():
            # We don't want to replace a starting conjurer with Wizards
            replace_parent_pile = not str(campaign_effect).startswith("replace")
            for raw_target in special_dict.get(str(campaign_effect), []):
                for target in _split_targets(raw_target, replace_parent_pile):
                    if target not in ALL_CSOS.index:
                        unrecognized_csos.append(target)
                    else:
                        stamps_and_effects.append([campaign_effect, target])
        if len(stamps_and_effects) > 0:
            # Only the target of an effect with a single target is a pile of the
            # kingdom; e.g. Typhoon's list or the replacements of the starting
            # cards aren't
            num_targets = defaultdict(int)
            for effect, _ in stamps_and_effects:
                num_targets[effect] += 1
            new_targets = ALL_CSOS.loc[
                [
                    t[1]
                    for t in stamps_and_effects
                    if num_targets[t[0]] == 1
                    and t[1] not in cards.index
                    and t[1] not in landscapes.index
                    and t[0] not in ["replace_copper", "replace_estate", "trash_pile"]
                ]
            ]
            cards = pd.concat(
                [
                    cards,
                    new_targets.loc[new_targets["IsInSupply"]],
                ]
            )
            landscapes = pd.concat(
                [
                    landscapes,
                    new_targets.loc[new_targets["IsExtendedLandscape"]],
                ]
            )
        if "" in unrecognized_csos:
            unrecognized_csos.remove("")
        if "bane" in unrecognized_csos:
            unrecognized_csos.remove("bane")
        if add_unrecognized_notes and len(unrecognized_csos) > 0:
            un_str = ", ".join([f"'{cso}'" for cso in unrecognized_csos])
            note_str += f"The following inputs could not be associated with any known CSOs: {un_str}\n"
        if add_unrecognized_notes and len(duplicates) > 0:
            dup_counts = {entry: duplicates.count(entry) for entry in duplicates}
            note_str += f"Duplicates: {dup_counts}\n"
        k = Kingdom(
            cards.index.to_list(),
            landscapes=landscapes.index.to_list(),
            campaign_effects=campaign_effects.index.to_list(),
            use_colonies=use_colonies,
            use_shelters=use_shelters,
            bane_pile=bane_pile,
            obelisk_pile=obelisk_pile,
            ferryman_pile=ferryman_pile,
            riverboat_card=riverboat_card,
            mouse_card=mouse_card,
            druid_boons=druid_boons,
            army_pile=army_pile,
            divine_wind_cso_str=divine_wind_cso_str,
            traits=traits,
            notes=note_str,
            name=name,
            stamps_and_effects=stamps_and_effects,
            is_campaign=is_campaign,
        )
        if check_validity:
            k.invalidity_reasons = InvalidityReason.check_kingdom_validity(k)
        return k

    @classmethod
    def from_dict(cls, kingdom_dict: dict[str, Any]) -> Kingdom:
        """Construct a kingdom from a dictionary."""
        sanitized_dict = {
            k: v for k, v in kingdom_dict.items() if k in cls.__dataclass_fields__  # type: ignore
        }
        return Kingdom(**sanitized_dict)

    @property
    def get_starting_deck(self) -> list[str]:
        """Get the starting deck for this kingdom."""
        heirloom_dict = {
            "pixie": "goat",
            "cemetery": "haunted_mirror",
            "pooka": "cursed_gold",
            "fool": "lucky_coin",
            "shepherd": "pasture",
            "tracker": "pouch",
            "secret_cave": "magic_lamp",
        }
        starting_deck = ["copper"] * 7
        if self.use_shelters:
            starting_deck += ["necropolis", "hovel", "overgrown_estate"]
        else:
            starting_deck += ["estate"] * 3
        for card in self.cards:
            if card in heirloom_dict:
                starting_deck[starting_deck.index("copper")] = heirloom_dict[card]
            if "double_heirloom" in self.campaign_effects:
                starting_deck[starting_deck.index("copper")] = heirloom_dict[card]
        if "double_deck" in self.campaign_effects:
            starting_deck += starting_deck
        effect_targets = self.effect_targets
        for target in effect_targets.get("replace_estate", []):
            starting_deck[starting_deck.index("estate")] = target
        for target in effect_targets.get("replace_copper", []):
            starting_deck[starting_deck.index("copper")] = target
        starting_deck += effect_targets.get("add_card", [])
        if "add_each_pile" in self.campaign_effects:
            for card in self.cards:
                c = ALL_CSOS.loc[card]
                if "Action" in c["Types"] or "Treasure" in c["Types"]:
                    starting_deck.append(card)
        return starting_deck

    @property
    def buy_availability(self) -> Literal["no", "maybe", "yes"]:
        """Check whether the kingdom has any cards that provide +buy."""
        g_qualities = self.get_unique_qualtypes("gain")
        if "Buys" in g_qualities:
            return "yes"
        elif "Buys*" in g_qualities:
            return "maybe"
        return "no"

    @property
    def divine_wind_subkingdom(self) -> Kingdom | None:
        if len(self.divine_wind_cso_str) == 0:
            return None
        return Kingdom.from_dombot_csv_string(self.divine_wind_cso_str)

    @property
    def has_modified_starting_deck(self) -> bool:
        """Check whether the starting deck has been modified."""
        return any(
            [
                effect in self.campaign_effects
                for effect in [
                    "replace_copper",
                    "replace_estate",
                    "double_deck",
                    "add_each_pile",
                    "add_card",
                ]
            ]
        )

    def __post_init__(self):
        self.cards = sanitize_cso_list(self.cards)
        self.landscapes = sanitize_cso_list(self.landscapes)
        self.campaign_effects = sanitize_cso_list(self.campaign_effects)
        self.mouse_card = sanitize_cso_name(self.mouse_card)
        self.bane_pile = sanitize_cso_name(self.bane_pile)
        self.druid_boons = sanitize_cso_list(self.druid_boons)
        self.army_pile = sanitize_cso_name(self.army_pile)
        self.obelisk_pile = sanitize_cso_name(self.obelisk_pile)
        self.ferryman_pile = sanitize_cso_name(self.ferryman_pile)
        self.riverboat_card = sanitize_cso_name(self.riverboat_card)
        self.traits = _normalize_target_pairs(self.traits, remove_duplicates=True)
        # Duplicates count here: replace_copper on silver twice replaces two Coppers
        self.stamps_and_effects = _normalize_target_pairs(self.stamps_and_effects)
        self.divine_wind_cso_str = _normalize_divine_wind_str(self.divine_wind_cso_str)
        # The following three are non-supply
        if self.ferryman_pile in self.cards:
            self.cards.remove(self.ferryman_pile)
        if self.riverboat_card in self.cards:
            self.cards.remove(self.riverboat_card)
        if self.mouse_card in self.cards:
            self.cards.remove(self.mouse_card)
        assert all([trait_tup[0] in self.landscapes for trait_tup in self.traits])
        key_list = self.cards + self.landscapes + self.campaign_effects
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
        if any([card in self.cards for card in ["marauder", "death_cart", "cultist"]]):
            key_list += ["ruins"]
        if self.druid_boons:
            key_list += self.druid_boons
        key_list = np.unique(key_list)
        full_kingdom_df = ALL_CSOS.loc[key_list]
        self.full_kingdom_df = sort_kingdom(full_kingdom_df)

        self.kingdom_card_df = sort_kingdom(
            self.full_kingdom_df.loc[self.cards]  # type: ignore
        )
        self.kingdom_landscape_df = sort_kingdom(
            self.full_kingdom_df.loc[self.landscapes]  # type: ignore
        )
        self.kingdom_campaign_effects_df = sort_kingdom(
            self.full_kingdom_df.loc[self.campaign_effects]  # type: ignore
        )
        self._set_quality_values()

        # TODO: Calculate extra piles necessary for the kingdom.
        # Also don't forgot to add a df for it?
        unique_expansions = np.unique(
            full_kingdom_df[~full_kingdom_df["IsCampaignEffect"]]["Expansion"]
        )
        exps_to_remove = []
        exps_to_add = []
        for exp in unique_expansions:
            if exp in RENEWED_EXPANSIONS:
                if (
                    not f"{exp}, 1E" in unique_expansions
                    and not f"{exp}, 2E" in unique_expansions
                ):
                    exps_to_add.append(EXPANSION_DICT[exp])
                exps_to_remove.append(exp)
        self.expansions = [
            str(exp)
            for exp in np.unique(unique_expansions.tolist() + exps_to_add)
            if exp not in exps_to_remove
        ]
        if isinstance(self.notes, dict):
            self.notes = dumps(self.notes)

    def __len__(self) -> int:
        return len(self.cards) + len(self.landscapes)

    @property
    def is_empty(self) -> bool:
        """Check whether this kingdom is empty."""
        return len(self.expansions) == 0

    @property
    def trait_targets(self) -> dict[str, list[str]]:
        """Mapping of the Traits to their targets (several only in campaigns)."""
        return _group_targets(self.traits)

    @property
    def effect_targets(self) -> dict[str, list[str]]:
        """Mapping of the campaign effects to their targets; a target may appear
        several times (e.g. two Coppers replaced by Silvers)."""
        return _group_targets(self.stamps_and_effects)

    def get_traits_on(self, cso_key: str) -> list[str]:
        """The Traits applying to the given pile."""
        return [trait for trait, target in self.traits if target == cso_key]

    def get_effects_on(self, cso_key: str) -> list[str]:
        """The campaign effects (e.g. Stamps) applying to the given pile."""
        return sorted({eff for eff, target in self.stamps_and_effects if target == cso_key})

    @property
    def card_and_landscape_text(self) -> str:
        """A description of all cards and landscapes in this kingdom."""
        card_names = [self.get_cso_name_with_extra(c) for c in self.cards]
        landscape_names = [self.get_cso_name_with_extra(c) for c in self.landscapes]
        card_text = "Cards:\n\t" + "\n\t".join(card_names)
        if len(self.landscapes) > 0:
            card_text += "\nLandscapes:\n\t" + "\n\t".join(landscape_names)
        if len(self.campaign_effects) > 0:
            effect_names = [
                self.get_cso_name_with_extra(c) for c in self.campaign_effects
            ]
            card_text += "\nStamps and Twists:\n\t" + "\n\t".join(effect_names)
        if self.use_shelters:
            card_text += "\nUse Shelters"
        if self.use_colonies:
            card_text += "\nUse Colonies/Platinum"
        return card_text.replace("\t", "  ")

    @property
    def is_valid(self) -> bool:
        """Check whether this kingdom is valid."""
        return len(self.invalidity_reasons) == 0

    @property
    def unpacked_notes(self) -> dict[str, Any]:
        """Return the notes as a dictionary if possible."""
        if self.notes == "":
            return {}
        try:
            return loads(self.notes)
        except JSONDecodeError:
            LOGGER.warning(f"Could not decode kingdom notes: {self.notes}")
            return {"Notes": self.notes}

    def get_cso_name_with_extra(self, cso_key: str) -> str:
        """Get the name of the card or landscape with the extra information."""
        return get_cso_name(cso_key) + self._get_cso_extras(cso_key)

    def _get_cso_extras(self, cso_key: str) -> str:
        """Provides the cso text for the given card key and adds special information
        provided by the kingdom (like bane, mouse, etc...)."""
        text = ""
        if cso_key == "ferryman":
            text += f" (+{get_cso_name(self.ferryman_pile)} as Extra)"
        elif cso_key == "young_witch":
            text += f" (+{get_cso_name(self.bane_pile)} as Bane)"
        elif cso_key == "approaching_army":
            text += f" (+{get_cso_name(self.army_pile)} as Attack)"
        elif cso_key == "riverboat":
            text += f" ({get_cso_name(self.riverboat_card)} as Boat)"
        elif cso_key == "way_of_the_mouse":
            text += f" ({get_cso_name(self.mouse_card)} as Mouse)"
        elif cso_key == "obelisk":
            text += f" ({get_cso_name(self.obelisk_pile)} as Obelisk)"
        elif cso_key == "druid":
            text += (
                f" (With: {', '.join(get_cso_name(boon) for boon in self.druid_boons)})"
            )
        for targets in [
            self.trait_targets.get(cso_key, []),
            self.effect_targets.get(cso_key, []),
        ]:
            if targets:
                text += f" (On: {', '.join(get_cso_name(t) for t in targets)})"
        # Do the same thing the other way round:
        if cso_key == self.bane_pile:
            text += f" >>>Bane<<<"
        if cso_key == self.army_pile:
            text += f" >>>For Approaching Army<<<"
        if cso_key == self.obelisk_pile:
            text += f" >>>Obelisk<<<"
        for trait_or_effect in self.get_traits_on(cso_key) + self.get_effects_on(cso_key):
            text += f" >>>{get_cso_name(trait_or_effect)}<<<"
        return text

    def _get_special_dict(
        self, sani_func: Callable[[str], str], add_stamps=True
    ) -> defaultdict[str, list[str]]:
        """Get a dictionary with all of the special cards and their extra information,
        e.g. ``{"young_witch": [" (Moat)"]}``. A Trait or campaign effect with several
        targets gets one entry per target, which are printed separately."""
        special_dict: defaultdict[str, list[str]] = defaultdict(list)
        if self.bane_pile:
            special_dict["young_witch"].append(sani_func(self.bane_pile))
        if self.army_pile:
            special_dict["approaching_army"].append(sani_func(self.army_pile))
        if self.druid_boons:
            boon_str = ", ".join([sani_func(boon) for boon in self.druid_boons])
            special_dict["druid"].append(boon_str)
        if self.obelisk_pile:
            special_dict["obelisk"].append(sani_func(self.obelisk_pile))
        if self.ferryman_pile:
            special_dict["ferryman"].append(sani_func(self.ferryman_pile))
        if self.riverboat_card:
            special_dict["riverboat"].append(sani_func(self.riverboat_card))
        if self.mouse_card:
            special_dict["way_of_the_mouse"].append(sani_func(self.mouse_card))
        if self.divine_wind_cso_str:
            special_dict["divine_wind"].append(
                Kingdom.from_dombot_csv_string(
                    self.divine_wind_cso_str
                ).get_dombot_csv_string(ignore_col_shelt=True)
            )
        for trait, target in self.traits:
            special_dict[trait].append(sani_func(target))
        if add_stamps:
            for stamp, target in self.stamps_and_effects:
                special_dict[stamp].append(sani_func(target))
        formatted: defaultdict[str, list[str]] = defaultdict(lambda: [""])
        for key, vals in special_dict.items():
            formatted[key] = [f" ({val})" for val in vals]
        return formatted

    def get_dombot_csv_string(self, ignore_col_shelt=False) -> str:
        """Construct a comma-separated string that can be fed to DomBot to generate
        the kingdom.
        """
        # Remove the / for split piles:
        cards = [card.split("/")[0] for card in self.cards]
        special_dict = self._get_special_dict(get_cso_name)
        proper_strings = [
            get_cso_name(cso) + extra
            for cso in cards + self.landscapes
            for extra in special_dict[cso]
        ]
        if not ignore_col_shelt:
            proper_strings.append("Shelters" if self.use_shelters else "No Shelters")
            proper_strings.append("Colonies" if self.use_colonies else "No Colonies")
        if self.is_campaign:
            # Not understood by DomBot, which doesn't support campaign features anyway
            proper_strings.append("Campaign")
        sep_string = ", ".join(sorted(proper_strings))
        if len(self.campaign_effects) == 0:
            return sep_string
        special_dict = self._get_special_dict(lambda x: x)
        effect_strings = []
        for effect_name in self.campaign_effects:
            effect_type = (
                ALL_CSOS.loc[effect_name]["Types"][0]
                .lower()
                .replace("setup effect", "start")
            )
            effect = effect_type + "_" + effect_name
            effect_strings += [effect + extra.strip() for extra in special_dict[effect_name]]
        return sep_string + " -x " + ", ".join(effect_strings)

    def get_sanitized_tgg_string(self) -> str:
        """Get a sanitized string representation of the kingdom."""
        special_dict = self._get_special_dict(sanitize_cso_name, add_stamps=False)
        proper_strings = [
            sanitize_cso_name(cso) + extra
            for cso in self.cards + self.landscapes + self.campaign_effects
            for extra in special_dict[cso]
        ]

        k_str = ", ".join(sorted(proper_strings))
        if self.use_shelters:
            k_str += ", shelters"
        if self.use_colonies:
            k_str += ", colonies"
        if self.campaign_effects:
            effect_targets = self.effect_targets
            k_str += " -x "
            k_str += ", ".join(
                f"{eff}({target})" if eff in effect_targets else eff
                for eff in sorted(self.campaign_effects)
                if eff
                for target in effect_targets.get(eff, [""])
            )
        return k_str

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
        text += "CSV representation:\n\n" + self._get_csv_repr()
        return text

    def get_dict_repr(self) -> dict[str, Any]:
        """Return the dictionary representation of the kingdom,
        using only the properties that should be exposed.
        """
        return asdict(
            self, dict_factory=lambda x: _dict_factory_func(x, self.__yaml_ignore__)
        )

    def _get_csv_repr(self) -> str:
        """TODO: proper Bane/Trait/Mouse/Druid Boons representation, currently you should use the dombot str"""
        return ", ".join(card for card in self.full_kingdom_df["Name"])

    def _set_quality_values(self):
        """Update the quality values for this kingdom by summing them up."""
        for qual in QUALITIES_AVAILABLE:
            val = get_total_quality(qual, self.full_kingdom_df)
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
        if len(df) == 0:
            return {}
        avail_types = reduce(lambda x, y: x + y, df[qual])
        if len(avail_types) == 0:
            return {}
        unique_types, counts = np.unique(avail_types, return_counts=True)
        return {t: c for t, c in zip(unique_types, counts)}

    def get_qualtype_string(self, qual: str, cutoff_len: int | None = 100) -> str:
        text = f"{qual.capitalize() + ':':10s}"
        if len((types := self.get_unique_qualtypes(qual))) > 0:
            types = [
                k if types[k] == 1 else f"{k} [x{types[k]}]"
                for k in sorted(types.keys())
            ]
            text += ", ".join(sorted(types))
        else:
            text += "-"
        if cutoff_len is not None and len(text) > cutoff_len:
            text = text[:cutoff_len] + "..."
        return text

    def get_component_string(
        self, cutoff_len: int | None = 180, show_exp=False, exclude_trash_mat=True
    ) -> str:
        """Retrieve the string describing the extra components and csos needed for this kingdom."""
        comp = self.full_kingdom_df["Extra Components"].tolist()
        excluded = ["Trash mat", "-"] if exclude_trash_mat else ["-"]
        unzipped = [cso for cso_list in comp for cso in cso_list if cso not in excluded]
        uni_comp = list(np.unique(unzipped))
        # TODO: Add expansions from which they come
        if self.use_shelters:
            shelt = "Shelters (Dark Ages)" if show_exp else "Shelters"
            uni_comp.append(shelt)
        if self.use_colonies:
            colplat = (
                "Colonies/Platinum (Prosperity)" if show_exp else "Colonies/Platinum"
            )
            uni_comp.append(colplat)
        text = "EXTRAS:   "
        comp_str = text + (", ".join(uni_comp) if len(uni_comp) > 0 else "None needed")
        if cutoff_len is not None and len(comp_str) > cutoff_len:
            comp_str = comp_str[:cutoff_len] + "..."
        return comp_str

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

    # def get_actual_expansions(self):
    #     """Returns the actual expansions used; e.g., if Base, 1E and Base, 2E are both present, they will both be
    #     returned, but if there is only Base and Base 1E, only Base 1E will be returned, and if there's only
    #     Base, just Base 2E will be returned."""
