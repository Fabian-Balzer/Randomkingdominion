"""The combos and interactions found per kingdom for the Oracle's kingdom lists."""

import pandas as pd
import pytest

import random_kingdominion as rk
from random_kingdominion.streamlit_util.combo_and_inter_setup.util import (
    add_combo_inter_info_for_kingdoms,
)
from random_kingdominion.streamlit_util.constants import (
    get_cached_combo_df,
    get_cached_inter_df,
)
from random_kingdominion.utils import filter_combo_or_inter_df_for_csos


def _expected(cards: list[str], landscapes: list[str]) -> tuple[list, list, list]:
    """What filtering both tables for the kingdom's CSOs returns."""
    csos = set(cards + landscapes)
    inters = filter_combo_or_inter_df_for_csos(get_cached_inter_df(), csos, True)
    combos = filter_combo_or_inter_df_for_csos(get_cached_combo_df(), csos, True)
    return inters.index.tolist(), combos.index.tolist(), combos["Type"].tolist()


def _first_dailies(num: int) -> list[tuple[list[str], list[str]]]:
    """As the Oracle sees them: the DataFrame fills in missing landscapes."""
    manager = rk.KingdomManager()
    manager.load_tgg_dailies()
    df = manager.dataframe_repr.head(num)
    return list(zip(df["cards"], df["landscapes"]))


@pytest.mark.parametrize(
    "cards, landscapes",
    [
        (["outpost", "village", "smithy"], []),  # outpost___outpost counts once
        (["elder", "amulet", "village"], []),  # Elder is looked up as Townsfolk
        (["outpost"], []),  # A single CSO takes the pairs with any of them
        ([], []),
    ],
    ids=["self_pair", "split_pile_member", "single_cso", "empty"],
)
def test_pairs_match_the_filter(cards: list[str], landscapes: list[str]):
    df = add_combo_inter_info_for_kingdoms(
        pd.DataFrame({"cards": [cards], "landscapes": [landscapes]})
    )
    row = df.iloc[0]
    assert (row["interactions"], row["combos"], row["combo_types"]) == _expected(
        cards, landscapes
    )


def test_pairs_of_stored_kingdoms_match_the_filter():
    """The per-CSO lookup replaced filtering both tables for every kingdom (M28)."""
    kingdoms = _first_dailies(100)
    df = add_combo_inter_info_for_kingdoms(
        pd.DataFrame(kingdoms, columns=["cards", "landscapes"])
    )
    found = list(zip(df["interactions"], df["combos"], df["combo_types"]))
    assert found == [_expected(cards, landscapes) for cards, landscapes in kingdoms]
    assert df["num_interactions"].sum() > 0 and df["num_combos"].sum() > 0
