import pandas as pd

from ...constants import ALL_CSOS, PATH_CARD_INFO
from ...cso_frame_utils import listlike_contains
from ...logger import LOGGER
from .. import get_cso_name, sanitize_cso_name
from .constants import ALL_LOOT_GIVERS


def _set_up_replacements_for_combos(
    df: pd.DataFrame, replacement_str: str, replacements: list, verbose: bool = False
) -> pd.DataFrame:
    """For combos involving a replacement_str (like 'Loot', 'Shadow', or 'Horse'), create new entries for each possible replacement."""
    new_rows = []
    for _, row in df.iterrows():
        if replacement_str not in row["CSO1/CSO2"].split("/"):
            continue
        for replacement in replacements:
            other = [
                cso
                for cso in (row["CSO1"], row["CSO2"])
                if cso.lower() != replacement_str.lower()
            ][0]
            new_csos = sorted([replacement, other])
            repl_name = get_cso_name(replacement)
            updated_desc = row["Description"].replace(
                f"{{{replacement_str}}}", repl_name
            )
            new_rows.append(
                {
                    "CSO1/CSO2": "/".join(new_csos),
                    "CSO1": new_csos[0],
                    "CSO2": new_csos[1],
                    "Type": row["Type"],
                    "Description": updated_desc,
                    "temp_ident": "/".join(new_csos),
                }
            )
    df = df[~df["CSO1/CSO2"].apply(lambda x: replacement_str in x.split("/"))]
    if verbose:
        msg = f"Expanded {len(new_rows)} combo entries by replacing '{replacement_str}' with actual CSOs.\n"
        msg += "\n".join(
            [row["temp_ident"] + "\n\t" + row["Description"][:100] for row in new_rows]
        )
        LOGGER.info(msg)
    extra_df = pd.DataFrame(new_rows)
    df = pd.concat([df, extra_df], ignore_index=True)
    # Merge duplicates
    dup_mask = df.duplicated(subset=["temp_ident"], keep=False)
    if dup_mask.any():
        dup_rows = df[dup_mask]
        msg = f"Found {len(dup_rows)} duplicate combo entries when expanding {replacement_str} givers:\n"
        for _, row in dup_rows.iterrows():
            msg += f"{row['temp_ident']}\n\t{row['Description'][:100]}\n"
        LOGGER.info(msg)
    # df = df[~dups]
    # Merge descriptions for duplicates
    merged_rows = []
    dups = df[dup_mask]
    for _, group in dups.groupby("temp_ident"):
        merged_desc = " ".join(group["Description"].tolist()).strip()
        merged_rows.append(
            {
                "CSO1/CSO2": group.iloc[0]["CSO1/CSO2"],
                "CSO1": group.iloc[0]["CSO1"],
                "CSO2": group.iloc[0]["CSO2"],
                "Type": group.iloc[0]["Type"],
                "Description": merged_desc,
                "temp_ident": group.iloc[0]["temp_ident"],
                "YTLink": group.iloc[0].get("YTLink", ""),
                "YTComment": group.iloc[0].get("YTComment", ""),
            }
        )
    merged_df = pd.DataFrame(merged_rows)
    df = pd.concat([df[~dup_mask], merged_df], ignore_index=True)
    return df


def set_up_all_replacements(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    df = _set_up_replacements_for_combos(df, "Loot", ALL_LOOT_GIVERS, verbose)
    shadows = ALL_CSOS[listlike_contains(ALL_CSOS["Types"], "Shadow")].index.tolist()
    df = _set_up_replacements_for_combos(df, "Shadow", shadows, verbose)
    horse_gainers = ALL_CSOS[
        listlike_contains(ALL_CSOS["gain_types"], "Horses")
    ].index.tolist()
    df = _set_up_replacements_for_combos(df, "Horse", horse_gainers, verbose)
    return df


def get_combo_df(verbose: bool = False) -> pd.DataFrame:
    """Load the combo dataframe from file."""
    fpath = PATH_CARD_INFO.joinpath("raw_combo_data.csv")
    df = pd.read_csv(fpath, sep=";")
    # Write sorted version for consistency
    df.sort_values(by=["CSO1/CSO2"]).to_csv(fpath, sep=";", index=False)
    df["CSO1"] = df["CSO1/CSO2"].apply(
        lambda x: sanitize_cso_name(sorted(x.split("/"))[0])
    )
    df["CSO2"] = df["CSO1/CSO2"].apply(
        lambda x: sanitize_cso_name(sorted(x.split("/"))[1])
    )
    df["temp_ident"] = df["CSO1"] + "/" + df["CSO2"]
    df = set_up_all_replacements(df, verbose)
    df = df.drop(columns=["CSO1/CSO2", "temp_ident"]).sort_values(by=["CSO1", "CSO2"])
    # Clean up YT links for now until I implement a system to handle multiple links
    df["YTLink"] = df["YTLink"].str.split(" & ").str[0].fillna("")
    df["YTComment"] = df["YTComment"].str.split(" & ").str[0].fillna("")
    return df[sorted(df.columns)]
