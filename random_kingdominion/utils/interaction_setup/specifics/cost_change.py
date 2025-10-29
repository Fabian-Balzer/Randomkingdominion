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
        "Even if you have an empty discard pile while overpaying on the Stonemason buy, it will be gained (to your discard pile) first, causing the Fisherman to cost $5 for the overpay.",
        df,
    )
    add_interaction(
        "Charm",
        "Destrier",
        "If you choose the 'Gain Card with same cost' option for two Charms and then buy a Destrier (e.g. costing $6 at that moment), you will first gain the Destrier, then another card costing $5, then one costing $4 (and Destriers will cost $3).\nIf, after playing Charms, you gain some other card costing $6, you may not gain a Destrier that cost $6 prior to that as it will change its cost to $5 due to the gain.",
        df,
    )
    add_interaction(
        "Charm",
        "Wayfarer",
        "If you choose the 'Gain Card with same cost' option, you will always (unless you gain another card in-between somehow with e.g. Haggler) be able to gain a Wayfarer off of any card you gain next, since Wayfarer changes its cost to said card. This even works with Debt and Potion cost cards.",
        df,
    )
    add_interaction(
        "Ferry",
        "Wayfarer",
        "If you put the -$2 token on Wayfarer, it will cost $4 at the beginning of your turn, but then change its cost to the one of the next card you gain (and not $2 less than that). Also, if you put the -$2 token on the last card you gained (e.g. via a Workshop) earlier during a turn, Wayfarer's cost will change with it.",
        df,
    )
    add_interaction(
        "Family of Inventors",
        "Wayfarer",
        "Wayfarer will assume the cost of the card you gained last, even if a Favor token has been put on its pile. If you reduce the cost of the last-gained card with a Favor at the beginning of your Buy phase, Wayfarer's cost will change along with that.",
        df,
    )
    add_interaction(
        "Charm",
        "Fisherman",
        "If you choose the 'Gain Card with same cost' option for Charm and then gain a Fisherman costing $2 (and it goes to your discard pile), you will be able to gain a $5-cost card from Charm. Conversely, you could gain a $5-cost card first (to your discard pile), and then gain Fisherman off the Charm.",
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
        "Destrier",
        "Wayfarer",
        "When gaining a Destrier, Wayfarer will cost as much as the Destrier costs after the gain (e.g. if you buy Destrier for $6, Wayfarer will cost $5 afterwards).",
        df,
    )
    add_interaction(
        "Taskmaster",
        "Fisherman",
        "For Taskmaster, the cost of Fisherman when you gain it is important, you will not renew Taskmaster's ability if Fisherman costs $2 when (before) you gain it.",
        df,
    )
    add_interaction(
        "Taskmaster",
        "Destrier",
        "For Taskmaster, the cost of Destrier when you gain it is important. You will only renew Taskmaster's ability if Destrier costs $5 at the moment you gain it.",
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
    add_interaction(
        "Fisherman",
        "Livery",
        "After having played Livery, Fisherman's cost is evaluated when you gain it, so you will not gain a Horse when gaining a Fisherman that costs $2.",
        df,
    )
    add_interaction(
        "Destrier",
        "Livery",
        "After having played Livery, Destrier's cost is evaluated when you gain it, so you will be able to gain a Horse even if the cost of Destrier is less than $4 afterwards.",
        df,
    )
    add_interaction(
        "Wayfarer",
        "Quarry",
        "Wayfarer will always have the same cost as the last card you gained using it. Therefore, if you gain a Silver, then play Quarry, Wayfarer will still cost $3. If you gain an Action card costing $3, then play Quarry, Wayfarer will also cost $1.",
        df,
    )


def _add_stonemason_potion_interactions(df: pd.DataFrame):
    potion_cost_cards = [
        "Alchemist",
        "Apothecary",
        "Familiar",
        "Golem",
        "Scrying Pool",
        "University",
        "Possession",
    ]

    for card in potion_cost_cards:
        add_interaction(
            "Stonemason",
            card,
            f"You may overpay with Potions when buying Stonemason to gain two {card}s.",
            df,
        )


##########################################################################################################
# Final function
def add_all_cost_change_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all cost change interactions to the DataFrame."""
    num_before = len(df)
    _add_individual_cost_change_interactions(df)
    _add_stonemason_potion_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} cost change interactions.")
