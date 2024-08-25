"""Helper functions needed for kingdom creation and manipulation."""

from typing import Any

import numpy as np
import pandas as pd


def _calculate_total_quality(values: list[int]) -> int:
    """Calculate the total quality value of a list of integers.
    The total quality value is a number between 0 and 4 that represents the overall quality
    of a list of integers, which is at least the maximum of the values in the list.
    The total quality value is iteratively calculated as follows:
    - 0: If the list is empty, or if the maximum value is 0.
    - 1: If the maximum value is 1.
    - 2: If the maximum value is 2, or if there are at least four 1s.
    - 3: If the maximum value is 3, or if there are at least three 2s (also, four 1s count as a 2).
    - 4: If the maximum value is 4, or if there are at least two 3s (also, three 2s count as a 3).

    Parameters
    ----------
    values : list[int]
        A list of integers to be evaluated.

    Returns
    -------
        int
        The total quality value of the list.

    Examples
    --------
    >>> _calculate_total_quality([1, 2, 3, 4, 4])
    4
    >>> _calculate_total_quality([1, 1, 1, 1, 2])
    3
    >>> _calculate_total_quality([1, 1, 1, 1, 1])
    2
    >>> _calculate_total_quality([3, 1, 1, 1, 1, 1])
    3
    """
    # Remove all zeros from the list
    values = [val for val in values if val != 0]

    # Initialize array with zeros representing 0, 1, 2, 3, 4
    counts = np.zeros(5)

    # If there are 5-i values of the same thing, increment the value count of the next one
    # e.g. a list of [1, 1, 1, 1, 2] should be counted as two 2s. because there are four
    # ones, three 2s will be counted as a single 3, and two 3s will yield a 4.
    for i in range(4):
        counts[i] += values.count(i)
        if i == 0:
            continue
        counts[i + 1] += counts[i] // (5 - i)

    # Look where the first nonzero value sits.
    return np.nonzero(counts)[0][-1] if np.any(counts) else 0


def _get_total_quality(qual_name: str, kingdom_df: pd.DataFrame) -> int:
    value_list = kingdom_df[qual_name + "_quality"].to_list()
    return _calculate_total_quality(value_list)


def sort_kingdom(df: pd.DataFrame) -> pd.DataFrame:
    """Sort the kingdom such that the supply cards come first, then the landscapes,
    then it is sorted by cost, then by name.
    """
    # To ensure Potion and Debt Cost will be ranked first:
    df["CostSort"] = df["Cost"].str.replace("$", "Z")
    df["NameSort"] = df["Name"]
    df = df.sort_values(
        by=[
            "IsInSupply",
            "IsLandscape",
            "IsExtendedLandscape",
            "IsOtherThing",
            "CostSort",
            "NameSort",
        ],
        ascending=[False, False, False, False, True, True],
    )
    return df.drop(["NameSort", "CostSort"], axis=1)


def _is_value_not_empty_or_true(val: Any) -> bool:
    """Check whether the given value is not empty, or true if it's a boolean."""
    if isinstance(val, bool):
        return val  # If it's false, we want
    if val is None:
        return False
    if isinstance(val, (str, list)):
        return len(val) != 0
    return True


def _dict_factory_func(attrs: list[tuple[str, str]], ignore_keys: set) -> dict:
    """Custom dictionary factory function to make sure no unnecessary empty
    values are saved.
    This includes all booleans since they are false by default.
    """
    return {
        k: v
        for (k, v) in attrs
        if _is_value_not_empty_or_true(v) and k not in ignore_keys
    }


def sanitize_cso_name(name: str) -> str:
    """Return a sanitized version of the name of the cso."""
    if isinstance(name, float):
        return ""
    name = (
        name.lower()
        .strip()
        .replace(" / ", "/")
        .replace(" ", "_")
        .replace("'", "")
        .replace("’", "")
    )
    if name == "harem" or name == "farm":
        return "harem_farm"
    return name


def sanitize_cso_list(cso_list: list[str], sort=True) -> list[str]:
    """Sanitize each cso in a list of csos."""
    if isinstance(cso_list, float):
        return []
    san_list = [sanitize_cso_name(cso) for cso in cso_list]
    if sort:
        return sorted(san_list)
    return san_list
