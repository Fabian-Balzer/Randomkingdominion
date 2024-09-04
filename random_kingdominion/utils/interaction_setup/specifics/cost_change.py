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
    add_interaction(
        "Destrier",
        "Border Village",
        "Even if a Border Village is the first card you gain this turn, you may gain a Destrier off of it.",
        df,
    )
    add_interaction(
        "Destrier",
        "Haggler",
        "Destrier's cost will be evaluated after each gain, so if you buy a Destrier costing $6, you may gain a card cheaper than $5 afterwards from Haggler. On the other hand, you may gain an initially $6-costing Destrier off of a Gold buy.",
        df,
    )
    add_interaction(
        "Destrier",
        "Architect's Guild",
        "Destrier's cost will be evaluated after each gain, so if you gain a Destrier costing $6, you may gain a card cheaper than $5 afterwards using Architect's Guild. On the other hand, you may gain an initially $6-costing Destrier off of a Gold gain using Architect's Guild.",
        df,
    )
    add_interaction(
        "Destrier",
        "Growth",
        "Destrier's cost will be evaluated after each gain, so you may gain an initially $6-costing Destrier off of a Gold gain when Growth is active.",
        df,
    )
    add_interaction(
        "Fisherman",
        "Architect's Guild",
        "Fisherman's cost will be evaluated after each gain, so if you e.g. gain a Fisherman for $2, you may use two Favors to gain a card costing less than $5 (as long as the Fisherman is in the Discard Pile). On the other hand, you normally cannot gain a Fisherman for $2 off of a $5 cost gain using Architect's Guild.",
        df,
    )
    add_interaction(
        "Fisherman",
        "Haggler",
        "Fisherman's cost will be evaluated after each gain, so if you e.g. buy a Fisherman for $2 after having played a Haggler, you will be able to gain a card costing less than $5 (as long as the Fisherman is in the Discard Pile). On the other hand, you normally cannot gain a Fisherman for $2 off of a $5 cost gain.",
        df,
    )
    add_interaction(
        "Fisherman",
        "Growth",
        "Fisherman's cost will be evaluated after each gain, so you can usually not gain one after having gained a Silver when Growth is active.",
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
