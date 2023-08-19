from typing import Sequence

import numpy as np
import pandas as pd


@pd.api.extensions.register_series_accessor("list")
class ListAccessorSeries:
    """Accessor for listlike columns in Series."""

    def __init__(self, pandas_obj: pd.Series):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        if len(obj) > 0:
            assert isinstance(obj.iloc[0], Sequence)

    def contains(self, value) -> pd.Series:
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
        return self._obj.apply(lambda entries: value in entries)

    def contains_any(self, value_list: Sequence) -> pd.Series:
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
        return self._obj.apply(
            lambda entries: np.intersect1d(entries, value_list).size > 0
        )


@pd.api.extensions.register_dataframe_accessor("list_filter")
class ListFilterAccessorDataFrame:
    """Adds filtering capabilities for listlike columns of the dataframe."""

    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj

    def contains(self, colname: str, value) -> pd.DataFrame:
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
        df = self._obj
        return df[df[colname].list.contains(value)]

    def contains_any(self, colname: str, value_list: Sequence) -> pd.DataFrame:
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
        df = self._obj
        return df[df[colname].list.contains_any(value_list)]
