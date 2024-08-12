import numpy as np
import pandas as pd
import pytest

import random_kingdominion as rk


@pytest.fixture
def df() -> pd.DataFrame:
    # The main card-holding-dataframe to test
    return rk.ALL_CSOS


def test_quality_availability(df: pd.DataFrame):
    for quality in rk.QUALITIES_AVAILABLE:
        assert quality + "_quality" in df.columns


def test_quality_reasonability(df: pd.DataFrame):
    for quality in rk.QUALITIES_AVAILABLE:
        assert set(np.unique(df[quality + "_quality"])).issubset([0, 1, 2, 3])


def _test_type_availability(df: pd.DataFrame, qual_name: str):
    """Back and forth test that everything labelled as having the given quality has
    an qual type and vice versa"""
    subset = df[df[f"{qual_name}_quality"] > 0]
    for _, row in subset.iterrows():
        assert (
            len(row[f"{qual_name}_types"]) > 0
        ), f"No {qual_name} types specified for {row['Name']} with {row[f'{qual_name}_quality']}"

    subset2 = df[df[f"{qual_name}_types"].apply(lambda x: len(x) > 0)]
    for _, row in subset2.iterrows():
        assert (
            row[f"{qual_name}_quality"] > 0
        ), f"No {qual_name} quality specified for {row['Name']} with {row[f'{qual_name}_types']}"


def test_thinning_type_availability(df: pd.DataFrame):
    _test_type_availability(df, "thinning")


def test_attack_type_availability(df: pd.DataFrame):
    _test_type_availability(df, "attack")


def test_gain_type_availability(df: pd.DataFrame):
    _test_type_availability(df, "gain")


def test_village_type_availability(df: pd.DataFrame):
    _test_type_availability(df, "village")


def test_draw_type_availability(df: pd.DataFrame):
    _test_type_availability(df, "draw")


def test_expansion_availability(df: pd.DataFrame):
    expansions = np.unique(df["Expansion"])
    for exp in rk.RENEWED_EXPANSIONS:
        if exp not in ["Cornucopia", "Guilds"]:
            assert exp + ", 2E" in expansions
