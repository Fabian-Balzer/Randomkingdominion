"""Tests for the constants.py file."""

import pandas as pd

import random_kingdominion as rk


def test_filenames():
    for fname in [rk.FPATH_CARD_DATA, rk.FPATH_RAW_DATA]:
        assert fname.is_file()


def test_filepaths():
    for fpath in [
        rk.PATH_ASSETS,
        rk.PATH_CARD_INFO,
        rk.PATH_CARD_PICS,
        rk.PATH_MAIN,
        rk.PATH_MODULE,
    ]:
        assert fpath.is_dir()


def test_list_columns_are_parsed_as_lists():
    # read_dataframe_from_file parses them with ast.literal_eval (M16)
    for colname in ["Types", "Extra Components", "draw_types"]:
        assert rk.ALL_CSOS[colname].apply(lambda x: isinstance(x, list)).all(), colname


def test_cso_occurrences_are_counted_once_per_pair():
    pairs = pd.Index(["moat___village", "outpost___outpost", "moat___outpost"])
    counts = rk.count_cso_occurrences(pairs, pd.Index(["moat", "outpost", "smithy"]))
    assert counts.tolist() == [2, 2, 0]


def test_cso_occurrence_counts_match_the_pairs():
    """The vectorised count (M14) agrees with checking every pair for every CSO."""
    pairs = rk.ALL_INTERACTIONS.index.to_series().str.split("___")
    counts = rk.count_cso_occurrences(rk.ALL_INTERACTIONS.index, rk.ALL_CSOS.index)
    for cso in ["moat", "outpost", "black_market", "village"]:
        assert counts[cso] == pairs.apply(lambda pair: cso in pair).sum(), cso
