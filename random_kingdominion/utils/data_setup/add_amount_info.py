from functools import reduce

import pandas as pd

from ...constants import (
    ROTATOR_DICT,
    SPLITPILE_DICT,
)


def _determine_amount(cso: pd.Series) -> str:
    if "Loot" in cso.Types:
        return "2"
    if "State" in cso.Types:
        if cso.Name == "Lost in the Woods":
            return "1"
        else:
            return "2*"
    iscastle = "Castle" in cso.Types and not cso.Name == "Castles"
    if iscastle:
        if cso.Name in [
            "Humble Castle",
            "Small Castle",
            "Opulent Castle",
            "King's Castle",
        ]:
            return "1*"
        else:
            return "1"
    isknight = "Knight" in cso.Types and not cso.Name == "Knights"
    isartifact = "Artifact" in cso.Types
    isally = "Ally" in cso.Types
    isprize = ("Prize" in cso.Types) or ("Reward" in cso.Types)
    isProphecy = "Prophecy" in cso.Types
    iszombie = "Zombie" in cso.Name
    if any(
        [
            cso.IsExtendedLandscape,
            cso.IsOtherThing,
            isknight,
            isartifact,
            isally,
            isprize,
            iszombie,
            isProphecy,
        ]
    ):
        return "1"
    if "Ruin" in cso.Types:
        return "?"
    if "Heirloom" in cso.Types:
        return "2*"
    if "Shelter" in cso.Types:
        return "2*"
    special_dict = {
        "Copper": 46,
        "Silver": 40,
        "Gold": 30,
        "Curse": "10*",
        "Platinum": 12,
        "Ruins": "10*",
        "Horse": 30,
        "Potion": 16,
        "Teacher": 5,
        "Peasant": "10*",
        "Champion": 5,
        "Will-o'-Wisp": 12,
        "Wish": 12,
        "Imp": 12,
        "Ghost": 5,
        "Rats": 20,
        "Ports": 12,
    }
    if cso.Name in special_dict:
        return str(special_dict[cso.Name])
    if "Traveller" in cso.Types:
        return "5"
    if cso.Name in ROTATOR_DICT:
        return "4x4"
    if cso.Name in reduce(lambda x, y: x + y, ROTATOR_DICT.values()):
        return "4"
    splitpile_cards = reduce(
        lambda x, y: x + y, [name.split("/") for name in SPLITPILE_DICT.keys()]
    )
    if cso.Name in splitpile_cards:
        return "5"
    if cso.Name in SPLITPILE_DICT:
        return "2x5"
    if cso.Name in reduce(lambda x, y: x + y, ROTATOR_DICT.values()):
        return "4"
    if "Victory" in cso.Types:
        return "8*"
    return "10"


def add_amount_info(df: pd.DataFrame) -> pd.DataFrame:
    df["Amount"] = df.apply(_determine_amount, axis=1)
    return df
