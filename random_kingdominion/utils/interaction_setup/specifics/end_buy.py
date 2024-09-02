"""Interactions that occur when a card or event ends the Buy Phase."""

import pandas as pd

from ..constants import AFFECTED_BY_END_BUY, BACK_TO_ACTION_CSOS
from ..interaction_util import add_interaction


def _add_end_buy_interaction(card_a: str, card_b: str, df: pd.DataFrame):
    if card_a in ["Hermit", "Exploration"] and card_b != "Launch":
        rule = f"When you return to your Action phase using {card_b}, you are ending your Buy phase but gain a card at the same time, so {card_a} can't trigger. {card_a} can still trigger at the end of a future buy phase."
    else:
        rule = f"When you return to your Action phase using {card_b}, you are ending your Buy phase, so {card_a} can trigger."
    add_interaction(card_a, card_b, rule, df)


def _add_end_buy_river_shrine_interaction(buy_ending_cso: str, df: pd.DataFrame):
    rule = f"You can only gain cards via River Shrine if you didn't gain any cards in any buy phase during your turn. Therefore, you ."
    if buy_ending_cso == "Launch":
        rule += f"can only do so if you didn't gain any cards both in the Launch- and after-Launch buy phase."
    else:
        rule += f"can never do so after buying {buy_ending_cso}, even if you don't gain cards in your last buy phase."
    add_interaction(buy_ending_cso, "River Shrine", rule, df)


def _add_footpad_end_of_buy_phase_interaction(buy_ending_cso: str, df: pd.DataFrame):
    if buy_ending_cso == "Launch":
        return
    rule = f"If you return to your Action phase using {buy_ending_cso}, you are still gaining the card during the Buy phase, so Footpad's ability doesn't trigger."
    add_interaction("Footpad", buy_ending_cso, rule, df)


def _add_gatekeeper_end_of_buy_phase_interaction(buy_ending_cso: str, df: pd.DataFrame):
    if buy_ending_cso == "Launch":
        return
    rule = f"If you return to your Action phase using {buy_ending_cso}, you get to choose whether you first resolve {buy_ending_cso} or Gatekeeper."
    add_interaction("Gatekeeper", buy_ending_cso, rule, df)


##########################################################################################################
# Final function
def add_all_end_buy_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all buy-phase-ending interactions to the DataFrame."""
    num_before = len(df)
    for card_b in BACK_TO_ACTION_CSOS:
        for card_a in AFFECTED_BY_END_BUY:
            _add_end_buy_interaction(card_a, card_b, df)
        _add_end_buy_river_shrine_interaction(card_b, df)
        _add_footpad_end_of_buy_phase_interaction(card_b, df)
        _add_gatekeeper_end_of_buy_phase_interaction(card_b, df)
    add_interaction(
        "Demand",
        "Cavalry",
        "If you Demand a Cavalry, you will gain a Horse and the Cavalry on top of your deck, then draw them, and return to your Action phase.",
        df,
    )
    add_interaction(
        "Demand",
        "Villa",
        "If you Demand a Villa, you will gain a Horse and the Villa on top of your deck, get +1 Action, and return to your Action phase.",
        df,
    )

    if verbose:
        print(f"Added {len(df) - num_before} end-buy interactions.")
