"""Module for trying to find card info and write them to card_info"""
# %%

import json
from collections import defaultdict

import numpy as np
import pandas as pd

from .constants import FPATH_CARD_DATA

PATHBASE = "../card_info/specifics/"


def get_draw_quality(df):
    df["DrawQualityTest"] = (
        (2 * pd.to_numeric(df["Cards"], errors="coerce")).fillna(0).astype(np.int64)
    )
    df.loc[(pd.to_numeric(df["Cards"], errors="coerce") == 1), "DrawQualityTest"] = 0
    with open(PATHBASE + "DrawQuality.txt", "r") as f:
        data = json.load(f)
        data = defaultdict(lambda: 0, data)
    old_data = df[["Name", "DrawQualityTest", "DrawQuality"]].to_dict()
    old_data = {
        old_data["Name"][i]: old_data["DrawQualityTest"][i]
        for i in range(len(old_data["Name"]))
    }
    new_data = {
        name: max(data[name], old_data[name]) for name in sorted(old_data.keys())
    }
    # Get rid of cantrips providing draw
    for key in new_data:
        if new_data[key] == 1:
            new_data[key] = 0
    custom_values = {
        "Band of Nomads": 1,
        "Battle Plan": 3,
        "Blacksmith": 5,
        "Broker": 4,
        "Bustling Village": 1,
        "Settlers": 1,
        "Capital City": 2,
        "Captain": 2,
        "Cavalry": 5,
        "Citadel": 2,
        "Conjurer": 1,
        "Crop Rotation": 2,
        "Courtyard": 5,
        "Crypt": 2,
        "Demand": 1,
        "Distant Shore": 3,
        "Flag": 1,
        "Garrison": 2,
        "Goatherd": 2,
        "Hermit": 2,
        "Highwayman": 6,
        "Hireling": 4,
        "Hunter": 5,
        "Invest": 1,
        "Ironmonger": 1,
        "King's Court": 2,
        "Lich": 8,
        "Madman": 8,
        "Marquis": 7,
        "Mastermind": 2,
        "Mountain Folk": 3,
        "Nobles": 5,
        "Patrician": 1,
        "Piazza": 1,
        "Prince": 3,
        "Ranger": 6,
        "Ride": 2,
        "Royal Galley": 1,
        "Scholar": 7,
        "Scrap": 1,
        "Sibyl": 5,
        "Sleigh": 2,
        "Stampede": 4,
        "Stronghold": 6,
        "Summon": 1,
        "Tormentor": 2,
        "Village Green": 1,
        "Way of the Chameleon": 2,
        "Way of the Mole": 2,
        "Way of the Owl": 5,
        "Wharf": 8,
        "Wishing Well": 3,
        "Castles": 0,
        "Knights": 1,
        "Herald": 2,
        "Augurs": 2,
        "Wizards": 2,
        "Forts": 3,
        "Townsfolk": 4,
        "Clashes": 4,
        "Odysseys": 1,
        "Catapult/Rocks": 0,
        "Encampment/Plunder": 5,
        "Gladiator/Fortune": 0,
        "Sauna/Avanto": 6,
        "Patrician/Emporium": 1,
        "Settlers/Bustling Village": 3,
    }
    for key in custom_values:
        new_data[key] = custom_values[key]
    # print("\n".join([f"{key:15}: {val}" for key, val in new_data.items()]))
    # new_data = {name: data[name] -1 if 1 < data[name] < 4 else data[name] for name in data.keys()}
    with open(f"../card_info/specifics/DrawQuality.txt", "w") as f:
        json.dump(new_data, f)


def get_village_quality(df):
    df["VillageQualityTest"] = 0
    # All regular Villages get the value of 5
    df.loc[
        (pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2)
        & (pd.to_numeric(df["Cards"], errors="coerce") == 1),
        "VillageQualityTest",
    ] = 5
    # All villages with no + card get the value 3
    df.loc[
        (pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2)
        & (pd.to_numeric(df["Cards"], errors="coerce").fillna(0) == 0),
        "VillageQualityTest",
    ] = 3
    # All villages with more cards get the value 6
    df.loc[
        (pd.to_numeric(df["Actions / Villagers"], errors="coerce") == 2)
        & (pd.to_numeric(df["Cards"], errors="coerce").fillna(0) > 1),
        "VillageQualityTest",
    ] = 6
    my_villages = df[["Name", "VillageQualityTest"]].to_dict()
    my_villages = {
        my_villages["Name"][i]: my_villages["VillageQualityTest"][i]
        for i in range(len(my_villages["Name"]))
    }
    # Throne rooms get a value of 4,
    other_villages = {
        "Throne Room": 4,
        "Diplomat": 4,
        "Tribute": 2,
        "Nobles": 3,
        "Fishing Village": 6,
        "Tactician": 1,
        "Golem": 3,
        "King's Court": 6,
        "Hamlet": 4,
        "Trusty Steed": 7,
        "Crossroads": 5,
        "Squire": 3,
        "Ironmonger": 6,
        "Procession": 4,
        "Herald": 5,
        "Coin of the Realm": 4,
        "Royal Carriage": 4,
        "Lost Arts": 6,
        "Disciple": 4,
        "Teacher": 5,
        "Champion": 10,
        "Sacrifice": 3,
        "Villa": 3,
        "Bustling Village": 6,
        "Crown": 4,
        "Ghost Town": 5,
        "Conclave": 3,
        "Zombie Apprentice": 3,
        "Lackeys": 4,
        "Acting Troupe": 4,
        "Silk Merchant": 1,
        "Recruiter": 8,
        "Scepter": 3,
        "Exploration": 3,
        "Academy": 10,
        "Piazza": 3,
        "Barracks": 5,
        "Innovation": 3,
        "Citadel": 5,
        "Snowy Village": 5,
        "Village Green": 6,
        "Mastermind": 6,
        "Paddock": 3,
        "Delay": 2,
        "Toil": 2,
        "March": 1,
        "Sauna": 2,
        "Captain": 6,
        "Prince": 4,
        "Royal Galley": 4,
        "Contract": 2,
        "Lich": 2,
        "Town": 5,
        "Cursed Village": 6,
        "Capital City": 5,
        "Broker": 2,
        "Merchant Camp": 4,
        "Specialist": 4,
        "Band of Nomads": 1,
        "City-state": 3,
        "League of Shopkeepers": 2,
        "Castles": 0,
        "Knights": 1,
        "Augurs": 0,
        "Wizards": 1,
        "Forts": 0,
        "Townsfolk": 0,
        "Clashes": 0,
        "Odysseys": 0,
        "Catapult/Rocks": 0,
        "Encampment/Plunder": 4,
        "Gladiator/Fortune": 0,
        "Sauna/Avanto": 3,
        "Patrician/Emporium": 0,
        "Settlers/Bustling Village": 5,
    }
    other_villages = defaultdict(lambda: 0, other_villages)
    new_data = {
        name: max(other_villages[name], my_villages[name])
        for name in sorted(my_villages.keys())
    }
    # print(df[df["Name"] == "Lost City"]
    #       [["Name", "Actions / Villagers", "Cards", "VillageQualityTest"]])
    # for i, card in df[(df["VillageQuality"] == 0) & (df["Actions / Villagers"].notna()) & (pd.to_numeric(df["Actions / Villagers"], errors="coerce") != 1)].iterrows():
    # print(f'"{card["Name"]}": ', end=", ")
    with open(PATHBASE + "VillageQuality.txt", "w") as f:
        json.dump(new_data, f)


def get_trashing_quality(df):
    df["ThinningQualityTest"] = 0
    df.fillna("", inplace=True)
    df.loc[
        (~df["Trash / Return"].str.lower().apply(lambda x: x in ["self", "self?"]))
        & (df["Trash / Return"].str.len() != 0),
        "ThinningQualityTest",
    ] = 10  # The self-trashers are only returned, so we don't want them in here
    for i in range(5):
        df.loc[(df["Trash / Return"].str.contains(str(i))), "ThinningQualityTest"] = (
            i * 2
        )
        df.loc[(df["Exile"].str.contains(str(i))), "ThinningQualityTest"] = i * 2
    my_trashers = df[["Name", "ThinningQualityTest"]].to_dict()
    my_trashers = {
        my_trashers["Name"][i]: my_trashers["ThinningQualityTest"][i]
        for i in range(len(my_trashers["Name"]))
    }
    other_trashers = {
        "Mint": 5,
        "Forge": 6,
        "Count": 5,
        "Donate": 10,
        "Monastery": 6,
        "Sauna": 2,
        "Banish": 5,
        "Procession": 1,
        "Castles": 0,
        "Knights": 1,
        "Augurs": 1,
        "Wizards": 3,
        "Forts": 0,
        "Townsfolk": 0,
        "Clashes": 0,
        "Odysseys": 0,
        "Catapult/Rocks": 2,
        "Encampment/Plunder": 0,
        "Gladiator/Fortune": 0,
        "Sauna/Avanto": 3,
        "Patrician/Emporium": 0,
        "Settlers/Bustling Village": 0,
    }
    # Look at values that wouldn't make sense, i. e. Procession having 2
    # print(set(df["Trash / Return"]))
    # print(", ".join(['"' + row[1]["Name"] + '": ' + str(row[1]["ThinningQualityTest"]) for row in df[df["ThinningQualityTest"] == 10][["Name", "Trash / Return", "ThinningQualityTest"]].iterrows()]))
    # print(df[df["Trash / Return"].str.contains("1\?")]["Name"])
    # print("\n".join([f'"{name}": ' for name in df[df["ThinningQualityTest"] > 5]["Name"]]))
    for key in other_trashers:
        my_trashers[key] = other_trashers[key]
    with open(PATHBASE + "ThinningQuality.txt", "w") as f:
        json.dump(my_trashers, f)


def get_attack_types(df):
    attack_dict = {}
    attack_dict["Handsize"] = [
        "Bureaucrat",
        "Militia",
        "Minion",
        "Torturer",
        "Cutpurse",
        "Ghost Ship",
        "Goons",
        "Followers",
        "Margrave",
        "Urchin",
        "Pillage",
        "Sir Michael",
        "Knights",
        "Mercenary",
        "Taxman",
        "Relic",
        "Soldier",
        "Catapult",
        "Catapult/Rocks",
        "Legionary",
        "Raider",
        "Villain",
        "Skirmisher",
        "Archer",
        "Clashes",
        "Haunted Woods",
        "Gang of Pickpockets",
    ]
    attack_dict["Trashing"] = [
        "Swindler",
        "Thief",
        "Bandit",
        "Saboteur",
        "Pirate Ship",
        "Noble Brigand",
        "Rogue",
        "Dame Anna",
        "Dame Josephine",
        "Dame Molly",
        "Dame Natalie",
        "Dame Sylvia",
        "Sir Bailey",
        "Sir Destry",
        "Sir Martin",
        "Sir Michael",
        "Sir Vander",
        "Knights",
        "Giant",
        "Warrior",
        "Cardinal",
        "Barbarian",
    ]
    attack_dict["Junking"] = [
        "Swindler",
        "Witch",
        "Replace",
        "Torturer",
        "Ambassador",
        "Sea Hag",
        "Familiar",
        "Mountebank",
        "Young Witch",
        "Jester",
        "Noble Brigand",
        "Marauder",
        "Cultist",
        "Soothsayer",
        "Giant",
        "Catapult",
        "Catapult/Rocks",
        "Idol",
        "Old Witch",
        "Black Cat",
        "Coven",
        "Barbarian",
        "Sorcerer",
        "Sorceress",
        "Wizards",
        "Augurs",
        "Circle of Witches",
    ]
    attack_dict["Deck order"] = [
        "Bureaucrat",
        "Spy",
        "Sea Hag",
        "Scrying Pool",
        "Ghost Ship",
        "Rabble",
        "Haunted Woods",
        "Fortune Teller",
        "Jester",
        "Oracle",
    ]  # Not considering margrave or soothsayer etc.
    # All trashing attacks mess with deck order
    attack_dict["Deck order"] = attack_dict["Deck order"] + attack_dict["Trashing"]
    attack_dict["Turn worsening"] = [
        "Bridge Troll",
        "Swamp Hag",
        "Relic",
        "Enchantress",
        "Gatekeeper",
        "Highwayman",
        "Warlord",
        "Clashes",
    ]
    attack_dict["Doom"] = list(df[df["Types"].apply(lambda x: "Doom" in x)]["Name"])
    attack_dict["Doom"] = [
        att
        for att in attack_dict["Doom"]
        if att not in ["Leprechaun", "Cursed Village"]
    ]
    attack_dict["Scoring"] = [
        "Witch",
        "Swindler",
        "Replace",
        "Torturer",
        "Sea Hag",
        "Familiar",
        "Mountebank",
        "Young Witch",
        "Jester",
        "Followers",
        "Giant",
        "Catapult",
        "Catapult/Rocks",
        "Idol",
        "Old Witch",
        "Black Cat",
        "Coven",
        "Barbarian",
        "Swamp Hag",
        "Wizards",
        "Augurs",
        "Circle of Witches",
    ]
    cards = {}
    attack_dict["Indirect"] = [
        "Possession",
        "Raid",
        "Ill-Gotten Gains",
        "Masquerade",
        "Haunted Castle",
    ]
    for attack_type in attack_dict:
        for card in attack_dict[attack_type]:
            if card in cards.keys():
                cards[card].append(attack_type)
            else:
                cards[card] = [attack_type]
    with open(PATHBASE + "AttackType.txt", "w") as f:
        json.dump(cards, f)
    # print("\n".join([f'{key}: [""],' for key in df[df["Types"].apply(lambda x: "Attack" in x)]["Name"]]))


def assign_attack_strength(df):
    """Assign the impact of each attack on a scale of 0 to 3 corresponding to
    None, Weak, Medium, and Strong.
    This impact is determined by my gut feeling and is based on how centralizing
    the card is in an average game."""
    with open(f"../card_info/specifics/AttackType.txt", "r") as f:
        data = json.load(f)
    # print("\n".join([f"\"{key}\": ," for key in data]))
    assignments = {
        "Bureaucrat": 1,
        "Militia": 2,
        "Minion": 2,
        "Torturer": 3,
        "Cutpurse": 2,
        "Ghost Ship": 3,
        "Goons": 2,
        "Followers": 3,
        "Margrave": 2,
        "Urchin": 2,
        "Pillage": 2,
        "Sir Michael": 3,
        "Knights": 3,
        "Mercenary": 2,
        "Taxman": 1,
        "Relic": 1,
        "Soldier": 1,
        "Catapult": 2,
        "Catapult/Rocks": 2,
        "Legionary": 2,
        "Raider": 1,
        "Villain": 1,
        "Skirmisher": 1,
        "Archer": 2,
        "Clashes": 2,
        "Swindler": 3,
        "Thief": 2,
        "Bandit": 1,
        "Circle of Witches": 2,
        "Saboteur": 1,
        "Pirate Ship": 1,
        "Noble Brigand": 1,
        "Rogue": 1,
        "Dame Anna": 2,
        "Dame Josephine": 2,
        "Dame Molly": 2,
        "Dame Natalie": 2,
        "Dame Sylvia": 2,
        "Sir Bailey": 2,
        "Sir Destry": 2,
        "Sir Martin": 2,
        "Sir Vander": 2,
        "Giant": 1,
        "Warrior": 2,
        "Haunted Woods": 3,
        "Cardinal": 2,
        "Barbarian": 3,
        "Witch": 3,
        "Replace": 1,
        "Ambassador": 3,
        "Sea Hag": 2,
        "Familiar": 3,
        "Mountebank": 3,
        "Young Witch": 1,
        "Jester": 2,
        "Marauder": 1,
        "Cultist": 3,
        "Soothsayer": 2,
        "Idol": 2,
        "Old Witch": 2,
        "Black Cat": 2,
        "Coven": 2,
        "Sorcerer": 1,
        "Sorceress": 1,
        "Wizards": 1,
        "Augurs": 1,
        "Spy": 1,
        "Scrying Pool": 1,
        "Rabble": 2,
        "Fortune Teller": 1,
        "Oracle": 1,
        "Bridge Troll": 1,
        "Swamp Hag": 3,
        "Enchantress": 2,
        "Gatekeeper": 1,
        "Highwayman": 1,
        "Warlord": 2,
        "Leprechaun": 0,
        "Skulk": 2,
        "Cursed Village": 0,
        "Tormentor": 1,
        "Vampire": 2,
        "Werewolf": 2,
        "Possession": 3,
        "Raid": 1,
        "Ill-Gotten Gains": 2,
        "Masquerade": 1,
        "Haunted Castle": 1,
    }
    with open(PATHBASE + "AttackQuality.txt", "w") as f:
        json.dump(assignments, f)
    print("Written updated Attack Strength values to AttackQuality.txt")


def assign_interactivity_value(df):
    """Assign a value for interactive cards. Attack Cards inherently have an
    interactivity value of 2.
    This interactivity is determined by my gut feeling and is based on how much
    a card is going to invoke player interaction."""
    with open(f"../card_info/specifics/AttackType.txt", "r") as f:
        data = json.load(f)
    # print("\n".join([f"\"{key}\": ," for key in data]))
    interactivity_vals = {key: 2 for key in data}
    # print("\n".join(list(df[df["Expansion"]=="Promo"]["Name"])))
    additional_values = {
        "Moat": 1,
        "Council Room": 1,
        "Poacher": 1,
        "Diplomat": 2,
        "Tribute": 3,
        "Masquerade": 3,
        "Swindler": 3,
        "Minion": 1,
        "Embargo": 2,
        "Lighthouse": 1,
        "Smugglers": 2,
        "Watchtower": 1,
        "Bishop": 2,
        "City": 1,
        "Contraband": 2,
        "Vault": 1,
        "Advisor": 2,
        "Fool's Gold": 1,
        "Trader": 1,
        "Embassy": 1,
        "Border Guard": 2,
        "Flag Bearer": 3,
        "Patron": 1,
        "Swashbuckler": 1,
        "Treasurer": 2,
        "Flag": 2,
        "Horn": 2,
        "Key": 2,
        "Lantern": 2,
        "Treasure Chest": 2,
        "Fleet": 2,
        "Road Network": 3,
        "Horse Traders": 2,
        "Tournament": 2,
        "Young Witch": 3,
        "Jester": 3,
        "Possession": 1,
        "Faithful Hound": 1,
        "Guardian": 2,
        "Pixie": 1,
        "Fool": 2,
        "Blessed Village": 1,
        "Necromancer": 2,
        "Sacred Grove": 2,
        "Page": 1,
        "Peasant": 1,
        "Caravan Guard": 2,
        "Magpie": 1,
        "Messenger": 1,
        "Bridge Troll": 1,
        "Swamp Hag": 3,
        "Mission": 1,
        "Plan": 1,
        "Raid": 1,
        "Champion": 2,
        "Overlord": 1,
        "Encampment/Plunder": 1,
        "Patrician/Emporium": 1,
        "Settlers/Bustling Village": 1,
        "Catapult/Rocks": 3,
        "Chariot Race": 2,
        "Farmer's Market": 2,
        "Gladiator/Fortune": 3,
        "Gladiator": 3,
        "Temple": 2,
        "Wild Hunt": 2,
        "Castles": 2,
        "Tax": 3,
        "Salt the Earth": 1,
        "Aqueduct": 2,
        "Arena": 1,
        "Basilica": 1,
        "Battlefield": 1,
        "Baths": 1,
        "Defiled Shrine": 2,
        "Keep": 2,
        "Labyrinth": 1,
        "Mountain Pass": 2,
        "Carpenter": 1,
        "Barbarian": 3,
        "Skirmisher": 3,
        "Herb Gatherer": 1,
        "Student": 1,
        "Battle Plan": 2,
        "Archer": 3,
        "Augurs": 2,
        "Wizards": 2,
        "Forts": 1,
        "Townsfolk": 1,
        "Clashes": 3,
        "Odysseys": 1,
        "Circle of Witches": 2,
        "Family of Inventors": 3,
        "Beggar": 2,
        "Forager": 1,
        "Market Square": 1,
        "Band of Misfits": 1,
        "Graverobber": 1,
        "Pillage": 3,
        "Rebuild": 1,
        "Knights": 3,
        "Black Cat": 3,
        "Sleigh": 1,
        "Goatherd": 3,
        "Sheepdog": 1,
        "Stockpile": 1,
        "Village Green": 1,
        "Coven": 3,
        "Falconer": 2,
        "Animal Fair": 1,
        "Bargain": 2,
        "Invest": 3,
        "Way of the Butterfly": 1,
        "Way of the Horse": 1,
        "Way of the Squirrel": 1,
        "Way of the Turtle": 1,
        "Black Market": 1,
        "Envoy": 2,
        "Sauna/Avanto": 1,
        "Governor": 3,
    }
    for key in additional_values:
        interactivity_vals[key] = additional_values[key]
    with open(PATHBASE + "InteractivityQuality.txt", "w") as f:
        json.dump(interactivity_vals, f)
    print("Written updated interactivity values to InteractivityQuality.txt")


def reevaluate_draw_quality():
    """Rank the draw quality on a scale of 0 to 3 corresponding to
    None, Weak, Medium, and Strong draw."""
    with open(f"../card_info/specifics/DrawQuality_Old.txt", "r") as f:
        data = json.load(f)
    # print("\n".join([f"\"{key}\": {val}," for key, val in data.items() if val > 0 and val < 2]))
    for key, qual in data.items():
        data[key] = min(int(qual * 2 / 3), 3)
    print("\n".join([f'"{key}": {val},' for key, val in data.items() if val > 0]))
    corrections = {
        "Band of Nomads": 1,
        "Bustling Village": 1,
        "Conjurer": 1,
        "Demand": 1,
        "Invest": 1,
        "Ironmonger": 1,
        "Odysseys": 1,
        "Patrician": 1,
        "Patrician/Emporium": 1,
        "Piazza": 1,
        "Royal Galley": 1,
        "Scrap": 1,
        "Settlers": 1,
        "Settlers/Bustling Village": 1,
        "Summon": 1,
        "Village Green": 1,
        "Adventurer": 1,
        "Apothecary": 2,
        "Encampment/Plunder": 2,
        "Garrison": 2,
        "Forts": 2,
        "Hunter": 2,
        "Jack of All Trades": 1,
        "Minion": 2,
        "Mountain Folk": 1,
        "Prince": 1,
        "Recruiter": 0,
        "Sleigh": 2,
        "Wishing Well": 1,
        "Zombie Apprentice": 2,
    }
    for key in corrections:
        data[key] = corrections[key]
    with open(f"../card_info/specifics/DrawQuality.txt", "w") as f:
        json.dump(data, f)
    print("Written updated Draw values to DrawQuality.txt")


def reevaluate_village_quality():
    """Rank the village quality on a scale of 0 to 3 corresponding to
    None, Weak, Medium, and Strong village.
    Anything providing the ability to play additional Action cards counts as
    at least a weak village"""
    with open(f"../card_info/specifics/VillageQuality_Old.txt", "r") as f:
        data = json.load(f)
    print(
        "\n".join(
            [f'"{key}": {val},' for key, val in data.items() if val > 0 and val < 2]
        )
    )
    for key, qual in data.items():
        data[key] = min(int(qual * 2 / 3), 3)
    print("\n".join([f'"{key}": {val},' for key, val in data.items() if val > 0]))
    corrections = {
        "Band of Nomads": 1,
        "Knights": 1,
        "March": 1,
        "Silk Merchant": 1,
        "Wizards": 1,
        "Academy": 3,
        "Acting Troupe": 2,
        "Bandit Camp": 2,
        "Barracks": 2,
        "Bazaar": 2,
        "Blessed Village": 2,
        "Border Village": 2,
        "Broker": 1,
        "Bustling Village": 3,
        "Capital City": 2,
        "Captain": 2,
        "Champion": 3,
        "Citadel": 2,
        "City": 2,
        "City Quarter": 2,
        "City-state": 1,
        "Coin of the Realm": 2,
        "Conclave": 2,
        "Contract": 1,
        "Crossroads": 2,
        "Crown": 2,
        "Cursed Village": 2,
        "Dame Molly": 2,
        "Delay": 1,
        "Diplomat": 2,
        "Disciple": 2,
        "Encampment": 2,
        "Encampment/Plunder": 2,
        "Exploration": 2,
        "Farming Village": 2,
        "Festival": 2,
        "Fishing Village": 3,
        "Fortress": 2,
        "Ghost Town": 2,
        "Golem": 2,
        "Hamlet": 2,
        "Herald": 2,
        "Hideout": 2,
        "Hostelry": 2,
        "Hunting Lodge": 2,
        "Inn": 2,
        "Innovation": 1,
        "Ironmonger": 2,
        "King's Court": 3,
        "Lackeys": 2,
        "League of Shopkeepers": 1,
        "Lich": 2,
        "Lost Arts": 3,
        "Lost City": 2,
        "Madman": 2,
        "Mastermind": 3,
        "Merchant Camp": 2,
        "Mining Village": 2,
        "Mountain Village": 2,
        "Native Village": 2,
        "Necropolis": 1,
        "Nobles": 2,
        "Paddock": 2,
        "Piazza": 1,
        "Plaza": 2,
        "Port": 3,
        "Prince": 1,
        "Procession": 2,
        "Recruiter": 3,
        "Royal Carriage": 2,
        "Royal Galley": 2,
        "Sacrifice": 2,
        "Sauna": 1,
        "Sauna/Avanto": 1,
        "Scepter": 1,  # Only playing Actions during Action phase
        "Settlers/Bustling Village": 2,  # Bustleroo is hard to get to
        "Shanty Town": 2,
        "Snowy Village": 2,
        "Specialist": 2,
        "Squire": 2,
        "Teacher": 3,
        "Throne Room": 2,
        "Toil": 1,
        "Town": 2,
        "Tribute": 1,
        "Trusty Steed": 3,
        "University": 2,
        "Villa": 2,
        "Village": 2,
        "Village Green": 3,
        "Walled Village": 2,
        "Wandering Minstrel": 2,
        "Way of the Ox": 2,
        "Worker's Village": 2,
        "Zombie Apprentice": 0,
        "Page": 2,  # TODO: Remove this if Village qual is considered later
        "Peasant": 2,
    }
    for key in corrections:
        data[key] = corrections[key]
    with open(f"../card_info/specifics/VillageQuality.txt", "w") as f:
        json.dump(data, f)
    print("Written updated Village values to VillageQuality.txt")


def reevaluate_thinning_quality():
    """Rank the trashing quality on a scale of 0 to 3 corresponding to
    None, Weak, Medium, and Strong trashing."""
    with open(f"../card_info/specifics/ThinningQuality_Old.txt", "r") as f:
        data = json.load(f)
    print(
        "\n".join(
            [f'"{key}": {val},' for key, val in data.items() if val > 0 and val < 2]
        )
    )
    for key, qual in data.items():
        data[key] = min(int(qual), 3)
    print("\n".join([f'"{key}": {val},' for key, val in data.items() if val > 0]))
    corrections = {
        "Augurs": 1,
        "Chapel": 3,
        "Moneylender": 2,
        "Remodel": 2,
        "Mine": 1,
        "Sentry": 3,
        "Lurker": 0,
        "Masquerade": 2,
        "Steward": 3,
        "Replace": 2,
        "Trading Post": 2,
        "Upgrade": 2,
        "Ambassador": 3,
        "Lookout": 2,
        "Island": 1,
        "Salvager": 2,
        "Treasure Map": 2,
        "Transmute": 1,
        "Apprentice": 2,
        "Loan": 2,
        "Trade Route": 1,
        "Bishop": 2,
        "Mint": 2,
        "Expand": 2,
        "Forge": 3,
        "Remake": 3,
        "Jester": 0,
        "Develop": 1,
        "Jack of All Trades": 1,
        "Spice Merchant": 2,
        "Trader": 2,
        "Farmland": 2,
        "Forager": 2,
        "Hermit": 1,
        "Death Cart": 2,
        "Procession": 0,
        "Rats": 2,
        "Count": 2,
        "Counterfeit": 2,
        "Graverobber": 1,
        "Junk Dealer": 2,
        "Rebuild": 1,
        "Altar": 2,
        "Dame Anna": 3,
        "Mercenary": 3,
        "Stonemason": 2,
        "Doctor": 3,
        "Taxman": 1,
        "Butcher": 1,
        "Ratcatcher": 2,
        "Raze": 2,
        "Amulet": 2,
        "Miser": 1,
        "Transmogrify": 1,
        "Bonfire": 2,
        "Plan": 2,
        "Trade": 1,
        "Catapult": 2,
        "Sacrifice": 2,
        "Temple": 3,
        "Small Castle": 1,
        "Donate": 3,
        "Advance": 2,
        "Banquet": 0,
        "Ritual": 1,
        "Salt the Earth": 0,
        "Monastery": 3,
        "Cemetery": 2,
        "Exorcist": 2,
        "Pooka": 2,
        "Bat": 3,
        "Zombie Apprentice": 2,
        "Zombie Mason": 2,
        "Goat": 2,
        "The Flame's Gift": 2,
        "Locusts": 1,
        "War": 1,
        "Ducat": 2,
        "Improve": 1,
        "Hideout": 2,
        "Priest": 2,
        "Research": 2,
        "Recruiter": 2,
        "Treasurer": 2,
        "Cathedral": 3,
        "Sewers": 2,
        "Goatherd": 2,
        "Scrap": 2,
        "Bounty Hunter": 2,
        "Displace": 2,
        "Sanctuary": 2,
        "Enhance": 1,
        "Transport": 0,
        "Banish": 3,
        "Invest": 0,
        "Enclave": 0,
        "Way of the Camel": 0,
        "Way of the Goat": 2,
        "Way of the Worm": 0,
        "Sentinel": 3,
        "Broker": 2,
        "Carpenter": 1,
        "Modify": 2,
        "Swap": 1,
        "Student": 2,
        "Acolyte": 1,
        "Peaceful Cult": 3,
        "Woodworkers' Guild": 2,
        "Church": 2,
        "Dismantle": 1,
        "Sauna": 2,
        "Governor": 1,
        "Knights": 1,
        "Catapult/Rocks": 2,
        "Sauna/Avanto": 2,
        "Augurs": 1,
        "Wizards": 2,
        "Urchin": 2,  # Being connected to mercenary, TODO: Fix once this is considered
        "Vampire": 2,
    }
    for key in corrections:
        data[key] = corrections[key]
    with open(f"../card_info/specifics/ThinningQuality.txt", "w") as f:
        json.dump(data, f)
    print("Written updated thinning values to ThinningQuality.txt")


def main():
    df = pd.read_csv(FPATH_CARD_DATA, sep=";", header=0)
    # print(df.columns)
    # get_attack_types(df)
    # assign_attack_strength(df)
    # assign_interactivity_value(df)
    # reevaluate_draw_quality()
    # reevaluate_village_quality()
    # reevaluate_thinning_quality()
    # get_draw_quality(df)
    # get_village_quality(df)
    # get_trashing_quality(df)
    return df


if __name__ == "__main__":
    df = main()

    with open(f"../card_info/specifics/VillageQuality.txt", "r") as f:
        data = json.load(f)
    for i, stufe in enumerate(["Weak", "Medium strength", "Strong"], start=1):
        print(f"{stufe} villages:")
        print(", ".join([key for key, val in data.items() if val == i]))
