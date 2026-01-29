"""Interactions that occur whenever you gain a card + Overpay interactions."""

import pandas as pd

from ....constants import ALL_CSOS
from ....cso_series_utils import listlike_contains
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
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


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


def _add_on_gain_play_enlightenment_interactions(
    on_gain_play_cso: str, df: pd.DataFrame
):
    if on_gain_play_cso == "Gondola":
        rule = f"If Enlightenment is active and you gain a Gondola in your buy phase, you can play an Treasure from your hand, which will give you the usual effect."
    else:
        rule = f"If Enlightenment is active and you gain a Treasure in your buy phase, you can play it immediately using {on_gain_play_cso}, causing you to receive the usual effect."
    add_interaction("Enlightenment", on_gain_play_cso, rule, df)


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


def _add_on_gain_play_inventor_interactions(on_gain_play_cso: str, df: pd.DataFrame):
    if on_gain_play_cso == "Gondola":
        rule = f"When you gain a Gondola with an Inventor and use its on-gain ability to play an Inventor from your hand, since the first Inventor is not resolved, its cost-reduction does not apply then."
    else:
        rule = f"When you play an Inventor to gain and play another Inventor immediately using {on_gain_play_cso}, the cost of the cards will not yet be reduced as the first Inventor's 'gain a card costing up to $4' effect has not been resolved."
    add_interaction("Inventor", on_gain_play_cso, rule, df)


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
    if on_gain_play_cso in ["Gondola", "Silver Mine"]:
        return
    rule = f"If you gain a Siren and use {on_gain_play_cso} to play the Siren, Siren no longer requires you to trash an Action card from your hand in order to not trash the Siren."
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
    topdecker: str, on_play_cso: str, df: pd.DataFrame, choice=False
):
    if on_play_cso == "Gondola":
        return
    elif choice:
        rule = f"When you gain a card, you can decide whether to immediately play it using {on_play_cso}, or topdeck it using {topdecker}."
    else:
        rule = f"When you gain a card using {topdecker} and immediately play it using {on_play_cso}, you will not be able to topdeck it."
    if topdecker == "Progress":
        rule = f"When you gain a card while Progress is active, you get to choose between topdecking it and playing it immediately using {on_play_cso} (you can only do one)."
    add_interaction(topdecker, on_play_cso, rule, df)


def _add_all_on_gain_basilica_interactions(df: pd.DataFrame):
    add_interaction(
        "Basilica",
        "Nomads",
        "Gaining a Nomads in your Buy phase will give you $2, and thus also give you 2 Basilica VP even if you have $0 prior to gaining them.",
        df,
    )
    add_interaction(
        "Basilica",
        "Marchland",
        "Gaining Marchlands in your Buy phase and discarding at least 2 cards for $ will also give you 2 Basilica VP even if you have $0 prior to gaining them.",
        df,
    )


def _add_all_on_gain_colonnade_interactions(df: pd.DataFrame):
    rule = "Colonnade/City-State|Innovation---If you use {card_b} to immediately play an Action you gained, you can take 2 VP from Colonnade."
    add_multiple_interactions_from_single(rule, df)
    rule = "Colonnade/Inheritance---If you have bought Inheritance, Estates count as Actions on your turn, and therefore will give you 2 VP when bought with an Estate in play."
    add_multiple_interactions_from_single(rule, df)
    rule = "Colonnade/Trail|Berserker---If you gain a {card_b} during your Buy phase and play it immediately, you can take 2 VP from Colonnade."
    add_multiple_interactions_from_single(rule, df)


##########################################################################################################
# Shuffle trigger Interactions
def _add_on_shuffle_trigger_siren_interaction(other: str, df: pd.DataFrame):
    if other == "Trail":
        return
    rule = f"If you gain a Siren and somehow trigger a shuffle by drawing a card using {other}, you are no longer required to trash an Action card for the Siren to stay in your deck."
    add_interaction("Siren", other, rule, df)


##########################################################################################################
### On-Gain-Topdecking interactions
def _add_on_gain_topdeck_siren_interaction(
    topdeck_cso: str, df: pd.DataFrame, choice=False, force=False
):
    if choice:
        rule = f"If you gain a Siren and choose to topdeck it using {topdeck_cso}, you don't need to trash an Action card in order for it to stay in your deck."
    elif force:
        rule = f"If you gain a Siren and topdeck it using {topdeck_cso}, you don't need to trash an Action card in order for the Siren to stay in your deck."
    else:
        rule = f"If you gain a Siren onto your deck using {topdeck_cso}, you still need to trash an Action card from your hand in order to not trash the Siren."
    add_interaction("Siren", topdeck_cso, rule, df)


def _add_on_gain_topdeck_villa_interaction(
    topdeck_cso: str, df: pd.DataFrame, choice=False
):
    if choice:
        rule = f"If you gain a Villa, you can decide whether to topdeck it using {topdeck_cso}, or gain it to your hand. In any case, you will receive +1 Action and return to your Action phase if you're in your buy phase."
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


def _add_on_gain_to_hand_haunted_woods_interactions(
    df: pd.DataFrame, to_hand_card: str
):
    add_interaction(
        "Haunted Woods",
        to_hand_card,
        f"If you buy a {to_hand_card} while under the Haunted Woods attack, you are forced to topdeck it (the {to_hand_card}) immediately.",
        df,
    )


##########################################################################################################
### On-Gain-Set-Aside interactions
def _add_on_gain_set_aside_siren_interaction(set_aside_cso: str, df: pd.DataFrame):
    rule = f"If you gain a Siren and set it aside using {set_aside_cso}, you still need to trash an Action from your hand in order to not trash the Siren."
    if set_aside_cso in ["Rapid Expansion", "Hasty"]:
        rule = f"If you gain a Siren and set it aside using {set_aside_cso}, since it's set aside after being gained, it will stay there even if you fail to trash an Action."
    add_interaction("Siren", set_aside_cso, rule, df)


def _add_on_gain_set_aside_gatekeeper_interaction(set_aside_cso: str, df: pd.DataFrame):
    rule = f"If you are under the Gatekeeper attack and gain an Action or Treasure you don't have a copy of in Exile and set it aside using {set_aside_cso}, you still need to Exile it."
    if set_aside_cso in ["Rapid Expansion", "Hasty"]:
        rule = f"If you are under the Gatekeeper attack and gain an Action or Treasure you don't have a copy of in Exile and set it aside using {set_aside_cso} first, you do not Exile it."
    add_interaction("Gatekeeper", set_aside_cso, rule, df)


##########################################################################################################
### On-Gain-to-Hand interactions
def _add_on_gain_hand_siren_interaction(hand_cso: str, df: pd.DataFrame):
    if hand_cso == "Silver Mine":
        return
    rule = f"If you gain a Siren and put it in your hand using {hand_cso}, you still need to trash an Action from your hand in order to not trash the Siren."
    add_interaction("Siren", hand_cso, rule, df, add_together_if_present=True)


def _add_on_gain_hand_gatekeeper_interaction(hand_cso: str, df: pd.DataFrame):
    rule = f"If you gain an Action or Treasure and put it in your hand using {hand_cso} while under the Gatekeeper attack, you still need to Exile it if you don't have a copy of it in Exile unless you somehow manage to play it during the on-gain-window (e.g. via City-State, or if it has a reaction that plays it, like Sheepdog or Berserker)."
    if hand_cso == "Falconer":
        rule += " Note that if you gain a Falconer to your hand somehow while under the Gatekeeper attack (e.g. via Artisan), reacting and playing it means that you do not have to Exile it."
    add_interaction("Gatekeeper", hand_cso, rule, df, add_together_if_present=True)


def _add_multi_gain_gatekeeper_interaction(df: pd.DataFrame):
    multi_gain = {
        "Cache": "Coppers",
        "Pillage": "Spoils",
        "Stonemason": "cards from the same pile",
        "Ball": "cards from the same pile",
        "Banquet": "Coppers",
        "Conquest": "Silvers",
        "Sleigh": "Horses",
        "Cavalry": "Horses",
        "Paddock": "Horses",
        "Weaver": "Silvers",
    }
    for cso, gain_desc in multi_gain.items():
        rule = f"If you gain two {gain_desc} using {cso} while under the Gatekeeper attack, if you don't already have a copy in Exile, you need to exile the first, but may discard the exiled copy along with the gain of the second."
        add_interaction("Gatekeeper", cso, rule, df)
    multi_gain_with_num = {
        "Treasure Map": "four Golds",
        "Magic Lamp": "three Wishes",
        "Trusty Steed": "four Silvers",
        "Courser": "four Silvers",
        "Trade": "two or more Silvers",
        "Hostelry": "two or more Horses",
        "Livery": "two or more Horses",
        "Stampede": "five Horses",
        "Charm": "two or more copies of the same card upon gain",
        "Haggler": "two or more cheaper copies of the same card upon buy",
        "Feodum": "three Silvers",
        "Windfall": "three Golds",
    }
    for cso, gain_desc in multi_gain_with_num.items():
        rule = f"If you gain {gain_desc} with {cso} while under the Gatekeeper attack, if you don't already have a copy in Exile, you need to exile the first, but may discard the exiled copy along with the gain of the last copy."
        add_interaction("Gatekeeper", cso, rule, df)
    double_gain = ["Experiment", "Port"]
    for cso in double_gain:
        rule = f"If you gain two {cso}s while under the Gatekeeper attack, if you don't already have a copy in Exile, you need to exile the first, but may discard the exiled copy along with the gain of the second."
        add_interaction("Gatekeeper", cso, rule, df, add_together_if_present=True)
    # Fortune/Beggar
    rule = f"If you gain a Fortune while having two or more Gladiators in play while under the Gatekeeper attack, if you don't already have a copy of Gold in Exile, you need to exile the first, but may discard the exiled copy along with any later Gold gains."
    add_interaction("Gatekeeper", "Fortune", rule, df)


def _add_beggar_extra_interactions(df: pd.DataFrame):
    add_interaction(
        "Beggar",
        "Sheepdog",
        f"If you react with a Beggar to an Attack, the first Silver you gain is topdecked, so you will draw it if you react with a Sheepdog to the second Silver gain. If you react Sheepdog to the first Silver gain, you draw two cards, topdeck it, and gain the other one to the discard pile, or can react with Sheepdog to the second Silver gain and draw the first one immediately. NOTE THAT ON THE TGG CLIENT, THIS IS CURRENTLY IMPLEMENTED THE OTHER WAY AROUND.",
        df,
    )
    add_interaction(
        "Gatekeeper",
        "Beggar",
        "If you react with a Beggar to a subsequent Attack (not the initial Gatekeeper play) while under the Gatekeeper attack and don't have a Silver in Exile, the first Silver you would gain onto your deck is Exiled, and if you decide to discard it with the second Silver gain, you don't get to have one topdecked. NOTE THAT ON THE TGG CLIENT, THIS IS CURRENTLY IMPLEMENTED THE OTHER WAY AROUND.",
        df,
    )


def _add_on_gain_hand_sheepdog_interaction(hand_cso: str, df: pd.DataFrame):
    if hand_cso == "Silver Mine":
        return
    rule = f"If you gain a Sheepdog to your hand using {hand_cso}, you can immediately react to its own gain and play it."
    add_interaction("Sheepdog", hand_cso, rule, df, add_together_if_present=True)


def _add_on_gain_topdeck_gatekeeper_interaction(
    topdeck_cso: str, df: pd.DataFrame, choice=False
):
    rule = f"If you gain a card that you do not have a copy of in Exile and topdeck it first using {topdeck_cso} while under the Gatekeeper attack, you do not need to put it into Exile."
    if topdeck_cso == "Sleigh":
        rule = f"If you gain an Action or Treasure that you do not have a copy of in Exile while under the Gatekeeper attack, you can choose to first react with Sleigh to topdeck or put it into your hand, in which case you do not put it into Exile."
    elif topdeck_cso == "Watchtower":
        rule = f"If you gain an Action or Treasure that you do not have a copy of in Exile while under the Gatekeeper attack, you can choose to first react with Watchtower to topdeck or trash it, in which case you do not put it into Exile."
    elif choice:
        rule = f"If you gain an Action or Treasure that you do not have a copy of in Exile while under the Gatekeeper attack, you can choose to first topdeck it using {topdeck_cso}, in which case you do not put it into Exile."
    elif topdeck_cso == "Invasion":
        rule = f"If you are under the Gatekeeper attack and buy Invasion, both the Action card and the Loot you gain are Exiled (instead of topdecked and played) unless you have a copy of it in Exile."
    elif topdeck_cso == "Progress":
        rule = f"When you gain an Action or Treasure of which you do not have a copy in Exile while Progress is active and you are under the Gatekeeper attack, you may decide whether to topdeck or Exile it."
    else:
        rule = f"When you gain an Action or Treasure using {topdeck_cso} while under the Gatekeeper attack, it will be gained on top of your deck and then Exiled if you do not have a copy of it in Exile."
    add_interaction("Gatekeeper", topdeck_cso, rule, df)


def _add_on_gain_topdeck_rapid_expansion_interaction(
    topdeck_cso: str, df: pd.DataFrame, choice=False
):
    if topdeck_cso == "Sleigh":
        rule = f"When you gain a card while Rapid Expansion is active, you can decide to topdeck it or put it into your hand using {topdeck_cso}, instead of setting it aside."
    elif topdeck_cso == "Watchtower":
        rule = f"When you gain a card while Rapid Expansion is active, you can decide to topdeck or trash it using {topdeck_cso}, instead of setting it aside."
    elif choice:
        rule = f"When you gain a card while Rapid Expansion is active, you can decide to topdeck it using {topdeck_cso} instead of setting it aside."
    elif topdeck_cso == "Invasion":
        rule = f"If Rapid Expansion is active, both the Action card and the Loot you gain are set aside (instead of topdecked and played)."
    else:
        rule = f"When you gain a card using {topdeck_cso}, it will be gained on top of your deck and then be set aside if Rapid Expansion is active."
    add_interaction("rapid expansion", topdeck_cso, rule, df)


##########################################################################################################
### Stuff where turn order is important
def _add_all_skirmisher_interactions(df: pd.DataFrame):
    add_interaction(
        "Invest",
        "Skirmisher",
        "If you have invested in Skirmisher or another Attack card and your opponent gains one after having played Skirmisher, you first discard down to 3 cards in hand, and then draw due to Invest",
        df,
    )
    add_interaction(
        "Skirmisher",
        "Falconer",
        "If your opponent has played a Skirmisher and gains an Attack card while you have a Falconer in hand, you first have to discard down to three cards in hand, and only then can react the Falconer since the different things happen in turn order.",
        df,
    )
    add_interaction(
        "Monkey",
        "Skirmisher",
        "If you have played a Monkey and your opponent gains an Attack after having played Skirmisher, you first discard down to 3 cards in hand, and then draw due to Monkey since the different things happen in turn order.",
        df,
    )


def _add_all_haunted_castle_interactions(df: pd.DataFrame):
    add_interaction(
        "Haunted Castle",
        "Falconer",
        "If your opponent gains Haunted Castle and you have a Falconer in hand, you first have to topdeck two cards, and only then can react the Falconer since the different things happen in turn order.",
        df,
    )
    add_interaction(
        "Monkey",
        "Haunted Castle",
        "If you have played a Monkey and your opponent gains a Haunted Castle, you first topdeck two cards, and then draw due to Monkey since the different things happen in turn order.",
        df,
    )
    add_interaction(
        "Road Network",
        "Haunted Castle",
        "If you have bought Road Network and your opponent gains a Haunted Castle, you first topdeck two cards, and then draw due to Road Network since the different things happen in turn order.",
        df,
    )


def _add_all_haunted_woods_interactions(df: pd.DataFrame):
    add_interaction(
        "Haunted Woods",
        "Falconer",
        "If you buy a dual-or-more-type card with a Falconer in hand while under the Haunted Woods attack, you can choose to first react the Falconer to gain a cheaper card to hand and then topdeck your hand afterwards, or first topdeck your hand (including the Falconer).",
        df,
    )
    add_interaction(
        "Sheepdog",
        "Haunted Woods",
        "If you buy a card with a Sheepdog in hand while under the Haunted Woods attack, you can choose to first play the Sheepdog and then topdeck your hand afterwards, or first topdeck your hand (including the Sheepdog).",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Marchland",
        "If you buy a Marchland while under the Haunted Woods attack, you can choose whether to discard cards from your hand for $ from Marchland's on-gain effect, or to topdeck the cards in your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Souk",
        "If you buy a Souk while under the Haunted Woods attack, you can choose whether to first trash up to two cards from your hand, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Siren",
        "If you buy a Siren while under the Haunted Woods attack, you can choose whether to first trash an Action from your hand, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Farmland",
        "If you buy a Farmland while under the Haunted Woods attack, you can choose whether to first trash a card from your hand to gain one costing $2 more, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Farmhands",
        "If you buy a Farmhands while under the Haunted Woods attack, you can choose whether to first set aside an Action or Treasure from your hand, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Grand Castle",
        "If you buy a Grand Castle while under the Haunted Woods attack, you can choose whether to first reveal your hand for VP, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Cemetery",
        "If you buy a Cemetery while under the Haunted Woods attack, you can choose whether to first trash cards from your hand, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Blessed Village",
        "If you buy a Blessed Village while under the Haunted Woods attack, you can choose whether to first take a Boon, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Cursed Village",
        "If you buy a Cursed Village while under the Haunted Woods attack, you can choose whether to first receive the next Hex, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Ducat",
        "If you buy a Ducat while under the Haunted Woods attack, you can choose whether to first trash a Copper from your hand, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Cavalry",
        "If you buy a Cavalry while under the Haunted Woods attack, you can choose whether to first draw two cards and then topdeck your hand, or whether to first topdeck your hand and then draw.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Gondola",
        "If you buy a Gondola while under the Haunted Woods attack, you can choose whether to first play an Action card from your hand and then topdeck, or whether to first topdeck your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Hostelry",
        "If you buy a Hostelry while under the Haunted Woods attack, you can choose whether to discard Treasures for Horses and then topdeck your hand, or to first topdeck the cards in your hand.",
        df,
    )
    add_interaction(
        "Haunted Woods",
        "Villa",
        "If you buy a Villa while under the Haunted Woods attack, you can put it into your hand after topdecking it (and your hand).",
        df,
    )


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
        "Spell Scroll",
        "Hasty",
        "When you gain a Hasty card with Spell Scroll, you won't be able to play it this turn as it is set aside before that.",
        df,
    )
    add_interaction(
        "Spell Scroll",
        "Rapid Expansion",
        "When you gain a card with Spell Scroll while Rapid Expansion is active, you won't be able to play it this turn as it is set aside before that.",
        df,
    )
    add_interaction(
        "blockade",
        "rapid expansion",
        "Once Rapid Expansion (RE) is triggered, any Actions or Treasures gained by Blockade will be set aside by RE and thus not truly be Blockaded (you clean up the Blockade during Clean-up).",
        df,
    )
    add_interaction(
        "continue",
        "rapid expansion",
        "When Rapid Expansion is active, the Action card gained from a Continue buy is set aside before it can be played (you still get +1 Action, +1 Buy and return to your Action phase).",
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
        _add_on_gain_play_changeling_interaction(on_play_cso, df)
        _add_on_gain_play_duplicate_interaction(on_play_cso, df)
        _add_on_gain_play_enlightenment_interactions(on_play_cso, df)
        _add_on_gain_play_galleria_interaction(on_play_cso, df)
        _add_on_gain_play_gatekeeper_interaction(on_play_cso, df)
        _add_on_gain_play_guildmaster_interaction(on_play_cso, df)
        _add_on_gain_play_haggler_interaction(on_play_cso, df)
        _add_on_gain_play_inventor_interactions(on_play_cso, df)
        _add_on_gain_play_kiln_interaction(on_play_cso, df)
        _add_on_gain_play_livery_interaction(on_play_cso, df)
        _add_on_gain_play_search_interaction(on_play_cso, df)
        _add_on_gain_play_skirmisher_interaction(on_play_cso, df)
        _add_on_gain_play_siren_interaction(on_play_cso, df)
        for shuffle_trigger_cso in CAN_CAUSE_SHUFFLE_TRIGGER_ON_GAIN:
            _add_on_play_shuffle_trigger_interaction(
                on_play_cso, shuffle_trigger_cso, df
            )
        if on_play_cso not in ["Gondola", "Spell Scroll"]:
            _add_on_gain_play_topdecker_interaction("Progress", on_play_cso, df)
            for topdecker in WILL_TOPDECK_ON_GAIN:
                _add_on_gain_play_topdecker_interaction(topdecker, on_play_cso, df)
            for topdecker in CAN_TOPDECK_ON_GAIN:
                _add_on_gain_play_topdecker_interaction(
                    topdecker, on_play_cso, df, choice=True
                )
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
        _add_on_gain_topdeck_rapid_expansion_interaction(topdeck_cso, df, choice=True)
        _add_on_gain_topdeck_gatekeeper_interaction(topdeck_cso, df, choice=True)
    for topdeck_cso in WILL_TOPDECK_ON_GAIN:
        _add_on_gain_topdeck_siren_interaction(topdeck_cso, df)
        _add_on_gain_topdeck_villa_interaction(topdeck_cso, df)
        _add_on_gain_topdeck_rapid_expansion_interaction(topdeck_cso, df)
        _add_on_gain_topdeck_gatekeeper_interaction(topdeck_cso, df)
    for topdeck_cso in MUST_TOPDECK_ON_GAIN:
        _add_on_gain_topdeck_siren_interaction(topdeck_cso, df, force=True)
        _add_on_gain_topdeck_villa_interaction(topdeck_cso, df)
        _add_on_gain_topdeck_gatekeeper_interaction(topdeck_cso, df)
    for night_to_hand_gain in GAINS_SELF_TO_HAND_CARDS:
        if night_to_hand_gain == "Villa":
            continue
        _add_on_gain_to_hand_haunted_woods_interactions(df, night_to_hand_gain)
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
        _add_on_gain_set_aside_gatekeeper_interaction(set_aside_cso, df)
    for hand_cso in GAINS_TO_HAND:
        _add_on_gain_hand_siren_interaction(hand_cso, df)
        _add_on_gain_hand_gatekeeper_interaction(hand_cso, df)
        _add_on_gain_hand_sheepdog_interaction(hand_cso, df)
    _add_all_haunted_woods_interactions(df)
    _add_all_haunted_castle_interactions(df)
    _add_all_skirmisher_interactions(df)
    _add_multi_gain_gatekeeper_interaction(df)
    _add_beggar_extra_interactions(df)
    _add_other_on_gain_interactions(df)
    _add_all_on_gain_basilica_interactions(df)
    _add_all_on_gain_colonnade_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} on-gain interactions.")
