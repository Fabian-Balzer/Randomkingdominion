import pandas as pd
import streamlit as st

from ..constants import (
    ALL_COMBOS,
    ALL_INTERACTIONS,
    EXPANSION_LIST,
    PATH_ASSETS,
    PATH_CARD_INFO,
    RENEWED_EXPANSIONS,
    VALID_COMBO_TYPES,
    load_combo_or_inter_df,
)
from ..utils import get_expansion_icon_path, get_modification_timestamp


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

# from streamlit_cookies_controller import CookieController


@st.cache_data
def get_cached_expansions():
    return [exp for exp in EXPANSION_LIST if exp not in RENEWED_EXPANSIONS]


# COOKIES = CookieController()

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
def _load_cached_inter_df(mod_time: int) -> pd.DataFrame:
    """Loads the available interactions and adds some
    streamlit-relevant columns to them."""
    _ = mod_time + 1  # Dummy calculation to trigger cache invalidation
    df = load_combo_or_inter_df("interaction")
    return _prepare_combo_inter_df(df)


def get_cached_inter_df() -> pd.DataFrame:
    """Get the streamlit-cached interaction dataframe."""
    fpath = PATH_CARD_INFO.joinpath("good_interaction_data.csv")
    mod_time = get_modification_timestamp(fpath)
    return _load_cached_inter_df(mod_time)


@st.cache_data
def _load_cached_combo_df(mod_time: int) -> pd.DataFrame:
    """Loads the available combos and adds some
    streamlit-relevant columns to them."""
    _ = mod_time + 1  # Dummy calculation to trigger cache invalidation
    df = load_combo_or_inter_df("combo")
    df["YTLink"] = df["YTLink"].fillna("")
    df["YTComment"] = df["YTComment"].fillna("")
    return _prepare_combo_inter_df(df).sort_values(by=["CSO1", "CSO2"])


def get_cached_combo_df() -> pd.DataFrame:
    """Get the streamlit-cached combo dataframe."""
    fpath = PATH_CARD_INFO.joinpath("good_combo_data.csv")
    mod_time = get_modification_timestamp(fpath)
    return _load_cached_combo_df(mod_time)


def count_cso_occurrences(pair_index: pd.Index, cso_index: pd.Index) -> pd.Series:
    """Count in how many of the ``"cso1___cso2"`` pairs each CSO occurs; a pair of
    a CSO with itself (e.g. ``"outpost___outpost"``) only counts once."""
    pairs = pair_index.to_series().str.split("___").apply(set)
    return pairs.explode().value_counts().reindex(cso_index, fill_value=0)


@st.cache_data
def _load_cached_csos(combo_mod_time: int, inter_mod_time: int) -> pd.DataFrame:
    _ = combo_mod_time + inter_mod_time  # Only there to key the cache
    from random_kingdominion import ALL_CSOS

    df = ALL_CSOS.copy()

    df["Name and Expansion"] = df.apply(
        lambda x: f"{x['Name']} ({x['Expansion']})", axis=1
    )
    df["num_combos"] = count_cso_occurrences(ALL_COMBOS.index, df.index)
    df["num_interactions"] = count_cso_occurrences(ALL_INTERACTIONS.index, df.index)
    return df


def get_cached_csos() -> pd.DataFrame:
    """Get the streamlit-cached CSO dataframe."""
    return _load_cached_csos(
        get_modification_timestamp(PATH_CARD_INFO.joinpath("good_combo_data.csv")),
        get_modification_timestamp(
            PATH_CARD_INFO.joinpath("good_interaction_data.csv")
        ),
    )


ALL_CACHED_CSOS = get_cached_csos()


ST_ICONS = {
    "randomizer": "🔀",
    "oracle": "💥",
    "cso_overview": "📂",
    "interactions": "↔️",
    "combos": "🎊",
    "about": "ℹ️",
    "quiz": "❓",
    "winrate": "📈",
    "cso_qualities": "📊",
    "expansions": "🗃️",
    "mechanics": "⚙️",
    "landscapes": "🖼️",
    "bans": "🚫",
    "card_levels": "📚",
    "kingdom_qualities": "🏰",
    "future_development": "🔮",
    "changelog": "📝",
    "feedback": "💬",
    "components": "📤",
    "other": "🔧",
    "video": "📹",
    "filter": "🔍",
    "links": "🔗",
    "download": "⬇️",
    "combo_type_rush": "🏃",
    "combo_type_combo": "🎉",
    "combo_type_synergy": "🤝",
    "combo_type_weak_synergy": "👌",
    "combo_type_counter": "🛡️",
    "combo_type_nombo": "❌",
}
