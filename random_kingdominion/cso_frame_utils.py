"""A module with a bunch of handy static methods to manipulate Dataframes"""

from functools import reduce
from typing import Literal, Sequence

import numpy as np
import pandas as pd

from .cso_series_utils import (
    listlike_contains,
    listlike_contains_any,
    listlike_is_empty,
)


def add_column(
    df: pd.DataFrame, column_name: str, values: pd.Series | Sequence
) -> pd.DataFrame:
    """Adds a column to the dataframe (to be used with the pipe functionality).
    Example usage:
        >>> new_df = df.pipe(add_column, 'C', [7, 8, 9])
    """
    new_df = df.copy()  # Create a copy of the original DataFrame
    new_df[column_name] = values  # Add the new column
    return new_df


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


def get_sub_df_for_true_landscape(df: pd.DataFrame, exclude_ways=False) -> pd.DataFrame:
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


def get_sub_df_for_special_card(
    df: pd.DataFrame,
    special_card_to_pick_for: (
        Literal[
            "ferryman",
            "way_of_the_mouse",
            "young_witch",
            "riverboat",
            "approaching_army",
        ]
        | None
    ) = None,
) -> pd.DataFrame:
    """Get a subset of the given DataFrame containing only cards that are part of the
    supply.
    Can be reduced to cards costing $2 and $3.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to filter
    special_card_to_pick_for : Literal["ferryman", "way_of_the_mouse", "young_witch", "riverboat"], optional
        Whether the cards should be filtered to be eligible for the given special pick,
            by default None

    Returns
    -------
    pd.DataFrame
        The filtered dataframe
    """
    pool = df[df["IsInSupply"]]
    if special_card_to_pick_for == "young_witch":
        pool = _get_sub_df_for_cost(pool, ["$2", "$3", "$2+", "$3+"])
        return pool
    elif special_card_to_pick_for == "ferryman":
        banned_for_ferryman = ["Young Witch", "Riverboat"]
        pool = _get_sub_df_for_cost(pool, ["$3", "$4", "$3+", "$4+"])
        pool = pool[~np.in1d(pool["Name"], banned_for_ferryman)]
        return pool
    elif special_card_to_pick_for == "approaching_army":
        banned_for_army = [
            "Young Witch"
        ]  # Don't want to deal with the annoyances of that stuff xD
        pool = pool[listlike_contains(pool["Types"], "Attack")]
        pool = pool[~np.in1d(pool["Name"], banned_for_army)]
        return pool
    # In the case of mouse or riverboat, we are picking single cards rather
    # than piles, such that single Knights etc. can also be part.
    pool = df[
        df["IsRealSupplyCard"]
    ]  # TODO: Filter stuff where the parent is already in the pool
    if special_card_to_pick_for == "way_of_the_mouse":
        # Ban useless cards, and also cards that just have effects that mirror other ways as you might as well play with these.
        banned_for_mouse = [
            "Tent",  # Sheep
            "Battle Plan",  # might be Pig without attacks
            "Sheepdog",  # Otter
            "Farmer's Market",  # No place to gather tokens, only + Buy
            "Aristocrat",  # Does nothing
            "Riverboat",  # Too annoying to consider
            "Ratcatcher",  # Pig
            "Guide",  # Pig
            "Watchtower",  # Owl
            "Page",  # Pig
            "Peasant",  # Monkey
            "Faithful Hound",  # Otter
            "Pixie",  # Pig
            "Lackeys",  # Otter
            "Snake Witch",  # Pig (?)
            "Fishmonger",  # Monkey
            "Embargo",  # Sheep
            "Moat",  # Otter
            "Black Cat",  # Otter
        ]
        pool = _get_sub_df_for_cost(pool, ["$2", "$3", "$2+", "$3+"])
        pool = pool[listlike_contains(pool["Types"], "Action")]
        pool = pool[~np.in1d(pool["Name"], banned_for_mouse)]
    elif special_card_to_pick_for == "riverboat":
        banned_for_riverboat = ["Royal Carriage", "Ferryman", "Distant Lands"]
        pool = _get_sub_df_for_cost(pool, ["$5", "$5*"])
        pool = pool[listlike_contains(pool["Types"], "Action")]
        pool = pool[~listlike_contains(pool["Types"], "Duration")]
        pool = pool[~np.in1d(pool["Name"], banned_for_riverboat)]
    return pool


def sample_single_cso_from_df(df: pd.DataFrame) -> str:
    """Samples the next CSO from the given DataFrame while
    respecting the weight situation."""
    if len(df) == 0:
        return ""
    weights = df["CSOWeight"] if "CSOWeight" in df.columns else None
    return df.sample(1, weights=weights).index[0]


def _get_weight_for_cso(
    name: str,
    disliked: list[str],
    liked: list[str],
    dislike_weight=0.5,
    like_weight=2.0,
) -> float:
    if name in disliked:
        return dislike_weight
    if name in liked:
        return like_weight
    return 1


def add_weight_column(
    df: pd.DataFrame,
    disliked: list[str],
    liked: list[str],
    dislike_weight=0.5,
    like_weight=2.0,
) -> pd.DataFrame:
    """Adds a weight column to the given DataFrame by taking the liked and
    disliked list into consideration.
    """
    df["CSOWeight"] = df.index.map(
        lambda name: _get_weight_for_cso(
            name, disliked, liked, dislike_weight, like_weight
        )
    )
    # Give single knights lower chances to appear. This should only be relevant for Riverboat for now.
    df["CSOWeight"] = df.apply(
        lambda row: (
            row["CSOWeight"] if "Knight" not in row["Types"] else row["CSOWeight"] / 9
        ),
        axis=1,
    )
    return df
