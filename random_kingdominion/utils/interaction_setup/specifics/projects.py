"""Interactions that occur with projects"""

import pandas as pd

from random_kingdominion.utils.utils import get_cso_name

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)


def _add_sewers_interactions(df: pd.DataFrame):
    add_interaction(
        "priest",
        "sewers",
        "If you trash a card with Sewers in reaction to Priest's trash, Sewers does not give you the extra $2 from Priest's ability. This is because Sewers triggers after Priest's 'Trash a card from your hand' which is before 'For the rest of this turn, when you trash a card, + $2.'",
        df,
    )
    add_interaction(
        "forager",
        "sewers",
        "If you trash a Treasure that is unique to the trash with Sewers in reaction to Forager's trashing, said Treasure will be considered by Forager's check for unique Treasures, i.e. yield $.",
        df,
    )
    add_interaction(
        "mountain shrine",
        "sewers",
        "If you trash an Action card using Sewers in reaction to Mountain Shrine's trashing, said Action will be considered by Mountain Shrine's check for Actions, and you will draw 2 cards even if that's the only Action in the trash.",
        df,
    )


##########################################################################################################
# Final function
def add_all_project_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all project interactions to the DataFrame."""
    num_before = len(df)
    _add_sewers_interactions(df)
    # Fleet interactions on extra turn page.
    if verbose:
        print(f"Added {len(df) - num_before} project interactions.")
