"""Interactions that occur with cards changing their costs"""

import pandas as pd

from ..interaction_util import add_interaction


def _add_individual_cost_change_interactions(df: pd.DataFrame):
    """Adds interactions involving destrier, fisherman, and wayfarer"""
    add_interaction(
        "stonemason",
        "destrier",
        "When you gain two Action cards each costing exactly the amount you overpaid, only one of them can ever be Destrier because its cost is checked as you gain it and not when you overpay.",
        df,
    )
    add_interaction(
        "stonemason",
        "wayfarer",
        "Wayfarer will at first assume Stonemason's $2 cost after the overpay, and then the cost of whichever card you choose to gain first.",
        df,
    )
    add_interaction(
        "stonemason",
        "fisherman",
        "Even if you have an empty discard pile while overpaying on the Stonemason buy, it will be gained (to your discard pile) first, causing the Fisherman to always cost $5 for the overpay.",
        df,
    )
    add_interaction(
        "Charm",
        "Destrier",
        "If you choose the 'Gain Card with same cost' option for two Charms and then gain a Destrier (e.g. costing $6 at that moment), you will first gain another card costing $6, then one costing $5, and then, at last, the Destrier (and Destriers will cost $4). If, after playing Charms, you gain some other card costing $6, you may gain a Destrier costing $6, but only once as it will cost $1 less afterwards.",
        df,
    )
    add_interaction(
        "change",
        "fisherman",
        "It is occasionally possible for cost reduction to make the gained card cost less $ than the trashed card after gaining. In this case the D incurred is the absolute value of the new $ difference. For example, if you trash a $2 Fisherman and gain a Silver, the Fisherman now costs $5, and you take 2D.",
        df,
    )
    add_interaction(
        "Fisherman",
        "Wayfarer",
        "After gaining a Fisherman to your Discard pile, even if it only cost $2, Wayfarer will cost $5 afterwards.",
        df,
    )
    add_interaction(
        "Taskmaster",
        "Fisherman",
        "For Taskmaster, the cost Fisherman has when you gain it is important.",
        df,
    )
    add_interaction(
        "Taskmaster",
        "Destrier",
        "For Taskmaster, the cost of Destrier when you gain it is important.",
        df,
    )


##########################################################################################################
# Final function
def add_all_cost_change_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all cost change interactions to the DataFrame."""
    num_before = len(df)
    _add_individual_cost_change_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} cost change interactions.")
