"""Add card levels from dominion.games to the card database."""

import json

import pandas as pd

from ...constants import FPATH_CARD_DATA
from ...logger import LOGGER
from .. import sanitize_cso_name


def add_card_levels(df: pd.DataFrame) -> pd.DataFrame:
    """Add card levels from dominion.games to the card database."""
    p = FPATH_CARD_DATA.parent / "card_pool_levels.json"
    with open(p, "r", encoding="utf-8") as f:
        card_pool_levels = json.load(f)
    level_dict = {
        sanitize_cso_name(card): level
        for level, cards in card_pool_levels.items()
        for card in cards
    }
    corrections = {
        "augur_pile": "augurs",
        "clash_pile": "clashes",
        "fort_pile": "forts",
        "odyssey_pile": "odysseys",
        "townsfolk_pile": "townsfolk",
        "wizard_pile": "wizards",
    }
    level_dict = {
        corrections.get(name, name): level for name, level in level_dict.items()
    }
    df["tmp_index"] = df["Name"].map(sanitize_cso_name)
    unknown_names = [
        name for name in level_dict if name not in df["tmp_index"].tolist()
    ]
    if unknown_names:
        LOGGER.warning(f"Unknown names in level_dict: {unknown_names}")
    df["card_level"] = df["tmp_index"].map(level_dict)
    df["card_level"] = df["card_level"].fillna(0).astype(int)

    df = df.drop(columns=["tmp_index"])
    return df
