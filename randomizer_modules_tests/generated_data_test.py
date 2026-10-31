"""The generated card data in card_info/ must match its sources (M12).

`scripts/set_up_database.py` builds the `good_*.csv` files, and the app only reads
those. These tests rebuild them in memory and fail if a committed file is out of
date, e.g. after editing a specifics file without rerunning the script.
"""

import difflib

import pandas as pd
import pytest

import random_kingdominion as rk
from random_kingdominion.utils.data_setup import build_card_df
from random_kingdominion.utils.interaction_setup import (
    build_interaction_df,
    find_combo_data_errors,
    get_combo_df,
)


def _csv_lines(text: str) -> list[str]:
    # git may check the files out with CRLF line endings
    return text.replace("\r\n", "\n").splitlines()


def _assert_matches_committed_file(df: pd.DataFrame, fname: str, flag: str):
    rebuilt = _csv_lines(df.to_csv(sep=";", index=False))
    committed = _csv_lines(
        rk.PATH_CARD_INFO.joinpath(fname).read_text(encoding="utf-8")
    )
    if rebuilt == committed:
        return
    diff = list(
        difflib.unified_diff(
            committed, rebuilt, "committed", "rebuilt", lineterm="", n=0
        )
    )
    pytest.fail(
        f"card_info/{fname} is out of date, run "
        f"`python scripts/set_up_database.py {flag} -o`. First differences:\n"
        + "\n".join(diff[:20])
    )


def test_card_data_matches_raw_data_and_specifics():
    _assert_matches_committed_file(build_card_df(), "good_card_data.csv", "-m")


def test_interaction_data_matches_specifics():
    _assert_matches_committed_file(
        build_interaction_df(), "good_interaction_data.csv", "-i"
    )


def test_combo_data_matches_raw_combo_data():
    df = get_combo_df(verbose=False)
    assert find_combo_data_errors(df) == []
    _assert_matches_committed_file(df, "good_combo_data.csv", "-c")
