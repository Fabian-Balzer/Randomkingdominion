"""Interactions that occur with allies"""

import pandas as pd

from ....logger import LOGGER
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


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
    add_interaction(
        "Voyage",
        "City-State",
        "On your Voyage turn, when you gain an Action, you can (bar some exceptions) play it using City-State without that counting towards the three-card limit, even if you have already played three cards from your hand. Exceptions are gain-to-hand effects (like Swap or Sculptor).",
        df,
        add_together_if_present=True,
    )
    add_interaction(
        "Voyage",
        "Buried Treasure",
        "On your Voyage turn, when you gain a Buried Treasure, you can (bar some exceptions) play it immediately without that counting towards the three-card limit, even if you have already played three cards from your hand. Exceptions are gain-to-hand effects (like Sculptor).",
        df,
        add_together_if_present=True,
    )
    add_interaction(
        "Voyage",
        "Berserker",
        "On your Voyage turn, when you gain a Berserker, you can (bar some exceptions) play it immediately without that counting towards the three-card limit, even if you have already played three cards from your hand. Exceptions are gain-to-hand effects (like Swap or Sculptor).",
        df,
        add_together_if_present=True,
    )


def _add_all_plateau_shepherds_interactions(df: pd.DataFrame):
    add_interaction(
        "Cheap",
        "Plateau Shepherds",
        "[Relevant if Cheap is on $3 or $2 cost card] If Cheap is assigned to a card initially costing $3, it becomes a $2 cost card as far as Plateau Shepherds (PS) is concerned. Conversely, a card reduced to costing $1 due to Cheap will not be eligible for PS anymore.",
        df,
    )
    add_interaction(
        "Flourishing Trade",
        "Plateau Shepherds",
        "If Flourishing Trade is active by the end of the game, the new (reduced) cost of cards will be considered for Plateau Shepherds (PS), so you would e.g. be awarded PS points for Silvers, but not for Estates.",
        df,
    )
    add_interaction(
        "Canal",
        "Plateau Shepherds",
        "Since Canal only reduces the cost of cards during your turns, at the end of the game, it doesn't reduce the cost of cards as far as Plateau Shepherds (PS) is concerned.",
        df,
    )
    add_interaction(
        "Ferry",
        "Plateau Shepherds",
        "Since Ferry only reduces the cost of cards during your turns, at the end of the game, the Ferry token does not reduce the cost of cards as far as Plateau Shepherds (PS) is concerned.",
        df,
    )
    # If multiple allies were allowed, the interaction with Family of Inventors would be important.


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
        "[If you get Hexed with Deluded or Envious] At the start of your Buy phase, you may choose the order of returning Envious or Deluded, and playing Actions with Market Towns. If you play a Leprechaun at the start of your Buy phase and receive Envious or Deluded, you return it that same turn.",
        df,
    )
    add_interaction(
        "Frigate",
        "Fellowship of Scribes",
        "If you're under the Frigate attack, you can choose the order of discarding/drawing with Scribes, i.e. after playing an Action, you may first discard down to 4 cards in hand, and then use a Favor to draw 1 card, or (if you already had only 4 cards in hand) draw 1 card using Scribes and then discard down to 4 again.",
        df,
    )

    clerk_allies = "Desert Guides|Cave Dwellers/Clerk---You may react Clerks both before and after using Favors for {card_a}, but not in-between; you could e.g. react Clerk, use {card_a} two times, and then react another Clerk you've just drawn. After that, you may not use {card_a} again."
    add_multiple_interactions_from_single(clerk_allies, df)


##########################################################################################################
# Final function
def add_all_allies_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all allies interactions to the DataFrame."""
    num_before = len(df)
    _add_all_city_state_interactions(df)
    _add_individual_allies_interactions(df)
    if verbose:
        LOGGER.info(f"Added {len(df) - num_before} allies interactions.")
