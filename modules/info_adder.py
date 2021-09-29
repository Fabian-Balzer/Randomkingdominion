"""Module for trying to find card info and write them to card_info"""


import json
import pandas as pd
import numpy as np
from collections import defaultdict


PATHBASE = "../card_info/specifics/"


def get_card_quality(df):
    df["DrawQualityNew"] = (2*pd.to_numeric(df["Cards"], errors='coerce')).fillna(0).astype(np.int64)
    with open(PATHBASE + "DrawQuality.txt", "r") as f:
        data = json.load(f)
        data = defaultdict(lambda: 0, data)
    old_data = df[["Name", "DrawQualityNew"]].to_dict()
    old_data = {old_data["Name"][i]: old_data["DrawQuality"][i] for i in range(len(old_data["Name"]))}
    new_data = {name: max(data[name], old_data[name]) for name in sorted(old_data.keys())}
    # new_data = {name: data[name] -1 if 1 < data[name] < 4 else data[name] for name in data.keys()}
    with open(f"../card_info/specifics/DrawQuality.txt", "w") as f:
        json.dump(new_data, f)


def get_village_quality(df):
    df["VillageQualityTest"] = 0
    # All regular Villages get the value of 5
    df.loc[(pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2) \
        & (pd.to_numeric(df["Cards"], errors="coerce") == 1), "VillageQualityTest"] = 5
    # All villages with no + card get the value 3
    df.loc[(pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2) \
        & (pd.to_numeric(df["Cards"], errors="coerce").fillna(0) == 0), "VillageQualityTest"] = 3
    # All villages with more cards get the value 6
    df.loc[(pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2) \
        & (pd.to_numeric(df["Cards"], errors="coerce").fillna(0) > 1), "VillageQualityTest"] = 6
    my_villages = df[["Name", "VillageQualityTest"]].to_dict()
    my_villages = {my_villages["Name"][i]: my_villages["VillageQualityTest"][i] for i in range(len(my_villages["Name"]))}
    # Throne rooms get a value of 4,
    other_villages = {"Throne Room": 4, "Diplomat": 4, "Tribute": 2, "Nobles": 3, "Fishing Village": 4, "Tactician": 1, "Golem": 3, "King's Court": 6, "Hamlet": 4, "Trusty Steed": 7, "Crossroads": 5, "Squire": 3, "Ironmonger": 6, "Procession": 4, "Herald": 5, "Coin of the Realm": 4, "Royal Carriage": 4, "Lost Arts": 6, "Disciple": 4, "Teacher": 5, "Champion": 10, "Sacrifice": 3, "Villa": 3, "Bustling Village": 6, "Crown": 4, "Ghost Town": 5, "Conclave": 3, "Zombie Apprentice": 3, "Lackeys": 4, "Acting Troupe": 4, "Silk Merchant": 1, "Recruiter": 8, "Scepter": 3, "Exploration": 3, "Academy": 10, "Piazza": 3, "Barracks": 5, "Innovation": 4, "Citadel": 5, "Snowy Village": 5, "Village Green": 6, "Mastermind": 6, "Paddock": 3, "Toil": 2, "March": 1, "Sauna": 2, "Captain": 6, "Prince": 4}
    other_villages = defaultdict(lambda: 0, other_villages)
    new_data = {name: max(other_villages[name], my_villages[name]) for name in sorted(my_villages.keys())}
    print(df[df["Name"] == "Lost City"][["Name", "Actions / Villagers", "Cards", "VillageQualityTest"]])
    for i, card in df[(df["VillageQuality"] == 0) & (df["Actions / Villagers"].notna()) & (pd.to_numeric(df["Actions / Villagers"], errors="coerce") != 1)].iterrows():
        print(f'"{card["Name"]}": ', end=", ")

    with open(PATHBASE + "VillageQuality.txt", "w") as f:
        json.dump(new_data, f)


def get_trashing_quality(df):
    df["TrashingQualityTest"] = 0
    df.fillna('', inplace=True)
    df.loc[(~df["Trash / Return"].str.lower().apply(lambda x: x in ["self", "self?"])) & (df["Trash / Return"].str.len() != 0), "TrashingQualityTest"] = 10  # The self-trashers are only returned, so we don't want them in here
    for i in range(5):
        df.loc[(df["Trash / Return"].str.contains(str(i))), "TrashingQualityTest"] = i*2
        df.loc[(df["Exile"].str.contains(str(i))), "TrashingQualityTest"] = i*2
    my_trashers = df[["Name", "TrashingQualityTest"]].to_dict()
    my_trashers = {my_trashers["Name"][i]: my_trashers["TrashingQualityTest"][i] for i in range(len(my_trashers["Name"]))}
    other_trashers = {"Mint": 5, "Forge": 6, "Count": 5, "Donate": 10, "Monastery": 6, "Sauna": 2, "Banish": 5}
    other_trashers = defaultdict(lambda: 0, other_trashers)
    new_data = {name: max(other_trashers[name], my_trashers[name]) for name in sorted(my_trashers.keys())}
    # print(set(df["Trash / Return"]))
    # print(", ".join(['"' + row[1]["Name"] + '": ' + str(row[1]["TrashingQualityTest"]) for row in df[df["TrashingQualityTest"] == 10][["Name", "Trash / Return", "TrashingQualityTest"]].iterrows()]))
    # print(df[df["Trash / Return"].str.contains("1\?")]["Name"])
    # print("\n".join([f'"{name}": ' for name in df[df["TrashingQualityTest"] > 5]["Name"]]))

    with open(PATHBASE + "TrashingQuality.txt", "w") as f:
        json.dump(new_data, f)



def main():
    fpath = "../card_info/good_card_data.csv"
    df = df = pd.read_csv(fpath, sep=";", header=0)
    get_trashing_quality(df)


if __name__ == '__main__':
    main()