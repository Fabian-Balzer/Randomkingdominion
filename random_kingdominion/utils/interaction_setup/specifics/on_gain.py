"""Interactions that occur whenever you gain a card + Overpay interactions."""

import pandas as pd

from ..constants import (
    CAN_CAUSE_SHUFFLE_TRIGGER_ON_GAIN,
    CAN_PLAY_CARD_ON_GAIN,
    CAN_TOPDECK_ON_GAIN,
    GAINS_SELF_TO_HAND_CARDS,
    GAINS_TO_HAND,
    GAINS_TO_SET_ASIDE,
    MUST_TOPDECK_ON_GAIN,
    TGG_BUG_DISCLAIMER,
    WILL_TOPDECK_ON_GAIN,
)
from ..interaction_util import add_interaction


### On-Gain/Overpay interactions
def _add_on_overpay_infirmary_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso in ["Spell Scroll", "Gondola"]:
        return
    rule = f"When you overpay for Infirmary, you choose between the effect of the overpay and {on_gain_play_cso} triggering. If you choose {on_gain_play_cso}, Infirmary's overpay will be unable to play itself any number of times (because Infirmary already moved). {on_gain_play_cso} will also be unable to play Infirmary if you choose the overpay first, for the same reason."
    add_interaction("Infirmary", on_gain_play_cso, rule, df)


def _add_on_gain_play_duplicate_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain a Gondola and play a Duplicate from your hand, you may call it directly to gain another Gondola."
    else:
        rule = f"When you gain Duplicate and play it immediately using {on_gain_play_cso}, you may call it directly to gain another copy of it."
    add_interaction("Duplicate", on_gain_play_cso, rule, df)


def _add_on_gain_play_gatekeeper_interaction(
    on_gain_play_cso: str, df: pd.DataFrame, extra_str=""
):
    if on_gain_play_cso == "Gondola":
        return
    rule = f"If your opponent has played Gatekeeper, you gain a{extra_str} card and you don't have a copy of the gained card in Exile, you may choose whether to resolve {on_gain_play_cso} or the exiling first; if you play the gained{extra_str} card, it cannot be moved to Exile and vice versa."
    if on_gain_play_cso == "Berserker":
        rule = f"If your opponent has played Gatekeeper, you gain a Berserker and you don't have a copy of Berserker in Exile, you may choose whether to resolve playing the Berserker or the exiling first; if you play it, it cannot be moved to Exile and vice versa."
    add_interaction("Gatekeeper", on_gain_play_cso, rule, df)


def _add_on_gain_play_galleria_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain a Gondola and play a Galleria from your hand, you will immediately get +Buy from the Gondola gain."
    else:
        rule = f"When you gain a cost-reducing card (like Highway, Bridge, or Inventor) and play it immediately using {on_gain_play_cso} after having played a Galleria, the card's cost before the gain will determine whether you get +Buy (e.g. you won't get +Buy if Highway costs $5 before gaining and playing it).\nOn the other hand, if you gain a Galleria and play it immediately using {on_gain_play_cso}, you will get +Buy from the Galleria gain if you have reduced its cost to $3 or $4 prior to the gain."
    add_interaction("Galleria", on_gain_play_cso, rule, df)


def _add_on_gain_play_haggler_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you buy and gain a Gondola and play a Haggler from your hand, you will gain a card costing less than the Gondola."
    else:
        rule = f"When you buy and gain a Haggler and play it immediately using {on_gain_play_cso}, you will gain a card costing less than it."
    add_interaction("Haggler", on_gain_play_cso, rule, df)


def _add_on_gain_play_livery_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain a Gondola and play a Livery from your hand, you will gain a Horse due to the Gondola gain."
    else:
        rule = f"When you gain a Livery and play it immediately using {on_gain_play_cso}, you gain a Horse from its gain."
    add_interaction("Livery", on_gain_play_cso, rule, df)


def _add_on_gain_play_guildmaster_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain a Gondola and play a Guildmaster from your hand, you will receive a Favor due to the Gondola gain."
    else:
        rule = f"When you gain a Guildmaster and play it immediately using {on_gain_play_cso}, you receive a Favor from its gain."
    add_interaction("Guildmaster", on_gain_play_cso, rule, df)


def _add_on_gain_play_search_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain the last Gondola and play a Search from your hand, you will not gain a Loot from the Gondola gain due to Search's 'Next Time' wording.{TGG_BUG_DISCLAIMER}"
    else:
        rule = f"When you gain the last Search and play it immediately using {on_gain_play_cso}, it will not be trashed and you will not gain a Loot due to its 'Next Time' wording.{TGG_BUG_DISCLAIMER}"
    add_interaction("Search", on_gain_play_cso, rule, df)


def _add_on_gain_play_gondola_sec_shrine_interaction(df: pd.DataFrame):
    rule = "When you gain a Gondola and play a Secluded Shrine from your hand via its on-gain ability, you may not immediately trash two cards from your hand due Secluded Shrine's 'Next Time' wording."
    add_interaction("Gondola", "Secluded Shrine", rule, df)


def _add_on_gain_play_skirmisher_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        return
    rule = f"When you gain a Skirmisher and play it immediately using {on_gain_play_cso}, its effect will trigger, causing your opponents to discard."
    add_interaction("Skirmisher", on_gain_play_cso, rule, df)


def _add_on_gain_play_kiln_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain a Gondola and play a Kiln from your hand, you will not be able to gain another Gondola due to Kiln's 'Next Time' wording. Instead, the next card you play will be subject to its effect."
    else:
        rule = f"When you gain a Kiln and play it immediately using {on_gain_play_cso}, you will not be able to gain another Kiln due to its 'Next Time' wording. Instead, the next card you play will be subject to its effect."
    add_interaction("Kiln", on_gain_play_cso, rule, df)


def _add_on_gain_play_siren_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        return
    rule = f"If you gain a Siren and use {on_gain_play_cso} to play the Siren, Siren no longer requires you to trash an action card from your hand in order to not trash the Siren."
    add_interaction("Siren", on_gain_play_cso, rule, df)


def _add_on_gain_play_changeling_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When gaining a Gondola, you can both exchange it for a Changeling and make use of its on-gain effect."
    else:
        rule = f"If you play a gained card using {on_gain_play_cso}, you cannot exchange it for a Changeling afterwards. Conversely, you cannot play it anymore after having exchanged it for a Changeling."
    add_interaction("Changeling", on_gain_play_cso, rule, df)


def _add_on_gain_play_improve_interaction(on_gain_play_cso: str, df: pd.DataFrame):
    rule = f"You can play cards you gain via an Improve trash using {on_gain_play_cso} during your Clean-up phase. This might lead to weird effects such as Encampment immediately returning to its pile, and Crown being useless."
    add_interaction(
        on_gain_play_cso,
        "Improve",
        rule,
        df,
    )


def _add_on_play_shuffle_trigger_interaction(
    on_gain_play_cso: str, shuffle_trigger_cso: str, df: pd.DataFrame
):
    if on_gain_play_cso == "Gondola":
        return
    rule = f"If you gain a card and use {shuffle_trigger_cso} to cause a shuffle, you cannot play it using {on_gain_play_cso} anymore (but you could choose to resolve the on-gain play first)."
    add_interaction(shuffle_trigger_cso, on_gain_play_cso, rule, df)


def _add_on_gain_play_topdecker_interaction(
    topdecker: str, on_play_cso: str, df: pd.DataFrame
):
    if on_play_cso == "Gondola":
        return
    else:
        rule = f"When you gain a card using {topdecker} and immediately play it using {on_play_cso}, you will not be able to topdeck it."
    add_interaction(topdecker, on_play_cso, rule, df)


##########################################################################################################
# Shuffle trigger Interactions
def _add_on_shuffle_trigger_siren_interaction(other: str, df: pd.DataFrame):
    if other == "Trail":
        return
    rule = f"If you gain a Siren and somehow trigger a shuffle by drawing a card using {other}, you still may trash an Action card from you hand, but the Siren will fail to trash itself and it will stay in your deck."
    add_interaction("Siren", other, rule, df)


##########################################################################################################
### On-Gain-Topdecking interactions
def _add_on_gain_topdeck_siren_interaction(
    topdeck_cso: str, df: pd.DataFrame, choice=False, force=False
):
    if choice:
        rule = f"If you gain a Siren and topdeck it using {topdeck_cso}, you don't need to trash an Action card in order for it to stay in your deck."
    elif force:
        rule = f"If you gain a Siren and topdeck it using {topdeck_cso}, you don't need to trash an Action card in order for the Siren to stay in your deck."
    else:
        rule = f"If you gain a Siren and topdeck it using {topdeck_cso}, you still need to trash an Action card from your hand in order to not trash the Siren."
    add_interaction("Siren", topdeck_cso, rule, df)


def _add_on_gain_topdeck_villa_interaction(
    topdeck_cso: str, df: pd.DataFrame, choice=False
):
    if choice:
        rule = f"If you gain a Villa, you can decide whether to topdeck it using {topdeck_cso}, or gain it to your hand. In any case, you will receive +1 Action and return to you Action phase if you're in your buy phase."
    elif topdeck_cso == "Progress":
        rule = f"If you gain a Villa while Progress is active, it is topdecked instead of put into your hand (unless you gain it on top of your deck directly with e.g. Armory, in which case it paradoxically is put into your hand afterwards)."
    else:
        rule = f"If you gain a Villa using {topdeck_cso}, it is first topdecked and then you put it into your hand."
    add_interaction("Villa", topdeck_cso, rule, df)


def _add_on_gain_topdeck_night_to_hand_interaction(
    topdeck_cso: str, night_to_hand_card: str, df: pd.DataFrame, choice=False
):
    if choice:
        rule = f"If you gain a {night_to_hand_card}, you can decide whether to topdeck it using {topdeck_cso}, or gain it to your hand."
    else:
        rule = f"If you gain a {night_to_hand_card} using {topdeck_cso}, it is topdecked instead of being gained to your hand."
    add_interaction(night_to_hand_card, topdeck_cso, rule, df)


##########################################################################################################
### On-Gain-Set-Aside interactions
def _add_on_gain_set_aside_siren_interaction(set_aside_cso: str, df: pd.DataFrame):
    rule = f"If you gain a Siren and set it aside using {set_aside_cso}, you still need to trash an Action from your hand in order to not trash the Siren."
    if set_aside_cso in ["Rapid Expansion", "Hasty"]:
        rule = f"If you gain a Siren and set it aside using {set_aside_cso}, since it's set aside after being gained, it will stay there even if you fail to trash an Action."
    add_interaction("Siren", set_aside_cso, rule, df)


##########################################################################################################
### On-Gain-to-Hand interactions
def _add_on_gain_hand_siren_interaction(hand_cso: str, df: pd.DataFrame):
    rule = f"If you gain a Siren and put it in your hand using {hand_cso}, you still need to trash an Action from your hand in order to not trash the Siren."
    add_interaction("Siren", hand_cso, rule, df, add_together_if_present=True)


def _add_on_gain_hand_gatekeeper_interaction(hand_cso: str, df: pd.DataFrame):
    rule = f"If you gain a card and put it in your hand using {hand_cso} while under the Gatekeeper attack, you still need to Exile it if you don't have a copy of it in Exile."
    add_interaction("Gatekeeper", hand_cso, rule, df, add_together_if_present=True)


def _add_on_gain_hand_sheepdog_interaction(hand_cso: str, df: pd.DataFrame):
    rule = f"If you gain a Sheepdog to your hand using {hand_cso}, you can immediately react to its own gain and play it."
    add_interaction("Sheepdog", hand_cso, rule, df, add_together_if_present=True)


##########################################################################################################
# Other stuff
def _add_other_on_gain_interactions(df: pd.DataFrame):
    # Charm is a special case of an on-gain-play cso because it can only be gained and directly played via Spell Scroll
    add_interaction(
        "Spell Scroll",
        "Charm",
        "When you play a Charm by gaining it via Spell Scroll and choose the 'gain another card' option, you will not gain another $5 cost card due to its 'Next Time' wording. Instead, you'll gain a differently named card with the same cost for the next card you gain.",
        df,
    )
    add_interaction(
        "blockade",
        "rapid expansion",
        "Once Rapid Expansion (RE) is triggered, any Actions or Treasures gained by Blockade will be set aside by RE and thus not truly be Blockaded (you clean up the Blockade during Clean-up).",
        df,
    )
    add_interaction(
        "quartermaster",
        "rapid expansion",
        "Once Rapid Expansion (RE) is triggered, any Actions or Treasures gained by Quartermaster will be set aside by RE and thus not put onto Quartermaster.",
        df,
    )

    add_interaction(
        "Siren",
        "Gatekeeper",
        "If you gain a Siren while under Gatekeeper attack (and don't have a Siren in Exile), you can choose which effect (exiling Siren or trashing an Action for it) to resolve first, and the Siren stays in Exile even if you don't trash an Action afterwards.",
        df,
    )


##########################################################################################################
# Final function
def add_all_on_gain_interactions(df: pd.DataFrame, verbose=False):
    """Adds all on-gain interactions to the DataFrame."""
    num_before = len(df)
    for on_play_cso in CAN_PLAY_CARD_ON_GAIN:
        _add_on_overpay_infirmary_interaction(on_play_cso, df)
        _add_on_gain_play_gatekeeper_interaction(on_play_cso, df)
        _add_on_gain_play_duplicate_interaction(on_play_cso, df)
        _add_on_gain_play_galleria_interaction(on_play_cso, df)
        _add_on_gain_play_guildmaster_interaction(on_play_cso, df)
        _add_on_gain_play_haggler_interaction(on_play_cso, df)
        _add_on_gain_play_livery_interaction(on_play_cso, df)
        _add_on_gain_play_search_interaction(on_play_cso, df)
        _add_on_gain_play_skirmisher_interaction(on_play_cso, df)
        _add_on_gain_play_siren_interaction(on_play_cso, df)
        _add_on_gain_play_changeling_interaction(on_play_cso, df)
        _add_on_gain_play_kiln_interaction(on_play_cso, df)
        for shuffle_trigger_cso in CAN_CAUSE_SHUFFLE_TRIGGER_ON_GAIN:
            _add_on_play_shuffle_trigger_interaction(
                on_play_cso, shuffle_trigger_cso, df
            )
        if on_play_cso not in ["Gondola", "Spell Scroll"]:
            for topdecker in WILL_TOPDECK_ON_GAIN:
                _add_on_gain_play_topdecker_interaction(topdecker, on_play_cso, df)
    for on_play_cso in ["Innovation", "City-State"]:
        _add_on_gain_play_improve_interaction(on_play_cso, df)
    # Sailor can also play durations on gain
    _add_on_gain_play_search_interaction("Sailor", df)
    _add_on_gain_play_siren_interaction("Sailor", df)
    _add_on_gain_play_gatekeeper_interaction("Sailor", df, " Duration")

    # Some other on-gain play interactions
    _add_on_gain_play_gatekeeper_interaction("Berserker", df)
    _add_on_gain_play_gondola_sec_shrine_interaction(df)

    for shuffle_trigger_cso in CAN_CAUSE_SHUFFLE_TRIGGER_ON_GAIN:
        _add_on_shuffle_trigger_siren_interaction(shuffle_trigger_cso, df)

    # Topdecking and setting aside interactions
    for topdeck_cso in CAN_TOPDECK_ON_GAIN:
        _add_on_gain_topdeck_siren_interaction(topdeck_cso, df, choice=True)
        _add_on_gain_topdeck_villa_interaction(topdeck_cso, df, choice=True)
    for topdeck_cso in WILL_TOPDECK_ON_GAIN:
        _add_on_gain_topdeck_siren_interaction(topdeck_cso, df)
        _add_on_gain_topdeck_villa_interaction(topdeck_cso, df)
    for topdeck_cso in MUST_TOPDECK_ON_GAIN:
        _add_on_gain_topdeck_siren_interaction(topdeck_cso, df, force=True)
        _add_on_gain_topdeck_villa_interaction(topdeck_cso, df)
    for night_to_hand_gain in GAINS_SELF_TO_HAND_CARDS:
        if night_to_hand_gain == "Villa":
            continue
        for topdeck_cso in CAN_TOPDECK_ON_GAIN:
            _add_on_gain_topdeck_night_to_hand_interaction(
                topdeck_cso, night_to_hand_gain, df, choice=True
            )
        for topdeck_cso in WILL_TOPDECK_ON_GAIN + MUST_TOPDECK_ON_GAIN:
            _add_on_gain_topdeck_night_to_hand_interaction(
                topdeck_cso, night_to_hand_gain, df
            )

    for set_aside_cso in GAINS_TO_SET_ASIDE:
        _add_on_gain_set_aside_siren_interaction(set_aside_cso, df)
    for hand_cso in GAINS_TO_HAND:
        _add_on_gain_hand_siren_interaction(hand_cso, df)
        _add_on_gain_hand_gatekeeper_interaction(hand_cso, df)
        _add_on_gain_hand_sheepdog_interaction(hand_cso, df)
    _add_other_on_gain_interactions(df)

    if verbose:
        print(f"Added {len(df) - num_before} on-gain interactions.")
