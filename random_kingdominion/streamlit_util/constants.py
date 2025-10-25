from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from ..constants import (
    ALL_COMBOS,
    ALL_INTERACTIONS,
    EXPANSION_LIST,
    RENEWED_EXPANSIONS,
    VALID_COMBO_TYPES,
)
from ..utils import filter_combo_or_inter_df_for_csos, get_expansion_icon_path

# from streamlit_cookies_controller import CookieController


@st.cache_data
def get_cached_expansions():
    return [exp for exp in EXPANSION_LIST if exp not in RENEWED_EXPANSIONS]


# COOKIES = CookieController()

STATIC_FPATH = Path("./static")
ALL_EXPANSIONS = get_cached_expansions()
NUM_EXPS = len(ALL_EXPANSIONS)
LIKE_BAN_OPTIONS = {
    "Banned": "These CSOs are excluded from the draw pool during randomization.",
    "Required": "These CSOs will be included in the kingdom (unless they are from different expansions than the selected ones, in that case it depends on whether you want to allow that). This overrides any bans.",
    "Disliked": "These CSOs will have a lower probability of showing up.",
    "Liked": "These CSOs will have a higher probability of showing up.",
}


def _prepare_combo_inter_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add useful columns (display name, image, expansion)
    to a dataframe containing pairs of CSOs that are used to display combos
    or interactions.
    """
    from random_kingdominion import ALL_CSOS

    name_dict = ALL_CSOS["Name"].to_dict()
    img_dict = ALL_CSOS["ImagePath"].to_dict()
    exp_dict = ALL_CSOS["Expansion"].to_dict()
    df["CSO 1"] = df["CSO1"].apply(name_dict.get)
    df["CSO 2"] = df["CSO2"].apply(name_dict.get)
    df["img_1"] = df["CSO1"].apply(lambda x: "app/static/card_pictures/" + img_dict[x])
    df["img_2"] = df["CSO2"].apply(lambda x: "app/static/card_pictures/" + img_dict[x])
    df["exp_1"] = df["CSO1"].apply(exp_dict.get)
    df["exp_2"] = df["CSO2"].apply(exp_dict.get)

    df["exp_img_1"] = df["exp_1"].apply(
        lambda x: "app/static/" + get_expansion_icon_path(x, relative_only=True)
    )
    df["exp_img_2"] = df["exp_2"].apply(
        lambda x: "app/static/" + get_expansion_icon_path(x, relative_only=True)
    )
    return df


@st.cache_data
def get_cached_inter_df() -> pd.DataFrame:
    """Loads the available interactions and adds some
    streamlit-relevant columns to them."""
    df = ALL_INTERACTIONS.copy()
    return _prepare_combo_inter_df(df)


@st.cache_data
def get_cached_combo_df() -> pd.DataFrame:
    """Loads the available interactions and adds some
    streamlit-relevant columns to them."""
    df = ALL_COMBOS.copy()
    df["YTLink"] = df["YTLink"].fillna("")
    df["YTComment"] = df["YTComment"].fillna("")
    return _prepare_combo_inter_df(df).sort_values(by=["CSO1", "CSO2"])


@st.cache_data
def _load_csos():
    from random_kingdominion import ALL_CSOS

    df = ALL_CSOS.copy()

    df["Name and Expansion"] = df.apply(
        lambda x: f"{x['Name']} ({x['Expansion']})", axis=1
    )
    df["num_combos"] = df.index.to_series().apply(
        lambda x: np.sum(
            ALL_COMBOS.index.to_series().str.split("___").apply(lambda y: x in y)
        )
    )
    df["num_interactions"] = df.index.to_series().apply(
        lambda x: np.sum(
            ALL_INTERACTIONS.index.to_series().str.split("___").apply(lambda y: x in y)
        )
    )
    return df


ALL_CACHED_CSOS = _load_csos()


def _get_combo_color_dict() -> dict[str, str]:
    """Returns a dictionary mapping combo types to colors for display."""
    colors = [
        "#856404",  # dark yellow
        "#155724",  # dark green
        "#198754",  # green
        "#d4edda",  # light green
        "#721c24",  # dark red
        "#f8d7da",  # grey
    ]
    # Add alpha values:
    colors = [f"{color}70" for color in colors]
    color_dict = dict(zip(VALID_COMBO_TYPES, colors))
    return color_dict


COMBO_COLOR_DICT = _get_combo_color_dict()


ST_ICONS = {
    "randomizer": "🔀",
    "oracle": "💥",
    "cso_overview": "📂",
    "interactions": "↔️",
    "combos": "🎊",
    "about": "❓",
    "winrate": "📈",
    "cso_qualities": "📊",
    "expansions": "🗃️",
    "mechanics": "⚙️",
    "landscapes": "🖼️",
    "bans": "🚫",
    "kingdom_qualities": "🏰",
    "future_development": "🔮",
    "changelog": "📝",
    "feedback": "💬",
    "components": "📤",
    "other": "🔧",
    "video": "📹",
}
