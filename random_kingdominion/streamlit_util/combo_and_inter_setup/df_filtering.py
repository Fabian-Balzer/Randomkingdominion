import pandas as pd
import streamlit as st

from ...constants import VALID_COMBO_TYPES
from ...utils import filter_combo_or_inter_df_for_csos
from ..constants import ST_ICONS, get_cached_expansions
from .constants import PAIR_TYPE
from .util import (
    get_combo_icon,
    get_name,
    st_build_combo_type_filter,
    st_parse_csv_input,
)


def build_combo_inter_filter_expansion(
    df: pd.DataFrame, pair_type: PAIR_TYPE
) -> pd.DataFrame:
    """Builds the filter for the interactions or combos.
    df: pd.DataFrame: The combo or interaction dataframe to filter"""
    flex = st.container(horizontal=True, horizontal_alignment="left")
    name = get_name(pair_type)
    key_in_exp = f"{pair_type}_require_same_exp"
    req_same_exp = flex.checkbox(
        f"Req. Same Expansion",
        value=st.session_state.get(key_in_exp, False),
        key=key_in_exp,
        help=f"Limit to {name}s where both CSOs are from the same expansion",
    )
    if req_same_exp:
        df = df[df["exp_1"] == df["exp_2"]]

    relevant_expansions = [
        exp
        for exp in get_cached_expansions()
        if exp in df["exp_1"].unique() or exp in df["exp_2"].unique()
    ]
    key = f"{pair_type}_expansion_filter"
    exp_defaults = [
        e for e in st.session_state.get(key, []) if e in relevant_expansions
    ]
    expansions = flex.multiselect(
        "Expansions",
        relevant_expansions,
        default=exp_defaults,
        key=key,
        help=f"Filter for {name}s from the selected expansions. If left empty, all expansions are included.",
        placeholder="Select expansions to filter for",
    )
    key = f"{pair_type}_require_all_exps"
    require_all = flex.checkbox(
        "Req. All Expansions",
        value=st.session_state.get(key, False),
        key=key,
        help=f"If checked, only {name}s that include all Expansions provided here are shown.",
    )
    if len(expansions) > 0:
        if require_all:
            df = df[df["exp_1"].isin(expansions) & df["exp_2"].isin(expansions)]
        else:
            df = df[df["exp_1"].isin(expansions) | df["exp_2"].isin(expansions)]
    return df


def build_combo_inter_filter_other(
    df: pd.DataFrame, pair_type: PAIR_TYPE
) -> pd.DataFrame:
    """Builds the filter for the combos or interactions.
    df: pd.DataFrame: The combo or interactions dataframe to filter"""
    name = get_name(pair_type)
    st.write(f"Here you might apply additional filters for the {name}s to display.")
    cols = st.columns(3)
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
    elif pair_type == "inter":
        self_inter_key = "inter_exclude_self_interactions"
        exclude_self_interactions = cols[2].checkbox(
            "Exclude self-interactions",
            value=st.session_state.get(self_inter_key, False),
            key=self_inter_key,
            help=f"Exclude {name}s which describe self-interactions of CSOs that are also covered within the FAQs of those CSOs.",
        )
        if exclude_self_interactions:
            df = df[df["CSO1"] != df["CSO2"]]
    return df


def build_combo_inter_filter_for_csos(
    df: pd.DataFrame, pair_type: PAIR_TYPE
) -> pd.DataFrame:
    """Builds the filter for combos or interactions for a given list of csos.
    We pretend it to be a kingdom as we can easily sanitize it that way.
    df: pd.DataFrame: The interactions dataframe to filter"""
    flex = st.container(
        horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"
    )
    name = get_name(pair_type)
    cso_container = flex.container()
    with flex:
        key_req = f"{pair_type}_require_all_csos"
        require_all = st.checkbox(
            "Require all CSOs",
            value=st.session_state.get(key_req, True),
            key=key_req,
            help=f"If checked, only {name}s that include all CSOs provided here are shown (unless you only input one).",
        )
    with cso_container:
        logic = "AND" if require_all else "OR"
        key_filt_logic = f"{pair_type}_cso_filtering_input"
        csv_input = st.text_input(
            f"Enter CSOs you want the {name}s to be filtered for with a logical {logic}. Separate using commas. Split pile parts will redirect to their parent pile.",
            value=st.session_state.get(key_filt_logic, ""),
            help=f"Enter a kingdom string to filter for {pair_type}s. The kingdom string should be formatted as a comma-separated list of CSO names.",
            key=key_filt_logic,
            placeholder="e.g. Siren, Sailor, Stonemason, Elder, Destrier, ...",
        )
    if csv_input != "" and csv_input is not None:
        csos_to_filter = st_parse_csv_input(csv_input)
    else:
        return df
    if len(csos_to_filter) == 0:
        return df
    df = filter_combo_or_inter_df_for_csos(df, csos_to_filter, require_all=require_all)
    return df


def _reset_all_filters(pair_type: PAIR_TYPE):
    st.session_state[f"{pair_type}_cso_filtering_input"] = ""
    st.session_state[f"{pair_type}_expansion_filter"] = []
    st.session_state[f"{pair_type}_require_all_csos"] = True
    st.session_state[f"{pair_type}_exclude_ways"] = False
    st.session_state[f"{pair_type}_require_all_exps"] = False
    st.session_state[f"{pair_type}_exclude_first_edition"] = True
    st.session_state[f"{pair_type}_require_same_exp"] = False
    if pair_type == "combo":
        default = [
            t + " " + get_combo_icon(t) for t in VALID_COMBO_TYPES if "Weak" not in t
        ]
        st.session_state["combos_types_filter"] = default
        st.session_state["combo_yt_link_only"] = False
    elif pair_type == "inter":
        st.session_state["inter_exclude_self_interactions"] = False


def st_build_combo_inter_filters(
    df: pd.DataFrame, pair_type: PAIR_TYPE
) -> pd.DataFrame:
    name = get_name(pair_type)
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
    with exp.container():
        flex = st.container(
            horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"
        )
        content_container = flex.container()
    if flex.button("Reset Filters", icon="❌", type="primary"):
        _reset_all_filters(pair_type)
        st.rerun()
    if pair_type == "combo":
        with content_container:
            selected = st_build_combo_type_filter(
                f"{ST_ICONS['combos']}Allowed Combo Types",
                key="combos_types_filter",
                default="all_but_weak",
            )
            df = df[df["Type"].isin(selected)]
    if num_initial > (num_after_first := len(df)):
        filt_str += ST_ICONS["combos"]
    tabs = content_container.tabs(tab_names)
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
