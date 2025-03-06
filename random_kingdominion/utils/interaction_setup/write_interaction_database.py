from ...constants import PATH_ASSETS
from ..utils import write_dataframe_to_file
from .interaction_util import get_empty_interaction_df
from .specifics import *
from ...logger import LOGGER


def write_interaction_database(overwrite: bool = False, verbose: bool = True):
    df = get_empty_interaction_df()
    # MECHANICS
    add_all_cost_change_interactions(df, verbose=verbose)
    add_all_end_buy_interactions(df, verbose=verbose)
    add_all_on_clean_up_interactions(df, verbose=verbose)
    add_all_on_discard_interactions(df, verbose=verbose)
    add_all_on_gain_interactions(df, verbose=verbose)
    add_all_on_start_of_turn_interactions(df, verbose=verbose)
    add_all_victory_card_play_interactions(df, verbose=verbose)
    # LANDSCAPES
    add_all_event_interactions(df, verbose=verbose)
    add_all_project_interactions(df, verbose=verbose)
    add_all_trait_interactions(df, verbose=verbose)
    add_all_way_interactions(df, verbose=verbose)
    add_all_prophecy_interactions(df, verbose=verbose)
    add_all_allies_interactions(df, verbose=verbose)
    # INDIVIDUALS
    add_all_individual_card_interactions(df, verbose=verbose)
    # Write to file
    fpath = PATH_ASSETS.joinpath("other/interactions.csv")
    write_dataframe_to_file(df, fpath, overwrite=overwrite, verbose=verbose)
    if verbose:
        LOGGER.info(
            f"Wrote the interaction database with {len(df)} interactions in total."
        )
