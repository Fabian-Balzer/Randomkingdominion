from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk
from random_kingdominion.streamlit_util.constants import ST_ICONS  # type: ignore

rk.build_page_header(
    "Dominion Kingdom Oracle",
    (
        "This page allows you to easily input a kingdom to visualize its engine qualities "
        "and take a more detailed look on its Card-Shaped Objects (CSOs). "
        "The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form."
    ),
    "Learn more about the CSO and kingdom qualities on the about page.",
)

_SelectionType = Literal[
    "TGG Dailies",
    "TGG Campaigns",
    "Recommended",
    "Reddit's KOTW",
    "Fabi's Recommendations",
]


@st.cache_data
def load_existing_kingdoms(
    selection_type: _SelectionType,
) -> pd.DataFrame:
    """Load kingdoms from the given selection type and return them as a DataFrame."""
    manager = rk.KingdomManager()
    if selection_type == "TGG Dailies":
        manager.load_tgg_dailies()
    if selection_type == "TGG Campaigns":
        manager.load_campaigns(curated_only=True)
    elif selection_type == "Recommended":
        manager.load_recommended_kingdoms()
    elif selection_type == "Reddit's KOTW":
        manager.load_kingdoms_from_yaml(rk.FPATH_KINGDOMS_KOTW_REDDIT)
    elif selection_type == "Fabi's Recommendations":
        manager.load_fabi_recsets_kingdoms()
    df = manager.dataframe_repr
    df = rk.add_combo_inter_info_for_kingdoms(df)
    df["has_video_link"] = df["notes"].apply(
        lambda x: isinstance(x, dict) and x.get("link", "") != ""
    )
    # Register a name that includes the expansions
    exp_repr = df["expansions"].apply(
        lambda x: ", ".join(x) if len(x) < 4 else f"{len(x)} expansions"
    )
    sani_wr = ""
    if selection_type == "TGG Dailies":
        sani_wr = df["winrate"].apply(
            lambda x: f" [WR: {x*100:.1f} %]" if x != "" else " [WR: N/A]"
        )
    vid_icon = ST_ICONS["video"]
    extr_name = df["notes"].apply(
        lambda x: (
            " - " + (vid_icon if x.get("link", "") != "" else "") + x.get("name", "")
            if isinstance(x, dict)
            else ""
        )
    )
    df["name_with_exps"] = df["name"] + sani_wr + extr_name + " (" + exp_repr + ")"
    df["csos"] = df.apply(lambda x: x["cards"] + x["landscapes"], axis=1)
    return df


def _build_kingdom_select_box(
    df: pd.DataFrame, name_extra: str = "", selbox_extra: str = ""
):
    """Build the selection box that also sets the kingdom input and
    the kingdom name in the select box"""
    sel = st.selectbox(
        f"Choose from {len(df)} Kingdoms{selbox_extra}",
        [""] + df["name_with_exps"].tolist(),
        key="kingdom_select_existing",
    )
    old_select = st.session_state.get("old_selected_kingdom", "")
    if sel == old_select:
        # In this case, we should not update the kingdom input, otherwise
        # it will overwrite user input.
        # This leads to a slight bug (user selecting kingdom, then modifying
        # it, then selecting it again), but I think that's negligible.
        pass
    elif sel != "" and isinstance(sel, str):
        series = df[df["name_with_exps"] == sel].iloc[0]
        kingdom = rk.Kingdom.from_dict(series.to_dict())
        st.session_state["kingdom_input"] = kingdom.get_dombot_csv_string()
        if name_extra != "":
            kingdom.name += f" [{name_extra}]"
        st.session_state["kingdom_name"] = kingdom.name
        st.session_state["kingdom_notes"] = kingdom.notes
    else:
        st.session_state["kingdom_name"] = ""
        st.session_state["kingdom_notes"] = ""
    st.session_state["old_selected_kingdom"] = sel


def _build_reference_widget():
    """Build a widget to reference where the kingdoms are from."""
    selected_stuff = st.session_state.get("kingdom_select_group", "Recommended")
    if selected_stuff == "Recommended":
        st.link_button(
            "More sets 🔗",
            "https://kieranmillar.github.io/extra-recommended-sets/",
            help="Huge thanks to Kieran Millar whose [Extra Recommended Kingdoms page](https://kieranmillar.github.io/extra-recommended-sets/) I got the data for the recommended kingdoms from! Be sure to check out his additional recommended sets!",
        )
    elif selected_stuff == "TGG Dailies":
        st.link_button(
            "TGG Dailies 🔗",
            "https://store.steampowered.com/app/1131620/Dominion/",
            help="The TGG Dailies are a set of daily kingdoms provided in the [Temple Gates Games Client](https://store.steampowered.com/app/1131620/Dominion/), where you compete against the Hard AI.\nThanks to the amazing people on the TGG discord I managed to collect these (most notably ``probably-lost``, ``igorbone`` and ``Diesel Pioneer``).",
        )
    elif selected_stuff == "Reddit's KOTW":
        st.link_button(
            "Reddit's KOTW 🔗",
            "https://www.reddit.com/r/dominion/search/?q=flair%3Akotw&sort=new",
            help="The Kingdom of the Week is a weekly event on the [Dominion subreddit](https://www.reddit.com/r/dominion/) with a special kingdom being covered each week.",
        )


def _get_short_info(selected_stuff: str) -> str:
    if selected_stuff == "Recommended":
        return "The kingdoms recommended by DXV himself, found in the rulebooks of the Dominion expansions, and mixing two expansions at max. Shoutout to Kieran Millar's [Extra Recommended Kingdoms page](https://kieranmillar.github.io/extra-recommended-sets/) where these these kingdoms are conveniently provided."
    elif selected_stuff == "TGG Dailies":
        return "The TGG Dailies are kingdoms provided each day in the Temple Gates Games (TGG) (Steam/mobile) client, where you compete against the Hard AI.\\\nShoutout to the amazing people on the TGG discord who helped me collect these (most notably ``probably-lost``, ``igorbone`` and ``Diesel Pioneer``).\\\nThese will only contain the kingdoms up to the point when I've last updated this website."
    elif selected_stuff == "TGG Campaigns":
        return "The kingdoms from the curated campaigns of the Dominion expansions available on the Temple Gates Games (Steam/mobile) client. These each consist of a series of 10 kingdoms that can have surprising effects that aren't available elsewhere - have fun exploring them!"
    elif selected_stuff == "Fabi's Recommendations":
        return "My personal recommendations of kingdoms I randomly stumbled upon, played in the TGG client against the Hard AI, and deemed to be interesting.\\\nHave fun with those!\\\nThey usually contain a large amount of expansions, so they might be more suitable for online play than in-person setup, but go for whatever you prefer!"
    elif selected_stuff == "Reddit's KOTW":
        return "The Kingdom of the Week (KOTW) is a weekly event on the Dominion subreddit, where a curated kingdom is covered. These usually offer especially interesting interactions.\\\nCheck out the [Dominion subreddit](https://www.reddit.com/r/dominion/) for more information; the selection available here might not be fully up to date."
    else:
        return "Unknown"


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
    available_csos = rk.sanitize_cso_list(np.unique([cso for cso_list in df["csos"] for cso in cso_list]), sort=False)  # type: ignore
    available_csos = sorted(rk.ALL_CSOS.loc[available_csos]["Name"])
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        require_all_csos = st.checkbox(
            "Require all",
            help="If checked, all selected CSOs need to be in the sets, otherwise, any of them will do.",
            key="kingdom_select_require_all_csos",
        )
    with cols[0]:
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
            lambda x: filt_func([rk.sanitize_cso_name(cso) in x for cso in cso_filters])
        )
        df = df[cso_mask]
    return df


def _build_combo_inter_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    selected_stuff = st.session_state.get("kingdom_select_group", "Recommended")
    vid_available = selected_stuff in ["TGG Dailies", "TGG Campaigns"]
    col_spec = [0.6, 0.2, 0.2] if vid_available else [0.67, 0.33]
    cols = st.columns(col_spec)
    combo_req = cols[0].segmented_control(
        options=rk.VALID_COMBO_TYPES,
        selection_mode="multi",
        label=f"{ST_ICONS['combos']}Synergy types to require",
        help="Which synergy types to filter for (if none selected, no filtering is applied).",
        key="kingdom_select_combos_to_require",
        width="stretch",
    )
    inter_req = cols[1].radio(
        label=f"{ST_ICONS['interactions']}Quirky rules interactions",
        options=["No filter", "At least one", "Exclude"],
        index=0,
        horizontal=False,
        help="Decide how to filter for quirky rules interactions.",
        key="kingdom_select_inters_to_filter",
    )
    if vid_available:
        video_req = cols[2].checkbox(
            f"{ST_ICONS['video']}Require playthrough link",
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
        df = df[rk.listlike_contains_any(df["combo_types"], combo_req)]
    return df


def _build_random_selection_button(df: pd.DataFrame, name_extra: str = ""):
    if st.button(
        "Random\nSelection",
        key="kingdom_select_random_selection",
        use_container_width=True,
        icon="🎲",
        type="primary",
        help="Select a random kingdom from those currently eligible.",
    ):
        if len(df) > 0:
            series = df.sample().iloc[0]
            kingdom = rk.Kingdom.from_dict(series.to_dict())
            st.session_state["kingdom_input"] = kingdom.get_dombot_csv_string()
            if name_extra != "":
                kingdom.name += f" [{name_extra}]"
            st.session_state["kingdom_name"] = kingdom.name
            st.session_state["kingdom_notes"] = kingdom.notes


_winrate_info_str = (
    "The winrate of the TGG Hard AI was kindly "
    "provided to me by Jeff - thanks a lot!\\\n"
    "The winrate $\\eta$ is defined as "
    "$\\eta = \\frac{{N_{{\\rm First Wins}}}}{{N_{{\\rm First Wins}} + N_{{\\rm First Losses}}}}$ "
    "where $N_{{\\rm First Wins}}$ and $N_{{\\rm First Losses}}$ "
    "are the number of games the players won against Hard AI or lost against any AI "
    "(so a bit biased as many people don't play against Hard AI!) on their first playthrough."
    "It is only available for kingdoms played after mid December 2023, "
    "which is when AI difficulty settings were introduced to the Daily.\\\n"
    "If you're filtering for it, all kingdoms where it's unavailable are excluded."
)


def _build_tgg_winrate_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        apply_winrate_filter = st.checkbox(
            "Filter by winrate",
            help="If checked, you can filter the kingdoms by the winrate of the TGG Hard AI. The winrate is an approximation and might not be accurate.",
            key="kingdom_select_winrate_filter_checkbox",
        )
    with cols[0]:
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
    if apply_winrate_filter:
        st.info(_winrate_info_str)
    if apply_winrate_filter:
        df = df[df["winrate"] != ""]
        df = df[df["winrate"].between(*winrate_slider)]
    return df


def _build_filter_widget(
    df: pd.DataFrame,
    selection_type: _SelectionType,
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


def build_existing_kingdom_select(
    selection_type: _SelectionType,
):
    """Build a way for the user to select one of the given existing kingdoms
    provided via the dataframe.
    """
    df = load_existing_kingdoms(selection_type)
    df = _build_filter_widget(df, selection_type)

    if len(df) == 0:
        st.warning("No kingdoms available for your selection.")
        return

    extra_str = (
        selection_type[:12] + "..." if len(selection_type) > 15 else selection_type
    )
    filt_str = st.session_state.get("kingdom_select_filter_str", "")
    selbox_extra = f" (FILTERED{filt_str})" if filt_str else ""
    if selection_type == "TGG Dailies":
        selbox_extra += (
            f" [with winrate if available, plus {ST_ICONS['video']} name if available]"
        )
    cols = st.columns([0.75, 0.15, 0.1])
    with cols[0]:
        _build_kingdom_select_box(df, extra_str, selbox_extra)
    with cols[1]:
        _build_random_selection_button(df, extra_str)
    with cols[2]:
        _build_reference_widget()


with st.container(border=True):
    selection = st.segmented_control(
        "Set of existing kingdoms to visualize:",
        [
            "Recommended",
            "TGG Dailies",
            "TGG Campaigns",
            "Reddit's KOTW",
            "Fabi's Recommendations",
        ],
        default=st.session_state.get("kingdom_select_group", None),
        key="kingdom_select_group",
        width="stretch",
    )
    if selection is not None:
        with st.expander("More info on these kingdoms", expanded=False, icon="ℹ️"):
            st.info(_get_short_info(selection))
        build_existing_kingdom_select(selection)  # type: ignore

cols = st.columns([0.8, 0.2])
with cols[0]:
    kingdom = rk.build_kingdom_text_input()


def navigate_to_randomizer():
    """Navigate to the randomizer page with the current kingdom."""
    st.session_state["partial_random_kingdom"] = kingdom.get_dombot_csv_string()
    st.switch_page("streamlit_pages/randomizer.py")


with cols[1]:
    if st.button(
        "To Randomizer",
        icon=rk.ST_ICONS["randomizer"],
        help="Start randomization from this selection",
        use_container_width=True,
        disabled=kingdom.is_empty,
    ):
        navigate_to_randomizer()

rk.build_kingdom_input_warning(kingdom, ref_to_randomizer=True)
if kingdom.is_empty:
    st.write("No kingdom selected")
else:
    with st.container(border=True):
        rk.display_kingdom(kingdom, is_randomizer_view=False)

    with st.sidebar:
        rk.display_sidebar_kingdom_info(kingdom, loc="oracle")

if (link := kingdom.unpacked_notes.get("link", "")) != "":
    with st.expander("Playthrough", expanded=True, icon=ST_ICONS["video"]):
        st.write("Check out a video where I explain and play this kingdom!")
        _, container, _ = st.columns([20, 60, 20])
        with container:
            with st.container(border=True):
                st.video(link)

with st.expander("Disclaimer", expanded=False):
    st.warning(
        "Be aware that this is a very superficial view of the kingdom and does not take into account special card interactions, and that some of my takes on individual cards' qualities might seem surprising. Check out the about page for more information on those."
    )
