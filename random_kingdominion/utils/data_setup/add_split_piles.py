import pandas as pd

from ...constants import ROTATOR_DICT, SPLITPILE_DICT


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
        "Ruins": {
            "Name": "Ruins",
            "Expansion": "Dark Ages",
            "Types": "Action - Ruins",
            "Cost": "$0",
            "Text": "If any Kingdom card has the type Looter (Cultist, Death Cart, and Marauder have this type), then the Ruins pile is used this game. Shuffle the Ruins cards, then count out 10 per player after the first - 10 for two players, 20 for three players, and so on. Put the pile face down with the top card face up. The remaining Ruins are not used this game.",
            "IsLandscape": False,
            "IsOtherThing": True,
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
