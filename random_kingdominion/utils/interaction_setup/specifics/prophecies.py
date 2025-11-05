"""Interactions that occur with prophecy"""

import pandas as pd

from ..constants import (
    ACTION_TREASURES,
    ALL_LOOT_GIVERS,
    ALL_LOOTS,
    GATHERING_CARDS,
    TGG_BUG_DISCLAIMER,
    TRAVELLER_BASE_CARDS,
    ALL_HORSE_GAINERS,
)
from ....constants import HEIRLOOM_DICT
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
        "Once Divine Wind has been triggered, if you play any card from the initial supply using Way of the Butterfly, it cannot return to its pile, and will fail to do anything except for going into your play area.",
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
    # More interactions in 'events'
    for gathering_cso in GATHERING_CARDS:
        _add_gathering_divine_wind_interaction(gathering_cso, df)

    for traveller_base_cso in TRAVELLER_BASE_CARDS:
        _add_traveller_divine_wind_interaction(traveller_base_cso, df)

    _add_individual_divine_wind_interactions(df)


def _add_all_harsh_winter_interactions(df: pd.DataFrame):
    black_market = "With Harsh Winter active, no Debt is added or removed to the Black Market deck when buying cards from it, as it is not a pile."
    add_interaction("black_market", "harsh_winter", black_market, df)
    ferryman = "When you gain a Ferryman while Harsh Winter is active, you add or remove Debt also for the set-aside Ferryman pile."
    add_interaction("harsh_winter", "ferryman", ferryman, df)
    possession = "On a Possession turn, no player gains cards on their own turn, so Harsh Winter does not apply even if it's active."
    add_interaction("harsh_winter", "possession", possession, df)
    changeling = "When you exchange a card you gain with Changeling while Harsh Winter is active, Harsh Winter does not apply to the Changeling pile. However, since you still gained a card from the original pile, you do add or remove Debt for that pile."
    add_interaction("harsh_winter", "changeling", changeling, df)
    trader = "When you react a Trader to exchange a card you would gain with Silver while Harsh Winter is active, Harsh Winter does not apply to the Silver pile, but you still add or remove Debt for the original pile."
    add_interaction("harsh_winter", "trader", trader, df)
    travellers = "Harsh Winter/Peasant|Page---When you exchange a Traveller such as {card_b} while Harsh Winter is active, Harsh Winter does not apply to the Traveller pile. However, if you manage to somehow gain a Traveller from the Trash (e.g. via Shaman or Lich) with Harsh Winter active, Debt is added or removed for that pile, even if it's not a Supply pile. You get to decide (during setup) whether all of the non-{card_b} Travellers are part of one pile or multiple piles for the purposes of Harsh Winter. On the TGG client, they are considered separate piles."
    add_multiple_interactions_from_single(travellers, df)
    exchange_dict = {"Vampire": "Bat", "Hermit": "Madman"}
    for card, exchange in exchange_dict.items():
        rule = f"When you exchange a {card} while Harsh Winter is active, Harsh Winter does not apply to the {exchange} pile. However, if you manage to somehow gain a {exchange} from the Trash (e.g. via Shaman or Lich) with Harsh Winter active, Debt is added or removed for that pile."
        add_interaction("harsh_winter", card, rule, df)
    tax_rule = "While Harsh Winter is active, when you gain a card in your Buy phase, you can resolve Harsh Winter and Tax in either order. Usually you want to resolve Tax first: If the pile has D, your choices are: take the D with Tax and add 2D with Harsh Winter; or take the D with Harsh Winter and take 0D with Tax. If the pile has no D, your choices are: take 0D with Tax and then add 2D with Harsh Winter; or add 2D with Harsh Winter and then take the 2D with Tax."
    add_interaction("harsh_winter", "tax", tax_rule, df)
    joust = "The Rewards are considered a single pile. Once Harsh Winter is active, when you gain a Reward during your turn, you add or remove Debt for the Reward pile."
    add_interaction("harsh_winter", "joust", joust, df)
    tournament = "The Prizes are considered a single pile. Once Harsh Winter is active, when you gain a Prize during your turn, you add or remove Debt for the Prize pile."
    add_interaction("harsh_winter", "tournament", tournament, df)
    for loot_giver in ALL_LOOT_GIVERS:
        rule = f"When you gain a Loot via {loot_giver} during your turn while Harsh Winter is active, you add or remove Debt for the Loot pile."
        add_interaction("harsh_winter", loot_giver, rule, df)
    for card, heirloom in HEIRLOOM_DICT.items():
        rule = f"When you somehow gain {heirloom} (e.g. via Shaman or Treasurer) during your turn while Harsh Winter is active, since it does not have a pile, you do not add or remove Debt anywhere."
        add_interaction("harsh_winter", card, rule, df)
    for card in ALL_HORSE_GAINERS:
        rule = f"When you gain Horses during your turn via {card} while Harsh Winter is active, you add or remove Debt for the Horse pile."
        add_interaction("harsh_winter", card, rule, df)


def _add_enlightenment_interactions(df: pd.DataFrame):
    # More interactions at Black Market, and also at Events (concerning the tokens)
    act_treas_str = (
        "|".join(ACTION_TREASURES)
        + "/Enlightenment---If Enlightenment is active, {card_a}'s Action phase mode is overwritten by Enlightenment."
    )
    add_multiple_interactions_from_single(
        act_treas_str, df, add_together_if_present=True
    )
    add_interaction(
        "Capitalism",
        "Enlightenment",
        "Once Enlightenment is active, Capitalism will turn all of its targets into cantrips during the Action phase.",
        df,
    )
    add_interaction(
        "Continue",
        "Enlightenment",
        "Once Enlightenment is active, you can buy Continue to gain and play any non-Attack Action-Treasure (even Silver) costing at most $4. Since you return to your Action phase first before playing it, you will always get +1 Card and +1 Action from it.",
        df,
    )
    add_interaction(
        "Highwayman",
        "Enlightenment",
        "Once Enlightenment is active, while you're under Highwayman attack, for the first Treasure you play during your Action phase, you will get to choose which effect should apply first, so you can still get +1 Card, +1 Action.",
        df,
    )
    add_interaction(
        "Sauna",
        "Enlightenment",
        "Once Enlightenment is active, when you play Silver during your Action phase after having played a Sauna, you will first be prompted to trash a card, and only afterwards get +1 Card, +1 Action.",
        df,
    )
    add_interaction(
        "Clashes",
        "Enlightenment",
        "Once Enlightenment is active and Treasures become Actions, you may only play at most two of each during your turns while under Warlord attack.",
        df,
    )
    add_interaction(
        "Delusion",
        "Enlightenment",
        "Once Enlightenment is active and Treasures become Actions, Delusion will disallow you from buying Treasures.",
        df,
    )
    replay_inter = "Daimyo|Flagship/Enlightenment---If you play {card_a} as the last card during your Action phase while Enlightenment is active, the first Treasure you play during your Buy phase will be replayed for its Treasure effect."
    add_multiple_interactions_from_single(replay_inter, df)


def _add_panic_interactions(df: pd.DataFrame):
    for loot in ALL_LOOTS:
        if loot in ["Endless Chalice", "Jewels"]:
            inter = f"Since you never discard {loot} from play after playing it (bar e.g. Highwayman), you never return it for Panic."
        else:
            inter = f"When you discard {loot} from play while Panic is active, you return it to the top of the Loot pile. When discarding multiple, you get to choose the order."
        add_interaction("Panic", loot, inter, df)
    for loot_giver in ALL_LOOT_GIVERS:
        inter = f"When you discard a Loot gained from {loot_giver} from play while Panic is active, you need to return it to the top of the Loot pile. When discarding multiple, you get to choose the order. Endless Chalice and Jewels are exceptions as they (bar e.g. Highwayman) never get discarded from play."
        add_interaction("Panic", loot_giver, inter, df)
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
    add_interaction(
        "panic",
        "crown",
        f"Even if you play Crown before Panic becomes active, if Panic becomes active later that turn, you need to return the Crown to its pile when you discard it from play.",
        df,
    )


def _add_progress_interactions(df: pd.DataFrame):
    add_interaction(
        "Progress",
        "Continue",
        "When you buy Continue while Progress is active, you have to topdeck the gained card and won't be able to play it.",
        df,
    )
    add_interaction(
        "Progress",
        "Spell Scroll",
        "When you play a Spell Scroll while Progress is active, you have to topdeck the gained card and won't be able to play it.",
        df,
    )
    add_interaction(
        "Progress",
        "Invasion",
        "When you buy Invasion while Progress is active, you have to topdeck the gained Loot and won't be able to play it.",
        df,
    )
    add_interaction(
        "Progress",
        "Mining Road",
        "When you gain a Treasure while Progress is active, you can choose between playing it directly, or topdecking it (you only get to do one of these).",
        df,
    )


##########################################################################################################
# Final function
def add_all_prophecy_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all prophecy interactions to the DataFrame."""
    num_before = len(df)
    _add_all_divine_wind_interactions(df)
    _add_enlightenment_interactions(df)
    _add_all_harsh_winter_interactions(df)
    _add_panic_interactions(df)
    _add_progress_interactions(df)
    # Rapid Expansion stuff mostly in on-gain
    if verbose:
        print(f"Added {len(df) - num_before} prophecy interactions.")
