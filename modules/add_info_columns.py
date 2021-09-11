import json
from collections import defaultdict
import pandas as pd


def do_lists_have_common(l1, l2):
    """Returns a bool wether two lists share at least one common element."""
    return len([y for y in l1 if y in l2]) > 0


def test_landscape(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    landscapelist = ["Event", "Project", "Way", "Landmark"]
    series = df["Types"].apply(lambda x: do_lists_have_common(x, landscapelist))
    return series


def test_other(df):
    """Tests whether the given object is a Hex, Boon, State or Artifact"""
    otherlist = ["Hex", "Boon", "State", "Artifact"]
    series = df["Types"].apply(lambda x: do_lists_have_common(x, otherlist))
    return series


def test_in_supply(df):
    """Creates a mask of all cards that are not kingdom cards.
    These things are:
        spirits, heirlooms, prizes, Spoils, Ruins, Shelters, Knights,
        Mercenary, Bat, Wish, Horse, Plunder, Bustling Village, Rocks,
        Travellers (except page and peasant), Zombies"""
    typelist = ["Traveller", "Spirit", "Heirloom", "Prize", "Ruins", "Zombie",
                "Knight", "Shelter", "Madman", "Castle"]
    namelist = ["Bat", "Wish", "Horse", "Spoils", "Plunder", "Bustling Village",
                "Rocks", "Mercenary", "Madman", "Colony", "Platinum", "Teacher",
                "Champion", "Estate", "Duchy", "Province", "Copper", "Curse",
                "Silver", "Gold"]
    series = ((df["Types"].apply(lambda x: do_lists_have_common(x, typelist)) &
              df["Name"].apply(lambda x: x not in ["Page", "Peasant"])) |
              df["Name"].apply(lambda x: x in namelist) |
              df["IsLandscape"] |
              df["IsOtherThing"])
    return ~series


def get_draw_quality(cardname):
    """Pulls the draw quality of a card from an external dictionary.
    The draw quality is a number x with 0 <= x <= 10, where x = 2*n for
    n being the number of cards the card draws.
    Cards with no draw have x = 0, cards with weird draw were judged by my gut feeling,
    i. e. Scrying Pool has x = 10 while Courtyard has x = 5."""
    with open("card_info/draw_qualities.txt", "r") as f:
        data = json.load(f)
        draw_dict = defaultdict(lambda: 0, data)
    return draw_dict[cardname]


def get_attack_type(cardname):
    """Pulls the attack type of an attack of a card from an external dictionary."""
    with open("card_info/attack_types.txt", "r") as f:
        data = json.load(f)
        draw_dict = defaultdict(lambda: [], data)
    return draw_dict[cardname]


def add_bool_columns(df):
    """Adds some boolean columns and saves the types as a list"""
    df["Types"] = df["Types"].str.split(" - ")
    df["IsLandscape"] = test_landscape(df)
    df["IsOtherThing"] = test_other(df)
    df["IsInSupply"] = test_in_supply(df)
    df["DrawQuality"] = df["Name"].apply(get_draw_quality)
    df["AttackType"] = df["Name"].apply(get_attack_type)
    # df["IsAltVP"]
    # df["IsCantrip"]
    # df["IsWorkshop"]
    # df["IsVillage"]
    # df["IsTrasher"]
    # df["IsPeddler"]
    # df["HasPlusBuy"]
    # df["IsSifter"]
    return df


def add_knight_pile(df):
    knighttext = ('Shuffle the Knights pile before each game with it. '
    "Keep it face down except for the top card, which is the only one "
    'that can be bought or gained.')
    keys = ["Name", "Set", "Types", "Cost", "Text", "IsLandscape", "IsOtherThing",
            "IsInSupply"]
    values = ["Knights", "Dark Ages", ["Action", "Attack", "Knights"],
              "$5* ", knighttext, False, False, True]
    values = [[val] for val in values]
    my_dict = dict(zip(keys, values))
    knight_line = pd.DataFrame(my_dict)
    df = df.append(knight_line, sort=False)
    return df


def add_castle_pile(df):
    castletext = ('Sort the Castle pile by cost, putting the more '
        'expensive Castles on the bottom. For a 2-player game, '
        'use only one of each Castle. Only the top card of the pile can be gained or bought.')
    keys = ["Name", "Set", "Types", "Cost", "Text", "IsLandscape", "IsOtherThing",
            "IsInSupply"]
    values = ["Castles", "Empires", ["Victory", "Castle"],
              "$3* ", castletext, False, False, True]
    values = [[val] for val in values]
    my_dict = dict(zip(keys, values))
    castle_line = pd.DataFrame(my_dict)
    df = df.append(castle_line, sort=False)
    return df


def add_info_columns(df):
    df.pipe(add_bool_columns)
    df = add_knight_pile(df)
    df = add_castle_pile(df)
    return df