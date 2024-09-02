import numpy as np
import pandas as pd

from ...constants import COFFER_GIVERS, DEBT_INDUCERS


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
        extra_components.append("-$1 tokens")
    if name in ["Relic", "Borrow", "Raid"]:
        extra_components.append("-Card tokens")
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
            "+$1 tokens",
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
