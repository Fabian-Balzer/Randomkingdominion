"""Parsing DomBot strings (e.g. ``"village, young_witch(moat), no colonies"``) in
steps, for `Kingdom.from_dombot_csv_string` (M19): normalize the string, tokenize it
into a tree of entries, resolve the entries into CSOs and special targets, and get
the `Kingdom` fields from that, i.e. decide which targets become piles."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from ..constants import ALL_CSOS
from ..utils import sanitize_cso_name

# Other separators in use, e.g. TGG's "-m" before Colonies and Shelters, and "-x"
# before the campaign effects
_SEPARATORS = ["-m ", "-x ", ". ", "; "]
_SPELLINGS = {
    "landscapes: ": ", ",
    "city_state": "city-state",
    "will_o_wisp": "will-o-wisp",
}
# Longest spelling first; "colony/platinum" would become "colonies/colonies"
_COLONY_SPELLINGS = ["colony/platinum", "colony", "platinum"]

# Specials with a single target, and the `Kingdom` field the target goes into
_SINGLE_TARGET_SPECIALS = {
    "young_witch": "bane_pile",
    "bane": "bane_pile",  # Not understood by DomBot, to be dropped (M19, step 8)
    "ferryman": "ferryman_pile",
    "riverboat": "riverboat_card",
    "way_of_the_mouse": "mouse_card",
    "obelisk": "obelisk_pile",
    "approaching_army": "army_pile",
}
# Their targets are specific cards: a Lich replacing a Copper, not the Wizards pile
_EFFECTS_ON_SPECIFIC_CARDS = {
    "replace_copper",
    "replace_estate",
    "replace_estate_from_pile",
    "add_card",
    "in_play",
    "tavern",
}
# Their targets aren't piles of the kingdom (unlike e.g. a Stamp's)
_EFFECTS_WITHOUT_PILES = {
    "replace_copper",
    "replace_estate",
    "add_card",
    "in_play",
    "tavern",
    "trash_pile",
}


@dataclass(frozen=True)
class _CsoKeys:
    all: frozenset[str]
    supply: frozenset[str]
    landscapes: frozenset[str]
    traits: frozenset[str]
    effects: frozenset[str]
    parent_piles: dict[str, str]


@lru_cache(maxsize=1)
def _get_cso_keys() -> _CsoKeys:
    """The keys of each kind of CSO; `ALL_CSOS` isn't changed after import. Set
    lookups instead of `ALL_CSOS.loc` (~20 µs each)."""

    def keys(column: str) -> frozenset[str]:
        return frozenset(ALL_CSOS.index[ALL_CSOS[column]])

    parent_piles = ALL_CSOS.loc[ALL_CSOS["HasParentPile"], "ParentPile"]
    return _CsoKeys(
        all=frozenset(ALL_CSOS.index),
        supply=keys("IsInSupply"),
        landscapes=keys("IsExtendedLandscape"),
        traits=keys("IsTrait"),
        effects=keys("IsCampaignEffect"),
        parent_piles={k: sanitize_cso_name(p) for k, p in parent_piles.items()},
    )


def _to_key(name: str, replace_parent_pile: bool = True) -> str:
    """Like `sanitize_cso_name`, without its lookup (and log) per name."""
    key = sanitize_cso_name(name.strip(" _"))
    if replace_parent_pile:
        return _get_cso_keys().parent_piles.get(key, key)
    return key


def normalize_dombot_string(dombot_str: str) -> str:
    """Unify the separators, the case and some spellings, and write the colon
    syntax with parentheses.

    Examples
    --------
    >>> normalize_dombot_string("Moat, Way_of_the_Mouse:Menagerie. Landscapes: Alms")
    'moat, way_of_the_mouse(menagerie), , alms'
    """
    for separator in _SEPARATORS:
        dombot_str = dombot_str.replace(separator, ", ")
    dombot_str = dombot_str.lower()
    for spelling, replacement in _SPELLINGS.items():
        dombot_str = dombot_str.replace(spelling, replacement)
    return re.sub(r":\s*([^,()]*?)\s*(?=[,()]|$)", r"(\1)", dombot_str)


@dataclass(frozen=True)
class DomBotEntry:
    """An entry of a DomBot string, with the entries in its parentheses as its
    arguments, e.g. ``ferryman(young_witch(vassal))``."""

    name: str
    """The text in front of the parentheses."""
    args: tuple[DomBotEntry, ...] = ()
    text: str = ""
    """The whole entry as written (after normalizing), for the notes."""


def _find_unmatched_parentheses(dombot_str: str) -> tuple[list[int], list[int]]:
    """The positions of each "(" that isn't closed and each ")" not opened."""
    unclosed: list[int] = []
    unopened: list[int] = []
    for i, char in enumerate(dombot_str):
        if char == "(":
            unclosed.append(i)
        elif char == ")":
            if unclosed:
                unclosed.pop()
            else:
                unopened.append(i)
    return unclosed, unopened


def _balance_parentheses(dombot_str: str, notes: list[str]) -> str:
    """Drop each ")" that wasn't opened, and close each "(" at the end of its entry,
    i.e. in front of the next comma at its level, as the parser before M19 did:
    "young_witch(moat, smithy" means "young_witch(moat), smithy"."""
    _, unopened = _find_unmatched_parentheses(dombot_str)
    if unopened:
        dropped = set(unopened)
        dombot_str = "".join(c for i, c in enumerate(dombot_str) if i not in dropped)
        notes.append(f"Ignored {len(unopened)} ')' without a '('.")
    unclosed, _ = _find_unmatched_parentheses(dombot_str)
    # From the right, so that all parentheses after the current one are balanced
    for start in reversed(unclosed):
        end, depth = start + 1, 0
        while end < len(dombot_str) and (depth > 0 or dombot_str[end] != ","):
            depth += {"(": 1, ")": -1}.get(dombot_str[end], 0)
            end += 1
        dombot_str = dombot_str[:end] + ")" + dombot_str[end:]
    if unclosed:
        notes.append(f"Closed {len(unclosed)} '(' at the end of the entry.")
    return dombot_str


def tokenize_dombot_string(dombot_str: str) -> tuple[list[DomBotEntry], list[str]]:
    """Split a normalized DomBot string into its entries, each with the entries in
    its parentheses (any depth), and notes on what was ignored or fixed.

    Examples
    --------
    >>> entries, notes = tokenize_dombot_string("ferryman(young_witch(vassal)), moat")
    >>> [(entry.name, [arg.name for arg in entry.args]) for entry in entries]
    [('ferryman', ['young_witch']), ('moat', [])]
    >>> entries[0].args[0].args[0].text
    'vassal'
    >>> entries, notes = tokenize_dombot_string("young_witch(moat, smithy")
    >>> [entry.text for entry in entries], notes
    (['young_witch(moat)', 'smithy'], ["Closed 1 '(' at the end of the entry."])
    """
    notes: list[str] = []
    balanced = _balance_parentheses(dombot_str, notes)
    entries, _ = _parse_entries(balanced, 0, notes)
    return entries, notes


def _parse_entries(
    dombot_str: str, pos: int, notes: list[str]
) -> tuple[list[DomBotEntry], int]:
    """The comma-separated entries from `pos` up to the end or the closing
    parenthesis of the enclosing entry, and the position of that end."""
    entries = []
    while True:
        entry, pos = _parse_entry(dombot_str, pos, notes)
        if entry is not None:
            entries.append(entry)
        if pos >= len(dombot_str) or dombot_str[pos] == ")":
            return entries, pos
        pos += 1  # The comma


def _parse_entry(
    dombot_str: str, pos: int, notes: list[str]
) -> tuple[DomBotEntry | None, int]:
    """The entry starting at `pos` (None if empty), and the position after it."""
    start = pos
    while pos < len(dombot_str) and dombot_str[pos] not in ",()":
        pos += 1
    name = dombot_str[start:pos].strip()
    args: list[DomBotEntry] = []
    if pos < len(dombot_str) and dombot_str[pos] == "(":
        args, pos = _parse_entries(dombot_str, pos + 1, notes)
        pos += 1  # The closing parenthesis, as they are balanced
    end, depth = pos, 0
    while pos < len(dombot_str) and (depth > 0 or dombot_str[pos] not in ",)"):
        depth += {"(": 1, ")": -1}.get(dombot_str[pos], 0)
        pos += 1
    text = dombot_str[start:end].strip()
    if trailing := dombot_str[end:pos].strip():
        notes.append(f"Ignored '{trailing}' after '{text}'.")
    if not name and not args:
        return None, pos
    return DomBotEntry(name, tuple(args), text), pos


@dataclass
class ParsedDomBotKingdom:
    """What a DomBot string specifies, before deciding which targets are piles."""

    csos: list[str] = field(default_factory=list)
    """The recognized CSOs listed on their own (not as targets), in input order."""
    specials: dict[str, str] = field(default_factory=dict)
    """The targets of single-target specials by `Kingdom` field, e.g.
    ``{"bane_pile": "moat"}``."""
    druid_boons: list[str] = field(default_factory=list)
    divine_wind_cso_str: str = ""
    trait_targets: dict[str, list[str]] = field(default_factory=dict)
    effect_targets: dict[str, list[str]] = field(default_factory=dict)
    """Targets may repeat: two Silvers replacing two Coppers."""
    use_colonies: bool = False
    use_shelters: bool = False
    is_campaign: bool = False
    unrecognized: list[str] = field(default_factory=list)
    ignored_targets: list[str] = field(default_factory=list)
    """Targets of CSOs that take none, or more than they take, as "cso(target)"."""
    duplicates: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def resolve_dombot_entries(entries: list[DomBotEntry]) -> ParsedDomBotKingdom:
    """Resolve the tokenized entries into CSO keys and special targets. A target
    resolves its own targets without being listed itself: in
    ``ferryman(young_witch(vassal))``, Young Witch is Ferryman's pile and Vassal
    the Bane.

    Examples
    --------
    >>> entries, _ = tokenize_dombot_string("ferryman(young_witch(vassal)), moat")
    >>> parsed = resolve_dombot_entries(entries)
    >>> parsed.csos, parsed.specials
    (['ferryman', 'moat'], {'bane_pile': 'vassal', 'ferryman_pile': 'young_witch'})
    """
    keys = _get_cso_keys()
    parsed = ParsedDomBotKingdom()
    use_colonies: bool | None = None
    use_shelters: bool | None = None
    counted_texts = []
    for entry in entries:
        name, text = entry.name, entry.text
        if not entry.args:
            # Only standalone entries: "start_double_pile(colony)" targets Colony
            for spelling in _COLONY_SPELLINGS:
                name = name.replace(spelling, "colonies")
            text = name
            if name == "campaign":  # Marks a kingdom that may use campaign rules
                parsed.is_campaign = True
                continue
        key = _to_key(name)
        # A campaign effect may appear several times, e.g. replacing two Coppers
        if key not in keys.effects:
            counted_texts.append(text)
        if not entry.args and ("colonies" in name or "shelters" in name):
            if "colonies" in name and use_colonies is None:
                use_colonies = "no" not in name
            if "shelters" in name and use_shelters is None:
                use_shelters = "no" not in name
            continue
        if key in keys.all:
            parsed.csos.append(key)
        elif key not in _SINGLE_TARGET_SPECIALS:
            if key:
                parsed.unrecognized.append(key)
            continue
        _resolve_targets(key, entry.args, parsed)
    parsed.use_colonies = bool(use_colonies)
    parsed.use_shelters = bool(use_shelters)
    parsed.unrecognized = list(dict.fromkeys(parsed.unrecognized))
    parsed.duplicates = {
        text: num for text, num in Counter(counted_texts).items() if num > 1
    }
    return parsed


def _resolve_target(
    arg: DomBotEntry,
    parsed: ParsedDomBotKingdom,
    replace_parent_pile: bool = True,
    resolve_own_targets: bool = True,
) -> str:
    """The key of a target ("" if unknown), after resolving its own targets."""
    key = _to_key(arg.name, replace_parent_pile)
    if key not in _get_cso_keys().all:
        if key:
            parsed.unrecognized.append(key)
        return ""
    if resolve_own_targets:
        _resolve_targets(key, arg.args, parsed)
    return key


def _note_unsupported_specials(
    cso_name: str, args: tuple[DomBotEntry, ...], parsed: ParsedDomBotKingdom
) -> None:
    """The piles of Divine Wind and Typhoon only join the kingdom later, so their
    specials don't apply to it (M19, step 9)."""
    if nested := [arg.text for arg in args if arg.args]:
        parsed.notes.append(
            f"Specials inside {cso_name} aren't supported yet, ignored the targets of: {', '.join(nested)}."
        )


def _resolve_targets(
    key: str, args: tuple[DomBotEntry, ...], parsed: ParsedDomBotKingdom
) -> None:
    """Put the targets of the given CSO, and their own targets, into `parsed`."""
    if not args:
        return
    keys = _get_cso_keys()
    ignored = [f"{key}({arg.text})" for arg in args]
    if key in _SINGLE_TARGET_SPECIALS:
        field_name = _SINGLE_TARGET_SPECIALS[key]
        if field_name not in parsed.specials:
            if target := _resolve_target(args[0], parsed):
                parsed.specials[field_name] = target
        elif parsed.specials[field_name] != _to_key(args[0].name):
            parsed.ignored_targets.append(ignored[0])  # The first one counts
        parsed.ignored_targets += ignored[1:]
    elif key == "druid":
        boons = [_resolve_target(arg, parsed, False) for arg in args]
        if not parsed.druid_boons:
            parsed.druid_boons = [boon for boon in boons if boon]
        elif sorted(parsed.druid_boons) != sorted(boons):
            parsed.ignored_targets += ignored
    elif key == "divine_wind":
        _note_unsupported_specials("Divine Wind", args, parsed)
        if not parsed.divine_wind_cso_str:
            parsed.divine_wind_cso_str = ", ".join(arg.name for arg in args)
    elif key in keys.traits:
        if len(args) > 1:  # Several targets of a Trait are listed separately
            joined = ", ".join(arg.text for arg in args)
            parsed.unrecognized.append(sanitize_cso_name(joined))
        elif target := _resolve_target(args[0], parsed):
            parsed.trait_targets.setdefault(key, []).append(target)
    elif key in keys.effects:
        replace_parent_pile = key not in _EFFECTS_ON_SPECIFIC_CARDS
        if is_typhoon := key == "typhoon":
            _note_unsupported_specials("Typhoon", args, parsed)
        for arg in args:
            target = _resolve_target(
                arg, parsed, replace_parent_pile, resolve_own_targets=not is_typhoon
            )
            if target:
                parsed.effect_targets.setdefault(key, []).append(target)
    else:
        parsed.ignored_targets += ignored


def get_kingdom_fields(
    parsed: ParsedDomBotKingdom,
    syntax_notes: list[str] | None = None,
    add_unrecognized_notes: bool = True,
) -> dict[str, Any]:
    """The `Kingdom` fields for a resolved DomBot string: the CSOs become piles,
    and so do a Bane, the Army pile, a Trait's supply targets and the target of
    an effect with a single target (except replacements of starting cards and
    other `_EFFECTS_WITHOUT_PILES`). The notes list what wasn't used.

    Examples
    --------
    >>> entries, _ = tokenize_dombot_string("ferryman(young_witch(vassal)), moat")
    >>> fields = get_kingdom_fields(resolve_dombot_entries(entries))
    >>> fields["cards"], fields["ferryman_pile"], fields["bane_pile"]
    (['ferryman', 'moat', 'vassal'], 'young_witch', 'vassal')
    """
    keys = _get_cso_keys()
    specials = parsed.specials
    piles = parsed.csos + [specials.get("bane_pile", ""), specials.get("army_pile", "")]
    piles = list(dict.fromkeys(pile for pile in piles if pile))
    cards = [pile for pile in piles if pile in keys.supply]
    landscapes = [pile for pile in piles if pile in keys.landscapes]
    campaign_effects = [pile for pile in piles if pile in keys.effects]
    ignored_targets = list(parsed.ignored_targets)
    # Outside of campaigns, a Trait has exactly one supply pile as its target;
    # several targets or non-supply ones (e.g. Gold) are kept, and the validity
    # check marks them as campaign-only
    traits = []
    for trait, targets in parsed.trait_targets.items():
        if trait not in landscapes:  # Only as a target itself
            ignored_targets += [f"{trait}({target})" for target in targets]
            continue
        traits += [[trait, target] for target in dict.fromkeys(targets)]
    new_piles = [target for _, target in traits if target in keys.supply]
    stamps_and_effects = []
    for effect, targets in parsed.effect_targets.items():
        if effect not in campaign_effects:
            ignored_targets += [f"{effect}({target})" for target in targets]
            continue
        stamps_and_effects += [[effect, target] for target in targets]
        # Not the targets of e.g. Typhoon, which lists several
        if len(targets) == 1 and effect not in _EFFECTS_WITHOUT_PILES:
            new_piles += targets
    for pile in new_piles:
        if pile in keys.supply and pile not in cards:
            cards.append(pile)
        elif pile in keys.landscapes and pile not in landscapes:
            landscapes.append(pile)
    notes = list(syntax_notes or []) + parsed.notes
    if add_unrecognized_notes and parsed.unrecognized:
        unrecognized = ", ".join(f"'{cso}'" for cso in parsed.unrecognized)
        notes.append(
            "The following inputs could not be associated with any known CSOs: "
            + unrecognized
        )
    if add_unrecognized_notes and ignored_targets:
        ignored = ", ".join(f"'{target}'" for target in ignored_targets)
        notes.append(
            f"The following targets were ignored, as their CSO takes none or only one: {ignored}"
        )
    if add_unrecognized_notes and parsed.duplicates:
        notes.append(f"Duplicates: {parsed.duplicates}")
    return {
        "cards": cards,
        "landscapes": landscapes,
        "campaign_effects": campaign_effects,
        "use_colonies": parsed.use_colonies,
        "use_shelters": parsed.use_shelters,
        "druid_boons": parsed.druid_boons,
        "divine_wind_cso_str": parsed.divine_wind_cso_str,
        "traits": traits,
        "stamps_and_effects": stamps_and_effects,
        "is_campaign": parsed.is_campaign,
        "notes": "".join(f"{note}\n" for note in notes),
    } | specials
