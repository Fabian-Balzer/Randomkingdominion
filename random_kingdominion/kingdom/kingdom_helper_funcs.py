"""Helper functions needed for kingdom creation and manipulation."""
import numpy as np
import pandas as pd


def _calculate_total_quality(values: list[int]) -> int:
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
    total_quality_value = np.nonzero(counts)[0][-1]

    return total_quality_value


def _get_total_quality(qual_name: str, kingdom_df: pd.DataFrame) -> int:
    value_list = kingdom_df[qual_name + "_quality"].to_list()
    return _calculate_total_quality(value_list)


def _sort_kingdom(df: pd.DataFrame) -> pd.DataFrame:
    """Sort the kingdom such that the supply cards come first, then the landscapes,
    then it is sorted by cost, then by name.
    """
    # To ensure Potion and Debt Cost will be ranked first:
    df["CostSort"] = df["Cost"].str.replace("$", "Z")
    df["NameSort"] = df["Name"]
    df = df.sort_values(
        by=["IsInSupply", "IsLandscape", "IsOtherThing", "CostSort", "NameSort"],
        ascending=[False, False, False, True, True],
    )
    return df.drop(["NameSort", "CostSort"], axis=1)


def _is_value_not_empty_or_true(val: any) -> bool:
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
