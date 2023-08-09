"""Module containing constants, not to be modified!"""
import os
from pathlib import Path

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
    ]
)

PATH_MODULE = Path(__file__).resolve().parent
PATH_MAIN = PATH_MODULE.parent
PATH_CARD_INFO = PATH_MAIN.joinpath("card_info")
PATH_CARD_PICS = PATH_MAIN.joinpath("card_pictures")
PATH_ASSETS = PATH_MAIN.joinpath("assets")

FPATH_RAW_DATA = PATH_CARD_INFO.joinpath("raw_card_data.csv")
FPATH_CARD_DATA = PATH_CARD_INFO.joinpath("good_card_data.csv")
FPATH_RANDOMIZER_CONFIG = PATH_ASSETS.joinpath("randomization_config.ini")


class EmptyError(Exception):
    pass
