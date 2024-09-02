"""Interactions that occur with TYPEE"""

import pandas as pd

from ..constants import TGG_BUG_DISCLAIMER
from ..interaction_util import (
    add_interaction,
    add_multiple_interactions,
    add_multiple_interactions_from_single,
)


##########################################################################################################
# Final function
def add_all_TYPEE_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all TYPEE interactions to the DataFrame."""
    num_before = len(df)

    if verbose:
        print(f"Added {len(df) - num_before} TYPEE interactions.")
