"""Interactions that occur with events"""

import pandas as pd

from ....constants import ROTATOR_DICT, SPLITPILE_DICT
from ..constants import KNIGHTS, RUINS, TOKEN_EVENTS
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_populate_split_pile_interaction(pile_name: str, df: pd.DataFrame):
    rule = f"Buying Populate will gain the top card of the {pile_name} pile, even if it's not an Action card."
    add_interaction(pile_name, "Populate", rule, df)


def _add_populate_interactions(df: pd.DataFrame):
    add_interaction(
        "Castles",
        "Populate",
        "Buying Populate will not gain Castles, even if the Castle on top is an Action card, since they are not an Action supply pile.",
        df,
    )
    castle_stuff = "Small Castle|Opulent Castle/Populate---Buying Populate will never gain {card_a}, even if it is on top, since the Castles are not an Action supply pile."
    add_multiple_interactions_from_single(castle_stuff, df)
    add_interaction(
        "Ruins",
        "Populate",
        "Buying Populate will gain the Ruins card currently on top since they are an Action Supply pile.",
        df,
    )
    add_interaction(
        "Knights",
        "Populate",
        "Buying Populate will gain the top card of the knights pile.",
        df,
    )
    add_interaction(
        "Populate",
        "Inheritance",
        "If you have bought Inheritance, you still will not gain an Estate from buying Populate since Populate only gains cards from Action Supply piles, and Estate is still just a Victory Supply pile.",
        df,
    )
    for pile_name in [
        "Gladiator/Fortune",
        "Catapult/Rocks",
        "Clashes",
        "Encampment/Plunder",
    ]:
        _add_populate_split_pile_interaction(pile_name, df)


def _add_token_event_interactions(event: str, token: str, df: pd.DataFrame):
    rule = f"You can never put the {token} token on the Castles pile (even with Small or Opulent Castle on top) because they are only a Victory Supply pile, not an Action supply pile."
    splitpiles = (
        list(SPLITPILE_DICT.keys()) + list(ROTATOR_DICT.keys()) + ["Ruins", "Knights"]
    )
    for pile in splitpiles:
        rule = f"You may put the {token} token on the {pile} pile using {event}. This will affect all of its cards."
        add_interaction(pile, event, rule, df)
    for traveller in ["Page", "Peasant"]:
        rule = f"Putting the {token} token on the {traveller} pile using {event} will affect only {traveller}, not any card you exchange it for."
    if event not in ["Plan", "Ferry"]:
        rule = f"Once Divine Wind is triggered, the {token} token is removed from its pile upon the pile's removal if you have bought {event} before that."
        add_interaction(event, "Divine Wind", rule, df)
    if event == "Seaway":
        rule = f"After buying Inheritance, you may gain an Estate and put your +Buy token on it using Seaway."
        add_interaction("Inheritance", event, rule, df)
        return
    rule = f"Even after buying Inheritance, you may not put the {token} token on the Estate pile using {event} as it's not an Action supply pile."
    add_interaction("Inheritance", event, rule, df)
    for castle in ["Small Castle", "Opulent Castle", "Castles"]:
        add_interaction(castle, event, rule, df)


def _add_individual_event_interactions(df: pd.DataFrame):
    # INVEST
    castle_stuff = "Invest/Small Castle|Opulent Castle---You can Invest in {card_b} if it's on top, but would only draw cards if an opponent gained a copy of it (which is not possible in 2-player mode)."
    add_multiple_interactions_from_single(castle_stuff, df)
    knights = "|".join(KNIGHTS)
    knight_stuff = f"Invest/Knights|{knights}---You can Invest in Knights, but this will never draw you cards (since your opponent will never gain a copy of them) and they might be stranded in Exile."
    add_multiple_interactions_from_single(knight_stuff, df)
    ruins = "|".join(RUINS)
    ruins_stuff = f"Invest/{ruins}---You can Invest in Ruins, but you will only draw cards if another player gains a copy of the exact Ruins you exiled."
    add_multiple_interactions_from_single(ruins_stuff, df)
    for event, token in TOKEN_EVENTS.items():
        _add_token_event_interactions(event, token, df)


##########################################################################################################
# Final function
def add_all_event_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all event interactions to the DataFrame."""
    num_before = len(df)
    _add_populate_interactions(df)
    _add_individual_event_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} event interactions.")
