import os
from math import ceil, floor
from typing import Optional

import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .constants import PATH_ASSETS, RENEWED_EXPANSIONS


def ask_file_overwrite(fpath: str) -> bool:
    """Prompts the user if there already exists a file at the given fpath

    Parameters
    ----------
    fpath : FullFilePath
        filename and path of the file that is supposed to be written

    Returns
    -------
    bool
        True if the file should be replaced, otherwise False
    """
    path, fname = os.path.split(fpath)
    if not os.path.exists(fpath):
        print(f"Writing the file '{fpath}'")
        return True
    answer = input(
        f"The file '{fname}' already exists at {path}. Continue and replace it (y/n)?\n>>> "
    )

    for _ in range(5):
        if not answer:
            raise RuntimeError("Stopped execution.")
        if answer.lower() in ["y", "yes"]:
            print(f"Overwriting '{fpath}'")
            return True
        if answer.lower() in ["n", "no"]:
            print(f"Skipped writing '{fpath}' as it already existed.")
            return False
        answer = input(
            "Please answer with 'y' (overwrite) or 'n' (skip overwrite)?\n>>> "
        )


def read_dataframe_from_file(fpath: str, eval_lists=False):
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath, sep=";", header=0)
        if eval_lists:
            for colname in df.columns:
                if "type" in colname:
                    # Make sure we properly handle lists
                    df[colname] = df[colname].apply(eval)
    else:
        raise FileNotFoundError(
            2, "Couldn't find the raw card data file, please download it first."
        )
    return df


def write_dataframe_to_file(df: pd.DataFrame, fpath: str):
    """Writes the given dataframe to a file"""
    if not ask_file_overwrite(fpath):
        return
    df.to_csv(fpath, sep=";", index=False)
    print(
        f"Successfully wrote the dominion cards to the file '{fpath}' in the current path."
    )


def filter_column(df: pd.DataFrame, colname: str, entries: list[str]) -> pd.DataFrame:
    """Filters a dataframe for rows where the column is in the provided entries, e.g.
    for a column containing the expansions ["Base", "Base", "Intrigue"], you
    could filter with entries=["Intrigue", "Empires"]
    """
    df = df.loc[df[colname].apply(lambda x: x in entries)]
    return df


def is_in_requested_types(given_types: list[str], types_to_check: list[str]):
    """Check if all of the given_types are in the types_to_check.
    An empty string is always considered to be in the 'types_to_check'"""
    if "" in given_types:
        return True
    for type in given_types:
        if not type in types_to_check:
            return False
    return True


def display_cards(label_dict, layout_dict, name, num_rows=2, size=(150, 320)):
    # Delete the old display
    for i in reversed(range(layout_dict[f"{name}display"].count())):
        layout_dict[f"{name}display"].itemAt(i).widget().setParent(None)
    num_items = len(label_dict[f"{name}List"])
    num_cols = ceil(num_items / num_rows)
    for i, widget in enumerate(label_dict[f"{name}List"]):
        row = floor(i / num_cols)
        col = i - row * num_cols
        wid = QWidget()
        wid.setFixedSize(*size)
        lay = QVBoxLayout(wid)
        lay.setContentsMargins(1, 1, 1, 1)
        entry = label_dict[f"{name}List"][i]
        if isinstance(entry, dict):
            lay.addWidget(entry["Button"])
            lay.addWidget(entry["Pic"])
            lay.addWidget(entry["Label"])
        else:
            lay.addWidget(entry)
        layout_dict[f"{name}display"].addWidget(wid, row, col)


def get_expansion_icon(exp: str) -> str:
    """Returns the image path for the given expansion icon."""
    base = PATH_ASSETS.joinpath("icons/expansions/")
    conversion_dict = {}
    for outdated_exp in RENEWED_EXPANSIONS:
        conversion_dict[outdated_exp + ", 1E"] = outdated_exp + "_old"
        conversion_dict[outdated_exp + ", 2E"] = outdated_exp
    if exp in conversion_dict:
        exp = conversion_dict[exp]
    return str(base.joinpath(exp.replace(" ", "_") + ".png"))


def get_attack_icon(at: str) -> str:
    """Returns the image path for the given attack icon."""
    fpath = PATH_ASSETS.joinpath(f"icons/attack_types/{at}.png")
    return str(fpath)
