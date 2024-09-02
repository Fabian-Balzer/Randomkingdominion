import json
from collections import defaultdict
from functools import reduce

import pandas as pd

from ...constants import PATH_CARD_INFO, QUALITIES_AVAILABLE
from ...utils.utils import ask_file_overwrite


def write_dict_to_json_nicely(
    new_dict: dict, filepath: str, always_overwrite=False, sort=True
):
    if always_overwrite or ask_file_overwrite(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(new_dict, f, sort_keys=sort, separators=(",\n", ": "))


def read_json_dict_from_file(fpath: str) -> dict:
    with open(fpath, "r", encoding="utf-8") as f:
        old_dict = json.load(f)
    return old_dict


def get_specific_info(
    cso: str, info_type: str, default_value: int | list
) -> int | list:
    """Retrieves the info of info_type stored in the specifics folder."""
    try:
        fpath = PATH_CARD_INFO.joinpath(f"specifics/{info_type}.json")
        with fpath.open("r", encoding="utf-8") as f:
            data = json.load(f)
            quality_dict = defaultdict(lambda: default_value, data)
    except FileNotFoundError:
        print(f"Couldn't find the {info_type} file, skipped adding that info.")
        return default_value
    return quality_dict[cso]


def add_quality_info(df: pd.DataFrame) -> pd.DataFrame:
    info_types = {f"{qual}_quality": 0 for qual in QUALITIES_AVAILABLE}
    info_types |= {
        f"{qual}_types": [] for qual in QUALITIES_AVAILABLE if qual != "interactivity"
    }
    for info_type, default_value in info_types.items():
        df[info_type] = df["Name"].apply(
            lambda name: get_specific_info(name, info_type, default_value)
        )
    return df
