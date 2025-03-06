import numpy as np
import pandas as pd

from ...constants import (
    EXTENDED_LANDSCAPE_LIST,
    LANDSCAPE_LIST,
    OTHER_OBJ_LIST,
    ROTATOR_DICT,
    SPLIT_CARD_TYPES,
    SPLITPILE_CARDS,
    SPLITPILE_DICT,
)


def _do_lists_have_common(l1, l2):
    """Returns a bool wether two lists share at least one common element."""
    return len([y for y in l1 if y in l2]) > 0


def test_landscape(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    series = df["Types"].apply(lambda x: _do_lists_have_common(x, LANDSCAPE_LIST))
    return series


def test_extended_landscape(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    series = df["Types"].apply(
        lambda x: _do_lists_have_common(x, EXTENDED_LANDSCAPE_LIST)
    )
    return series


def test_other(df):
    """Tests whether the given object is a Hex, Boon, State or Artifact"""
    series = df["Types"].apply(lambda x: _do_lists_have_common(x, OTHER_OBJ_LIST))
    return series


def test_in_supply(df):
    """Creates a mask of all cards that are not kingdom cards.
    These things are:
        spirits, heirlooms, prizes, Spoils, Ruins, Shelters, Knights,
        Mercenary, Bat, Wish, Horse,
        Travellers (except page and peasant), Zombies, Allies, Split Piles,
        Rotating split piles, Prophecies
    """
    typelist = [
        "Traveller",
        "Spirit",
        "Heirloom",
        "Prize",
        "Reward",
        "Ruins",
        "Zombie",
        "Shelter",
        "Stamp",
        "Twist",
        "Setup Effect",
    ]
    typelist += SPLIT_CARD_TYPES
    # Some cards that are explicitly not part of the kingdom supply
    namelist = [
        "Bat",
        "Wish",
        "Horse",
        "Spoils",
        "Mercenary",
        "Madman",
        "Teacher",
        "Champion",
        "Estate",  # You could argue about the base cards, but this makes randomization easier.
        "Duchy",
        "Province",
        "Colony",
        "Curse",
        "Copper",
        "Silver",
        "Gold",
        "Platinum",
        "Potion",
    ] + SPLITPILE_CARDS
    # Knights as piles have a differing type from their instances
    still_include = [
        "Page",
        "Peasant",
        "Augurs",
        "Odysseys",
        "Townsfolk",
        "Wizards",
        "Clashes",
        "Forts",
        "Castles",
        "Ruins",
    ]
    series = (
        (
            df["Types"].apply(lambda x: _do_lists_have_common(x, typelist))
            & df["Name"].apply(lambda x: x not in still_include)
        )
        | df["Name"].apply(lambda x: x in namelist)
        | df["IsExtendedLandscape"]
        | df["IsOtherThing"]
    )
    return ~series


def test_real_supply_card(df: pd.DataFrame):
    split_headers = list(ROTATOR_DICT.keys()) + list(SPLITPILE_DICT.keys())
    # Splitpile cards are not part of the supply, but still cards, while their headers are not.
    is_no_split_header = ~np.isin(df["Name"], split_headers)
    series = (
        ~df["IsExtendedLandscape"]
        & ~df["IsOtherThing"]
        & (df["IsInSupply"] | df["IsPartOfSplitPile"])
        & is_no_split_header
    )
    return series


def add_bool_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Adds some boolean columns and saves the types as a list"""
    df["Types"] = df["Types"].str.split(" - ")
    df["IsLandscape"] = test_landscape(df)
    df["IsExtendedLandscape"] = test_extended_landscape(df)
    df["IsOtherThing"] = test_other(df)
    df["IsInSupply"] = test_in_supply(df)
    df["IsPartOfSplitPile"] = df["ParentPile"] != ""
    df["IsRealSupplyCard"] = test_real_supply_card(df)
    # df["IsCantrip"] = test_cantrip(df)
    return df
