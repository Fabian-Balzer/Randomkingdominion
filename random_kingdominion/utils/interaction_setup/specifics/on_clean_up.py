"""Interactions that occur with on_clean_up"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER, WAY_DICT
from ..interaction_util import add_interaction


def _add_single_way_reckless_inter(way: str, df: pd.DataFrame):
    if "chameleon" in way.lower():
        rule = f"If you play a Reckless Action card using Way of the Chameleon, you follow its cards vs. $$ switched-around instructions twice, you do not get to choose in between."
    else:
        rule = f"If you play a Reckless Action card using {way}, you will only play it as {way} once and then fail to follow its instructions the second time"
    if "turtle" in way.lower():
        rule += f". This means that you'll set aside the Reckless Action if played with {way}, and the next time you choose to play it normally, the normal Reckless effect will kick in."
    elif not any(
        [animal in way.lower() for animal in ["horse", "butterfly", "chameleon"]]
    ):
        rule += ", but you still have to return it when discarding it from play."
    else:
        rule += "."
    add_interaction("Reckless", way, rule, df)


def _add_reckless_interactions(df: pd.DataFrame):
    # Reckless + Alchemist, Scheme, Crypt, Trickster, Highwayman, Capital, Enchantress, and Ways
    add_interaction(
        "Reckless",
        "Alchemist",
        "If Alchemist is Reckless, you may topdeck if you have a Potion in play, circumventing Reckless' return-to-pile prompt.",
        df,
    )
    add_interaction(
        "Reckless",
        "Scheme",
        "If Reckless is on an Action card and you play a Scheme, topdecking the Reckless card circumvents Reckless' return-to-pile prompt.",
        df,
    )
    add_interaction(
        "Reckless",
        "Crypt",
        "If Reckless is on a Treasure and you stow it away with Crypt, you cannot return it to its pile and it will stay in the Crypt for later use.",
        df,
    )
    add_interaction(
        "Reckless",
        "Trickster",
        "If Reckless is on a Treasure and you played a Trickster on a turn you play said Treasure, you may set it aside, in which case you cannot return it to its pile, and will put it into your next hand instead.",
        df,
    )
    add_interaction(
        "Reckless",
        "Highwayman",
        "If you play a Reckless Treasure while under the Highwayman attack as the first Treasure, it does nothing at all, but is returned to its pile when discarded from play.\nIf Highwayman is Reckless, it is returned to its pile at the start of the next turn (and then you get +6 Cards).",
        df,
    )
    add_interaction(
        "Reckless",
        "Capital",
        "If Capital is Reckless, you get +$12 and +2 Buys when playing it. When you discard it from play, you get +6 Debt and have to return it to its pile.",
        df,
    )
    add_interaction(
        "Reckless",
        "Enchantress",
        "If you are under the Enchantress Attack and play a Reckless Action card as the first Action during your turn, you will only get +1 Card, +1 Action, fail to follow the instructions the second time, but still have to return the Reckless Action when you discard it from play.",
        df,
    )
    for way in WAY_DICT:
        _add_single_way_reckless_inter(way, df)


def _add_individual_on_cleanup_interactions(df: pd.DataFrame):
    add_interaction(
        "Journey",
        "Alchemist",
        "If you play Alchemists and Potion and buy Journey, you may topdeck the Alchemists for the Journey turn.",
        df,
    )
    add_interaction(
        "Journey",
        "Walled Village",
        "If you have no more than one other Action than the Walled Village in play, you can topdeck it for the Journey turn.",
        df,
    )
    add_interaction(
        "trail",
        "improve",
        "Trashing a Trail with Improve's ability will not trigger Trail's on-trash effect because the trashing occurs during Clean-up.",
        df,
    )
    add_interaction(
        "trail",
        "river shrine",
        "Gaining a Trail with River Shrine's ability will not trigger Trail's on-gain effect because the gaining occurs during Clean-up.",
        df,
    )
    add_interaction(
        "cargo_ship",
        "improve",
        "If you play a Cargo Ship and don't set anything aside with it before your Clean-up phase, Improve can trash it because it's going to be discarded as far as you know at that point. However, trashing a card from play does not negate its instructions, so you can still set aside the card you gain from Improve (or another card you gain that turn) through the instructions of Cargo Ship.",
        df,
    )
    add_interaction(
        "Highwayman",
        "capital",
        "If you are under Highwayman attack and play Capital as your first Treasure, you do not get +6$ and +1 Buy; however, you will still get 6D when discarding Capital from play.",
        df,
    )


##########################################################################################################
# Final function
def add_all_on_clean_up_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all on_clean_up interactions to the DataFrame."""
    num_before = len(df)
    _add_reckless_interactions(df)
    _add_individual_on_cleanup_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} on_clean_up interactions.")
