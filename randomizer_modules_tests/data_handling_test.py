import numpy as np
import pandas as pd
import pytest
import random_kingdominion as rm


@pytest.fixture
def df() -> pd.DataFrame:
    # The main card-holding-dataframe to test
    return rm.read_dataframe_from_file(rm.FPATH_CARD_DATA, True)


def test_quality_availability(df: pd.DataFrame):
    for quality in rm.QUALITIES_AVAILABLE:
        assert quality + "_quality" in df.columns


def test_quality_reasonability(df: pd.DataFrame):
    for quality in rm.QUALITIES_AVAILABLE:
        assert set(np.unique(df[quality + "_quality"])).issubset([0, 1, 2, 3])


def test_attack_type_availability(df: pd.DataFrame):
    """Back and forth test that everything labelled as attack has
    an attack type and vice versa"""
    subset = df[df["attack_quality"] > 0]
    for _, row in subset.iterrows():
        assert len(row["attack_types"]) > 0

    subset2 = df[df["attack_types"].apply(lambda x: len(x) > 0)]
    for _, row in subset2.iterrows():
        assert row["attack_quality"] > 0


def test_thinning_type_availability(df: pd.DataFrame):
    """Back and forth test that everything labelled as attack has
    an attack type and vice versa"""
    subset = df[df["thinning_quality"] > 0]
    for _, row in subset.iterrows():
        assert len(row["thinning_types"]) > 0

    subset2 = df[df["thinning_types"].apply(lambda x: len(x) > 0)]
    for _, row in subset2.iterrows():
        assert row["thinning_quality"] > 0


def test_expansion_availability(df: pd.DataFrame):
    expansions = np.unique(df["Expansion"])
    for exp in rm.RENEWED_EXPANSIONS:
        assert exp + ", 2E" in expansions
