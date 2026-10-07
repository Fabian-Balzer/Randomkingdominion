"""Interactions that occur with discarding stuff"""

import pandas as pd

from ....logger import LOGGER
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_arena_interactions(df: pd.DataFrame):
    arena_disc = "Arena/Weaver|Trail|Village Green|Faithful Hound---You may still discard a card like {card_b} for Arena even if there are no more VP tokens available. Be aware that there might be an Autoplay in the online clients skipping over this step that you'll have to turn off."
    add_multiple_interactions_from_single(arena_disc, df)


def _add_vassal_interactions(df: pd.DataFrame):
    vassal_disc = "Vassal/Village Green|Trail|Weaver---If you discard a {card_b} with Vassal and play it due to the discard effect, you don't get to play it again from the Vassal effect."
    add_multiple_interactions_from_single(vassal_disc, df)
    vassal_faith = "Vassal/Faithful Hound---If you discard Faithful Hound with Vassal and choose to set it aside, you cannot play it and vice versa. Note that there might be an Autoplay in the online clients skipping over this step (always setting aside the Faithful Hounds) that you might have to turn off."
    add_multiple_interactions_from_single(vassal_faith, df)


def _add_all_deck_into_discard_interactions(df: pd.DataFrame):
    deck_disc = "Scavenger|Chancellor|Messenger|Herb Gatherer|Trusty Steed/Trail|Village Green|Weaver|Tunnel|Faithful Hound---Playing {card_a} with a {card_b} in your deck does not count as discarding {card_b}, so you do not get to react."
    add_multiple_interactions_from_single(deck_disc, df)
    deck_disc = "Order of Masons|Avoid|Bad Omens/Trail|Village Green|Weaver|Tunnel|Faithful Hound---Putting cards into your discard pile via {card_a} with a {card_b} in your deck does not count as discarding {card_b}, so you do not get to react."
    add_multiple_interactions_from_single(deck_disc, df)


def _add_cutthroat_interaction(df: pd.DataFrame):
    rule = "If you activate a Tunnel by discarding to Cutthroat's attack, the Gold you gain from Tunnel won't activate said Cutthroat's Loot gaining effect."
    add_interaction("Cutthroat", "Tunnel", rule, df)


##########################################################################################################
# Final function
def add_all_on_discard_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all discarding interactions to the DataFrame."""
    num_before = len(df)
    _add_arena_interactions(df)
    _add_vassal_interactions(df)
    _add_all_deck_into_discard_interactions(df)
    _add_cutthroat_interaction(df)
    if verbose:
        LOGGER.info(f"Added {len(df) - num_before} discarding interactions.")
