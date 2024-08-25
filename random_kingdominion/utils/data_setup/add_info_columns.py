import json
from collections import defaultdict
from functools import reduce

import numpy as np
import pandas as pd

from ...constants import (
    COFFER_GIVERS,
    DEBT_INDUCERS,
    EXTENDED_LANDSCAPE_LIST,
    LANDSCAPE_LIST,
    OTHER_OBJ_LIST,
    PATH_CARD_INFO,
    QUALITIES_AVAILABLE,
    ROTATOR_DICT,
    SPLIT_CARD_TYPES,
    SPLITPILE_CARDS,
    SPLITPILE_DICT,
)
from ...utils.utils import ask_file_overwrite


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


def test_extended_landscape(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    series = df["Types"].apply(
        lambda x: do_lists_have_common(x, EXTENDED_LANDSCAPE_LIST)
    )
    return series


def test_other(df):
    """Tests whether the given object is a Hex, Boon, State or Artifact"""
    series = df["Types"].apply(lambda x: do_lists_have_common(x, OTHER_OBJ_LIST))
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
    ]
    series = (
        (
            df["Types"].apply(lambda x: do_lists_have_common(x, typelist))
            & df["Name"].apply(lambda x: x not in still_include)
        )
        | df["Name"].apply(lambda x: x in namelist)
        | df["IsExtendedLandscape"]
        | df["IsOtherThing"]
    )
    return ~series


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
    return ""


def add_parent_column(df: pd.DataFrame):
    df["ParentPile"] = df.apply(
        lambda x: _get_single_parent(x["Name"], x["Types"]), axis=1
    )
    return df


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
        if pilename == "Wizards":
            types += " - Liaison"
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
            "Split_Piles/" + pile["Name"].replace("/", "_").replace(" ", "_") + ".jpg"
        )
        pile_dict = {key: [val] for key, val in pile.items()}
        df = pd.concat([df, pd.DataFrame(pile_dict)])
    return df


def determine_amount(card: pd.Series) -> str:
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
    isprize = ("Prize" in card.Types) or ("Reward" in card.Types)
    isProphecy = "Prophecy" in card.Types
    iszombie = "Zombie" in card.Name
    if any(
        [
            card.IsExtendedLandscape,
            card.IsOtherThing,
            isknight,
            isartifact,
            isally,
            isprize,
            iszombie,
            isProphecy,
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


def _determine_extra_components(cso: pd.Series) -> list[str]:
    """Determines which CSOs are associated with the given card."""
    extra_components = []
    cso_types = cso["Types"]
    name = cso["Name"]
    cost = cso["Cost"] if cso["Cost"] is not np.nan else ""
    # Artifacts:
    arifact_dict = {
        "Border Guard": ["Horn", "Lantern"],
        "Treasurer": ["Key"],
        "Swashbuckler": ["Treasure Chest"],
        "Flag Bearer": ["Flag"],
    }
    if name in arifact_dict:
        extra_components += arifact_dict[name]
    # Nocturne stuff:
    nocturne_dict = {
        "Misery": ["Miserable", "Twice Miserable"],
        "Delusion": ["Deluded"],
        "Envy": ["Envious"],
        "Necromancer": ["Zombie Apprentice", "Zombie Mason", "Zombie Spy"],
        "Exorcist": ["Will-o'-Wisp", "Imp", "Ghost"],
        "Devil's Workshop": ["Imp"],
        "Tormentor": ["Imp"],
        "Vampire": ["Bat"],
        "Leprechaun": ["Wish"],
        "The Swamp's Gift": ["Will-o'-Wisp"],
        # Heirlooms:
        "Secret Cave": ["Magic Lamp", "Wish"],
        "Magic Lamp": ["Wish"],
        "Fool": ["Lost in the Woods", "Lucky Coin"],
        "Pixie": ["Goat"],
        "Cemetery": ["Haunted Mirror", "Ghost"],
        "Haunted Mirror": ["Ghost"],
        "Shepherd": ["Pasture"],
        "Pooka": ["Cursed Gold"],
        "Tracker": ["Pouch"],
    }
    if name in nocturne_dict:
        extra_components += nocturne_dict[name]
    if "Fate" in cso_types:
        extra_components += ["Boons", "Will-o'-Wisp"]
    if "Doom" in cso_types:
        extra_components += [
            "Hexes",
            "Miserable",
            "Twice Miserable",
            "Deluded",
            "Envious",
        ]
    # Mats and tokens
    if "Liaison" in cso_types or "Ally" in cso_types:
        extra_components += ["Favor tokens", "Favor mats"]
    if "Omen" in cso_types or "Prophecy" in cso_types:
        extra_components.append("Sun tokens")
    if "D" in cost or name in DEBT_INDUCERS:
        extra_components.append("Debt tokens")
    if name in COFFER_GIVERS:
        extra_components += ["Coffer tokens", "Coffer mats"]
    if "Villagers" in cso["village_types"] or name in [
        "Silk Merchant",
        "Patron",
        "Sculptor",
    ]:
        extra_components += ["Villager tokens", "Villager mats"]
    if "VP Chips" in cso["altvp_types"]:
        extra_components += ["VP tokens", "VP mats"]
    if "Reserve" in cso_types:
        extra_components.append("Reserve Mat")
    if (
        "Exile" in cso["thinning_types"]
        and name not in ["Island", "Miser"]
        or name
        in [
            "Camel Train",
            "Stockpile",
            "Cardinal",
            "Coven",
            "Gatekeeper",
            "Enclave",
            "Transport",
            "Invest",
            "Way of the Camel",
            "Way of the Worm",
        ]
    ):
        extra_components.append("Exile mats")
    if "Project" in cso_types:
        extra_components.append("Project cubes")
    # Extra piles that are added:
    if "Horses" in cso["gain_types"] or name in ["Ride", "Bargain"]:
        extra_components.append("Horses")
    if "Loot" in cso["gain_types"]:
        extra_components.append("Loots")
    if "Looter" in cso_types:
        extra_components.append("Ruins")
    if "P" in cost:
        extra_components.append("Potion")
    # Adventure tokens and other adventure stuff
    if name in ["Ranger", "Pilgrimage", "Giant"]:
        extra_components.append("Journey tokens")
    if name in ["Ball", "Bridge Troll"]:
        extra_components.append("- Coin tokens")
    if name in ["Relic", "Borrow", "Raid"]:
        extra_components.append("- Card tokens")
    token_dict = {
        "Lost Arts": "+ Action tokens",
        "Training": "+ Coin tokens",
        "Pathfinding": "+ Card tokens",
        "Seaway": "+ Buy tokens",
        "Plan": "Trashing tokens",
        "Ferry": "-$2 tokens",
        "Inheritance": "Estate tokens",
    }
    if name in token_dict:
        extra_components.append(token_dict[name])
    if name == "Page":
        extra_components += ["Page line (Treasure Hunter, Warrior, Hero, Champion)"]
    if name == "Peasant":
        extra_components += ["Peasant line (Soldier, Fugitive, Disciple, Teacher)"]
    if name in ["Peasant", "Teacher"]:
        extra_components += [
            "+ Action tokens",
            "+ Buy tokens",
            "+ Coin tokens",
            "+ Card tokens",
        ]
    # Random Seaside, Prosperity, Cornucopia and Dark Ages stuff:
    special = {
        "Island": ["Island mat"],
        "Native Village": ["Native Village mat"],
        "Pirate Ship": ["Pirate Ship mat + tokens"],
        "Embargo": ["Embargo tokens"],
        "Trade Route": ["Trade Route tokens"],
        "Tournament": ["Prizes"],
        "Joust": ["Rewards"],
        "Young Witch": ["Bane indicator"],
        "Urchin": ["Mercenary"],
        "Hermit": ["Madman"],
        "Marauder": ["Spoils"],
        "Pillage": ["Spoils"],
        "Bandit Camp": ["Spoils"],
        "Black Market": ["Black Market deck"],
        "Forts": ["Garrison tokens"],
        "Garrison": ["Garrison tokens"],
    }
    if name in special:
        extra_components += special[name]
    # Trashers that have no trashing quality but might populate the trash:
    other_trashers = [
        "Feast",
        "Lurker",
        "Mining Village",
        "Embargo",
        "Horn of Plenty",
        "Pillage",
        "Procession",
        "Engineer",
        "Ritual",
        "Gladiator",
        "Gladiator/Fortune",
        "Salt the Earth",
        "Farmers' Market",
        "Castles",
        "Changeling",
        "Secret Cave",
        "Tragic Hero",
        "Magic Lamp",
        "Locusts",
        "War",
        "Acting Troupe",
        "Old Witch",
        "Siren",
        "Search",
        "Cabin Boy",
        "Spell Scroll",
        "Peril",
        "Black Market",
    ]
    if (
        "Exile" not in cso["thinning_types"]
        and cso["thinning_quality"] > 0
        or name in other_trashers
        or "Trashing" in cso["attack_types"]
        or "Fate" in cso_types
        or "Doom" in cso_types
        or "Loots" in extra_components
    ):
        extra_components.append("Trash mat")
    return sorted(extra_components)


def add_extra_components(df: pd.DataFrame) -> pd.DataFrame:
    """Adds which CSOs and extra components are associated with each card."""
    df["Extra Components"] = df.apply(_determine_extra_components, axis=1)
    df["HasExtraComponents"] = df["Extra Components"].apply(lambda x: len(x) > 0)
    return df


def add_quality_info_columns(df):
    df = add_parent_column(df)
    df = add_bool_columns(df)
    # Set up the default values:
    info_types = {f"{qual}_quality": 0 for qual in QUALITIES_AVAILABLE}
    info_types |= {
        f"{qual}_types": [] for qual in QUALITIES_AVAILABLE if qual != "interactivity"
    }
    for info_type, default_value in info_types.items():
        df[info_type] = df["Name"].apply(
            lambda name: get_specific_info(name, info_type, default_value)
        )
    df["CardAmount"] = df.apply(determine_amount, axis=1)
    link_base = "https://wiki.dominionstrategy.com/index.php/"
    df["WikiLink"] = df["Name"].str.replace(" ", "_").apply(lambda x: link_base + x)
    df = add_extra_components(df)
    return df
