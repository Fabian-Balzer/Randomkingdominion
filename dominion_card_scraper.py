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
import re  # Regular expressions


string = ""
def fix_cost_expressions(htmlstring):
    """Replaces problematic cost expressions as they are given in pictures"""
    comstring = r'\<span class="coin-icon"\>\<img alt='  # String that is common
    comstring2 = r'\<span class="coin-icon"\>\<a href="/index.php/Potion" title="Potion"><img alt="P"'
    comstring3 = r'\<span class="debt-icon"\>\<a href="/index.php/Debt" title="Debt"><img alt='
    comstring4 = r'\<span class="coin-icon"\>\<a href="/index.php/Victory_point"'
    for i in list(range(15)) + ["X", " "]:  # 0 to 14 because of dominate.
        htmlstring = re.sub(f'{comstring}"\${i}".*?\<\/span\>', f"${i} ", htmlstring)
        htmlstring = re.sub(f'{comstring}"\${i}star".*?\<\/span\>', f"${i}* ", htmlstring)
        htmlstring = re.sub(f'{comstring}"\${i}plus".*?\<\/span\>', f"${i}+ ", htmlstring)
        htmlstring = re.sub(f'{comstring3}"{i}D".*?\<\/span\>', f"{i}D ", htmlstring)
    htmlstring = re.sub(f'{comstring2}.*?\<\/span\>', f"P ", htmlstring)
    htmlstring = re.sub(f'{comstring4}.*?\<\/span\>', f"VP ", htmlstring)
    htmlstring = re.sub(f'{comstring}".*?\<\/span\>', f" Coin ", htmlstring)
    htmlstring = htmlstring.replace("<br/>", "\\n")
    return htmlstring

def fix_cost_and_vp(doc):
    """As cost anv victory points are hidden in images, the parser has a hard time
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
    print(card_table.find('span', {"class": "coin-icon"}))
    htmlstring = str(card_table)
    global string
    string = htmlstring
    # htmlstring = fix_cost_expressions(htmlstring)
    df = pd.read_html(htmlstring, encoding='utf-8')[0]
    return df


def do_lists_have_common(l1, l2):
    """Returns a bool wether two lists share at least one common element."""
    return len([y for y in l1 if y in l2]) > 0


def test_cso(df):
    """Tests whether the given object is an Event, Project, Way or landmark."""
    csolist = ["Event", "Project", "Way", "Landmark"]
    series = df["Types"].apply(lambda x: do_lists_have_common(x, csolist))
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
              df["IsCSO"] |
              df["IsOtherThing"])
    return ~series


def add_bool_columns(df):
    """Adds some boolean columns and saves the types as a list"""
    df["Types"] = df["Types"].str.split(" - ")
    df["IsCSO"] = test_cso(df)
    df["IsOtherThing"] = test_other(df)
    df["IsInSupply"] = test_in_supply(df)
    return df


def add_knight_pile(df):
    knighttext = ('Shuffle the Knights pile before each game with it. '
    "Keep it face down except for the top card, which is the only one "
    'that can be bought or gained.')
    keys = ["Name", "Set", "Types", "Cost", "Text", "IsCSO", "IsOtherThing",
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
    keys = ["Name", "Set", "Types", "Cost", "Text", "IsCSO", "IsOtherThing",
            "IsInSupply"]
    values = ["Castles", "Empires", ["Victory", "Castle"],
              "$3* ", castletext, False, False, True]
    values = [[val] for val in values]
    my_dict = dict(zip(keys, values))
    castle_line = pd.DataFrame(my_dict)
    df = df.append(castle_line, sort=False)
    return df


def write_dataframe_to_file(df, filename):
    """Writes the given dataframe to a file"""
    if os.path.isfile(filename):
        answer = input(f"The file '{filename}' already exists.\nDo you want to overwrite (y) or cancel (n)?\n>>> ")
        while True:
            if answer is "n":
                print("Did not rewrite the file due to your concerns.")
                return
            if answer is "y":
                break
            answer = input("Please type y for overwriting or n for cancelling.\n>>> ")
    df.to_csv(filename, sep=";")
    print(f"Successfully wrote the dominion cards to the file '{filename}' in the current path.")


def write_image_database(df):
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


def main():
    df = retrieve_data()
    df.pipe(add_bool_columns)
    df = add_knight_pile(df)
    df = add_castle_pile(df)
    df["Cost"] = df["Cost"].str.replace("star", "*")
    df["Cost"] = df["Cost"].str.replace("plus", "+")
    write_image_database(df)
    write_dataframe_to_file(df, filename="card_data.csv")
    return df


if __name__ == "__main__":
    df = main()  # For me to inspect it in variable manager
