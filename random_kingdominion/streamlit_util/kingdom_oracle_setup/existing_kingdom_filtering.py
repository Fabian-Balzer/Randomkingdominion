import numpy as np
import pandas as pd
import streamlit as st

from ...constants import ALL_CSOS, VALID_COMBO_TYPES
from ...cso_series_utils import listlike_contains_any
from ...utils import sanitize_cso_list, sanitize_cso_name
from ..combo_and_inter_setup.df_filtering import st_build_combo_type_filter
from ..constants import ST_ICONS
from .constants import OracleSelectionType


def _build_exps_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    available_exps = np.unique(
        [exp for exp_list in df["expansions"] for exp in exp_list]
    )
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        selected_exps_only = st.checkbox(
            "Fully contained",
            help="If checked, only kingdoms that have all selected expansions in them will be filtered for.",
        )
        require_all_exps = st.checkbox(
            "All expansions included",
            help="If checked, all selected expansions need to be in the sets, otherwise, any of them will do.",
        )
    with cols[0]:
        any_all = "all" if require_all_exps else "any"
        limit_or_not = (
            "selected only" if selected_exps_only else "contains at least those"
        )
        placeholder = f"Choose expansions ({any_all} required, {limit_or_not})"
        default_exps = st.session_state.get("kingdom_select_exp_filters", [])
        default_exps = [e for e in default_exps if e in available_exps]
        exp_filters = st.multiselect(
            "Allowed expansions",
            available_exps,
            default=default_exps,
            key="kingdom_select_exp_filters",
            placeholder=placeholder + " to filter for",
            help="If no expansions are provided, no filters are applied.",
        )

    # If no expansion is selected, allow for all sets
    if len(exp_filters) > 0:
        if selected_exps_only:
            mask = df["expansions"].apply(
                lambda x: len(set(x).difference(exp_filters)) == 0
            )
            df = df[mask]
        filt_func = all if require_all_exps else any
        exp_mask = df["expansions"].apply(
            lambda x: filt_func([exp in x for exp in exp_filters])
        )
        df = df[exp_mask]
    return df


def _build_csos_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return df
    available_csos = sanitize_cso_list(np.unique([cso for cso_list in df["csos"] for cso in cso_list]), sort=False)  # type: ignore
    available_csos = sorted(ALL_CSOS.loc[available_csos]["Name"])
    flex = st.container(horizontal=True, vertical_alignment="bottom")
    select_box_container = flex.container()
    with flex:
        require_all_csos = st.checkbox(
            "Require all",
            help="If checked, all selected CSOs need to be in the sets, otherwise, any of them will do.",
            key="kingdom_select_require_all_csos",
        )
    with select_box_container:
        placeholder = (
            "Choose CSOs (all required)"
            if require_all_csos
            else "Choose CSOs (any required)"
        )
        # Need to filter if somehow an inaccessible CSO ends up in the filters
        default_vals = st.session_state.get("kingdom_select_cso_filters", [])
        default_vals = [v for v in default_vals if v in available_csos]
        cso_filters = st.multiselect(
            "Allowed CSOs",
            available_csos,
            default=default_vals,
            key="kingdom_select_cso_filters",
            placeholder=placeholder + " to filter for",
            help="If no CSOs are provided, no filters are applied.",
        )

    # If no CSO is selected, allow for all CSOs
    if len(cso_filters) > 0:
        filt_func = all if require_all_csos else any
        cso_mask = df["csos"].apply(
            lambda x: filt_func([sanitize_cso_name(cso) in x for cso in cso_filters])
        )
        df = df[cso_mask]
    return df


def _build_combo_inter_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    selected_stuff = st.session_state.get("kingdom_select_group", "Recommended")
    vid_available = selected_stuff in ["TGG Dailies", "TGG Campaigns"]
    flex = st.container(horizontal=True, vertical_alignment="bottom")
    with flex:
        combo_req = st_build_combo_type_filter(
            f"{ST_ICONS['combos']}Synergy types to require",
            key="kingdom_select_combos_to_require",
            default="none",
        )
    inter_req = flex.radio(
        label=f"{ST_ICONS['interactions']}Quirky rules interactions",
        options=["No filter", "At least one", "Exclude"],
        index=0,
        horizontal=False,
        help="Decide how to filter for quirky rules interactions.",
        key="kingdom_select_inters_to_filter",
    )
    if vid_available:
        video_req = flex.checkbox(
            f"{ST_ICONS['video']}Require\\\nplaythrough\\\nlink",
            help="If checked, only kingdoms with a playthrough by me will be kept.",
            key="kingdom_select_require_all_videos",
        )
        if video_req:
            df = df[df["has_video_link"]]

    if inter_req == "At least one":
        df = df[df["num_interactions"] > 0]
    elif inter_req == "Exclude":
        df = df[df["num_interactions"] == 0]

    if len(combo_req) > 0:
        df = df[listlike_contains_any(df["combo_types"], combo_req)]
    return df


def _build_tgg_winrate_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    flex = st.container(horizontal=True)
    with flex:
        apply_winrate_filter = st.checkbox(
            f"{ST_ICONS['winrate']}Activate Winrate Filter",
            help="If checked, you can filter the kingdoms by the winrate of the TGG Hard AI. The winrate is an approximation and might not be accurate.",
            key="kingdom_select_winrate_filter_checkbox",
        )
    with flex:
        winrate_slider = st.slider(
            "Winrate",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.01,
            key="kingdom_select_winrate_filter",
            help="Filter kingdoms by the winrate of the TGG Hard AI. The winrate is an approximation and might not be accurate.",
            disabled=not apply_winrate_filter,
        )
    _winrate_info_str = """
The winrate of the TGG Hard AI was kindly provided to me by Jeff - thanks a lot!

The winrate $ \\eta $ is defined as
$\\eta = \\frac{{N_{{\\rm First Wins}}}}{{N_{{\\rm First Wins}} + N_{{\\rm First Losses}}}}$
where $N_{{\\rm First Wins}}$ and $N_{{\\rm First Losses}}$
are the number of games the players won against Hard AI or lost against any AI
(so a bit biased as many people don't play against Hard AI!) on their first playthrough.
It is only available for kingdoms played after mid December 2023, which is when AI difficulty settings were introduced to the Daily.
If you're filtering for it, all kingdoms where it's unavailable are excluded."""

    if apply_winrate_filter:
        st.info(_winrate_info_str)
    if apply_winrate_filter:
        df = df[df["winrate"] != ""]
        df = df[df["winrate"].between(*winrate_slider)]
    return df


def st_build_existing_kingdom_filter_widget(
    df: pd.DataFrame,
    selection_type: OracleSelectionType,
) -> pd.DataFrame:
    """Build filtering widgets for the given selection type and return
    the filtered DataFrame."""
    filt_str = ""
    num_initial = len(df)
    with st.expander("Filtering options", expanded=True, icon="🔍"):
        tab_spec = [
            f"{ST_ICONS['cso_overview']}By CSOs",
            f"{ST_ICONS['expansions']}By Expansions",
            f"{ST_ICONS['combos']}{ST_ICONS['interactions']}By Combos/Interactions and more",
        ]
        if selection_type == "TGG Dailies":
            tab_spec.insert(2, f"{ST_ICONS['winrate']}By Winrate")
        tabs = st.tabs(tab_spec)
        with tabs[0]:
            df = _build_csos_filter_widget(df)
        if num_initial > (num_after_first := len(df)):
            filt_str += ST_ICONS["cso_overview"]
        with tabs[1]:
            df = _build_exps_filter_widget(df)
        if num_after_first > (num_after_second := len(df)):
            filt_str += ST_ICONS["expansions"]
        combo_tab_index = 2 if selection_type != "TGG Dailies" else 3
        with tabs[combo_tab_index]:
            df = _build_combo_inter_filter_widget(df)
        if num_after_second > (num_after_third := len(df)):
            filt_str += ST_ICONS["combos"]
        if selection_type == "TGG Dailies":
            with tabs[2]:
                df = _build_tgg_winrate_filter_widget(df)
            if num_after_third > (num_after_fourth := len(df)):
                filt_str += ST_ICONS["winrate"]
    st.session_state["kingdom_select_filter_str"] = filt_str
    return df
