import json

import pandas as pd

from ...constants import PATH_CARD_INFO, QUALITIES_AVAILABLE
from ...kingdom import sanitize_cso_name
from ...logger import LOGGER
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
            quality_dict = {sanitize_cso_name(k): v for k, v in data.items()}
    except FileNotFoundError:
        LOGGER.info(f"Couldn't find the {info_type} file, skipped adding that info.")
        return default_value
    return quality_dict.get(sanitize_cso_name(cso), default_value)


def check_usage_of_qualities(names: pd.Series, info_type: str):
    """Check if all entries in the names series have a quality info."""
    fpath = PATH_CARD_INFO.joinpath(f"specifics/{info_type}.json")
    with fpath.open("r", encoding="utf-8") as f:
        quality_dict = json.load(f)
    diff = set([sanitize_cso_name(k) for k in quality_dict.keys()]).difference(
        set(names.apply(sanitize_cso_name))
    )
    if diff:
        LOGGER.warning(
            f"The following entries in the {info_type} file are not used: {diff}"
        )


def add_quality_info(df: pd.DataFrame) -> pd.DataFrame:
    info_types = {f"{qual}_quality": 0 for qual in QUALITIES_AVAILABLE}
    info_types |= {
        f"{qual}_types": [] for qual in QUALITIES_AVAILABLE if qual != "interactivity"
    }
    for info_type, default_value in info_types.items():
        df[info_type] = df["Name"].apply(
            lambda name: get_specific_info(name, info_type, default_value)
        )
        check_usage_of_qualities(df["Name"], info_type)
    return df
