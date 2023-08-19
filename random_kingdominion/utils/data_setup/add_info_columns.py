import json
from collections import defaultdict
from functools import reduce

import pandas as pd

from random_kingdominion.constants import (LANDSCAPE_LIST,
                                                 OTHER_OBJ_LIST,
                                                 PATH_CARD_INFO,
                                                 QUALITIES_AVAILABLE,
                                                 ROTATOR_DICT,
                                                 SPECIAL_TYPES_AVAILABLE,
                                                 SPLITPILE_DICT)
from random_kingdominion.utils.utils import ask_file_overwrite


def write_dict_to_json_nicely(
    new_dict: dict, filepath: str, always_overwrite=False, sort=True
):
    if always_overwrite or ask_file_overwrite(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(new_dict, f, sort_keys=sort, separators=(",\n", ": "))


def read_json_dict_from_file(fpath: str) -> dict:
    with open(fpath, "r", encoding="utf-8") as f:
        old_dict = json.load(f)
    return old_dict


def do_lists_have_common(l1, l2):
    """Returns a bool wether two lists share at least one common element."""
    return len([y for y in l1 if y in l2]) > 0


def test_landscape(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    series = df["Types"].apply(lambda x: do_lists_have_common(x, LANDSCAPE_LIST))
    return series


def test_other(df):
    """Tests whether the given object is a Hex, Boon, State or Artifact"""
    series = df["Types"].apply(lambda x: do_lists_have_common(x, OTHER_OBJ_LIST))
    return series


def test_in_supply(df):
    """Creates a mask of all cards that are not kingdom cards.
    These things are:
        spirits, heirlooms, prizes, Spoils, Ruins, Shelters, Knights,
        Mercenary, Bat, Wish, Horse, Plunder, Bustling Village, Rocks,
        Travellers (except page and peasant), Zombies, Allies, Split Piles,
        Rotating split piles"""
    typelist = [
        "Traveller",
        "Spirit",
        "Heirloom",
        "Prize",
        "Ruins",
        "Zombie",
        "Knight",
        "Shelter",
        "Castle",
        "Augur",
        "Odyssey",
        "Townsfolk",
        "Wizard",
        "Clash",
        "Fort",
        "Ally",
    ]
    namelist = [
        "Bat",
        "Wish",
        "Horse",
        "Spoils",
        "Plunder",
        "Bustling Village",
        "Rocks",
        "Mercenary",
        "Madman",
        "Colony",
        "Platinum",
        "Teacher",
        "Champion",
        "Estate",
        "Duchy",
        "Province",
        "Copper",
        "Curse",
        "Silver",
        "Gold",
        "Potion",
        "Fortune",
        "Rocks",
        "Patrician",
        "Catapult",
        "Encampment",
        "Emporium",
        "Bustling Village",
        "Settlers",
        "Gladiator",
        "Sauna",
        "Avanto",
    ]
    still_include = [
        "Page",
        "Peasant",
        "Augurs",
        "Odysseys",
        "Townsfolk",
        "Wizards",
        "Clashes",
        "Forts",
    ]
    series = (
        (
            df["Types"].apply(lambda x: do_lists_have_common(x, typelist))
            & df["Name"].apply(lambda x: x not in still_include)
        )
        | df["Name"].apply(lambda x: x in namelist)
        | df["IsLandscape"]
        | df["IsOtherThing"]
    )
    return ~series


def add_bool_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Adds some boolean columns and saves the types as a list"""
    df["Types"] = df["Types"].str.split(" - ")
    df["IsLandscape"] = test_landscape(df)
    df["IsOtherThing"] = test_other(df)
    df["IsInSupply"] = test_in_supply(df)
    # df["IsCantrip"] = test_cantrip(df)
    return df


def get_specific_info(cardname, info_type, default_value):
    """Retrieves the info of info_type stored in the specifics folder."""
    try:
        fpath = PATH_CARD_INFO.joinpath(f"specifics/{info_type}.json")
        with fpath.open("r", encoding="utf-8") as f:
            data = json.load(f)
            quality_dict = defaultdict(lambda: default_value, data)
    except FileNotFoundError:
        print(f"Couldn't find the {info_type} file, skipped adding that info.")
        return default_value
    return quality_dict[cardname]


def add_split_piles(df):
    pathbase = "card_pictures/Split_Piles/"
    splitpile_dict = {
        "Castles": {
            "Name": "Castles",
            "Expansion": "Empires",
            "Types": "Victory - Castle",
            "Cost": "$3*",
            "Text": "Sort the Castle pile by cost, putting the more expensive Castles on the bottom. For a 2-player game, use only one of each Castle. Only the top card of the pile can be gained or bought.",
            "IsLandscape": False,
            "IsOtherThing": False,
            "IsInSupply": True,
        },
        "Knights": {
            "Name": "Knights",
            "Expansion": "Dark Ages",
            "Types": "Action - Attack - Knights",
            "Cost": "$5*",
            "Text": "Shuffle the Knights pile before each game with it. Keep it face down except for the top card, which is the only one that can be bought or gained.",
            "IsLandscape": False,
            "IsOtherThing": False,
            "IsInSupply": True,
        },
    }
    for pilename, cards in ROTATOR_DICT.items():
        types = f"Action - {pilename.strip('es')}"
        text = (
            f"This pile starts the game with 4 copies each of {', '.join(cards[:3])}, and {cards[3]}, in that order. Only the top card can be gained or bought.",
        )
        cost = df[df["Name"] == cards[0]]["Cost"].to_string(index=False)
        splitpile_dict[pilename] = {
            "Name": pilename,
            "Expansion": "Allies",
            "Types": types,
            "Cost": cost,
            "Text": text,
            "IsLandscape": False,
            "IsOtherThing": False,
            "IsInSupply": True,
        }
    for pile, cost in SPLITPILE_DICT.items():
        first, second = pile.split("/")
        types = "Action - Attack" if pile == "Catapult/Rocks" else "Action"
        expansion = "Empires" if not "Sauna" in pile else "Promo"
        splitpile_dict[pile] = {
            "Name": pile,
            "Expansion": expansion,
            "Types": types,
            "Cost": f"${cost}",
            "Text": f"This pile starts the game with 5 copies of {first} on top, then 5 copies of {second}. Only the top card of the pile can be gained or bought.",
            "IsLandscape": False,
            "IsOtherThing": False,
            "IsInSupply": True,
        }
    for pile in splitpile_dict.values():
        pile["ImagePath"] = (
            pathbase + pile["Name"].replace("/", "_").replace(" ", "_") + ".jpg"
        )
        pile_dict = {key: [val] for key, val in pile.items()}
        df = pd.concat([df, pd.DataFrame(pile_dict)])
    return df


def determine_amount(card: pd.Series):
    if "Loot" in card.Types:
        return "2"
    if "State" in card.Types:
        if card.Name == "Lost in the Woods":
            return "1"
        else:
            return "2*"
    iscastle = "Castle" in card.Types and not card.Name == "Castles"
    if iscastle:
        if card.Name in [
            "Humble Castle",
            "Small Castle",
            "Opulent Castle",
            "King's Castle",
        ]:
            return "1*"
        else:
            return "1"
    isknight = "Knight" in card.Types and not card.Name == "Knights"
    isartifact = "Artifact" in card.Types
    isally = "Ally" in card.Types
    isprize = "Prize" in card.Types
    iszombie = "Zombie" in card.Name
    if any(
        [
            card.IsLandscape,
            card.IsOtherThing,
            isknight,
            isartifact,
            isally,
            isprize,
            iszombie,
        ]
    ):
        return "1"
    if "Ruin" in card.Types:
        return "?"
    if "Heirloom" in card.Types:
        return "2*"
    if "Shelter" in card.Types:
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
    if card.Name in special_dict:
        return str(special_dict[card.Name])
    if "Traveller" in card.Types:
        return "5"
    if card.Name in ROTATOR_DICT:
        return "4x4"
    if card.Name in reduce(lambda x, y: x + y, ROTATOR_DICT.values()):
        return "4"
    splitpile_cards = reduce(
        lambda x, y: x + y, [name.split("/") for name in SPLITPILE_DICT.keys()]
    )
    if card.Name in splitpile_cards:
        return "5"
    if card.Name in SPLITPILE_DICT:
        return "2x5"
    if card.Name in reduce(lambda x, y: x + y, ROTATOR_DICT.values()):
        return "4"
    if "Victory" in card.Types:
        return "8*"
    return "10"


def add_info_columns(df):
    df = add_bool_columns(df)
    # Set up the default values:
    info_types = {f"{qual}_quality": 0 for qual in QUALITIES_AVAILABLE}
    info_types |= {f"{types}_types": [] for types in SPECIAL_TYPES_AVAILABLE}
    for info_type, default_value in info_types.items():
        df[info_type] = df["Name"].apply(
            lambda name: get_specific_info(name, info_type, default_value)
        )
    df["CardAmount"] = df.apply(determine_amount, axis=1)
    return df
