"""Interactions that occur with prophecy"""

import pandas as pd

from ..constants import (
    ACTION_TREASURES,
    ALL_LOOTS,
    GATHERING_CARDS,
    TGG_BUG_DISCLAIMER,
    TRAVELLER_BASE_CARDS,
)
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_gathering_divine_wind_interaction(other: str, df: pd.DataFrame):
    rule = f"Once Divine Wind is triggered and the {other} pile is removed from the supply, since there is no pile to gather VP tokens on, the gathering will have no effect."
    add_interaction("Divine Wind", other, rule, df)


def _add_traveller_divine_wind_interaction(other: str, df: pd.DataFrame):
    rule = f"Once Divine Wind is triggered and the {other} pile is removed from the supply, you cannot exchange your {other}s for other Travellers anymore since they have no pile to return to. You can however continue to exchange any Travellers further up the line as their non-supply piles stay."
    add_interaction("Divine Wind", other, rule, df)


def _add_individual_divine_wind_interactions(df: pd.DataFrame):
    add_interaction(
        "divine_wind",
        "encampment",
        "Once Divine Wind has been triggered, when you play an Encampment that came from the initial supply, if you don't reveal a Gold or Plunder, then you set aside the Encampment but since it has no pile to return to, it stays set aside for the rest of the game (it still counts as one of your cards for scoring).",
        df,
    )
    add_interaction(
        "divine_wind",
        "experiment",
        "Once Divine Wind has been triggered, when you play an Experiment that came from the initial supply, you get +2 Cards and +1 Action, but it does not return to a pile and stays in play. This is because Experiment does not have a pile to return to.",
        df,
    )
    add_interaction(
        "divine wind",
        "way of the horse",
        "Once Divine Wind has been triggered, if you play any card from the initial supply using Way of the Horse, you get +2 Cards and +1 Action, but it does not return to a pile as the pile to return to doesn't exist any longer.",
        df,
    )
    add_interaction(
        "divine wind",
        "way of the butterfly",
        "Once Divine Wind has been triggered, if you play any card from the initial supply using Way of the Butterfly, it cannot to its pile, and will fail to do anything except for going into your play area.",
        df,
    )
    add_interaction(
        "divine wind",
        "obelisk",
        "Once Divine Wind has been triggered, cards from the initial Obelisk pile will continue to be worth 2 VP.",
        df,
    )
    add_interaction(
        "divine wind",
        "young witch",
        "Once Divine Wind has been triggered, cards from the initial Bane pile will continue to be the Bane.",
        df,
    )
    add_interaction(
        "divine wind",
        "snake witch",
        "Once Divine Wind has been triggered, previously gained Snake Witches will never be able to Curse as they do not have a pile to return to.",
        df,
    )


def _add_all_divine_wind_interactions(df: pd.DataFrame):

    for gathering_cso in GATHERING_CARDS:
        _add_gathering_divine_wind_interaction(gathering_cso, df)

    for traveller_base_cso in TRAVELLER_BASE_CARDS:
        _add_traveller_divine_wind_interaction(traveller_base_cso, df)

    _add_individual_divine_wind_interactions(df)


def _add_enlightenment_interactions(df: pd.DataFrame):
    act_treas_str = (
        "|".join(ACTION_TREASURES)
        + "/Enlightenment---If Enlightenment is active, {card_a}'s Action phase mode is overwritten by Enlightenment."
    )
    add_multiple_interactions_from_single(act_treas_str, df)
    add_interaction(
        "Capitalism",
        "Enlightenment",
        "Once Enlightenment is active, Capitalism will turn all of its targets into cantrips during the Action phase.",
        df,
    )


def _add_panic_interactions(df: pd.DataFrame):
    for loot in ALL_LOOTS:
        if loot in ["Endless Chalice", "Jewels"]:
            inter = f"Since you never discard {loot} from play after playing it (bar e.g. Highwayman), you never return it for Panic."
        else:
            inter = f"When you discard {loot} from play while Panic is active, you return it to the top of the Loot pile. When discarding multiple, you get to choose the order."
        add_interaction("Panic", loot, inter, df)
    add_interaction(
        "panic",
        "tireless",
        f"When Tireless is on a Treasure and Panic is active, when discarding it from play you may decide whether to set it aside or return it to its pile.{TGG_BUG_DISCLAIMER}",
        df,
    )
    add_interaction(
        "panic",
        "capital",
        f"When discarding Capital from play and Panic is active, you need to return it to its pile and also get +6 Debt.",
        df,
    )


def _add_progress_interactions(df: pd.DataFrame):
    add_interaction(
        "Progress",
        "Continue",
        "When you buy Continue when Progress is active, you have to topdeck the gained card and won't be able to play it.",
        df,
    )


##########################################################################################################
# Final function
def add_all_prophecy_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all prophecy interactions to the DataFrame."""
    num_before = len(df)
    _add_all_divine_wind_interactions(df)
    _add_enlightenment_interactions(df)
    _add_panic_interactions(df)
    _add_progress_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} prophecy interactions.")
