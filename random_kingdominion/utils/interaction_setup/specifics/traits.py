"""Interactions that occur with trait"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_individual_trait_interactions(df: pd.DataFrame):
    add_interaction(
        "Cheap",
        "Plateau Shepherds",
        "If Cheap is assigned to a card initially costing $3, it becomes a $2 cost card as far as Plateau Shepherds (PS) is concerned. Conversely, a card reduced to costing $1 due to Cheap will not be eligible for PS anymore.",
        df,
    )
    add_interaction(
        "Frigate",
        "Fellowship of Scribes",
        "If you're under the Frigate attack, you can choose the order of discarding/drawing with Scribes, i.e. after playing an Action, you may first discard down to 4 cards in hand, and then use a Favor to draw 1 card, or (if you already had only 4 cards in hand) draw 1 card using Scribes and then discard down to 4 again.",
        df,
    )
    # Many more reckless interactions in the on-clean-up file.
    add_interaction(
        "Reckless",
        "Conspirator",
        "A Reckless card is not played twice as far as Conspirator is concerned. That means if you e.g. Reckless were on Conspirator and you would play it as the second Action this turn, you would only get +$4, not +$4 and +1 Card, +1 Action.",
        df,
    )
    add_interaction(
        "Reckless",
        "Crossroads",
        "If Crossroads is Reckless, the first time you play one will give you +6 Actions.",
        df,
    )
    add_interaction(
        "Inspiring",
        "Highwayman",
        "If you play an Inspiring Treasure as your first Treasure while under the Highwayman attack, you can still play a unique Action card with it.",
        df,
    )

    clerk_allies = "Desert Guides|Cave Dwellers/Clerk---You may react Clerks both before and after using Favors for {card_a}, but not in-between; you could e.g. react Clerk, use {card_a} two times, and then react another Clerk you've just drawn. After that, you may not use {card_a} again."
    add_multiple_interactions_from_single(clerk_allies, df)


##########################################################################################################
# Final function
def add_all_trait_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all trait interactions to the DataFrame."""
    num_before = len(df)
    # Tireless/Panic is in Prophecies.
    _add_individual_trait_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} trait interactions.")
