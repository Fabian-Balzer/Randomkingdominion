import os
from pathlib import Path
from typing import Collection

import pandas as pd
import yaml

from ..constants import (
    ALL_CSOS,
    PATH_ASSETS,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
    SPECIAL_QUAL_TYPES_AVAILABLE,
)
from .kingdom_helper_funcs import sanitize_cso_list


def get_modification_timestamp(fpath: Path) -> int:
    """Returns the modification timestamp of the given file path."""
    return fpath.stat().st_mtime_ns


def filter_combo_or_inter_df_for_csos(
    df: pd.DataFrame,
    csos: Collection[str],
    require_all=False,
    convert_to_parent_pile=True,
) -> pd.DataFrame:
    """Filter the interaction dataframe for interactions involving any of the given CSOs."""
    csos = sanitize_cso_list(csos, replace_parent_pile=convert_to_parent_pile)
    if not require_all or len(csos) <= 1:
        mask = df["CSO1"].isin(csos) | df["CSO2"].isin(csos)
        return df[mask]
    mask = df["CSO1"].isin(csos) & df["CSO2"].isin(csos)
    return df[mask]


def get_cso_name(cso_key: str, default_val: str = "NOT FOUND") -> str:
    """Savely return the name of the cso with the given key."""
    return ALL_CSOS["Name"].to_dict().get(cso_key, default_val)


def convert_upper_camel_to_snake_case(name: str) -> str:
    """Converts a string in UpperCamelCase to snake_case."""
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")


def get_version() -> str:
    """Return the version of the package."""
    return max(get_changelog().keys()).split(" ")[0]


def get_changelog() -> dict[str, list[str]]:
    """Return the changelog of the package, mapping the version to the changes."""
    with PATH_ASSETS.parent.joinpath("changelog.yaml").open("r") as f:
        yaml_data = yaml.safe_load(f.read())
    log = {k: v for dict_entry in yaml_data for k, v in dict_entry.items()}
    return {k: v if isinstance(v, list) else [v] for k, v in log.items()}


def copy_to_clipboard_pyperclip(text: str):
    """Copy text to clipboard, compatible with desktop and web environments."""
    import pyperclip  # type: ignore
    import streamlit as st
    import streamlit.components.v1 as components

    try:
        # Try using pyperclip for desktop environments
        pyperclip.copy(text)
        st.toast("Text copied to clipboard!", icon="📋")
    except pyperclip.PyperclipException:
        # Fallback to JavaScript for web environments
        components.html(
            f"""
            <script>
                function copyToClipboard(text) {{
                    const el = document.createElement('textarea');
                    el.value = text;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                }}
                copyToClipboard("{text}");
            </script>
        """,
            height=0,
        )
        st.toast("Tried to copy text to clipboard", icon="📋")


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
    question = f"The file '{fname}' already exists at {path}. Continue and Replace it (y/n)?\n>>> "
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


def write_dataframe_to_file(
    df: pd.DataFrame, fpath: str | Path, overwrite: bool = False, verbose: bool = True
):
    """Writes the given dataframe to a file"""
    if not overwrite and not ask_file_overwrite(fpath):
        return
    elif overwrite and os.path.exists(fpath):
        print(f"Overwriting '{fpath}' with {len(df)} rows.")
    df.to_csv(fpath, sep=";", index=False)
    if verbose:
        print(f"Successfully wrote the file '{fpath}' with {len(df)} rows.")


def override(func):
    """
    Decorator to indicate that a method is overridden.
    """
    return func


def get_expansion_icon_path(expansion: str, relative_only: bool = False) -> str:
    """Returns the image path for the given expansion icon."""
    base = "icons/expansions/"
    conversion_dict = {}
    for outdated_exp in RENEWED_EXPANSIONS:
        conversion_dict[outdated_exp + ", 1E"] = outdated_exp + "_old"
        conversion_dict[outdated_exp + ", 2E"] = outdated_exp
    for cguild_str in ["Cornucopia & Guilds, 2E", "Cornucopia", "Guilds"]:
        conversion_dict[cguild_str] = "CornGuilds"
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
        if (qualval := cso[qual + "_quality"]) == 0:  # type: ignore
            continue
        qual_string = f"<i>{qual.capitalize()}</i>:<br>&emsp;{qualval}"
        if qual in SPECIAL_QUAL_TYPES_AVAILABLE:
            qual_string += f" ({', '.join(cso[qual + '_types'])})"
        qual_strings.append(qual_string)
    return "<br>".join(qual_strings)
