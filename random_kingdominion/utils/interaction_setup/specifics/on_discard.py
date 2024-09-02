"""Interactions that occur with discarding stuff"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)


def _add_arena_interactions(df: pd.DataFrame):
    arena_disc = "Arena/Weaver|Trail|Village Green---You may still discard a card like {card_b} for Arena even if there are no more VP tokens available. Be aware that there might be an Autoplay in the online clients skipping over this step that you'll have to turn off."
    add_multiple_interactions_from_single(arena_disc, df)


def _add_vassal_interactions(df: pd.DataFrame):
    vassal_disc = "Vassal/Village Green|Trail|Weaver---If you discard a {card_b} with Vassal and play it due to the discard effect, you don't get to play it again from the Vassal effect."
    add_multiple_interactions_from_single(vassal_disc, df)


##########################################################################################################
# Final function
def add_all_on_discard_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all discarding interactions to the DataFrame."""
    num_before = len(df)
    _add_arena_interactions(df)
    _add_vassal_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} discarding interactions.")
