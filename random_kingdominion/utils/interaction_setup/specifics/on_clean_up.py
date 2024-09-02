"""Interactions that occur with on_clean_up"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)


def _add_individual_on_cleanup_interactions(df: pd.DataFrame):
    add_interaction(
        "Journey",
        "Alchemist",
        "If you play Alchemists and Potion and buy Journey, you may topdeck the Alchemists for the Journey turn.",
        df,
    )
    add_interaction(
        "Journey",
        "Walled Village",
        "If you have no more than one other Action than the Walled Village in play, you can topdeck it for the Journey turn.",
        df,
    )
    add_interaction(
        "Reckless",
        "Alchemist",
        "If Alchemist is Reckless, you may topdeck if you have a Potion in play, circumventing Reckless' return-to-pile prompt.",
        df,
    )
    add_interaction(
        "trail",
        "improve",
        "Trashing a Trail with Improve's ability will not trigger Trail's on-trash effect because the trashing occurs during Clean-up.",
        df,
    )
    add_interaction(
        "trail",
        "river shrine",
        "Gaining a Trail with River Shrine's ability will not trigger Trail's on-gain effect because the gaining occurs during Clean-up.",
        df,
    )
    add_interaction(
        "cargo_ship",
        "improve",
        "If you play a Cargo Ship and don't set anything aside with it before your Clean-up phase, Improve can trash it because it's going to be discarded as far as you know at that point. However, trashing a card from play does not negate its instructions, so you can still set aside the card you gain from Improve (or another card you gain that turn) through the instructions of Cargo Ship.",
        df,
    )
    add_interaction(
        "Highwayman",
        "capital",
        "If you are under Highwayman attack and play Capital as your first Treasure, you do not get +6$ and +1 Buy; however, you will still get 6D when discarding Capital from play.",
        df,
    )


##########################################################################################################
# Final function
def add_all_on_clean_up_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all on_clean_up interactions to the DataFrame."""
    num_before = len(df)
    _add_individual_on_cleanup_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} on_clean_up interactions.")
