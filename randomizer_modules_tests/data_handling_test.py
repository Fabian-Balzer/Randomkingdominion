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
        assert set(np.unique(df[quality + "_quality"])).issubset([0, 0.5, 1, 2, 3])


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


# Stamps whose images haven't been added to static/card_pictures yet; remove an entry
# once its image is there (the second test below fails until then)
_STAMP_IMAGES_TO_ADD = {
    f"CampaignEffects/stamps/{name}.png"
    for name in ["also_gold", "also_silver", "bonus_money", "coin_way", "cost_2d_less"]
}


def _card_picture_paths() -> set[str]:
    """All files below static/card_pictures, with their exact spelling."""
    return {
        path.relative_to(rk.PATH_CARD_PICS).as_posix()
        for path in rk.PATH_CARD_PICS.rglob("*")
        if path.is_file()
    }


def test_every_cso_has_an_image_with_exactly_this_path(df: pd.DataFrame):
    """Compared case-sensitively: Windows doesn't care, but Streamlit Cloud (Linux)
    can't find e.g. "Offers_Insight.png" if the file is "offers_insight.png"."""
    existing = _card_picture_paths()
    missing = sorted(set(df["ImagePath"]) - existing - _STAMP_IMAGES_TO_ADD)
    assert missing == [], f"{len(missing)} CSO images missing: {missing}"


def test_images_listed_as_to_be_added_are_still_missing():
    added = sorted(_STAMP_IMAGES_TO_ADD & _card_picture_paths())
    assert added == [], f"Remove these from _STAMP_IMAGES_TO_ADD: {added}"
