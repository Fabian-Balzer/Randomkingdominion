import os
from pathlib import Path

import pandas as pd
import PyQt5.QtWidgets as QW

from ..constants import (
    ALL_CSOS,
    PATH_ASSETS,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
    SPECIAL_QUAL_TYPES_AVAILABLE,
)


def copy_to_clipboard(text: str):
    """Copies the given text into the user's clipboard."""
    import win32clipboard

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def ask_file_overwrite(fpath: str | Path) -> bool:
    """Prompts the user if there already exists a file at the given fpath

    Parameters
    ----------
    fpath : FullFilePath
        filename and path of the file that is supposed to be written

    Returns
    -------
    bool
        True if the file should be replaced, otherwise False

    Raises
    ------
    RuntimeError
        If the user does not provide an answer
    """
    path, fname = os.path.split(fpath)
    if not os.path.exists(fpath):
        print(f"Writing the file '{fpath}'")
        return True
    question = f"The file '{fname}' already exists at {path}. Continue and replace it (y/n)?\n>>> "
    if ask_yes_now(question):
        print(f"Overwriting '{fpath}'")
        return True
    print(f"Skipped writing '{fpath}' as it already existed.")
    return False


def ask_yes_now(question: str) -> bool:
    """Ask the user a question and return True if the answer is 'yes' or 'y'
    and False if the answer is 'no' or 'n'."""
    answer = input(question)

    for _ in range(5):
        if not answer:
            raise RuntimeError("Stopped execution due to no input.")
        if answer.lower() in ["y", "yes"]:
            return True
        if answer.lower() in ["n", "no"]:
            return False
        answer = input(
            f"Please answer with 'y' or 'n',\nThe question was {question}\n>>> "
        )
    return False


def write_dataframe_to_file(df: pd.DataFrame, fpath: str | Path):
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


def get_expansion_icon_path(expansion: str, relative_only: bool = False) -> str:
    """Returns the image path for the given expansion icon."""
    base = "icons/expansions/"
    conversion_dict = {}
    for outdated_exp in RENEWED_EXPANSIONS:
        conversion_dict[outdated_exp + ", 1E"] = outdated_exp + "_old"
        conversion_dict[outdated_exp + ", 2E"] = outdated_exp
    conversion_dict["Cornucopia & Guilds, 2E"] = "CornGuilds"
    if expansion in conversion_dict:
        expansion = conversion_dict[expansion]
    rel_path = base + expansion.replace(" ", "_") + ".png"
    if relative_only:
        return rel_path
    return str(PATH_ASSETS.joinpath(rel_path))


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


def get_quality_icon_fpath(quality_name: str) -> Path:
    """Return the path to the icon for the given quality."""
    return PATH_ASSETS.joinpath(f"icons/qualities/{quality_name}.jpg")


def invert_dict(d: dict) -> dict:
    """Invert the given dictionary."""
    assert len(set(d.values())) == len(
        d
    ), "The values of the dictionary are not unique."
    return {v: k for k, v in d.items()}


def get_cso_quality_description(cso_key: str) -> str:
    """Return the qualities that are > 0 for the given card in a string."""
    cso = ALL_CSOS.loc[cso_key]
    qual_strings = []
    for qual in QUALITIES_AVAILABLE:
        if (qualval := cso[qual + "_quality"]) == 0:
            continue
        qual_string = f"<i>{qual.capitalize()}</i>:<br>&emsp;{qualval}"
        if qual in SPECIAL_QUAL_TYPES_AVAILABLE:
            qual_string += f" ({', '.join(cso[qual + '_types'])})"
        qual_strings.append(qual_string)
    return "<br>".join(qual_strings)
