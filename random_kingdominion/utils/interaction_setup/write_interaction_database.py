from ...constants import ALL_CSOS, PATH_CARD_INFO, VALID_COMBO_TYPES
from ...logger import LOGGER
from ..utils import write_dataframe_to_file
from .combo_util import get_combo_df
from .interaction_util import get_empty_interaction_df
from .specifics import *


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
    fpath = PATH_CARD_INFO.joinpath("good_interaction_data.csv")
    write_dataframe_to_file(df, fpath, overwrite=overwrite, verbose=verbose)
    if verbose:
        LOGGER.info(
            f"Wrote the interaction database with {len(df)} interactions in total."
        )


def write_combo_database(overwrite: bool = True, verbose: bool = True):
    """Basic Sanitization of the human-readable raw combo data into"""
    df = get_combo_df(verbose)
    error_occured = False
    for cso in set(df["CSO1"].tolist() + df["CSO2"].tolist()):
        if cso not in ALL_CSOS.index:
            LOGGER.warning(f"Found unknown CSO '{cso}' in combo data.")
            error_occured = True
    for _, row in df.iterrows():
        if row["Type"] not in VALID_COMBO_TYPES:
            LOGGER.warning(f"Found unknown combo type '{row['Type']}' in combo data for entry {row['CSO1']}/{row['CSO2']}.")
            error_occured = True
    if error_occured:
        LOGGER.error("Errors occured while processing the combo data.\nABORTING writing the combo database. Please fix the issues in 'raw_combo_data' and try again.")
        return
    fpath = PATH_CARD_INFO.joinpath("good_combo_data.csv")
    write_dataframe_to_file(df, fpath, overwrite=overwrite, verbose=verbose)
    if verbose:
        LOGGER.info(f"Wrote the combo database with {len(df)} combos in total.")