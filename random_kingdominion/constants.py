"""Module containing constants, not to be modified!"""

import os
from dataclasses import dataclass
from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import colormaps as cm  # type: ignore

from random_kingdominion.cso_frame_utils import get_unique_entries_of_list_column
from random_kingdominion.cso_series_utils import listlike_contains


@dataclass(frozen=True)
class ColorPalette:
    """Registry for the colors used"""

    selected_green = "rgba(108,197,90,0.7)"
    way = "rgb(218, 242, 254)"
    event = "rgb(160, 175, 178)"
    ally = "rgb(218, 196, 155)"
    landmark = "rgb(73, 156, 96)"
    trait = "rgb(150, 145, 186)"
    project = "rgb(236, 172, 165)"
    prophecy = "rgb(78, 171, 198)"

    def get_bar_level_color(self, level_value: int):
        """Return the color for one of the bar values"""
        assert 0 <= level_value <= 4, f"Wrong level value {level_value}"
        return cm.get_cmap("Greens")(level_value / 4)

    def get_color_for_type(self, type_name: str):
        """Return the color for the given type."""
        return getattr(self, type_name.lower())


def read_dataframe_from_file(fpath: str | Path, eval_lists=False):
    """Read a dataframe"""
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath, sep=";", header=0)
        if eval_lists:
            for colname in df.columns:
                if "type" in colname.lower():
                    # Make sure we properly handle lists
                    df[colname] = df[colname].apply(eval)
    else:
        raise FileNotFoundError(
            2, "Couldn't find the raw card data file, please download it first."
        )
    return df


def _init_main_df():
    """Sets up the main DataFrame."""
    # category_types = [qual + "_quality" for qual in QUALITIES_AVAILABLE]
    category_types = ["Expansion"]
    unnecessary_cols = [
        "Actions / Villagers",
        "Cards",
        "Buys",
        "Coins / Coffers",
        "Trash / Return",
        "Exile",
        "Junk",
        "Gain",
        "Victory Points",
    ]
    df = read_dataframe_from_file(FPATH_CARD_DATA, True)
    df["index_name"] = df["Name"].str.lower().str.replace(" ", "_").str.replace("'", "")
    df = (
        df.set_index("index_name")
        .astype({cat: "category" for cat in category_types})
        .drop(unnecessary_cols, axis=1)
    )
    # Add interesting boolean columns:
    types_of_interest = [
        "Way",
        "Ally",
        "Liaison",
        "Trait",
        "Action",
        "Treasure",
        "Boon",
        "Hex",
        "Omen",
        "Prophecy",
    ]
    for type_ in types_of_interest:
        df["Is" + type_] = listlike_contains(df.Types, type_)
    return df


def get_attack_types(all_cards) -> list[str]:
    """Gather the existing AttackTypes from the given dataframe."""
    all_types = reduce(lambda x, y: x + y, all_cards["attack_types"])
    return sorted(list(np.unique(all_types)))


# Expansions with a second edition
RENEWED_EXPANSIONS = [
    "Base",
    "Intrigue",
    "Seaside",
    "Hinterlands",
    "Prosperity",
    "Cornucopia",
    "Guilds",
]

EXPANSION_DICT = {
    exp: (
        exp + ", 2E"
        if exp not in ["Cornucopia", "Guilds"]
        else "Cornucopia & Guilds, 2E"
    )
    for exp in RENEWED_EXPANSIONS
}


# Stuff that qualities are available for
QUALITIES_AVAILABLE = [
    "village",
    "draw",
    "thinning",
    "gain",
    "attack",
    "altvp",
    "interactivity",
]


SPECIAL_QUAL_TYPES_AVAILABLE = sorted(["attack", "thinning", "gain", "draw", "village"])

PATH_MODULE = Path(__file__).resolve().parent
PATH_MAIN = PATH_MODULE.parent
PATH_CARD_INFO = PATH_MAIN.joinpath("card_info")
PATH_CARD_PICS = PATH_MAIN.joinpath("card_pictures")
PATH_ASSETS = PATH_MAIN.joinpath("assets")

FPATH_RAW_DATA = PATH_CARD_INFO.joinpath("raw_card_data.csv")
FPATH_CARD_DATA = PATH_CARD_INFO.joinpath("good_card_data.csv")
FPATH_RANDOMIZER_CONFIG = PATH_ASSETS.joinpath("randomization_config.ini")
FPATH_RANDOMIZER_CONFIG_DEFAULTS = PATH_ASSETS.joinpath(
    "randomization_config_default.ini"
)

FPATH_KINGDOMS_RECOMMENDED = PATH_ASSETS.joinpath("kingdoms/recommended.yml")
FPATH_KINGDOMS_LAST100 = PATH_ASSETS.joinpath("kingdoms/last_100.yml")


ROTATOR_DICT = {
    "Augurs": ["Herb Gatherer", "Acolyte", "Sorceress", "Sibyl"],
    "Wizards": ["Student", "Conjurer", "Sorcerer", "Lich"],
    "Forts": ["Tent", "Garrison", "Hill Fort", "Stronghold"],
    "Townsfolk": ["Town Crier", "Blacksmith", "Miller", "Elder"],
    "Clashes": ["Battle Plan", "Archer", "Warlord", "Territory"],
    "Odysseys": ["Old Map", "Voyage", "Sunken Treasure", "Distant Shore"],
}

SPLITPILE_DICT = {
    "Catapult/Rocks": 3,
    "Encampment/Plunder": 2,
    "Gladiator/Fortune": 3,
    "Sauna/Avanto": 4,
    "Patrician/Emporium": 2,
    "Settlers/Bustling Village": 2,
}

UNIQUEPILE_LIST = ["Castles", "Knights", "Loot"]
LANDSCAPE_LIST = ["Event", "Project", "Way", "Landmark", "Trait"]
EXTENDED_LANDSCAPE_LIST = LANDSCAPE_LIST + ["Ally", "Prophecy"]
OTHER_OBJ_LIST = ["Hex", "Boon", "State", "Artifact", "Loot"]

CARD_TYPES_AVAILABLE = [
    "Action",
    "Attack",
    "Reaction",
    "Treasure",
    "Victory",
    "Duration",
    "Command",
    "Looter",
    "Gathering",
    "Night",
    "Doom",
    "Fate",
    "Reserve",
    # "Traveller",
    "Liaison",
    "Omen",
    "Shadow",
]


MECHANICS = [
    "Vanilla Effects",  # CSOs with only +Buy/Action/Card/Coin.
    "Reaction",  # CSOs with the reaction type.
    "Throne",  # CSOs behaving similar to Throne Room.
    "Cantrip",  # CSOs that are cantrips, i.e. somehow provide + 1 Card + 1 Action.
    "Peddler",  # CSOs that are Peddlers.
    "Attack defense",  # CSOs enabling to mitigate attacks.
    "Choice",  # CSOs giving a choice of options.
    "Cost Reduction",  # CSOs lowering costs of other cards (including Quarry etc.)
    "Extra Turn",  # CSOs providing extra turns in some way.
    "Coffers",  # CSOs providing Coffers.
    "Overpay",  # CSOs having the Overpay mechanic.
    "Victory Tokens",  # CSOs providing VP tokens.
    "On-trash",  # CSOs that do something on trash.
    "On-gain",  # CSOs that do something on gain.
    "Split Pile",  # Cards part of a split pile (not rotating).
    "Reserve",  # CSOs with the reserve type.
    "Debt",  # CSOs that can give you debt.
    "Back-to-Action",  # CSOs allowing to return to the Action phase.
    "Heirloom",  # CSOs coming with a Heirloom.
    "Doom/Hexes",  # CSOs able to give out Hexes.
    "Fate/Boons",  # CSOs able to give out Boons.
    "Night",  # CSOs having the night type.
    "Horses",  # CSOs providing Horses.
    "Exile",  # CSOs that exile stuff (+ Island).
    "Villagers",  # CSOs providing Villagers.
    "Rotating Split Pile",  # Cards part of rotating split piles.
    "Liaisons/Allies",  # Allies and Liaisons.
    "Loot",  # CSOs providing Loot.
    "Next time",  # CSOs that have the 'Next Time' mechanic.
    "Shadow",  # Shadow cards.
    "Omens/Prophecies",  # Omens and Prophecies.
]
"""Mechanics or themes in the game."""

ALL_CSOS = _init_main_df()
"""All card-shaped objects as a dataframe."""
ALL_CSOS["Final Expansion"] = ALL_CSOS["Expansion"].apply(
    lambda x: EXPANSION_DICT.get(x, x)
)
EXPANSION_LIST: list[str] = [
    "Base, 1E",
    "Base, 2E",
    "Intrigue, 1E",
    "Intrigue, 2E",
    "Seaside, 1E",
    "Seaside, 2E",
    "Alchemy",
    "Prosperity, 1E",
    "Prosperity, 2E",
    "Cornucopia, 1E",
    "Guilds, 1E",
    "Cornucopia & Guilds, 2E",
    "Hinterlands, 1E",
    "Hinterlands, 2E",
    "Dark Ages",
    "Adventures",
    "Empires",
    "Nocturne",
    "Menagerie",
    "Renaissance",
    "Allies",
    "Plunder",
    "Rising Sun",
    "Promo",
]
"""All expansions as a list."""

ATTACK_TYPE_LIST: list[str] = get_unique_entries_of_list_column(
    ALL_CSOS, "attack_types"
)
ALL_CARDS = ALL_CSOS[
    ALL_CSOS["IsInSupply"] & ~ALL_CSOS["IsExtendedLandscape"]
].index.to_list()
"""All supply cards as a big list."""
ALL_LANDSCAPES = ALL_CSOS[(ALL_CSOS["IsExtendedLandscape"])].index.to_list()
"""All landscapes, allies and prophecies in a big list."""


COLOR_PALETTE = ColorPalette()


class EmptyError(Exception):
    pass
