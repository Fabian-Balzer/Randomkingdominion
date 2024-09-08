"""Interactions that occur with on_start_of_turn"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import add_interaction


def _add_individual_on_start_of_turn_interactions(df: pd.DataFrame):
    add_interaction(
        "hireling",
        "mastermind",
        "If you play Hireling at the start of your turn using Mastermind, you will draw three cards immediately.",
        df,
    )
    add_interaction(
        "hireling",
        "piazza",
        "If you play Hireling at the start of your turn using Piazza, you will draw a card immediately.",
        df,
    )
    add_interaction(
        "samurai",
        "mastermind",
        "If you play Samurai at the start of your turn using Mastermind, you will get +$3 immediately.",
        df,
    )
    add_interaction(
        "samurai",
        "piazza",
        "If you play Samurai at the start of your turn using Piazza, you will get +$1 immediately.",
        df,
    )
    add_interaction(
        "capitalism",
        "fishmonger",
        f"During your buy phase, you can play Fishmongers from your deck if you have bought Capitalism.{TGG_BUG_DISCLAIMER}",
        df,
    )
    add_interaction(
        "ninja",
        "invasion",
        f"When buying Invasion, you may play a Ninja from your deck as the Attack.",
        df,
    )


##########################################################################################################
# Final function
def add_all_on_start_of_turn_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all on_start_of_turn interactions to the DataFrame."""
    num_before = len(df)
    _add_individual_on_start_of_turn_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} on-start-of-turn interactions.")
