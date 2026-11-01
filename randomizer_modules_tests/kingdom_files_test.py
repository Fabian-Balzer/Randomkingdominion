"""The stored kingdoms in static/kingdoms/*.yml must be consistent (M24, and the
data issues found while writing the M5 parser tests)."""

from collections import Counter
from functools import cache
from pathlib import Path

import pytest
import yaml

import random_kingdominion as rk
from random_kingdominion.kingdom.invalidity_stuff import InvalidityReason

KINGDOM_DIR = rk.PATH_ASSETS.joinpath("kingdoms")
KINGDOM_FILES = sorted(KINGDOM_DIR.glob("*.yml"))
_SINGLE_TARGETS = [
    "bane_pile",
    "obelisk_pile",
    "ferryman_pile",
    "riverboat_card",
    "mouse_card",
    "army_pile",
]
_SPECIALS = _SINGLE_TARGETS + [
    "druid_boons",
    "divine_wind_cso_str",
    "traits",
    "stamps_and_effects",
]
_CAMPAIGN_ONLY_REASONS = {
    "trait_on_several_piles_outside_campaign",
    "trait_on_non_supply_pile_outside_campaign",
}


# Parsing all files takes ~2.5 s; the tests only read the entries
@cache
def _load(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def _entry_problems(info: dict) -> list[str]:
    csos = rk.ALL_CSOS
    problems = []
    for col in ["cards", "landscapes"]:
        entries = [rk.sanitize_cso_name(e) for e in info.get(col) or []]
        if duplicates := [e for e, n in Counter(entries).items() if n > 1]:
            problems.append(f"{col} twice: {duplicates}")
        if unknown := [e for e in entries if e not in csos.index]:
            problems.append(f"unknown {col}: {unknown}")
    for col, required, description in [
        ("landscapes", "IsExtendedLandscape", "a landscape"),
        ("cards", "IsInSupply", "a supply pile"),
    ]:
        entries = [rk.sanitize_cso_name(e) for e in info.get(col) or []]
        wrong = [e for e in entries if e in csos.index and not csos.loc[e, required]]
        if wrong:
            problems.append(f"in {col}, but not {description}: {wrong}")
    for col in _SINGLE_TARGETS:
        target = info.get(col, "")
        # Split piles may be stored with their parent, e.g. "patrician/emporium"
        if target and target.split("/")[0] not in csos.index:
            problems.append(f"{col} '{target}' is no CSO")
    return problems


@pytest.mark.parametrize("path", KINGDOM_FILES, ids=[p.name for p in KINGDOM_FILES])
def test_stored_kingdoms_have_consistent_entries(path: Path):
    problems = [
        f"{info.get('name', '?')}: {'; '.join(found)}"
        for info in _load(path)
        if (found := _entry_problems(info))
    ]
    assert problems == [], f"{path.name}:\n" + "\n".join(problems)


def test_only_campaign_kingdoms_use_campaign_rules():
    """A Trait on several piles or on a non-supply pile (e.g. Gold) is only possible
    in campaigns, which `load_campaigns` marks as such, and in the Sunday Dailies
    since February 2025 (`load_tgg_dailies`)."""
    problems = []
    for path in KINGDOM_FILES:
        if path.name == "campaigns.yml":
            continue
        for info in _load(path):
            if not info.get("traits"):
                continue
            if path.name == "tgg_dailies.yml" and rk.is_campaign_daily(info["name"]):
                continue
            kingdom = rk.Kingdom.from_dict(info)
            reasons = InvalidityReason.check_kingdom_validity(kingdom)
            problems += [
                f"{path.name} {kingdom.name}: {reason.get_description()}"
                for reason in reasons
                if reason.key in _CAMPAIGN_ONLY_REASONS
            ]
    assert problems == [], "\n".join(problems)


def test_tgg_dailies_on_sundays_are_loaded_as_campaigns():
    manager = rk.KingdomManager()
    manager.load_tgg_dailies()
    sunday = manager.get_kingdom_by_name("2026-10-18")  # Nearby on two piles
    assert sunday is not None and sunday.is_campaign
    saturday = manager.get_kingdom_by_name("2026-10-17")
    assert saturday is not None and not saturday.is_campaign


@pytest.mark.parametrize(
    "name, expected",
    [
        ("2025-02-02", True),  # The first Sunday in February 2025
        ("2026-10-18", True),
        ("2025-01-26", False),  # A Sunday before
        ("2025-02-01", False),  # A Saturday
        ("Plunder 3", False),
    ],
)
def test_is_campaign_daily(name: str, expected: bool):
    assert rk.is_campaign_daily(name) == expected


def _target_pairs(kingdom: rk.Kingdom) -> Counter:
    return Counter(tuple(pair) for pair in kingdom.traits + kingdom.stamps_and_effects)


@pytest.mark.slow
@pytest.mark.parametrize("name", ["tgg_dailies", "campaigns", "fabi_recsets"])
def test_stored_kingdoms_keep_the_targets_of_their_input(name: str):
    """scripts/data/new_kingdoms/<name>.txt is only used to create new entries of
    <name>.yml, which may be edited afterwards. But no Trait or Stamp target of the
    input may be missing, as with older parser versions: a second target was dropped
    as a duplicate, or a replacement stored as its pile (Ruins instead of Survivors).
    """
    stored = {info["name"]: info for info in _load(KINGDOM_DIR / f"{name}.yml")}
    lines = (rk.PATH_MAIN / f"scripts/data/new_kingdoms/{name}.txt").read_text(
        encoding="utf-8"
    )
    problems = []
    for line in lines.splitlines():
        if not line.strip():
            continue
        kingdom_name, kingdom_str = line.split("---")[:2]
        # Only entries with special targets can lose them
        if "(" not in kingdom_str or kingdom_name not in stored:
            continue
        parsed = rk.Kingdom.from_dombot_csv_string(kingdom_str, check_validity=False)
        kingdom = rk.Kingdom.from_dict(stored[kingdom_name])
        if missing := _target_pairs(parsed) - _target_pairs(kingdom):
            problems.append(f"{kingdom_name}: {sorted(missing.elements())}")
    header = f"{name}.yml lacks targets of {name}.txt:\n"
    assert problems == [], header + "\n".join(problems)


def test_start_effects_replace_by_cards_not_by_piles():
    """A starting card is replaced by a specific card (Survivors, Lich), not by its
    split pile (Ruins, Wizards), which older parser versions stored."""
    csos = rk.ALL_CSOS
    split_piles = set(
        csos.loc[csos["HasParentPile"], "ParentPile"].map(rk.sanitize_cso_name)
    )
    problems = [
        f"{path.name} {info.get('name', '?')}: {effect}({target})"
        for path in KINGDOM_FILES
        for info in _load(path)
        for effect, target in info.get("stamps_and_effects") or []
        if effect.startswith("replace") and target in split_piles
    ]
    assert problems == [], "\n".join(problems)


@pytest.mark.slow
def test_stored_kingdoms_survive_printing_and_parsing():
    """kingdom -> DomBot string -> kingdom gives the same kingdom, for all stored
    kingdoms with special targets (~530 of ~2200, ~25 s; the others have none)."""
    problems = []
    for path in KINGDOM_FILES:
        for info in _load(path):
            if not any(info.get(col) for col in _SPECIALS):
                continue
            kingdom = rk.Kingdom.from_dict(info)
            printed = kingdom.get_dombot_csv_string()
            reparsed = rk.Kingdom.from_dombot_csv_string(printed, name=kingdom.name)
            if reparsed != kingdom:
                problems.append(f"{path.name} {kingdom.name}: {printed}")
    assert problems == [], "\n".join(problems)
