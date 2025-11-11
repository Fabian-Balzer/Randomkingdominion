"""Interactions that occur with on_clean_up"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER, WAY_DICT
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_single_way_reckless_inter(way: str, df: pd.DataFrame):
    if "chameleon" in way.lower():
        rule = f"[Only if Reckless is on an Action card] If you play a Reckless Action card using Way of the Chameleon, you follow its cards vs. $$ switched-around instructions twice, you do not get to choose in between."
    else:
        rule = f"[Only if Reckless is on an Action card] If you play a Reckless Action card using {way}, you will only play it as {way} once and then fail to follow its instructions the second time"
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
    alch = "[Only if Reckless is on Alchemist] If Alchemist is Reckless, you may topdeck it during Clean-up if you have a Potion in play, circumventing Reckless' return-to-pile prompt."
    add_interaction("Reckless", "Alchemist", alch, df)
    m_camp = "[Only if Reckless is on Merchant Camp] If Merchant Camp is Reckless, you may topdeck it during Clean-up, circumventing Reckless' return-to-pile prompt."
    add_interaction("Reckless", "Merchant Camp", m_camp, df)
    tent = "[Only if Reckless is on Tent] If Tent is Reckless, you may topdeck it during Clean-up, circumventing Reckless' return-to-pile prompt."
    add_interaction("Reckless", "Tent", tent, df)
    w_vill = "[Only if Reckless is on Walled Village] If Walled Village is Reckless, you may topdeck it during Clean-up if you only have it and at most one other Action in play, circumventing Reckless' return-to-pile prompt."
    add_interaction("Reckless", "Walled Village", w_vill, df)
    scheme = "[Only if Reckless is on an Action] If Reckless is on any Action card and you play Scheme, topdecking the Reckless Action card before returning it to its pile will circumvent Reckless' return-to-pile prompt."
    add_interaction("Reckless", "Scheme", scheme, df)
    crypt = "[Only if Reckless is on a Treasure] If Reckless is on a Treasure and you stow it away with Crypt, you cannot return it to its pile and it will stay set-aside on Crypt to be put in hand later."
    add_interaction("Reckless", "Crypt", crypt, df)
    trickster = "[Only if Reckless is on a Treasure] If Reckless is on a Treasure and you played a Trickster on a turn you play said Treasure, you may set it aside before returning it to its pile, in which case you cannot return it to its pile, and will put it into your next hand instead."
    add_interaction("Reckless", "Trickster", trickster, df)
    herbalist = "[Only if Reckless is on a Treasure] If Reckless is on a Treasure and you played a Herbalist on a turn you play said Treasure, you may topdeck it before returning it to its pile, in which case you cannot return it to its pile."
    add_interaction("Reckless", "Herbalist", herbalist, df)
    hwman = "[Only if Reckless is on a Treasure] If Reckless is on a Treasure and you are under Highwayman attack when you play said Treasure, you cannot return it to its pile, and it will be discarded normally during Clean-up.\n[Only if Reckless is on Highwayman] If Highwayman is Reckless, it is returned to its pile at the start of the next turn (and then you get +6 Cards)."
    add_interaction("Reckless", "Highwayman", hwman, df)
    capital = "[Only if Reckless is on Capital] If Capital is Reckless, you get +$12 and +2 Buys when playing it. When you discard it from play, you get +6 Debt and have to return it to its pile."
    add_interaction("Reckless", "Capital", capital, df)
    ench = "[Only if Reckless is on an Action] If you are under the Enchantress Attack and play a Reckless Action card as the first Action during your turn, you will only get +1 Card, +1 Action, fail to follow the instructions the second time, but still have to return the Reckless Action when you discard it from play."
    add_interaction("Reckless", "Enchantress", ench, df)
    prince = "[Only if Reckless is on an Action] If you set aside a Reckless Action card with Prince, you never discard it from play, so you never have to return it to its pile."
    add_interaction("Reckless", "Prince", prince, df)
    for way in WAY_DICT:
        _add_single_way_reckless_inter(way, df)


def _add_all_walled_village_interactions(df: pd.DataFrame):
    journey = "If you have no more than one other Action than the Walled Village in play, you can topdeck it for the Journey turn."
    add_interaction("Journey", "Walled Village", journey, df)
    improve = "At the start of Clean-up, you may choose to resolve Improve's trashing first and only afterwards assess the amount of Action cards in play for Walled Village's topdecking."
    add_interaction("Improve", "Walled Village", improve, df)
    alchemist = "At the start of Clean-up, you may choose to resolve Alchemist's topdecking first (if you have a Potion in play) and only afterwards assess the amount of Action cards in play for Walled Village's topdecking."
    add_interaction("Alchemist", "Walled Village", alchemist, df)
    scheme = "Since you count the Action cards for Walled Village first before topdecking cards with Scheme, even if you plan on topdecking an Action card, it still gets counted for Walled Village's assessment."
    add_interaction("Scheme", "Walled Village", scheme, df)
    treasury = "Any topdecked Treasuries do not count as Action cards in play for Walled Village's topdecking."
    add_interaction("Treasury", "Walled Village", treasury, df)
    reserves = "Walled Village/Duplicate|Ratcatcher|Guide|Transmogrify|Royal Carriage|Teacher---Reserve cards such as {card_b} only count as being Actions in play if you called them, not if you play them to put them onto your Tavern mat."
    add_multiple_interactions_from_single(reserves, df)
    topdeck_self = "Walled Village/Tent|Merchant Camp---Since you count the Action cards for Walled Village first before discarding cards from play, even if you plan on topdecking {card_b}, it still gets counted for Walled Village's assessment."
    add_multiple_interactions_from_single(topdeck_self, df)
    tireless = "Since you count the Action cards for Walled Village first before discarding cards from play, Tireless cards will still be considered in play for Walled Village's assessment."
    add_interaction("Tireless", "Walled Village", tireless, df)


def _add_individual_on_cleanup_interactions(df: pd.DataFrame):
    add_interaction(
        "Journey",
        "Alchemist",
        "If you play Alchemists and buy Journey, if you have a Potion in play, you may topdeck the Alchemists for the Journey turn, and also on the Journey turn.",
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


def _add_all_merchant_camp_interactions(df: pd.DataFrame):
    rule = "Merchant Camp/Enchantress---Even if you don't play Merchant Camp normally, you may still topdeck it when you discard it from play."
    add_multiple_interactions_from_single(rule, df)
    ways = "|".join(WAY_DICT.keys())
    way_rule = f"Merchant Camp/{ways}---If you play Merchant Camp using {{card_b}}, you may still topdeck it when you discard it from play."
    add_multiple_interactions_from_single(way_rule, df)


def _add_all_tent_interactions(df: pd.DataFrame):
    rule = "Tent/Enchantress---Even if you don't play Tent normally, you may still topdeck it when you discard it from play."
    add_multiple_interactions_from_single(rule, df)
    ways = "|".join(WAY_DICT.keys())
    way_rule = f"Tent/{ways}---If you play Tent using {{card_b}}, you may still topdeck it when you discard it from play."
    add_multiple_interactions_from_single(way_rule, df)


##########################################################################################################
# Final function
def add_all_on_clean_up_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all on_clean_up interactions to the DataFrame."""
    num_before = len(df)
    _add_reckless_interactions(df)
    _add_all_merchant_camp_interactions(df)
    _add_all_tent_interactions(df)
    _add_all_walled_village_interactions(df)
    _add_individual_on_cleanup_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} on_clean_up interactions.")
