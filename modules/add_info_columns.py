import json
from collections import defaultdict

import pandas as pd


def do_lists_have_common(l1, l2):
    """Returns a bool wether two lists share at least one common element."""
    return len([y for y in l1 if y in l2]) > 0


def test_landscape(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    print(df["Types"])
    landscapelist = ["Event", "Project", "Way", "Landmark"]
    series = df["Types"].apply(
        lambda x: do_lists_have_common(x, landscapelist))
    return series


def test_other(df):
    """Tests whether the given object is a Hex, Boon, State or Artifact"""
    otherlist = ["Hex", "Boon", "State", "Artifact", "Ally"]
    series = df["Types"].apply(lambda x: do_lists_have_common(x, otherlist))
    return series


def test_in_supply(df):
    """Creates a mask of all cards that are not kingdom cards.
    These things are:
        spirits, heirlooms, prizes, Spoils, Ruins, Shelters, Knights,
        Mercenary, Bat, Wish, Horse, Plunder, Bustling Village, Rocks,
        Travellers (except page and peasant), Zombies, Allies, Split Piles,
        Rotating split piles"""
    typelist = ["Traveller", "Spirit", "Heirloom", "Prize", "Ruins", "Zombie",
                "Knight", "Shelter", "Castle", "Augur", "Odyssey", "Townsfolk", "Wizard", "Clash", "Fort", "Ally"]
    namelist = ["Bat", "Wish", "Horse", "Spoils", "Plunder", "Bustling Village",
                "Rocks", "Mercenary", "Madman", "Colony", "Platinum", "Teacher",
                "Champion", "Estate", "Duchy", "Province", "Copper", "Curse",
                "Silver", "Gold", "Potion", "Fortune", "Rocks", "Patrician",
                "Catapult", "Encampment", "Emporium", "Bustling Village",
                "Settlers", "Gladiator", "Sauna", "Avanto"]
    still_include = ["Page", "Peasant", "Augurs", "Odysseys", "Townsfolk", "Wizards", "Clashes", "Forts"]
    series = ((df["Types"].apply(lambda x: do_lists_have_common(x, typelist)) &
              df["Name"].apply(lambda x: x not in still_include)) |
              df["Name"].apply(lambda x: x in namelist) |
              df["IsLandscape"] |
              df["IsOtherThing"])
    return ~series


def add_bool_columns(df):
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
        with open(f"card_info/specifics/{info_type}.txt", "r") as f:
            data = json.load(f)
            draw_dict = defaultdict(lambda: default_value, data)
    except FileNotFoundError:
        return default_value
    return draw_dict[cardname]


def add_split_piles(df):
    pathbase = "card_pictures/Split_Piles/"
    splitpile_dict = {"Castles": {"Name": "Castles",
                                  "Expansion": "Empires",
                                  "Types": "Victory - Castle",
                                  "Cost": "$3*",
                                  "Text": 'Sort the Castle pile by cost, putting the more expensive Castles on the bottom. For a 2-player game, use only one of each Castle. Only the top card of the pile can be gained or bought.',
                                  "IsLandscape": False,
                                  "IsOtherThing": False,
                                  "IsInSupply": True
                                  },
                      "Knights": {"Name": "Knights",
                                  "Expansion": "Dark Ages",
                                  "Types": "Action - Attack - Knights",
                                  "Cost": "$5*",
                                  "Text": "Shuffle the Knights pile before each game with it. Keep it face down except for the top card, which is the only one that can be bought or gained.",
                                  "IsLandscape": False,
                                  "IsOtherThing": False,
                                  "IsInSupply": True,
                                  }, }
    for pile, cost in {"Catapult/Rocks": 3, "Encampment/Plunder": 2, "Gladiator/Fortune": 3, "Sauna/Avanto": 4, "Patrician/Emporium": 2, "Settlers/Bustling Village": 2}.items():
        first, second = pile.split("/")
        types = "Action - Attack" if pile == "Catapult/Rocks" else "Action"
        splitpile_dict[pile] = {"Name": pile,
                                "Expansion": "Empires",
                                "Types": types,
                                "Cost": f"${cost}",
                                "Text": f"This pile starts the game with 5 copies of {first} on top, then 5 copies of {second}. Only the top card of the pile can be gained or bought.",
                                "IsLandscape": False,
                                "IsOtherThing": False,
                                "IsInSupply": True
                                }
    for pilename, cards in {"Augurs": ["Herb Gatherer", "Acolyte", "Sorceress", "Sybil"], "Wizards": ["Student", "Conjurer", "Sorcerer", "Lich"], "Forts": ["Tent", "Garrison", "Hill Fort", "Stronghold"], "Townsfolk": ["Town Crier", "Blacksmith", "Miller", "Elder"], "Clashes": ["Battle Plan", "Archer", "Warlord", "Territory"], "Odysseys": ["Old Map", "Voyage", "Sunken Treasure", "Distant Shore"]}.items():
        type_dict = {"Augurs": "Augur", "Wizards": "Wizard",
                     "Odysseys": "Odyssey", "Clashes": "Clash", "Townsfolk": "Townsfolk", "Forts": "Fort"}
        types = f"Action - {type_dict[pilename]}"
        text = f"This pile starts the game with 4 copies each of {', '.join(cards[:3])}, and {cards[3]}, in that order. Only the top card can be gained or bought.",
        cost = df[df["Name"] == cards[0]]["Cost"].to_string(index=False)
        print(cost)
        splitpile_dict[pilename] = {"Name": pilename,
                                    "Expansion": "Allies",
                                    "Types": types,
                                    "Cost": cost,
                                    "Text": text,
                                    "IsLandscape": False,
                                    "IsOtherThing": False,
                                    "IsInSupply": True
                                    }

    for pile, cost in {"Catapult/Rocks": 3, "Encampment/Plunder": 2, "Gladiator/Fortune": 3, "Sauna/Avanto": 4, "Patrician/Emporium": 2, "Settlers/Bustling Village": 2}.items():
        first, second = pile.split("/")
        types = "Action - Attack" if pile == "Catapult/Rocks" else "Action"
        expansion = "Empires" if not "Sauna" in pile else "Promo"
        splitpile_dict[pile] = {"Name": pile,
                                "Expansion": expansion,
                                "Types": types,
                                "Cost": f"${cost}",
                                "Text": f"This pile starts the game with 5 copies of {first} on top, then 5 copies of {second}. Only the top card of the pile can be gained or bought.",
                                "IsLandscape": False,
                                "IsOtherThing": False,
                                "IsInSupply": True
                                }
    for pile in splitpile_dict.values():
        pile["ImagePath"] = pathbase + \
            pile["Name"].replace("/", "_").replace(" ", "_") + ".jpg"
        pile_dict = {key: [val] for key, val in pile.items()}
        pile_line = pd.DataFrame(pile_dict)
        df = df.append(pile_line, sort=False)
    return df


def add_info_columns(df):
    df = add_bool_columns(df)
    info_types = {"DrawQuality": 0, "AttackType": [""], "VillageQuality": 0,
                  "AltVPStrength": 0, "GainQuality": 0,
                  "PlusBuys": 0, "CoinValue": 0, "TrashingQuality": 0}
    for info_type, default_value in info_types.items():
        df[info_type] = df["Name"].apply(
            lambda name: get_specific_info(name, info_type, default_value))
    return df
