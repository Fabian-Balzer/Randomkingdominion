"""Module for trying to find card info and write them to card_info"""
# %%

import json
from collections import defaultdict

import numpy as np
import pandas as pd

PATHBASE = "../card_info/specifics/"


def get_draw_quality(df):
    df["DrawQualityTest"] = (
        2 * pd.to_numeric(df["Cards"], errors='coerce')).fillna(0).astype(np.int64)
    df.loc[(pd.to_numeric(df["Cards"], errors="coerce") == 1),
           "DrawQualityTest"] = 0
    with open(PATHBASE + "DrawQuality.txt", "r") as f:
        data = json.load(f)
        data = defaultdict(lambda: 0, data)
    old_data = df[["Name", "DrawQualityTest", "DrawQuality"]].to_dict()
    old_data = {old_data["Name"][i]: old_data["DrawQualityTest"][i]
                for i in range(len(old_data["Name"]))}
    new_data = {name: max(data[name], old_data[name])
                for name in sorted(old_data.keys())}
    # Get rid of cantrips providing draw
    for key in new_data:
        if new_data[key] == 1:
            new_data[key] = 0
    custom_values = {"Band of Nomads": 1, "Battle Plan": 3, "Blacksmith": 5, "Broker": 4, "Bustling Village": 1, "Settlers": 1, "Capital City": 2,
                     "Captain": 2, "Cavalry": 5, "Citadel": 2, "Conjurer": 1, "Crop Rotation": 2, "Courtyard": 5, "Crypt": 2, "Demand": 1, "Distant Shore": 3, "Flag": 1, "Garrison": 2, "Goatherd": 2, "Hermit": 2, "Highwayman": 6, "Hireling": 4, "Hunter": 5, "Invest": 1, "Ironmonger": 1, "King's Court": 2, "Lich": 8, "Madman": 8, "Marquis": 7, "Mastermind": 2, "Mountain Folk": 3, "Nobles": 5, "Patrician": 1, "Piazza": 1, "Prince": 3, "Ranger": 6, "Ride": 2, "Royal Galley": 1, "Scholar": 7, "Scrap": 1, "Sibyl": 5, "Sleigh": 2, "Stampede": 4, "Stronghold": 6, "Summon": 1, "Tormentor": 2, "Village Green": 1, "Way of the Chameleon": 2, "Way of the Mole": 2, "Way of the Owl": 5, "Wharf": 8, "Wishing Well": 3,
                     "Castles": 0, "Knights": 1,
                     "Augurs": 2, "Wizards": 2, "Forts": 3, "Townsfolk": 4, "Clashes": 4, "Odysseys": 1,
                     "Catapult/Rocks": 0, "Encampment/Plunder": 5, "Gladiator/Fortune": 0, "Sauna/Avanto": 6, "Patrician/Emporium": 1, "Settlers/Bustling Village": 3}
    for key in custom_values:
        new_data[key] = custom_values[key]
    # print("\n".join([f"{key:15}: {val}" for key, val in new_data.items()]))
    # new_data = {name: data[name] -1 if 1 < data[name] < 4 else data[name] for name in data.keys()}
    with open(f"../card_info/specifics/DrawQuality.txt", "w") as f:
        json.dump(new_data, f)


def get_village_quality(df):
    df["VillageQualityTest"] = 0
    # All regular Villages get the value of 5
    df.loc[(pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2)
           & (pd.to_numeric(df["Cards"], errors="coerce") == 1), "VillageQualityTest"] = 5
    # All villages with no + card get the value 3
    df.loc[(pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2)
           & (pd.to_numeric(df["Cards"], errors="coerce").fillna(0) == 0), "VillageQualityTest"] = 3
    # All villages with more cards get the value 6
    df.loc[(pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2)
           & (pd.to_numeric(df["Cards"], errors="coerce").fillna(0) > 1), "VillageQualityTest"] = 6
    my_villages = df[["Name", "VillageQualityTest"]].to_dict()
    my_villages = {my_villages["Name"][i]: my_villages["VillageQualityTest"][i]
                   for i in range(len(my_villages["Name"]))}
    # Throne rooms get a value of 4,
    other_villages = {"Throne Room": 4,
                      "Diplomat": 4, "Tribute": 2, "Nobles": 3, "Fishing Village": 6, "Tactician": 1, "Golem": 3, "King's Court": 6, "Hamlet": 4, "Trusty Steed": 7, "Crossroads": 5, "Squire": 3, "Ironmonger": 6, "Procession": 4, "Herald": 5, "Coin of the Realm": 4, "Royal Carriage": 4, "Lost Arts": 6, "Disciple": 4, "Teacher": 5, "Champion": 10, "Sacrifice": 3, "Villa": 3,
                      "Bustling Village": 6, "Crown": 4, "Ghost Town": 5, "Conclave": 3, "Zombie Apprentice": 3, "Lackeys": 4, "Acting Troupe": 4, "Silk Merchant": 1, "Recruiter": 8, "Scepter": 3, "Exploration": 3, "Academy": 10, "Piazza": 3, "Barracks": 5, "Innovation": 3, "Citadel": 5, "Snowy Village": 5, "Village Green": 6, "Mastermind": 6, "Paddock": 3, "Delay": 2, "Toil": 2, "March": 1, "Sauna": 2, "Captain": 6, "Prince": 4, "Royal Galley": 4, "Contract": 2, "Lich": 2, "Town": 5, "Cursed Village": 6, "Capital City": 5, "Broker": 2, "Merchant Camp": 4, "Specialist": 4, "Band of Nomads": 1, "City-state": 3, "League of Shopkeepers": 2,
                      "Castles": 0, "Knights": 1,
                      "Augurs": 0, "Wizards": 1, "Forts": 0, "Townsfolk": 0, "Clashes": 0, "Odysseys": 0,
                      "Catapult/Rocks": 0, "Encampment/Plunder": 4, "Gladiator/Fortune": 0, "Sauna/Avanto": 3, "Patrician/Emporium": 0, "Settlers/Bustling Village": 5}
    other_villages = defaultdict(lambda: 0, other_villages)
    new_data = {name: max(other_villages[name], my_villages[name])
                for name in sorted(my_villages.keys())}
    # print(df[df["Name"] == "Lost City"]
    #       [["Name", "Actions / Villagers", "Cards", "VillageQualityTest"]])
    # for i, card in df[(df["VillageQuality"] == 0) & (df["Actions / Villagers"].notna()) & (pd.to_numeric(df["Actions / Villagers"], errors="coerce") != 1)].iterrows():
    # print(f'"{card["Name"]}": ', end=", ")
    with open(PATHBASE + "VillageQuality.txt", "w") as f:
        json.dump(new_data, f)


def get_trashing_quality(df):
    df["TrashingQualityTest"] = 0
    df.fillna('', inplace=True)
    df.loc[(~df["Trash / Return"].str.lower().apply(lambda x: x in ["self", "self?"])) & (df["Trash / Return"].str.len()
                                                                                          != 0), "TrashingQualityTest"]=10  # The self-trashers are only returned, so we don't want them in here
    for i in range(5):
        df.loc[(df["Trash / Return"].str.contains(str(i))),
               "TrashingQualityTest"] = i * 2
        df.loc[(df["Exile"].str.contains(str(i))),
               "TrashingQualityTest"] = i * 2
    my_trashers = df[["Name", "TrashingQualityTest"]].to_dict()
    my_trashers = {my_trashers["Name"][i]: my_trashers["TrashingQualityTest"][i]
                   for i in range(len(my_trashers["Name"]))}
    other_trashers = {"Mint": 5, "Forge": 6, "Count": 5,
                      "Donate": 10, "Monastery": 6, "Sauna": 2, "Banish": 5,
                      "Procession": 1,
                      "Castles": 0, "Knights": 1,
                      "Augurs": 1, "Wizards": 3, "Forts": 0, "Townsfolk": 0,
                      "Clashes": 0, "Odysseys": 0,
                      "Catapult/Rocks": 2, "Encampment/Plunder": 0,
                      "Gladiator/Fortune": 0, "Sauna/Avanto": 3,
                      "Patrician/Emporium": 0, "Settlers/Bustling Village": 0}
    # Look at values that wouldn't make sense, i. e. Procession having 2
    # print(set(df["Trash / Return"]))
    # print(", ".join(['"' + row[1]["Name"] + '": ' + str(row[1]["TrashingQualityTest"]) for row in df[df["TrashingQualityTest"] == 10][["Name", "Trash / Return", "TrashingQualityTest"]].iterrows()]))
    # print(df[df["Trash / Return"].str.contains("1\?")]["Name"])
    # print("\n".join([f'"{name}": ' for name in df[df["TrashingQualityTest"] > 5]["Name"]]))
    for key in other_trashers:
        my_trashers[key] = other_trashers[key]
    with open(PATHBASE + "TrashingQuality.txt", "w") as f:
        json.dump(my_trashers, f)


def print_attacks(df):
    print("\n".join([f"{key}: ," for key in df[df["Types"].apply(lambda x: "Attack" in x)]["Name"]])


def main():
    fpath = "../card_info/good_card_data.csv"
    df = pd.read_csv(fpath, sep=";", header=0)
    print(df.columns)
    print_attacks(df)
    # get_draw_quality(df)
    # get_village_quality(df)
    # get_trashing_quality(df)


if __name__ == '__main__':
    main()
