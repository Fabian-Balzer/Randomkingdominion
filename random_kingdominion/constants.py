"""Module containing constants, not to be modified!"""
import os
from dataclasses import dataclass
from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import colormaps as cm
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

    def get_bar_level_color(self, level_value: int):
        """Return the color for one of the bar values"""
        assert 0 <= level_value <= 4, f"Wrong level value {level_value}"
        return cm.get_cmap("Greens")(level_value / 4)

    def get_color_for_type(self, type_name: str):
        """Return the color for the given type."""
        return getattr(self, type_name.lower())


def read_dataframe_from_file(fpath: str, eval_lists=False):
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
        "Ally",
        "Way",
        "Liaison",
        "Trait",
        "Action",
        "Treasure",
        "Boon",
    ]
    for type_ in types_of_interest:
        df["Is" + type_] = listlike_contains(df.Types, type_)
    return df


def get_attack_types(all_cards) -> list[str]:
    """Gather the existing AttackTypes from the given dataframe."""
    all_types = reduce(lambda x, y: x + y, all_cards["attack_types"])
    return sorted(list(np.unique(all_types)))


# Expansions with a second edition
RENEWED_EXPANSIONS = ["Base", "Intrigue", "Seaside", "Hinterlands", "Prosperity"]


# Stuff that qualities are available for
QUALITIES_AVAILABLE = sorted(
    [
        "attack",
        "draw",
        "interactivity",
        "thinning",
        "village",
        "altvp",
        "gain",
    ]
)

SPECIAL_TYPES_AVAILABLE = sorted(["attack", "thinning", "gain"])

PATH_MODULE = Path(__file__).resolve().parent
PATH_MAIN = PATH_MODULE.parent
PATH_CARD_INFO = PATH_MAIN.joinpath("card_info")
PATH_CARD_PICS = PATH_MAIN.joinpath("card_pictures")
PATH_ASSETS = PATH_MAIN.joinpath("assets")

FPATH_RAW_DATA = PATH_CARD_INFO.joinpath("raw_card_data.csv")
FPATH_CARD_DATA = PATH_CARD_INFO.joinpath("good_card_data.csv")
FPATH_RANDOMIZER_CONFIG = PATH_ASSETS.joinpath("randomization_config.ini")

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
OTHER_OBJ_LIST = ["Hex", "Boon", "State", "Artifact", "Ally", "Loot"]

ALL_CSOS = _init_main_df()
EXPANSION_LIST: list[str] = list(set(ALL_CSOS["Expansion"]))
ATTACK_TYPE_LIST: list[str] = get_unique_entries_of_list_column(
    ALL_CSOS, "attack_types"
)


COLOR_PALETTE = ColorPalette()


class EmptyError(Exception):
    pass
