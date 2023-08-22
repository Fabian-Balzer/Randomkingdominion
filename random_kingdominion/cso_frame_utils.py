"""A module with a bunch of handy static methods to manipulate Dataframes"""
from functools import reduce
from typing import Sequence

import numpy as np
import pandas as pd

from .cso_series_utils import (
    listlike_contains,
    listlike_contains_any,
    listlike_is_empty,
)


def get_unique_entries_of_list_column(df: pd.DataFrame, colname: str) -> list[str]:
    """Combine all unique entries of a list column (such as attack type)"""
    all_entries = reduce(lambda x, y: x + y, df[colname])
    return sorted(list(np.unique(all_entries)))


def contains_type(df: pd.DataFrame, type_name: str) -> bool:
    """Determin whether any of the csos share a type with the given type name.

    Parameters
    ----------
    type_name : str
        The requested type name

    Returns
    -------
    bool
        Whether any of the csos contain the given type
    """
    return np.sum(listlike_contains(df["Types"], type_name)) > 0


def get_sub_df_for_type(df: pd.DataFrame, type_name: str) -> pd.DataFrame:
    """Filter the cards for their types columns to contain the given type name,
    e.g. get_sub_df_for_type("Attack") would return all cards with the attack
    type.
    """
    return listlike_contains(df["Types"], type_name)


def get_sub_df_for_types(df: pd.DataFrame, type_names: list[str]) -> pd.DataFrame:
    """Filter the cards for their types columns to contain any of the given type
    names,
    e.g. get_sub_df_for_type("Attack") would return all cards with the attack
    type.
    """
    return df[listlike_contains_any(df["Types"], type_names)]


def get_sub_df_with_csos(df: pd.DataFrame, csos: list[str]) -> pd.DataFrame:
    """Acquire a subset of the DataFrame which only includes the given csos."""
    return df.loc[csos]


def get_string_of_combined_qualities(df: pd.DataFrame, qual_name: str) -> str:
    """Get a string to describe which csos contribute to the given
    quality, and how much they do that.

    Parameters
    ----------
    qual_name : str
        The name of the quality.

    Returns
    -------
    str
        The description containing the cards.
    """
    qual_name += "_quality"
    sub_df = df[df[qual_name] > 0].sort_values(qual_name)
    return ", ".join(
        [f"{card.Name} ({card[qual_name]})" for _, card in sub_df.iterrows()]
    )


def get_sub_df_of_categories(
    df: pd.DataFrame, colname: str, categories: list[str]
) -> pd.DataFrame:
    """Filters a dataframe for rows where the column is in the provided categories, e.g.
    for a column containing the expansions ["Base", "Base", "Intrigue"], you
    could filter with categories=["Intrigue", "Empires"].
    """
    return df[df[colname].isin(categories)]


def get_sub_df_listlike_contains(df: pd.DataFrame, colname: str, value) -> pd.DataFrame:
    """Filters the dataframe for all entries where the list entries in the
    given column contain the value

    Parameters
    ----------
    colname : str
        The name of the column
    value : Type of list entries
        The value to filter for

    Returns
    -------
    pd.DataFrame
        Filtered dataframe
    """
    return df[listlike_contains(df[colname], value)]


def get_sub_df_listlike_contains_any(
    df: pd.DataFrame, colname: str, value_list: Sequence
) -> pd.DataFrame:
    """Filters the dataframe for all entries where the list entries in the
    given column have overlap with the values

    Parameters
    ----------
    colname : str
        The name of the column
    value_list : Sequence
        The value to filter for

    Returns
    -------
    pd.DataFrame
        Filtered dataframe
    """
    return df[listlike_contains_any(df[colname], value_list)]


def get_sub_df_listlike_contains_any_or_is_empty(
    df: pd.DataFrame, colname: str, value_list: Sequence
) -> pd.DataFrame:
    """Filters the dataframe for all entries where the list entries in the
    given column have overlap with the values, or are empty lists.

    Parameters
    ----------
    colname : str
        The name of the column
    value_list : Sequence
        The value to filter for

    Returns
    -------
    pd.DataFrame
        Filtered dataframe
    """
    series = df[colname]
    contains_any_mask = listlike_contains_any(series, value_list)
    is_empty_mask = listlike_is_empty(series)
    return df[contains_any_mask | is_empty_mask]


def get_sub_df_for_landscape(df: pd.DataFrame, exclude_ways=False) -> pd.DataFrame:
    """Get a subset of the given pool containing only true landscapes (so no Allies)

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to filter
    exclude_ways : bool, optional
        Whether ways should also be excluded, by default False

    Returns
    -------
    pd.DataFrame
        The filtered dataframe
    """
    pool = df[df["IsLandscape"]]
    if exclude_ways:
        pool = pool[~pool["IsWay"]]
    return pool


def _get_sub_df_for_cost(pool: pd.DataFrame, cost_limits: list[str]) -> pd.DataFrame:
    return pool[pool.Cost.isin(cost_limits)]


def get_sub_df_for_card(df: pd.DataFrame, for_bane_or_mouse=False) -> pd.DataFrame:
    """Get a subset of the given DataFrame containing only cards that are part of the
    supply.
    Can be reduced to cards costing $2 and $3.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to filter
    for_bane_or_mouse : bool, optional
        Whether the cards should be filtered for ones that cost between $2 and $3,
            by default False

    Returns
    -------
    pd.DataFrame
        The filtered dataframe
    """
    pool = df[~df["IsLandscape"] & df["IsInSupply"]]
    if for_bane_or_mouse:
        pool = _get_sub_df_for_cost(pool, ["$2", "$3"])
    return pool


def sample_single_cso_from_df(df: pd.DataFrame) -> str:
    """Samples the next CSO from the given DataFrame while
    respecting the weight situation."""
    if len(df) == 0:
        return ""
    weights = df["CSOWeight"] if "CSOWeight" in df.columns else None
    return df.sample(1, weights=weights).iloc[0].Name


def _get_weight_for_cso(name: str, disliked: list[str], liked: list[str]) -> float:
    if name in disliked:
        return 0.5
    if name in liked:
        return 2
    return 1


def add_weight_column(
    df: pd.DataFrame, disliked: list[str], liked: list[str]
) -> pd.DataFrame:
    """Adds a weight column to the given DataFrame by taking the liked and
    disliked list into consideration.
    """
    df["CSOWeight"] = df["Name"].apply(
        lambda name: _get_weight_for_cso(name, disliked, liked)
    )
    return df
