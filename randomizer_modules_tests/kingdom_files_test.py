"""The stored kingdoms in static/kingdoms/*.yml must be consistent (M24, and the
data issues found while writing the M5 parser tests)."""

from collections import Counter
from pathlib import Path

import pytest
import yaml

import random_kingdominion as rk
from random_kingdominion.kingdom.invalidity_stuff import InvalidityReason

KINGDOM_FILES = sorted(rk.PATH_ASSETS.joinpath("kingdoms").glob("*.yml"))
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
    in campaigns, which `load_campaigns` marks as such."""
    problems = []
    for path in KINGDOM_FILES:
        if path.name == "campaigns.yml":
            continue
        for info in _load(path):
            if not info.get("traits"):
                continue
            kingdom = rk.Kingdom.from_dict(info)
            reasons = InvalidityReason.check_kingdom_validity(kingdom)
            problems += [
                f"{path.name} {kingdom.name}: {reason.get_description()}"
                for reason in reasons
                if reason.key in _CAMPAIGN_ONLY_REASONS
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
