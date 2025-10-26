from typing import Literal

import pandas as pd
import streamlit as st
from streamlit.elements.lib.column_types import ColumnConfig

from ..constants import VALID_COMBO_TYPES
from ..utils import filter_combo_or_inter_df_for_csos, sanitize_cso_list
from .constants import (
    ALL_CACHED_CSOS,
    COMBO_COLOR_DICT,
    ST_ICONS,
    get_cached_combo_df,
    get_cached_expansions,
    get_cached_inter_df,
)

_PAIR_TYPE = Literal["combo", "inter"]


def add_combo_inter_info_for_kingdoms(df: pd.DataFrame) -> pd.DataFrame:
    """Add combo and interaction information to the given DataFrame of kingdoms."""
    all_inters = get_cached_inter_df()
    all_combos = get_cached_combo_df()
    combo_infos = []
    combo_types = []
    inter_infos = []
    for _, row in df.iterrows():
        cards = row["cards"]
        landsc = row["landscapes"]
        kingdom_csos = set(cards + landsc)
        inters = filter_combo_or_inter_df_for_csos(all_inters, kingdom_csos, True)
        combos = filter_combo_or_inter_df_for_csos(all_combos, kingdom_csos, True)
        inter_infos.append(inters.index.tolist())
        combo_infos.append(combos.index.tolist())
        combo_types.append(combos["Type"].tolist())
    df["interactions"] = inter_infos
    df["num_interactions"] = df["interactions"].apply(len)
    df["combos"] = combo_infos
    df["combo_types"] = combo_types
    df["num_combos"] = df["combo_types"].apply(
        lambda x: x.count("Combo") + x.count("Synergy") + x.count("Rush")
    )
    return df


def _get_name(pair_type: _PAIR_TYPE) -> str:
    return "interaction" if pair_type == "inter" else "combo"


def build_combo_inter_filter_expansion(
    df: pd.DataFrame, pair_type: _PAIR_TYPE
) -> pd.DataFrame:
    """Builds the filter for the interactions or combos.
    df: pd.DataFrame: The combo or interaction dataframe to filter"""
    cols = st.columns([0.2, 0.8, 0.2])
    name = _get_name(pair_type)
    key_in_exp = f"{pair_type}_require_same_exp"
    req_same_exp = cols[0].checkbox(
        f"Require same expansion",
        value=st.session_state.get(key_in_exp, False),
        key=key_in_exp,
        help=f"Limit to {name}s where both CSOs are from the same expansion",
    )
    if req_same_exp:
        df = df[df["exp_1"] == df["exp_2"]]
    key = f"{pair_type}_require_all_exps"
    require_all = cols[2].checkbox(
        "Require all Expansions",
        value=st.session_state.get(key, False),
        key=key,
        help=f"If checked, only {name}s that include all Expansions provided here are shown.",
    )

    relevant_expansions = [
        exp
        for exp in get_cached_expansions()
        if exp in df["exp_1"].unique() or exp in df["exp_2"].unique()
    ]
    key = f"{pair_type}_expansion_filter"
    expansions = cols[1].multiselect(
        "Expansions",
        relevant_expansions,
        default=st.session_state.get(key, []),
        key=key,
        help=f"Filter for {name}s from the selected expansions. If left empty, all expansions are included.",
        placeholder="Select expansions to filter for",
    )
    if len(expansions) > 0:
        if require_all:
            df = df[df["exp_1"].isin(expansions) & df["exp_2"].isin(expansions)]
        else:
            df = df[df["exp_1"].isin(expansions) | df["exp_2"].isin(expansions)]
    return df


def build_combo_inter_filter_other(
    df: pd.DataFrame, pair_type: _PAIR_TYPE
) -> pd.DataFrame:
    """Builds the filter for the combos or interactions.
    df: pd.DataFrame: The combo or interactions dataframe to filter"""
    name = _get_name(pair_type)
    st.write(f"Here you might apply additional filters for the {name}s to display.")
    cols = st.columns(3 if pair_type == "combo" else 2)
    key_ways = f"{pair_type}_exclude_ways"
    exclude_ways = cols[0].checkbox(
        "Exclude Ways",
        value=st.session_state.get(key_ways, False),
        key=key_ways,
        help=f"Exclude {name}s that include Ways as these include a lot of similar ones.",
    )
    if exclude_ways:
        df = df[~df.index.str.contains("way_of_the_")]
    key_1e = f"{pair_type}_exclude_first_edition"
    exclude_first_edition = cols[1].checkbox(
        "Exclude 1E CSOs",
        value=st.session_state.get(key_1e, True),
        key=key_1e,
        help=f"Exclude {name}s revolving around CSOs from first editions.",
    )
    if exclude_first_edition:
        df = df[~df["exp_1"].str.contains("1E") & ~df["exp_2"].str.contains("1E")]
    if pair_type == "combo":
        yt_key = "combo_yt_link_only"
        yt_link_only = cols[2].checkbox(
            f"{ST_ICONS['video']}Only show combos with YouTube links",
            value=st.session_state.get(yt_key, False),
            key=yt_key,
            help=f"Only show {name}s that have a YouTube link associated with them.",
        )
        if yt_link_only:
            df = df[df["YTLink"] != ""]
    return df


def _parse_csv_input(csv_input: str) -> set[str]:
    """Parses a comma-separated string into a list of sanitized CSO names."""
    requested_csos = set(sanitize_cso_list(csv_input.split(",")))
    valid_csos = set(ALL_CACHED_CSOS.index.to_list())
    invalid = list(requested_csos - valid_csos)
    if len(invalid) > 0:
        is_plural = len(invalid) > 1
        if is_plural:
            invalids = "**', '**".join(invalid[:-1])
            invalids += f"**' and '**{invalid[-1]}"
        else:
            invalids = invalid[0]
        st.warning(
            f"The CSO{ 's' if is_plural else ''} '**{invalids}**' {'are' if is_plural else 'is'} not recognized. Did you spell everything correctly, and did you use commas as separators?"
        )
    return requested_csos


def build_combo_inter_filter_for_csos(
    df: pd.DataFrame, pair_type: _PAIR_TYPE
) -> pd.DataFrame:
    """Builds the filter for combos or interactions for a given list of csos.
    We pretend it to be a kingdom as we can easily sanitize it that way.
    df: pd.DataFrame: The interactions dataframe to filter"""
    cols = st.columns([0.8, 0.2])
    name = _get_name(pair_type)
    with cols[1]:
        key_req = f"{pair_type}_require_all_csos"
        require_all = st.checkbox(
            "Require all CSOs",
            value=st.session_state.get(key_req, True),
            key=key_req,
            help=f"If checked, only {name}s that include all CSOs provided here are shown (unless you only input one).",
        )
    with cols[0]:
        logic = "AND" if require_all else "OR"
        key_filt_logic = f"{pair_type}_cso_filtering_input"
        csv_input = st.text_input(
            f"Enter CSOs you want the {name}s to be filtered for with a logical {logic}.",
            value=st.session_state.get(key_filt_logic, ""),
            help=f"Enter a kingdom string to filter for {pair_type}s. The kingdom string should be formatted as a comma-separated list of CSO names.",
            key=key_filt_logic,
            placeholder="e.g. Siren, Sailor, Stonemason, Destrier, ...",
        )
    if csv_input != "" and csv_input is not None:
        csos_to_filter = _parse_csv_input(csv_input)
    else:
        return df
    if len(csos_to_filter) == 0:
        return df
    df = filter_combo_or_inter_df_for_csos(df, csos_to_filter, require_all=require_all)
    return df


def _build_combo_type_filter(df: pd.DataFrame) -> pd.DataFrame:
    default = [t for t in VALID_COMBO_TYPES if "Weak" not in t]
    selected = st.segmented_control(
        f"{ST_ICONS['combos']}Allowed Combo Types",
        VALID_COMBO_TYPES,
        default=default,
        selection_mode="multi",
        help="Which Combo Types to filter for, for description see above.",
        key="combos_types_filter",
    )
    return df[df["Type"].isin(selected)]


def _reset_all_filters(pair_type: _PAIR_TYPE):
    st.session_state[f"{pair_type}_cso_filtering_input"] = ""
    st.session_state[f"{pair_type}_expansion_filter"] = []
    st.session_state[f"{pair_type}_require_all_csos"] = True
    st.session_state[f"{pair_type}_exclude_ways"] = False
    st.session_state[f"{pair_type}_require_all_exps"] = False
    st.session_state[f"{pair_type}_exclude_first_edition"] = True
    st.session_state[f"{pair_type}_require_same_exp"] = False
    if pair_type == "combo":
        default = [t for t in VALID_COMBO_TYPES if "Weak" not in t]
        st.session_state["combos_types_filter"] = default
        st.session_state["combo_yt_link_only"] = False


def st_build_combo_inter_filters(
    df: pd.DataFrame, pair_type: _PAIR_TYPE
) -> pd.DataFrame:
    name = _get_name(pair_type)
    num_initial = len(df)
    tab_names = [
        f"{ST_ICONS['cso_overview']}CSO Filter",
        f"{ST_ICONS['expansions']}Expansion Filter",
        f"{ST_ICONS['other']}Other Filter",
    ]
    filt_str = ""
    exp = st.expander("Filtering options", expanded=True, icon=ST_ICONS["filter"])
    exp.write(
        f"""You may filter the {name}s by providing a list of CSOs, by expansions, or by other criteria."""
    )
    with st.container():
        cols = exp.columns([0.8, 0.2])
    if cols[1].button(
        "Reset Filters", use_container_width=True, icon="❌", type="primary"
    ):
        _reset_all_filters(pair_type)
        st.rerun()
    if pair_type == "combo":
        with cols[0]:
            df = _build_combo_type_filter(df)
    if num_initial > (num_after_first := len(df)):
        filt_str += ST_ICONS["combos"]
    tabs = cols[0].tabs(tab_names)
    with tabs[0]:
        df = build_combo_inter_filter_for_csos(df, pair_type)
    if num_after_first > (num_after_second := len(df)):
        filt_str += ST_ICONS["cso_overview"]
    with tabs[1]:
        df = build_combo_inter_filter_expansion(df, pair_type)
    if num_after_second > (num_after_third := len(df)):
        filt_str += ST_ICONS["expansions"]
    with tabs[2]:
        df = build_combo_inter_filter_other(df, pair_type)
    if num_after_third > len(df):
        filt_str += ST_ICONS["other"]
    st.session_state[f"{pair_type}_filter_str"] = filt_str
    return df


def _get_common_column_config() -> dict[str, ColumnConfig]:
    """Returns the common column config for both combos and interactions."""
    return {
        "img_1": st.column_config.ImageColumn("Img 1", width=22),  # type: ignore
        "img_2": st.column_config.ImageColumn("Img 2", width=22),  # type: ignore
        "CSO 1": st.column_config.TextColumn("CSO 1", width=60),  # type: ignore
        "CSO 2": st.column_config.TextColumn("CSO 2", width=60),  # type: ignore
        "exp_img_1": st.column_config.ImageColumn("Exp 1", width=22),  # type: ignore
        "exp_img_2": st.column_config.ImageColumn("Exp 2", width=22),  # type: ignore
    }


def st_display_inter_df(df: pd.DataFrame):
    """Displays the interactions DataFrame"""
    col_config = _get_common_column_config()
    col_config.update(
        {
            "Rule": st.column_config.TextColumn("Interaction Description"),
        }
    )
    with st.container():
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            column_config=col_config,
            column_order=[
                "CSO 1",
                "CSO 2",
                "Rule",
                "img_1",
                "img_2",
                "exp_img_1",
                "exp_img_2",
            ],
        )


def _highlight_combo_types(df: pd.DataFrame) -> pd.DataFrame:
    """Highlights the combo types in the DataFrame."""
    # Dark yellow, dark green, green, light green, dark red, grey:

    def highlight_type(val: str) -> str:
        return f"background-color: {COMBO_COLOR_DICT.get(val, '')}"

    return df.style.map(highlight_type, subset=["Type"])  # type: ignore


def _highlight_combo_yt_types(df: pd.DataFrame) -> pd.DataFrame:
    """Highlights the combo types in the DataFrame."""
    if not "YTComment" in df.columns:
        return df

    def highlight_yt(val: str) -> str:
        color = ""
        if "showcase" in val.lower():
            color = "#3FAE59"
        elif "playthrough" in val.lower():
            color = "#2e45a8"
        elif "match" in val.lower():
            color = "#a82e4b"
        return f"background-color: {color}70" if color else ""

    return df.map(highlight_yt, subset=["YTComment"])  # type: ignore


def st_display_combo_df(df: pd.DataFrame):
    """Displays the combos DataFrame"""
    col_config = _get_common_column_config()
    col_config.update(
        {
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Description": st.column_config.TextColumn("Description"),
            "YTLink": st.column_config.LinkColumn(
                "YouTube Link",
                help="Link to a YouTube video explaining the combo, or a video where it just occurs.",
                width=22,
                display_text="To YT",
            ),
            # TODO: Once implemented by streamlit, combine those columns to have the link display text be the comment. As of streamlit 1.5.0 this is not possible, it only allows for a fixed display text.
            "YTComment": st.column_config.TextColumn(
                "YouTube Info",
                help="More information about the YouTube link.",
                width=100,
            ),
        }
    )
    columns = [
        "CSO 1",
        "CSO 2",
        "Type",
        "Description",
        "img_1",
        "img_2",
        "exp_img_1",
        "exp_img_2",
    ]
    if (df["YTLink"] != "").any():
        columns.append("YTLink")
        columns.append("YTComment")
    df = _highlight_combo_types(df)
    df = _highlight_combo_yt_types(df)
    with st.container():
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            column_config=col_config,
            column_order=columns,
        )


def st_display_combo_or_inter_page(pair_type: _PAIR_TYPE):
    """Displays the combos or interactions page."""
    name = _get_name(pair_type)
    if pair_type == "inter":
        df = get_cached_inter_df()
    else:
        df = get_cached_combo_df()
    num_initial = len(df)
    df = st_build_combo_inter_filters(df, pair_type)
    filt_indicator = st.session_state.get(f"{pair_type}_filter_str", "")
    st.write(
        f"#### {filt_indicator}Filtering for {len(df)}/{num_initial} available pairwise {name}s of Card-Shaped Objects (CSOs)."
    )
    if pair_type == "inter":
        st_display_inter_df(df)
    else:
        st_display_combo_df(df)
    st.info("Hint: You can also sort by expansion in the expansion column.")
    if pair_type == "inter":
        st.info(
            "Note that the [Kingdom Oracle](/oracle) and the [Randomizer](/randomizer) will also display all relevant interactions for any given kingdom."
        )
