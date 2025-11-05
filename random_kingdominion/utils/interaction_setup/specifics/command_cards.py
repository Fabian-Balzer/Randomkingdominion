"""Interactions that occur with command"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)

# Some more stuff in individual_cards.py for Reserve interactions


def _add_all_daimyo_interactions(df: pd.DataFrame):
    # Enlightenment interactions handled in prophecies.py
    courier = "Daimyo/Courier---If you play Daimyo and then Courier to play a Daimyo from your discard pile, since the next non-Command card you replay is the Courier, it is replayed one more time afterwards by the Daimyo played from the discard pile."
    add_multiple_interactions_from_single(courier, df)
    gondola = "Daimyo/Gondola---If you play Daimyo and then a card that gains Gondola, which you use to play a Daimyo from your hand, since the next non-Command card you replay is said gainer, it is replayed one more time afterwards by the second Daimyo."
    add_multiple_interactions_from_single(gondola, df)
    vassal = "Daimyo/Vassal---If you play Daimyo and then Vassal, which discards and plays another Daimyo from your deck, since the next non-Command card you replay is the Vassal, it is replayed one more time afterwards by the second Daimyo."
    add_multiple_interactions_from_single(vassal, df)
    # Inspiring, Conclave, Imp and Shop cannot play another Daimyo unless the first one has somehow left play
    play_from_hand = "Daimyo/Throne Room|King's Court|Procession|Coronet|Crown|Disciple|Royal Galley|Elder|First Mate---If you play Daimyo and then {card_b}, which you use to play another Daimyo from your hand, since the next non-Command card you replay is the {card_b}, it is replayed one more time afterwards by the second Daimyo."
    add_multiple_interactions_from_single(play_from_hand, df)
    other_command = "Daimyo/Captain|Overlord|Band of Misfits---If you play Daimyo and then {card_b} and use that to play an Action card from the Supply, the Action card is replayed as {card_b} is a Command card."
    add_multiple_interactions_from_single(other_command, df)


def _add_all_prince_interaction(df: pd.DataFrame):
    add_interaction(
        "Prince",
        "Encampment",
        "If you set aside an Encampment with Prince, it will fail to set itself aside when you play it and don't reveal Gold or Plunder, so Prince replays it at the start of each turn successfully.",
        df,
    )
    add_interaction(
        "Prince",
        "Throne Room",
        "If you set aside a Throne Room with Prince, if you play another Duration card (such as Prince) with it at the start of one of your turns, the Duration card will be played twice, but since the initial Princed Throne room is not in play, its Duration effects will only apply once; If you double play e.g. a second Prince, you get to set aside two cards, but only the first one will be played again at the start of each of your turns, whil the second one will be stranded.",
        df,
    )


def _add_all_trash_this_to_interactions(df: pd.DataFrame):
    # Cabin Boy and Search do not apply here.
    overlord_trash_this_to = "Overlord|Necromancer/Mining Village|Embargo|Treasure Map|Death Cart|Pillage|Raze|Small Castle|Pixie|Acolyte---If you play {card_b} using {card_a} and try to trash itself, it stays where it was, and you do not get the effect you would have gotten from trashing it."
    add_multiple_interactions_from_single(overlord_trash_this_to, df)
    captain_bom_trash_this_to = "Captain|Band of Misfits/Mining Village|Embargo|Treasure Map|Death Cart|Raze|Pixie|Acolyte---If you play {card_b} using {card_a} and try to trash itself, it stays where it was, and you do not get the effect you would have gotten from trashing it."
    add_multiple_interactions_from_single(captain_bom_trash_this_to, df)
    prince_trash_this_to = "Prince/Mining Village|Embargo|Treasure Map|Death Cart|Raze|Pixie|Acolyte---If you have set aside {card_b} with Prince and try to trash itself when you play it, it stays where it was, and you do not get the effect you would have gotten from trashing it."
    add_multiple_interactions_from_single(prince_trash_this_to, df)
    urchin = "Overlord|Band of Misfits|Captain|Necromancer/Urchin---If you have played {card_b} using {card_a}, you will not get to trash it later once playing an Attack card. However, if you play Urchin and later play another Attack card using {card_a}, you will still get to trash the Urchin."
    add_multiple_interactions_from_single(urchin, df)
    knights = "Overlord|Necromancer/Knights---If you play a Knight using {card_a}, you do not trash it even if you trash an opponent's Knight with it."
    add_multiple_interactions_from_single(knights, df)
    knights2 = "Band of Misfits|Captain/Sir Martin---If you play Sir Martin using {card_a}, you do not trash it even if you trash an opponent's Knight with it."
    add_multiple_interactions_from_single(knights2, df)


def _add_all_trash_this_no_condition_interactions(df: pd.DataFrame):
    overlord_necro = "Overlord|Necromancer/Feast|Farmers' Market|Tragic Hero|Acting Troupe---If you play {card_b} using {card_a} and try to trash itself, it stays where it was, and *do* get the effect."
    add_multiple_interactions_from_single(overlord_necro, df)
    prince = "Prince/Feast|Farmers' Market|Tragic Hero|Acting Troupe---If you have set aside {card_b} with Prince and try to trash itself when you play it, it stays where it was, and you *do* get the effect."
    add_multiple_interactions_from_single(prince, df)
    captain_bom = "Captain|Band of Misfits/Feast|Farmers' Market|Acting Troupe---If you play {card_b} using {card_a}, it stays where it was, and *do* get the effect you would have gotten from trashing it."
    add_multiple_interactions_from_single(captain_bom, df)


def _add_all_workshop_interactions(df: pd.DataFrame):
    workshops = "Hermit|Groom|Ironworks|Feast|Workshop|Inventor|Carpenter|Craftsman"
    workshop_inter = f"Overlord|Band of Misfits|Captain/{workshops}---If you play {{card_b}} using {{card_a}}, you can gain a {{card_b}} with it (despite {{card_a}} saying 'leaving it there', as this just refers to the card moving into play)."
    add_multiple_interactions_from_single(
        workshop_inter, df, add_together_if_present=True
    )
    remodels = "Remodel|Change|Remake|Replace|Upgrade|Governor|Graverobber"
    remodel_inter = f"Overlord/{remodels}---If you play {{card_b}} using {{card_a}}, trashing an appropriate card from your hand, you can gain another {{card_b}} with it (despite {{card_a}} saying 'leaving it there', as this just refers to the card moving into play)."
    add_multiple_interactions_from_single(
        remodel_inter, df, add_together_if_present=True
    )
    remodel_inter = f"Band of Misfits|Captain/Remodel|Change|Remake---If you play {{card_b}} using {{card_a}}, trashing an appropriate card from your hand, you can gain another {{card_b}} with it (despite {{card_a}} saying 'leaving it there', as this just refers to the card moving into play)."
    add_multiple_interactions_from_single(
        remodel_inter, df, add_together_if_present=True
    )


##########################################################################################################
# Final function
def add_all_command_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all command interactions to the DataFrame."""
    num_before = len(df)
    _add_all_daimyo_interactions(df)
    _add_all_trash_this_to_interactions(df)
    _add_all_trash_this_no_condition_interactions(df)
    _add_all_workshop_interactions(df)
    _add_all_prince_interaction(df)

    if verbose:
        print(f"Added {len(df) - num_before} command interactions.")
