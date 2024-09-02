"""Interactions that occur with events"""

import pandas as pd

from ..interaction_util import add_interaction


def _add_populate_split_pile_interaction(pile_name: str, df: pd.DataFrame):
    rule = f"Buying Populate will gain the top card of the {pile_name} pile, even if it's not an Action card."
    add_interaction(pile_name, "Populate", rule, df)


def _add_populate_interactions(df: pd.DataFrame):
    add_interaction(
        "Castles",
        "Populate",
        "Buying Populate will not gain Castles, even if the Castle on top is an Action card, since they are not an Action supply pile.",
        df,
    )
    add_interaction(
        "Ruins",
        "Populate",
        "Buying Populate will gain the Ruins card currently on top since they are an Action Supply pile.",
        df,
    )
    add_interaction(
        "Knights",
        "Populate",
        "Buying Populate will gain the top card of the knights pile.",
        df,
    )
    for pile_name in [
        "Gladiator/Fortune",
        "Catapult/Rocks",
        "Clashes",
        "Encampment/Plunder",
    ]:
        _add_populate_split_pile_interaction(pile_name, df)


##########################################################################################################
# Final function
def add_all_event_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all event interactions to the DataFrame."""
    num_before = len(df)
    _add_populate_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} event interactions.")
