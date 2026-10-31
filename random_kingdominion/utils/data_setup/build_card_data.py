"""Build the main card table from the raw wiki data and the specifics files."""

import pandas as pd

from ...constants import FPATH_RAW_DATA, read_dataframe_from_file
from .add_additional_entries import add_additional_entries
from .add_additional_info_columns import add_additional_info_columns


def build_card_df() -> pd.DataFrame:
    """Build the card table from ``raw_card_data.csv`` and the quality and type files
    in ``card_info/specifics/``, i.e. what ``set_up_database.py -m`` writes to
    ``good_card_data.csv``."""
    df = read_dataframe_from_file(FPATH_RAW_DATA)
    df = add_additional_entries(df)
    return add_additional_info_columns(df)
