"""Interactions that occur with ways."""

import pandas as pd

from ..constants import ACTION_TREASURES, PLAYABLE_REACTION, WAY_DICT
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)


##########################################################################################################
### Way interactions
def _add_way_playble_reaction_interaction(
    way: str, other: str, df: pd.DataFrame, way_extras: list[str]
):
    rule = f"When you react and play {other} during another player's turn, you can decide to play it as {way}."
    if len(way_extras) > 0:
        extras = [extra if "+" in extra else f"+ {extra}" for extra in way_extras]
        extras = " and ".join(extras)
        rule += (
            f" Remember that {extras} can't normally be used on other player's turns."
        )
    add_interaction(way, other, rule, df)


def _add_way_interaction(
    way: str,
    other: str,
    df: pd.DataFrame,
    way_extras: list[str],
    is_treasure=False,
    phase="Buy",
):
    if is_treasure:
        rule = f"When you play {other}, you can still decide to play it as {way}, whether you are in your Action or in your {phase} phase."
    elif other == "Enlightenment":
        rule = f"Once Enlightenment is active, you can choose to play your treasures as {way} both in your Action and Buy phase."
    elif other == "Capitalism":
        rule = f"Once Capitalism is active, you can choose to play your new-found Action-Treasures as {way} both in your Action and Buy phase."
    elif other in ["Diplomat", "Secret Chamber"]:
        rule = f"You can react your {other}'s ability to an opponent playing an Attack card even if they play it as {way}."
    else:
        return
    if "Action" in way_extras:
        rule += f" Remember that + Actions can't be used during your {phase} phase."
    add_interaction(way, other, rule, df)


def _add_way_enchantress_interactions(way: str, df: pd.DataFrame):
    if way.split()[-1] in ["Chameleon", "Pig"]:
        return
    rule = f"If you are playing your first Action in a turn while being affected by the Enchantress attack, you can choose to play it as {way}, overriding Enchantress' spell."
    add_interaction(way, "Enchantress", rule, df)


def add_butterfly_return_fail_interaction(other: str, df: pd.DataFrame):
    rule = f"Since {other} doesn't have a pile, it will always fail to return when played using Way of the Butterfly."
    add_interaction("Way of the butterfly", other, rule, df)


def add_horse_return_fail_interaction(other: str, df: pd.DataFrame):
    rule = f"Since {other} doesn't have a pile, it will always fail to return when played using Way of the Horse, remaining in deck after providing +2 Cards and +1 Action."
    add_interaction("Way of the horse", other, rule, df)


def _add_way_harbor_village_interactions(
    way: str, df: pd.DataFrame, way_extras: list[str]
):
    if way == "Way of the Chameleon":
        rule = "If you play a card as Way of the Chameleon and get +$ because of that, you will get +$1 from Harbor Village."
    elif way == "Way of the Mouse":
        rule = "If you play a card as Way of the Mouse and get +$ because of that, you will get never get +$1 from Harbor Village as Way of the Mouse plays another card."
    elif "$" not in way_extras:
        return
    else:
        rule = f"If you play a card as {way} and get +$ because of that, you will get +$1 from a previously played Harbor Village."
    add_interaction(way, "Harbor Village", rule, df)


def _add_special_chameleon_interactions(df: pd.DataFrame):
    add_interaction(
        "enchantress",
        "way of the chameleon",
        "If you are playing your first Action in a turn using Way of the Chameleon while being affected by the Enchantress attack, you will still only get +1 Card +1 Action.",
        df,
    )
    add_interaction(
        "souk",
        "way_of_the_chameleon",
        "If you play a Souk as Way of the Chameleon, you will draw 7 cards, and then after drawing lose $1 for each card you have in your hand, without going below $0. ",
        df,
    )
    add_interaction(
        "Poor House",
        "Way of the Chameleon",
        "If you play a Poor House as Way of the Chameleon, you will draw 4 cards, and then after drawing lose $1 for each card you have in your hand, without going below $0.",
        df,
    )
    chameleon_next_turn_stuff = "Way of the Chameleon/Wharf|Merchant Ship|Enchantress|Tactician|Barge|Taskmaster---If you play {card_b} using {card_a}, remember that {card_a} only affects stuff happening *this turn*, so on your next turn, you will get the normal bonus from {card_b}."
    add_multiple_interactions_from_single(chameleon_next_turn_stuff, df)
    # Chameleon/Handsize stuff - Only Diplo states the obvious, THero, Guard Dog and Marquis do not
    csos = "Way of the Chameleon/Tragic Hero|Guard Dog|Marquis"
    inter = "If you play {card_b} using Way of the Chameleon, getting +$ instead of drawing cards, {card_b}'s condition will still be checked afterwards."
    add_multiple_interactions(csos, inter, df, True)
    cham_diplo = "Way of the Chameleon/Diplomat---If you play Diplomat using Way of the Chameleon, getting +$2 instead of +2 cards, you still get +2 actions even though Diplomat states '(after drawing)' when you in reality didn't draw any cards, assuming you have 5 or fewer cards in hand."
    add_multiple_interactions_from_single(cham_diplo, df, True)


def _add_special_butterfly_horse_interactions(df: pd.DataFrame):
    # MORE:
    # - DIVINE WIND in prophecies.py
    ss_but_horse = "Spell scroll/Way of the Butterfly|Way of the Horse---If you play Spell Scroll using {card_b}, it will return to the top of the Loot pile and be the next Loot anyone gains."
    add_multiple_interactions_from_single(ss_but_horse, df, True)
    # Stuff that doesn't have a pile
    NO_PILE_TO_RETURN_TO = (
        "Necropolis, Zombie Mason, Zombie Apprentice, Zombie Spy".split(", ")
    )
    for loner in NO_PILE_TO_RETURN_TO:
        add_butterfly_return_fail_interaction(loner, df)
        add_horse_return_fail_interaction(loner, df)
    add_interaction(
        "way of the horse",
        "riverboat",
        "If you play the Riverboat card (not Riverboat) using Way of the Horse, it stays set aside.",
        df,
    )
    add_interaction(
        "way of the butterfly",
        "riverboat",
        "If you play the Riverboat card (not Riverboat) using Way of the Butterfly, it fails to return to its pile, and nothing will happen.",
        df,
    )
    add_interaction(
        "way of the horse",
        "prince",
        "If you play the Princed Action using Way of the Horse, it stays set aside.",
        df,
    )
    add_interaction(
        "way of the butterfly",
        "prince",
        "If you play the Princed Action using Way of the Butterfly, it fails to return to its pile, and nothing will happen.",
        df,
    )


def _add_smugglers_mouse_interaction(df: pd.DataFrame):
    add_interaction(
        "smugglers",
        "way of the mouse",
        "If Smugglers is the Mouse card and you are able to somehow play it during your opponent's turn, you are able to gain the cards they gained on their previous turn.",
        df,
    )


##########################################################################################################
# Final function
def add_all_way_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all interactions involving ways to the DataFrame."""
    num_before = len(df)

    for way_name, extra_stuff in WAY_DICT.items():
        for reaction in PLAYABLE_REACTION:
            _add_way_playble_reaction_interaction(way_name, reaction, df, extra_stuff)
        for treasure in ACTION_TREASURES:
            _add_way_interaction(way_name, treasure, df, extra_stuff, is_treasure=True)
        for other in "Enlightenment, Capitalism".split(","):
            _add_way_interaction(way_name, other.strip(), df, extra_stuff)
        # Add werewolf interactions only for ways where it makes sense
        if way_name.split()[-1] not in ["Sheep", "Monkey", "Chameleon", "Ox", "Mule"]:
            _add_way_interaction(
                way_name,
                "Werewolf",
                df,
                is_treasure=True,
                way_extras=extra_stuff,
                phase="Night",
            )
        for other in ["Diplomat", "Secret Chamber"]:
            _add_way_interaction(way_name, other, df, [])
        _add_way_enchantress_interactions(way_name, df)
        _add_way_harbor_village_interactions(way_name, df, extra_stuff)
    _add_special_chameleon_interactions(df)
    _add_special_butterfly_horse_interactions(df)
    _add_smugglers_mouse_interaction(df)
    if verbose:
        print(f"Added {len(df) - num_before} interactions involving ways.")
