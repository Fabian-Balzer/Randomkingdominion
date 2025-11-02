"""Interactions that occur with command"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)

# Some more stuff in individual_cards.py for Reserve interactions


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
    _add_all_trash_this_to_interactions(df)
    _add_all_trash_this_no_condition_interactions(df)
    _add_all_workshop_interactions(df)

    if verbose:
        print(f"Added {len(df) - num_before} command interactions.")
