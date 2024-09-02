import pandas as pd
from ...constants import ROTATOR_DICT, SPLITPILE_DICT


def _get_single_parent(card_name: str, card_types: list[str]) -> str:
    for parent, children in ROTATOR_DICT.items():
        if card_name in children:
            return parent
    for parent in SPLITPILE_DICT:
        if card_name in parent.split("/"):
            return parent
    if "Knight" in card_types:
        return "Knights"
    if "Castle" in card_types:
        return "Castles"
    if "Ruins" in card_types:
        return "Ruins"
    return ""


def add_parent_column(df: pd.DataFrame):
    df["ParentPile"] = df.apply(
        lambda x: _get_single_parent(x["Name"], x["Types"]), axis=1
    )
    return df
