import numpy as np
import pandas as pd
import streamlit as st

from ..utils import sanitize_cso_name
from .constants import ALL_CACHED_CSOS, ST_ICONS


# Define the style function
def colorize(val):
    if not isinstance(val, int):
        return ""
    if val == 0:
        color = "rgba(255, 0, 0, 0.1)"
    elif val == 1:
        color = "rgba(50, 255, 50, 0.3)"
    elif val == 2:
        color = "rgba(50, 50, 255, 0.5)"
    elif val == 3:
        color = "rgba(255, 100, 100, 0.6)"
    else:  # Assuming only 0-3 are the values
        color = "#B64AE8AB"
    return f"background-color: {color}"


def get_stylized_df(df: pd.DataFrame) -> pd.DataFrame:
    styled_df = df.style.map(colorize)  # type: ignore
    return styled_df  # type: ignore


def get_short_qual_name(qual: str, long=False) -> str:
    if long:
        return qual.split("_")[0].capitalize()
    return qual[:2].capitalize() if "altvp" not in qual.lower() else "VP"


def get_col_config() -> dict[str, dict]:

    col_config = {
        f"{col}": {
            "label": f"{get_short_qual_name(col)}-Q",
            "width": 40,
            "help": col.replace("_", " ").title(),
        }
        for col in ALL_CACHED_CSOS.columns
        if "quality" in col
    }
    col_config |= {
        f"{col}": {
            "label": f"{get_short_qual_name(col, long=True)}-Types",
            "width": 100,
            "help": col.replace("_", " ").title(),
        }
        for col in ALL_CACHED_CSOS.columns
        if "types" in col
    }
    col_config["num_combos"] = {
        "label": ST_ICONS["combos"],
        "help": "Number of pairwise combos (or synergies, nombos, or counters) this CSO is involved in",
        "width": 30,
    }
    col_config["num_interactions"] = {
        "label": ST_ICONS["interactions"],
        "help": "Number of special pairwise rules interactions this CSO is involved in",
        "width": 30,
    }
    col_config["IsExtendedLandscape"] = {
        "label": "Landscape",
        "width": 40,
        "help": "Whether this CSO is an extended landscape (including Allies/Prophecies)",
    }
    col_config["IsOtherThing"] = {
        "label": "Other Thing",
        "width": 40,
        "help": "Whether this CSO is neither card nor landscape",
    }
    col_config["IsInSupply"] = {
        "label": "In Supply",
        "width": 40,
        "help": "Whether this CSO in the supply of a kingdom",
    }
    col_config["Extra Components"] = {
        "label": "Extra Components",
        "width": 100,
        "help": "The components needed to play with this CSO",
    }
    col_config["Text"] = {
        "label": "CSO Text",
        "width": 150,
        "help": "The text of the CSO, might be not perfectly formatted.",
    }
    col_config["Image"] = st.column_config.ImageColumn(  # type: ignore
        "Image",
        help="The image of the CSO",
    )
    col_config["Cost"] = {
        "label": "Cost",
        "help": "How much the CSO costs",
    }
    col_config["Types"] = {
        "label": "Types",
        "help": "The types of the CSO",
    }
    col_config["Expansion"] = {
        "label": "Expansion",
        "help": "The expansion the CSO is from",
    }
    return col_config


def get_column_order() -> list[str]:
    return [
        "Image",
        "Cost",
        "Expansion",
        "Types",
        "village_quality",
        "draw_quality",
        "thinning_quality",
        "gain_quality",
        "attack_quality",
        "altvp_quality",
        "interactivity_quality",
        "village_types",
        "draw_types",
        "thinning_types",
        "gain_types",
        "attack_types",
        "altvp_types",
        "Extra Components",
        "num_combos",
        "num_interactions",
        "Text",
        "IsExtendedLandscape",
        "IsOtherThing",
        "IsInSupply",
    ]


@st.fragment
def display_stylysed_cso_df(df: pd.DataFrame, with_reroll=False, **kwargs):
    df = df.copy()
    if with_reroll:
        df["Reroll?"] = np.zeros(len(df), dtype=bool)
    if "ImagePath" in df.columns:
        df["Image"] = df["ImagePath"].apply(lambda x: "app/static/card_pictures/" + x)
    styled_df = get_stylized_df(df)
    col_config = get_col_config()
    if with_reroll:
        col_config["Reroll?"] = st.column_config.CheckboxColumn(  # type: ignore
            "Reroll?",
            help="Select the CSOs to be rerolled",
            default=False,
        )
        data = st.data_editor(  # type: ignore
            styled_df,
            column_order=get_column_order() + ["Reroll?"],
            column_config=col_config,  # type: ignore
            disabled=get_column_order() + ["Name"],
            **kwargs,
        )
        st.session_state["CSOsToReroll"] = {
            sanitize_cso_name(k): v for k, v in data["Reroll?"].to_dict().items()
        }
    else:
        st.dataframe(
            styled_df,
            column_order=get_column_order(),
            column_config=get_col_config(),  # type: ignore
            **kwargs,
        )


# img_to_bytes and img_to_html inspired from https://pmbaumgartner.github.io/streamlitopedia/sizing-and-images.html
import base64
from pathlib import Path


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
        img_to_bytes(img_path)
    )
    return img_html
