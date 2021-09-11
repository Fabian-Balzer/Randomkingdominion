# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 10:09:11 2021

@author: Fabian Balzer

Code to read the table data and save it as CSV
"""



from bs4 import BeautifulSoup
import requests
import os
import os.path
import pandas as pd
from collections import defaultdict
from collections import OrderedDict
import json


def fix_cost_and_vp(doc):
    """As cost and victory points are hidden in images, the parser has a hard time
    reading it. Thus, we modify it a little to only have the alt value."""
    pics = doc.find_all('span', {"class": "coin-icon"})
    for pic in pics:
        alt_price = pic.find("img")["alt"]
        pic.string = alt_price
    return pics


def retrieve_data():
    """Reads the data from the wiki page and returns a dataframe with the
    necessary data"""
    wiki_url = "http://wiki.dominionstrategy.com/index.php/List_of_cards"
    table_class = "wikitable sortable"
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")
    card_table = soup.find('table', {'class': table_class})
    fix_cost_and_vp(card_table)
    # print(card_table.find('span', {"class": "coin-icon"}))
    htmlstring = str(card_table)
    df = pd.read_html(htmlstring, encoding='utf-8')[0]
    return df


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


def write_image_database(df):
    answer = input(f"\nDo you want to scrape the Wiki to create an image database?\n"
        f"This may take some time. Please write (y) or cancel (n).\n>>> ")
    while True:
        if answer is "n":
            print("Did not download an image database due to your concerns.")
            return
        if answer is "y":
            break
        answer = input("Please type y for creating an image db or n for cancelling.\n>>> ")
    dirname = "card_pictures"
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    for set_ in set(df["Set"]):
        p = f"{dirname}/{set_.replace(', ', '_')}"
        if not os.path.exists(p):
            os.makedirs(p)
    nums = len(df)
    print("Starting to download pictures, this might take a while")
    impaths = []
    for i, card in df.iterrows():
        cname = card["Name"].replace(' ', '_')
        set_ = card["Set"].replace(', ', '_')
        impath = f"{dirname}/{set_}/{cname}.jpg"
        if not os.path.exists(impath):
            save_image(impath, cname)
        impaths.append(impath)
        if i % 50 == 0:
            print(f"Currently at {i} of {nums} cards ({cname})")
    df["ImagePath"] = impaths
    print("Card image database successfully written.")


def save_image(impath, card_name):
    """Search the wiki for the pic url of card_name and save a picture in
    impath"""
    link_base = "http://wiki.dominionstrategy.com"
    sitename = link_base + f"/index.php/File:{card_name}.jpg"
    response = requests.get(sitename)
    soup = BeautifulSoup(response.text, "html.parser")
    ims = soup.find_all("img")
    pic_link = None
    for im in ims:
        # Find an image with a resolution between 300 and 1000, starting with
        # the lowest. This is probably pretty inefficient.
        for i in range(300, 1000):
            if card_name and f"{i}px" in im["src"]:
                pic_link = link_base + im["src"]
                break
    if pic_link is None:
        print(f"No picture matching criteria could be found for {card_name}.")
        return
    with open(impath, "wb") as f:
        site = requests.get(pic_link)
        f.write(site.content)


def write_dataframe_to_file(df, filename, folder):
    """Writes the given dataframe to a file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    fpath = folder + "/" + filename
    if os.path.isfile(fpath):
        answer = input(f"The file '{fpath}' already exists.\nDo you want to overwrite (y) or cancel (n)?\n>>> ")
        while True:
            if answer is "n":
                print("Did not rewrite the file due to your concerns.")
                return
            if answer is "y":
                break
            answer = input("Please type y for overwriting or n for cancelling.\n>>> ")
    df.to_csv(fpath, sep=";")
    print(f"Successfully wrote the dominion cards to the file '{fpath}' in the current path.")


def main():
    df = retrieve_data()
    df.pipe(add_bool_columns)
    df = add_knight_pile(df)
    df = add_castle_pile(df)
    df["Cost"] = df["Cost"].str.replace("star", "*")
    df["Cost"] = df["Cost"].str.replace("plus", "+")
    write_image_database(df)
    write_dataframe_to_file(df, filename="card_data.csv", folder="card_info")
    return df


if __name__ == "__main__":
    df = main()  # For me to inspect it in variable manager

mydict = {"Bureaucrat": ["Handsize", "Topdeck"],
"Militia": ["Handsize"],
"Spy": ["Topdeck"],
"Thief": ["Topdeck", "TreasureTrasher"],
"Bandit": ["Topdeck", "TreasureTrasher"],
"Witch": ["Curser"],
"Swindler": ["Topdeck", "AllTrasher", "Curser"],
"Minion": ["Handsize"],
"Replace": ["Curser"],
"Saboteur": ["Topdeck", "CostTrasher"],
"Torturer": ["Handsize", "Curser"],
"Ambassador": ["Junker"],
"Cutpurse": ["Handsize"],
"Pirate Ship": ["Topdeck", "TreasureTrasher"],
"Sea Hag": ["Topdeck", "Curser"],
"Ghost Ship": ["Topdeck", "Handsize"],
"Scrying Pool": ["Topdeck"],
"Familiar": ["Curser"],
"Mountebank": ["Curser", "Junker"],
"Rabble": ["Topdeck"],
"Goons": ["Handsize"],
"Fortune Teller": ["Topdeck"],
"Young Witch": ["Curser"],
"Jester": ["Topdeck", "Junker"],
"Followers": ["Curser", "Handsize"],
"Oracle": ["Topdeck"],
"Noble Brigand": ["Topdeck", "TreasureTrasher"],
"Margrave": ["Handsize"],
"Urchin": ["Handsize"],
"Marauder": ["Looter"],
"Cultist": ["Looter"],
"Pillage": ["Handsize"],
"Rogue": ["Topdeck", "CostTrasher"],
"Dame Anna": ["Topdeck", "CostTrasher"],
"Dame Josephine": ["Topdeck", "CostTrasher"],
"Dame Molly": ["Topdeck", "CostTrasher"],
"Dame Natalie": ["Topdeck", "CostTrasher"],
"Dame Sylvia": ["Topdeck", "CostTrasher"],
"Sir Bailey": ["Topdeck", "CostTrasher"],
"Sir Destry": ["Topdeck", "CostTrasher"],
"Sir Martin": ["Topdeck", "CostTrasher"],
"Sir Michael": ["Topdeck", "CostTrasher", "Handsize"],
"Sir Vander": ["Topdeck", "CostTrasher"],
"Mercenary": ["Handsize"],
"Taxman": ["Handsize"],
"Soothsayer": ["Curser"],
"Bridge Troll": ["MinusCoin"],
"Giant": ["Curser", "Topdeck" "CostTrasher"],
"Haunted Woods": ["Topdeck"],
"Relic": ["MinusCard"],
"Swamp Hag": ["Curser"],
"Soldier": ["Handsize"],
"Warrior": ["Topdeck", "CostTrasher"],
"Catapult": ["Curser", "Handsize"],
"Enchantress": ["Piggify"],
"Legionary": ["Handsize"],
"Skulk": ["Hexer"],
"Idol": ["Curser"],
"Tormentor": ["Hexer"],
"Vampire": ["Hexer"],
"Werewolf": ["Hexer"],
"Raider": ["Handsize"],
"Old Witch": ["Curser"],
"Villain": ["Handsize"],
"Black Cat": ["Curser"],
"Cardinal": ["Topdeck", "Exiler"],
"Coven": ["Curser"],
"Ill-Gotten Gains": ["Curser"],
"Possession": ["Possession"],
"Masquerade": ["Masquerade"],
"Raid": ["MinusCard"],
"Gatekeeper": ["Exiler"]}
with open("card_info/attack_types.txt", "w") as f:
    json.dump(mydict, f)