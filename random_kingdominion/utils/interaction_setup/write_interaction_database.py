from datetime import datetime
from typing import Literal

import pandas as pd

from ...constants import ALL_CSOS, PATH_CARD_INFO, VALID_COMBO_TYPES
from ...logger import LOGGER
from ..utils import write_dataframe_to_file
from .combo_util import get_combo_df
from .interaction_util import get_empty_interaction_df
from .specifics import *


def _log_combo_or_inter_changes(
    new_df: pd.DataFrame,
    old_df: pd.DataFrame,
    change_type: Literal["combo", "interaction"],
):
    added = pd.merge(
        new_df,
        old_df,
        on=["CSO1", "CSO2"],
        how="outer",
        indicator=True,
        suffixes=("", "_old"),
    ).query('_merge == "left_only"')
    changed = pd.merge(
        new_df,
        old_df,
        on=["CSO1", "CSO2"],
        how="inner",
        suffixes=("_new", "_old"),
    )
    removed = pd.merge(
        old_df,
        new_df,
        on=["CSO1", "CSO2"],
        how="outer",
        indicator=True,
        suffixes=("", "_new"),
    ).query('_merge == "left_only"')
    rule_colname = "Rule" if change_type == "interaction" else "Description"
    changed = changed[changed[rule_colname + "_new"] != changed[rule_colname + "_old"]]
    num_added, num_changed = len(added), len(changed)
    num_removed = len(removed)
    if (num_added + num_changed + num_removed) == 0:
        LOGGER.info(f"No changes in {change_type}s detected.")
        return
    changelog_text = datetime.now().strftime(
        f"\n\n## %Y-%m-%d %H:%M:%S\nAdded: {num_added}\nChanged: {num_changed} \nRemoved: {num_removed}\n"
    )
    if len(added) > 0:
        changelog_text += f"### Added {num_added} {change_type.capitalize()}s\n\n"

    def _get_comb_str(row, t_suf=""):
        comb_str = f"{row['CSO1']} - {row['CSO2']}"
        if change_type == "combo":
            comb_str += f" ({row[f'Type{t_suf}']})"
        return comb_str

    for _, row in added.iterrows():
        changelog_text += f"#### {_get_comb_str(row)}\n{row[rule_colname]}\n"
    if len(changed) > 0:
        changelog_text += f"\n### Changed {num_changed} {change_type.capitalize()}s\n\n"
    for _, row in changed.iterrows():
        changelog_text += f"#### {_get_comb_str(row, '_new')}\n{row[rule_colname + '_old']}\n*HAS BEEN CHANGED TO*\n{row[rule_colname + '_new']}\n"
    if len(removed) > 0:
        changelog_text += f"\n### Removed {num_removed} {change_type.capitalize()}s\n\n"
    for _, row in removed.iterrows():
        changelog_text += f"#### {_get_comb_str(row)}\n{row[rule_colname]}\n"
    # Write to changelog file
    fpath_changelog = PATH_CARD_INFO.joinpath(f"{change_type}_changelog.md")
    fpath_changelog.touch(exist_ok=True)
    # Insert at the top of the file:
    with fpath_changelog.open("w", encoding="utf-8") as f:
        # existing_text = f.read()
        # f.seek(0, 0)
        f.write(changelog_text)  # + existing_text)
    LOGGER.info(
        f"Logged {num_added} added, {num_changed} changed, {num_removed} removed {change_type}s to the {change_type} changelog."
    )


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
    add_all_extra_turn_interactions(df, verbose=verbose)
    add_all_command_interactions(df, verbose=verbose)
    # LANDSCAPES
    add_all_event_interactions(df, verbose=verbose)
    add_all_project_interactions(df, verbose=verbose)
    add_all_trait_interactions(df, verbose=verbose)
    add_all_way_interactions(df, verbose=verbose)
    add_all_prophecy_interactions(df, verbose=verbose)
    add_all_allies_interactions(df, verbose=verbose)
    # INDIVIDUALS
    add_all_individual_card_interactions(df, verbose=verbose)

    fpath = PATH_CARD_INFO.joinpath("good_interaction_data.csv")
    old_df = pd.read_csv(fpath, sep=";")
    _log_combo_or_inter_changes(df, old_df, "interaction")
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
            LOGGER.warning(
                f"Found unknown combo type '{row['Type']}' in combo data for entry {row['CSO1']}/{row['CSO2']}."
            )
            error_occured = True
    if error_occured:
        LOGGER.error(
            "Errors occured while processing the combo data.\nABORTING writing the combo database. Please fix the issues in 'raw_combo_data' and try again."
        )
        return
    fpath = PATH_CARD_INFO.joinpath("good_combo_data.csv")
    old_df = pd.read_csv(fpath, sep=";")
    _log_combo_or_inter_changes(df, old_df, "combo")
    write_dataframe_to_file(df, fpath, overwrite=overwrite, verbose=verbose)
    if verbose:
        LOGGER.info(f"Wrote the combo database with {len(df)} combos in total.")
