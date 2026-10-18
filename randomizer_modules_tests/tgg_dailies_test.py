"""Consistency checks for the stored TGG Dailies (static/kingdoms/tgg_dailies.yml)."""

from collections import Counter
from datetime import date, timedelta

import pytest
import yaml

from random_kingdominion.kingdom import KingdomManager
from random_kingdominion.kingdom.kingdom_manager import sort_kingdom_yaml_file

# Days for which it's clear that the Daily can't be recovered
KNOWN_MISSING_DAILIES: set[str] = set()

# Stored fields that don't describe the kingdom itself
_NON_KINGDOM_FIELDS = {"name", "idx", "notes", "winrate", "expansions"}


@pytest.fixture(scope="module")
def dailies() -> list[dict]:
    manager = KingdomManager()
    # Unsorted, to see the order in the file
    manager.load_tgg_dailies(sort=False)
    return manager.kingdoms


def test_daily_names_are_dates(dailies: list[dict]) -> None:
    invalid = []
    for daily in dailies:
        try:
            date.fromisoformat(daily["name"])
        except ValueError:
            invalid.append(daily["name"])
    assert not invalid, f"Dailies not named YYYY-MM-DD: {invalid}"


def test_daily_names_are_unique(dailies: list[dict]) -> None:
    counts = Counter(daily["name"] for daily in dailies)
    assert not [name for name, count in counts.items() if count > 1]


def test_every_day_between_first_and_last_daily_has_one(dailies: list[dict]) -> None:
    dates = {date.fromisoformat(daily["name"]) for daily in dailies}
    first, last = min(dates), max(dates)
    all_days = {first + timedelta(days=i) for i in range((last - first).days + 1)}
    missing = sorted(
        str(day) for day in all_days - dates if str(day) not in KNOWN_MISSING_DAILIES
    )
    assert not missing, f"{len(missing)} Dailies missing: {', '.join(missing)}"


def _get_kingdom_key(daily: dict) -> tuple:
    # The stored lists are already sanitized and sorted, so equal kingdoms have equal
    # entries apart from their name etc. (cheaper than building 1300+ Kingdoms)
    return tuple(
        sorted((k, repr(v)) for k, v in daily.items() if k not in _NON_KINGDOM_FIELDS)
    )


def test_daily_kingdoms_are_unique(dailies: list[dict]) -> None:
    first_by_key: dict[tuple, str] = {}
    duplicates = []
    for daily in sorted(dailies, key=lambda d: d["name"]):
        key = _get_kingdom_key(daily)
        if key in first_by_key:
            duplicates.append(f"{first_by_key[key]} = {daily['name']}")
        else:
            first_by_key[key] = daily["name"]
    assert not duplicates, f"Same kingdom on several days: {duplicates}"


def test_dailies_file_is_sorted_newest_first(dailies: list[dict]) -> None:
    names = [daily["name"] for daily in dailies]
    assert names == sorted(names, reverse=True), (
        "Sort it with kingdom_manager.sort_kingdom_yaml_file()"
    )


def test_sorting_a_kingdom_file_keeps_every_entry(tmp_path) -> None:
    entries = [
        {"name": "2024-01-02", "cards": ["village"], "idx": 2},
        {"name": "2024-01-03", "cards": ["smithy"], "idx": 3, "notes": {"a": 1}},
        # Entries without cards are skipped when loading, but mustn't get lost
        {"name": "2024-01-01", "idx": 1},
    ]
    fpath = tmp_path / "kingdoms.yml"
    fpath.write_text(yaml.safe_dump(entries), encoding="utf-8")

    sort_kingdom_yaml_file(fpath)
    newest_first = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    sort_kingdom_yaml_file(fpath, newest_first=False)
    oldest_first = yaml.safe_load(fpath.read_text(encoding="utf-8"))

    assert [e["name"] for e in newest_first] == ["2024-01-03", "2024-01-02", "2024-01-01"]
    assert oldest_first == newest_first[::-1]
    assert sorted(oldest_first, key=lambda e: e["idx"]) == sorted(
        entries, key=lambda e: e["idx"]
    )
