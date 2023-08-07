import numpy as np
import pandas as pd
import pytest
import randomizer_modules as rm


@pytest.fixture
def df() -> pd.DataFrame:
    # The main card-holding-dataframe to test
    return rm.read_dataframe_from_file(rm.FPATH_CARD_DATA, True)


def test_quality_availability(df: pd.DataFrame):
    for quality in rm.QUALITIES_AVAILABLE:
        assert quality + "Quality" in df.columns


def test_quality_reasonability(df: pd.DataFrame):
    for quality in rm.QUALITIES_AVAILABLE:
        assert set(np.unique(df[quality + "Quality"])).issubset([0, 1, 2, 3])


def test_attack_type_availability(df: pd.DataFrame):
    """Back and forth test that everything labelled as attack has
    an attack type and vice versa"""
    subset = df[df["AttackQuality"] > 0]
    for _, row in subset.iterrows():
        assert len(row["AttackType"]) > 0

    subset2 = df[df["AttackType"].apply(lambda x: len(x) > 0)]
    for _, row in subset2.iterrows():
        assert row["AttackQuality"] > 0


def test_thinning_type_availability(df: pd.DataFrame):
    """Back and forth test that everything labelled as attack has
    an attack type and vice versa"""
    subset = df[df["ThinningQuality"] > 0]
    for _, row in subset.iterrows():
        assert len(row["ThinningType"]) > 0

    subset2 = df[df["ThinningType"].apply(lambda x: len(x) > 0)]
    for _, row in subset2.iterrows():
        assert row["ThinningQuality"] > 0


def test_expansion_availability(df: pd.DataFrame):
    expansions = np.unique(df["Expansion"])
    for exp in rm.RENEWED_EXPANSIONS:
        assert exp + ", 2E" in expansions
