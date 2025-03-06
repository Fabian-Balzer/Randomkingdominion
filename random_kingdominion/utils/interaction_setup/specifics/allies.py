"""Interactions that occur with allies"""

import pandas as pd

from ....logger import LOGGER
from ..interaction_util import add_interaction


def _add_all_city_state_interactions(df: pd.DataFrame):
    # More in the on-gain file.
    add_interaction(
        "Sycophant",
        "City-State",
        "You can immediately use the Favors from gaining Sycophant to play it using City-State.",
        df,
    )
    add_interaction(
        "Guildmaster",
        "City-State",
        "After having played a Guildmaster, when you gain a card, you can immediately use the Favors from that gain to play it using City-State.",
        df,
        add_together_if_present=True,
    )


def _add_individual_allies_interactions(df: pd.DataFrame):
    add_interaction(
        "Sycophant",
        "Peaceful Cult",
        "You cannot immediately use the Favors from trashing Sycophant with Peaceful Cult (as the latter doesn't say 'Repeat as desired').",
        df,
    )
    add_interaction(
        "Market Towns",
        "Leprechaun",
        "At the start of your Buy phase, you may choose the order of returning Envious or Deluded, and playing Actions with Market Towns. If you play a Leprechaun at the start of your Buy phase and receive Envious or Deluded, you return it that same turn.",
        df,
    )


##########################################################################################################
# Final function
def add_all_allies_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all allies interactions to the DataFrame."""
    num_before = len(df)
    _add_all_city_state_interactions(df)
    _add_individual_allies_interactions(df)
    if verbose:
        LOGGER.info(f"Added {len(df) - num_before} allies interactions.")
