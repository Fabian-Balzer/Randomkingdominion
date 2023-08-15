"""Module containing constants, not to be modified!"""
from functools import reduce
from pathlib import Path

import numpy as np

from .utils import read_dataframe_from_file


def get_attack_types(all_cards) -> list[str]:
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


ALL_CARDS = read_dataframe_from_file(FPATH_CARD_DATA, eval_lists=True)
EXPANSIONS_LIST = list(set(ALL_CARDS["Expansion"]))
ATTACK_TYPE_LIST = get_attack_types(ALL_CARDS)


class EmptyError(Exception):
    pass
