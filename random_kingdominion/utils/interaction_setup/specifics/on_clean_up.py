"""Interactions that occur with on_clean_up"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER, WAY_DICT
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


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
        "If Reckless is on any Action card and you play Scheme, topdecking the Reckless Action card before returning it to its pile will circumvent Reckless' return-to-pile prompt.",
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
        "If Reckless is on a Treasure and you played a Trickster on a turn you play said Treasure, you may set it aside before returning it to its pile, in which case you cannot return it to its pile, and will put it into your next hand instead.",
        df,
    )
    add_interaction(
        "Reckless",
        "Herbalist",
        "If Reckless is on a Treasure and you played a Herbalist on a turn you play said Treasure, you may topdeck it before returning it to its pile, in which case you cannot return it to its pile.",
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
    add_interaction(
        "Reckless",
        "Prince",
        "If you set aside a Reckless Action card with Prince, you never discard it from play, so you never have to return it to its pile.",
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
    add_interaction(
        "Trickster",
        "capital",
        "Even if you set aside Capital using Trickster's ability, you will still get 6D since you discard it from play.",
        df,
    )
    add_interaction(
        "Capital",
        "herbalist",
        "Even if you topdeck Capital using Herbalist's ability, you will still get 6D since you discard it from play.",
        df,
    )
    add_interaction(
        "Crypt",
        "Capital",
        "If you play Capital and set it aside with Crypt, not get 6D since you did not discard Capital from play.",
        df,
    )
    crypt_stuff = "Crypt/Coronet|Crown---If you play a Duration card using {card_b}, you can still set it aside with Crypt that turn and will NOT get the duration effect off of both plays for the next turn (e.g. {card_b} on Wharf, you can Crypt the {card_b} away and will draw only 2 cards on the next turn). With Gear, this might even strand cards. Having played {card_b} on a previous turn on a Duration card, you can still set it aside with Crypt. Future throned Duration effects (like with Hireling) will then not occur any more."
    add_multiple_interactions_from_single(crypt_stuff, df)
    add_interaction(
        "Crypt",
        "King's Cache",
        "If you play a Duration Treasure using King's Cache (KC), you can still set it aside with Crypt that turn, but NOT get the duration effect off of all three plays for the next turn (e.g. KC on Astrolabe, you can Crypt away the KC and will only get +$1 and +1 Buys on your next turn). You can also Crypt the KC on a later turn.",
        df,
    )
    add_interaction(
        "Crypt",
        "Tiara",
        "If you play a Duration Treasure using Tiara, you can still set it aside with Crypt that turn, but NOT get the duration effect off of both plays for the next turn (e.g. Tiara on Astrolabe, you can Crypt away the Tiara and will get +$1 and +1 Buys on your next turn). You can also Crypt the Tiara on a later turn.",
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
