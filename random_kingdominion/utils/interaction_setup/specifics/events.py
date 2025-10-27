"""Interactions that occur with events"""

import pandas as pd

from ....constants import ROTATOR_DICT, SPLITPILE_DICT
from ..constants import KNIGHTS, RUINS, TOKEN_EVENTS
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_populate_split_pile_interaction(pile_name: str, df: pd.DataFrame):
    rule = f"Buying Populate will gain the top card of the {pile_name} pile, even if it's not an Action card."
    add_interaction(pile_name, "Populate", rule, df)


def _add_populate_interactions(df: pd.DataFrame):
    castle_stuff = "Buying Populate will never gain any Castle, even if Small Castle or Opulent Castle is on top, since the Castles are not an Action supply pile."
    add_interaction("Castles", "Populate", castle_stuff, df)
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
    add_interaction(
        "Populate",
        "Enlightenment",
        "Even if Enlightenment is active, you will not gain Treasures that you wouldn't otherwise have gained, as they do not become Action Supply piles.",
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
    add_interaction("Castles", event, rule, df)
    split_and_rot_split_piles = (
        list(SPLITPILE_DICT.keys()) + list(ROTATOR_DICT.keys()) + ["Ruins", "Knights"]
    )
    for pile in split_and_rot_split_piles:
        rule = f"You may put the {token} token on the {pile} pile using {event}. This will affect all of its cards."
        add_interaction(pile, event, rule, df)
    for traveller in ["Page", "Peasant"]:
        rule = f"Putting the {token} token on the {traveller} pile using {event} will affect only {traveller}, not any card you exchange it for."
        add_interaction(traveller, event, rule, df)
    rule = f"If you have put the {token} token on any pile using {event}, you may not put further tokens on it with Teacher."
    add_interaction("Peasant", event, rule, df, add_together_if_present=True)
    if event not in ["Plan", "Ferry"]:
        rule = f"Once Divine Wind is triggered, the {token} token is removed from its pile upon the pile's removal if you have bought {event} before that."
        add_interaction(event, "Divine Wind", rule, df)
    if event == "Seaway":
        rule = f"After buying Inheritance, you may gain an Estate and put your +Buy token on it using Seaway."
        add_interaction("Inheritance", event, rule, df)
        return
    rule = f"Even after buying Inheritance, you may not put the {token} token on the Estate pile using {event} as it's not an Action supply pile."
    add_interaction("Inheritance", event, rule, df)
    rule = f"Even if Enlightenment is active, you may not put the {token} token on any Treasure pile using {event} as it's not natively an Action supply pile."
    add_interaction("Enlightenment", event, rule, df)


def _add_individual_event_interactions(df: pd.DataFrame):
    # INVEST
    castle_stuff = "Invest/Castles---You can Invest in Small Castle or Opulent Castle if it's on top, but would only draw cards if an opponent gained a copy of it (which is not possible in 2-player mode)."
    add_multiple_interactions_from_single(castle_stuff, df)
    knight_stuff = f"Invest/Knights---You can Invest in Knights, but this will never draw you cards (since your opponent will never gain a copy of them) and they might be stranded in Exile."
    add_multiple_interactions_from_single(knight_stuff, df)
    ruins_stuff = f"Invest/Ruins---You can Invest in Ruins, but you will only draw cards if another player gains a copy of the exact Ruins you exiled."
    add_multiple_interactions_from_single(ruins_stuff, df)
    for event, token in TOKEN_EVENTS.items():
        _add_token_event_interactions(event, token, df)
    add_interaction(
        "Borrow",
        "Relic",
        "If the -1 Card token is already on your deck, buying Borrow will not give you +1$. Note that as of 2025-10, this is bugged in the TGG app, and you will get +1$ anyway.",
        df,
    )
    minus_card_stuff = "Relic|Borrow|Raid/Library|Watchtower|Jack of all Trades|Cursed Village|Way of the Owl|Siren|First Mate|Ronin---If you have your -1 Card Token on your deck when drawing with {card_b}, the Token is removed and the number of cards drawn to is the same as stated on {card_b} as long as you are supposed to draw at least 1 card."
    add_multiple_interactions_from_single(minus_card_stuff, df)
    minus_card_blacksmith = "Relic|Borrow|Raid/Townsfolk---If you have your -1 Card Token on your deck when drawing with Blacksmith, the Token is removed and the number of cards drawn to is the same as stated on Blacksmith as long as you are supposed to draw at least 1 card."
    add_multiple_interactions_from_single(minus_card_blacksmith, df)


##########################################################################################################
# Final function
def add_all_event_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all event interactions to the DataFrame."""
    num_before = len(df)
    _add_populate_interactions(df)
    _add_individual_event_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} event interactions.")
