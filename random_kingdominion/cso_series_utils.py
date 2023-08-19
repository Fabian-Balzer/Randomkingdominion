"""Module to help with utilities for Series objects"""
from typing import Sequence

import numpy as np
import pandas as pd


def listlike_contains(series: pd.Series, value) -> pd.Series:
    """Check whether the list values of the column contain the given value.

    Parameters
    ----------
    value : Same type as the entries of the list
        The value to search for

    Returns
    -------
    pd.Series
        A boolean Series

    Examples
    --------
        >>> series = pd.Series([["Butter", "Bread"], ["Butter", "Nothing"]])
        >>> series.list.contains("Bread")
    This would return pd.Series([True, False]).
    """
    return series.apply(lambda entries: value in entries)


def listlike_contains_any(series: pd.Series, value_list: Sequence) -> pd.Series:
    """Check whether the list values of the column have overlap with the value_list.

    Parameters
    ----------
    value_list : Same type as the entries of the list
        The values to check for

    Returns
    -------
    pd.Series
        A boolean Series

    Examples
    --------
        >>> series = pd.Series([["Butter", "Bread"], ["Butter", "Nothing"]])
        >>> series.list.contains_any(["Bread", "Nothing"])
    This would return pd.Series([True, True]).
    """
    return series.apply(lambda entries: np.intersect1d(entries, value_list).size > 0)


def listlike_is_empty(series: pd.Series) -> pd.Series:
    """Return a mask with boolean entries that indicate
    whether the entries of the listlike column are empty lists
    """
    return series.apply(lambda entries: len(entries) == 0)
