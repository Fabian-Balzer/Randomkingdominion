"""Interactions that occur when you might play a victory card that's not meant for being played."""

import pandas as pd

from ..interaction_util import add_interaction


def _add_grand_castle_interactions(df: pd.DataFrame):
    add_interaction(
        "Grand Castle",
        "Stronghold",
        "When you gain Grand Castle, you get points for opponent's Strongholds because they are in play.",
        df,
    )
    add_interaction(
        "Grand Castle",
        "Inheritance",
        "When you gain Grand Castle, you get points for opponent's Estates if they are in play because they inherited a Duration.",
        df,
    )


def _add_victory_card_play_interactions(df: pd.DataFrame):
    # Playing useless victory cards:
    add_interaction(
        "Hasty",
        "Territory",
        "[Only if Hasty is on the Clashes pile] If the Clashes pile is Hasty and you gain a Territory, you set it aside and play it at the start of your next turn (doing nothing, but counting as a card in play). At the end of that turn, you discard it from play.",
        df,
    )
    add_interaction(
        "Patient",
        "Territory",
        "[Only if Patient is on the Clashes pile] If the Clashes pile is Patient, you can set aside Territories and play them at the start of your next turn (doing nothing, but counting as a card in play). At the end of that turn, you discard them from play.",
        df,
    )
    add_interaction(
        "Inheritance",
        "Farmhands",
        "If you gain a Farmhands during your opponent's turn (e.g. due to Barbarian, Messenger, etc.) and they have bought Inheritance, you may set aside an Estate from your hand even if you have not bought Inheritance. In that case, it will be played at the start of your next turn (doing nothing, but counting as a card in play). At the end of that turn, you discard it from play.",
        df,
    )
    add_interaction(
        "Inheritance",
        "Warlord",
        "If you have inherited a card (e.g. Battle Plan) and are under Warlord attack, you may both play two copies of said card and two Estates during your turn.",
        df,
    )


##########################################################################################################
# Final function
def add_all_victory_card_play_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all victory card play interactions to the DataFrame."""
    num_before = len(df)
    _add_grand_castle_interactions(df)
    _add_victory_card_play_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} victory card playing interactions.")
