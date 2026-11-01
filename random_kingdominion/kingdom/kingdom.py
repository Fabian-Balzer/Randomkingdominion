"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from functools import cached_property, lru_cache, reduce
from json import JSONDecodeError, dumps, loads
from typing import Any, Callable, Iterable, Literal
from uuid import uuid4

import numpy as np
import pandas as pd

from ..constants import (
    ALL_CSOS,
    EXPANSION_DICT,
    HEIRLOOM_DICT,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
)
from ..logger import LOGGER
from ..utils import (
    get_cso_name,
    get_cso_sort_ranks,
    sanitize_cso_list,
    sanitize_cso_name,
)
from ..utils.kingdom_helper_funcs import explain_total_quality
from .dombot_parsing import (
    get_canonical_dombot_string,
    get_kingdom_fields,
    normalize_dombot_string,
    resolve_dombot_entries,
    tokenize_dombot_string,
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
    """The Divine Wind CSOs as sorted keys with their special targets, so that a
    kingdom compares equal however they were entered (display names or keys, any
    order), e.g. ``"distant_lands, page, young_witch(vassal)"``."""
    if not isinstance(divine_wind_str, str) or not divine_wind_str:
        return ""  # Also a missing value (NaN) in a DataFrame row
    return get_canonical_dombot_string(divine_wind_str)


def _sort_like_kingdom(keys: Iterable[str]) -> list[str]:
    """The keys in the order of `sort_kingdom`, without sorting a DataFrame."""
    ranks = get_cso_sort_ranks()
    return sorted(keys, key=ranks.__getitem__)


@lru_cache(maxsize=1)
def _get_heirlooms() -> dict[str, str]:
    """The Heirloom of each card that comes with one (Pixie → Goat)."""
    return {
        sanitize_cso_name(card): sanitize_cso_name(heirloom)
        for heirloom, card in HEIRLOOM_DICT.items()
    }


@lru_cache(maxsize=1)
def _get_quality_values() -> dict[str, dict[str, float]]:
    """The value of each quality per CSO."""
    return {qual: ALL_CSOS[f"{qual}_quality"].to_dict() for qual in QUALITIES_AVAILABLE}


@lru_cache(maxsize=1)
def _get_cso_expansions() -> dict[str, str | None]:
    """The expansion of each CSO as in `ALL_CSOS`, None for campaign effects."""
    return {
        key: None if is_effect else str(exp)
        for key, exp, is_effect in zip(
            ALL_CSOS.index, ALL_CSOS["Expansion"], ALL_CSOS["IsCampaignEffect"]
        )
    }


@lru_cache(maxsize=256)
def _get_divine_wind_kingdom(divine_wind_cso_str: str) -> Kingdom:
    """The validity check and the printing each parsed it again (~2 ms)."""
    return Kingdom.from_dombot_csv_string(divine_wind_cso_str)


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
    uses_bane_syntax: bool = field(default=False, compare=False, repr=False)
    """Whether the parsed input used ``bane(…)``, which DomBot doesn't understand."""
    idx: int = field(default_factory=lambda: int(uuid4()), compare=False)

    total_qualities: dict[str, float] = field(default_factory=dict, compare=False)
    csos_expansions: frozenset[str] = field(init=False, repr=False, compare=False)
    """The expansions of all CSOs (incl. the Divine Wind piles) as in `ALL_CSOS`,
    e.g. "Base" for cards in both editions, which `expansions` maps to one."""

    __yaml_ignore__ = {
        "extras",
        "total_qualities",
        "uses_bane_syntax",
        "csos_expansions",
    }

    @classmethod
    def from_dombot_csv_string(
        cls,
        csv_string: str,
        name: str = "",
        add_unrecognized_notes=True,
        check_validity=True,
    ) -> Kingdom:
        """Initialize the kingdom from a comma-separated string like the one DomBot
        produces with the !kingdom -r -l command. Special targets may be nested,
        e.g. ``ferryman(young_witch(vassal))``; see `dombot_parsing` for the steps.
        """
        normalized = normalize_dombot_string(csv_string)
        entries, syntax_notes = tokenize_dombot_string(normalized)
        parsed = resolve_dombot_entries(entries)
        fields = get_kingdom_fields(parsed, syntax_notes, add_unrecognized_notes)
        k = Kingdom(**fields, name=name)
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
        heirlooms = _get_heirlooms()
        effect_targets = self.effect_targets
        starting_deck = ["copper"] * 7
        if self.use_shelters:
            starting_deck += ["necropolis", "hovel", "overgrown_estate"]
        else:
            starting_deck += ["estate"] * 3
        for card in self.cards:
            if card in heirlooms:
                starting_deck[starting_deck.index("copper")] = heirlooms[card]
        # Each target's Heirloom replaces one more Copper
        for target in effect_targets.get("double_heirloom", []):
            if target not in heirlooms or target not in self.cards:
                raise ValueError(
                    f"Double Heirloom on '{target}', which is no kingdom card with an "
                    "Heirloom."
                )
            starting_deck[starting_deck.index("copper")] = heirlooms[target]
        if "double_deck" in self.campaign_effects:
            starting_deck += starting_deck
        # From the Supply or not, the replacement ends up in the starting deck
        estate_targets = effect_targets.get("replace_estate", []) + effect_targets.get(
            "replace_estate_from_pile", []
        )
        # With Shelters, Hovel goes first, then Overgrown Estate, then Necropolis. The
        # slots are fixed up front, so an Overgrown Estate put in isn't replaced again.
        estate_slots = [
            i
            for name in ["estate", "hovel", "overgrown_estate", "necropolis"]
            for i, card in enumerate(starting_deck)
            if card == name
        ]
        if len(estate_targets) > len(estate_slots):
            raise ValueError(
                f"{len(estate_targets)} Estate replacements, but only "
                f"{len(estate_slots)} Estates or Shelters in the starting deck."
            )
        for slot, target in zip(estate_slots, estate_targets):
            starting_deck[slot] = target
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
        """The Divine Wind piles as a kingdom of their own. Parsed once per string
        and shared between kingdoms, so don't modify it."""
        if len(self.divine_wind_cso_str) == 0:
            return None
        return _get_divine_wind_kingdom(self.divine_wind_cso_str)

    @property
    def has_modified_starting_deck(self) -> bool:
        """Check whether the starting deck has been modified."""
        return any(
            [
                effect in self.campaign_effects
                for effect in [
                    "replace_copper",
                    "replace_estate",
                    "replace_estate_from_pile",
                    "double_heirloom",
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
        if unknown := set(key_list) - _get_cso_expansions().keys():
            raise KeyError(f"{sorted(unknown)} not in the CSOs")
        self._full_keys = _sort_like_kingdom(set(key_list))
        self._set_quality_values()

        # TODO: Calculate extra piles necessary for the kingdom.
        cso_expansions = _get_cso_expansions()
        expansions = [
            exp for key in self._full_keys if (exp := cso_expansions[key]) is not None
        ]
        if (divine_wind := self.divine_wind_subkingdom) is not None:
            # Its piles join later, but are needed to set up the game (decided
            # 2026-11-01); before the edition mapping, as one set covers both
            expansions += divine_wind.csos_expansions
        self.csos_expansions = frozenset(expansions)
        unique_expansions = np.unique(expansions)
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
        return sorted(
            {eff for eff, target in self.stamps_and_effects if target == cso_key}
        )

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
        for trait_or_effect in self.get_traits_on(cso_key) + self.get_effects_on(
            cso_key
        ):
            text += f" >>>{get_cso_name(trait_or_effect)}<<<"
        return text

    def _get_special_targets(self, add_stamps=True) -> dict[str, list[list[str]]]:
        """The targets of each special CSO, one list per entry in parentheses, e.g.
        ``{"young_witch": [["moat"]], "druid": [[<its three Boons>]]}``. A Trait or
        campaign effect with several targets has one entry per target, which are
        printed separately."""
        special_targets: defaultdict[str, list[list[str]]] = defaultdict(list)
        for special, target in [
            ("young_witch", self.bane_pile),
            ("approaching_army", self.army_pile),
            ("obelisk", self.obelisk_pile),
            ("ferryman", self.ferryman_pile),
            ("riverboat", self.riverboat_card),
            ("way_of_the_mouse", self.mouse_card),
        ]:
            if target:
                special_targets[special].append([target])
        if self.druid_boons:
            special_targets["druid"].append(self.druid_boons)
        for trait, target in self.traits:
            special_targets[trait].append([target])
        if add_stamps:
            for stamp, target in self.stamps_and_effects:
                special_targets[stamp].append([target])
        return special_targets

    def _get_special_extras(
        self,
        cso_key: str,
        special_targets: dict[str, list[list[str]]],
        sani_func: Callable[[str], str],
        nested: set[str],
    ) -> list[str]:
        """The parentheses printed after the given CSO, one per entry, e.g.
        ``[" (Moat)"]`` for Young Witch, or ``[""]`` if it has none. A target that
        isn't printed on its own carries its own specials, the first time it's
        printed (tracked in `nested`): ``Ferryman (Young Witch (Vassal))``."""
        if cso_key == "divine_wind" and (divine_wind := self.divine_wind_subkingdom):
            return [f" ({divine_wind.get_dombot_csv_string(ignore_col_shelt=True)})"]
        if cso_key not in special_targets:
            return [""]
        printed_alone = set(self.cards + self.landscapes + self.campaign_effects)

        def format_target(target: str) -> str:
            if target in printed_alone or target in nested:
                return sani_func(target)
            nested.add(target)
            own_extras = self._get_special_extras(
                target, special_targets, sani_func, nested
            )
            return sani_func(target) + "".join(own_extras)

        return [
            f" ({', '.join(format_target(target) for target in entry)})"
            for entry in special_targets[cso_key]
        ]

    def get_dombot_csv_string(self, ignore_col_shelt=False) -> str:
        """Construct a comma-separated string that can be fed to DomBot to generate
        the kingdom.
        """
        # Remove the / for split piles:
        cards = [card.split("/")[0] for card in self.cards]
        special_targets = self._get_special_targets()
        nested: set[str] = set()
        proper_strings = [
            get_cso_name(cso) + extra
            for cso in cards + self.landscapes
            for extra in self._get_special_extras(
                cso, special_targets, get_cso_name, nested
            )
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
        effect_strings = []
        for effect_name in self.campaign_effects:
            effect_type = (
                ALL_CSOS.loc[effect_name]["Types"][0]
                .lower()
                .replace("setup effect", "start")
            )
            effect = effect_type + "_" + effect_name
            extras = self._get_special_extras(effect_name, special_targets, str, nested)
            effect_strings += [effect + extra.strip() for extra in extras]
        return sep_string + " -x " + ", ".join(effect_strings)

    def get_sanitized_tgg_string(self) -> str:
        """Get a sanitized string representation of the kingdom."""
        special_targets = self._get_special_targets()
        nested: set[str] = set()
        proper_strings = [
            sanitize_cso_name(cso) + extra
            for cso in self.cards + self.landscapes
            for extra in self._get_special_extras(
                cso, special_targets, sanitize_cso_name, nested
            )
        ] + [sanitize_cso_name(effect) for effect in self.campaign_effects]

        k_str = ", ".join(sorted(proper_strings))
        if self.use_shelters:
            k_str += ", shelters"
        if self.use_colonies:
            k_str += ", colonies"
        if self.campaign_effects:
            k_str += " -x "
            k_str += ", ".join(
                eff + extra.strip()
                for eff in sorted(self.campaign_effects)
                if eff
                for extra in self._get_special_extras(eff, special_targets, str, nested)
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

    def contains_young_witch(self) -> bool:
        """Checks whether this kingdom uses Young Witch and thus needs a Bane, also
        as a non-supply pile (e.g. Ferryman's)."""
        non_supply_piles = [self.ferryman_pile, self.riverboat_card, self.mouse_card]
        return "young_witch" in self.cards + non_supply_piles

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
        quality_values = _get_quality_values()
        for qual in QUALITIES_AVAILABLE:
            values = [quality_values[qual][key] for key in self._full_keys]
            self.total_qualities[qual] = explain_total_quality(values)[0]

    # Built on first use: most uses of a Kingdom (loading the stored ones, the
    # quiz's pools, printing) don't need them, and the four lookups took ~1.2 of
    # ~1.5 ms per Kingdom
    @cached_property
    def full_kingdom_df(self) -> pd.DataFrame:
        """All components of the kingdom except for Boons, Loot etc., but including
        Colonies, Shelters, and Ruins plus the special cards as well as Druid Boons,
        in the order of `sort_kingdom`."""
        return ALL_CSOS.loc[self._full_keys]

    @cached_property
    def kingdom_card_df(self) -> pd.DataFrame:
        return self.full_kingdom_df.loc[_sort_like_kingdom(self.cards)]

    @cached_property
    def kingdom_landscape_df(self) -> pd.DataFrame:
        return self.full_kingdom_df.loc[_sort_like_kingdom(self.landscapes)]

    @cached_property
    def kingdom_campaign_effects_df(self) -> pd.DataFrame:
        return self.full_kingdom_df.loc[_sort_like_kingdom(self.campaign_effects)]

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
