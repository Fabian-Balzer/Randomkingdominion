import os

import pandas as pd
import PyQt5.QtWidgets as QW

from ..constants import PATH_ASSETS, RENEWED_EXPANSIONS


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


def write_dataframe_to_file(df: pd.DataFrame, fpath: str):
    """Writes the given dataframe to a file"""
    if not ask_file_overwrite(fpath):
        return
    df.to_csv(fpath, sep=";", index=False)
    print(
        f"Successfully wrote the dominion cards to the file '{fpath}' in the current path."
    )


def override(func):
    """
    Decorator to indicate that a method is overridden.
    """
    # pylint: disable=unused-argument,invalid-name,missing-function-docstring
    return func


def get_expansion_icon_path(expansion: str) -> str:
    """Returns the image path for the given expansion icon."""
    base = PATH_ASSETS.joinpath("icons/expansions/")
    conversion_dict = {}
    for outdated_exp in RENEWED_EXPANSIONS:
        conversion_dict[outdated_exp + ", 1E"] = outdated_exp + "_old"
        conversion_dict[outdated_exp + ", 2E"] = outdated_exp
    if expansion in conversion_dict:
        expansion = conversion_dict[expansion]
    return str(base.joinpath(expansion.replace(" ", "_") + ".png"))


def get_row_and_col(index: int, max_columns: int) -> tuple[int, int]:
    """Calculate the row and column for the given index in a grid with
    max_columns as the maximum amount of columns."""
    row = index // max_columns
    column = index % max_columns
    return row, column


def clear_layout(layout: QW.QLayout):
    """Clear the given layout (remove all its children in a safe way)

    Parameters
    ----------
    layout : QW.QLayout
        The layout to be cleared
    """
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
