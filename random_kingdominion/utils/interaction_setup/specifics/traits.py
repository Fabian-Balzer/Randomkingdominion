"""Interactions that occur with trait"""

import pandas as pd

from random_kingdominion.constants import ALL_CSOS
from random_kingdominion.utils.kingdom_helper_funcs import sanitize_cso_name

from ..constants import TGG_BUG_DISCLAIMER, ALL_THRONE_CARDS
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


def _add_individual_trait_interactions(df: pd.DataFrame):
    add_interaction(
        "Cheap",
        "Plateau Shepherds",
        "[Relevant if Cheap is on $3 or $2 cost card] If Cheap is assigned to a card initially costing $3, it becomes a $2 cost card as far as Plateau Shepherds (PS) is concerned. Conversely, a card reduced to costing $1 due to Cheap will not be eligible for PS anymore.",
        df,
    )
    # Many more reckless interactions in the on-clean-up file.
    conspirator = "[Only if Reckless is on an Action card] A Reckless card is not played twice as far as Conspirator is concerned. That means if you e.g. Reckless were on Conspirator and you would play it as the second Action this turn, you would only get +$4, not +$4 and +1 Card, +1 Action."
    add_interaction("Reckless", "Conspirator", conspirator, df)
    crossroads = "[Only if Reckless is on Crossroads] If Crossroads is Reckless, the first time you play one will give you +6 Actions."
    add_interaction("Reckless", "Crossroads", crossroads, df)
    hwman = "[Only if Inspiring is on a Treasure] If you play an Inspiring Treasure as your first Treasure while under the Highwayman attack, you can still play a unique Action card with it."
    add_interaction("Inspiring", "Highwayman", hwman, df)
    for throne in ALL_THRONE_CARDS:
        rule = f"When you play a Reckless card using {throne}, it is played four times (although technically, two of these times the initial instructions are only followed again, and it is not a 'play' for the purpose of e.g. Conspirator)."
        key = sanitize_cso_name(throne)
        types = ALL_CSOS.loc[key]["Types"]
        alert_str = ""
        if "Action" in types and "Treasure" not in types:
            alert_str = "[Only if Reckless is on an Action card] "
        elif "Treasure" in types and "Action" not in types:
            alert_str = "[Only if Reckless is on a Treasure card] "
        rule = alert_str + rule
        add_interaction("Reckless", throne, rule, df)


##########################################################################################################
# Final function
def add_all_trait_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all trait interactions to the DataFrame."""
    num_before = len(df)
    # Tireless/Panic is in Prophecies.
    _add_individual_trait_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} trait interactions.")
