import json

import pandas as pd

from ...constants import PATH_CARD_INFO, QUALITIES_AVAILABLE
from ...logger import LOGGER
from ...utils import ask_file_overwrite, sanitize_cso_name


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


def get_types_information(
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


def modify_extra_info(row: pd.Series) -> pd.Series:
    """Modify qualities to include luck- or limit-based parameters such as DrawQuality for Loot or Boon stuff,"""
    relevant_qualities = [q for q in QUALITIES_AVAILABLE if q != "interactivity"]
    extra_info = row.get("gain_types", [])
    if "Loot" in extra_info or "Boons" in extra_info:
        for qual in relevant_qualities:
            if qual == "altvp":
                continue
            if row[qual + "_quality"] == 0:
                if "Boons" in extra_info:
                    if qual == "attack":
                        continue
                    if qual == "village" and row["Name"] != "Pixie":
                        continue
                row[qual + "_quality"] = 0.5
                row[qual + "_types"].append("Luck-based")
            if (
                qual == "gain"
                and "Buys" not in row["gain_types"]
                and "Buys*" not in row["gain_types"]
            ):
                row[qual + "_types"].append("Buys*")
    if "Looter" in row["Types"]:
        # Ruins may provide +Buy
        if row["gain_quality"] == 0:
            row["gain_quality"] = 0.5
            row["gain_types"].extend(["Luck-based", "Buys*"])
    if row["Name"] == "Knights":
        for qual in relevant_qualities:
            if row[qual + "_quality"] == 0:
                row[qual + "_quality"] = 0.5
                row[qual + "_types"].append("Limited")
            if qual == "gain":
                row[qual + "_types"].append("Buys*")
    if row["Name"] in ["Tournament", "Joust"]:
        for qual in relevant_qualities:
            if qual == "thinning":
                continue
            if row[qual + "_quality"] == 0:
                row[qual + "_quality"] = 0.5
                row[qual + "_types"].append("Limited")
    return row


def add_quality_info(df: pd.DataFrame) -> pd.DataFrame:
    info_types = {f"{qual}_quality": lambda: 0 for qual in QUALITIES_AVAILABLE}
    info_types |= {
        f"{qual}_types": lambda: list()
        for qual in QUALITIES_AVAILABLE
        if qual != "interactivity"
    }
    for info_type, default_func in info_types.items():
        df[info_type] = df["Name"].apply(
            lambda name: get_types_information(name, info_type, default_func())
        )
        check_usage_of_qualities(df["Name"], info_type)
    df = df.apply(modify_extra_info, axis=1)
    return df
