import pandas as pd
import streamlit as st

from ...kingdom import Kingdom
from ..constants import ST_ICONS
from .constants import (
    ALL_SELECTION_TYPES,
    OracleSelectionType,
    get_selection_description,
)
from .data_preparation import get_existing_kingdoms
from .existing_kingdom_filtering import st_build_existing_kingdom_filter_widget


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
        kingdom = Kingdom.from_dict(series.to_dict())
        st.session_state["oracle_kingdom_input"] = kingdom.get_dombot_csv_string()
        if name_extra != "":
            kingdom.name += f" [{name_extra}]"
        st.session_state["kingdom_name"] = kingdom.name
        st.session_state["kingdom_notes"] = kingdom.notes
        st.session_state["existing_selected_kingdom_str"] = (
            kingdom.get_dombot_csv_string()
        )
    else:
        st.session_state["kingdom_name"] = ""
        st.session_state["kingdom_notes"] = ""
        st.session_state["kingdom_links"] = {}
    st.session_state["old_selected_kingdom"] = sel


def _st_build_random_selection_button(df: pd.DataFrame, name_extra: str = ""):
    if st.button(
        "Random\nSelection",
        key="kingdom_select_random_selection",
        icon="🎲",
        type="primary",
        help="Select a random kingdom from those currently eligible.",
    ):
        if len(df) > 0:
            series = df.sample().iloc[0]
            kingdom = Kingdom.from_dict(series.to_dict())
            st.session_state["oracle_kingdom_input"] = kingdom.get_dombot_csv_string()
            if name_extra != "":
                kingdom.name += f" [{name_extra}]"
            st.session_state["kingdom_name"] = kingdom.name
            st.session_state["kingdom_notes"] = kingdom.notes
            st.session_state["existing_selected_kingdom_str"] = (
                kingdom.get_dombot_csv_string()
            )


def _st_build_reference_widget():
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


def _st_build_single_existing_kingdom_select(
    selection_type: OracleSelectionType,
):
    """Build a way for the user to select one of the given existing kingdoms
    provided via the dataframe.
    """
    df = get_existing_kingdoms(selection_type)
    df = st_build_existing_kingdom_filter_widget(df, selection_type)

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
            f" [with winrate, plus {ST_ICONS['video']} producers and name if available]"
        )
    flex = st.container(horizontal=True, vertical_alignment="bottom")
    with flex:
        _build_kingdom_select_box(df, extra_str, selbox_extra)
        _st_build_random_selection_button(df, extra_str)
        _st_build_reference_widget()


def st_build_existing_kingdom_select():
    """Build the existing kingdom selection widget."""
    cont = st.container(border=True)
    selection: OracleSelectionType | None = cont.segmented_control(
        "Set of existing kingdoms to visualize:",
        ALL_SELECTION_TYPES,
        default=st.session_state.get("kingdom_select_group", None),
        key="kingdom_select_group",
        width="stretch",
    )  # type: ignore
    if selection is not None:
        with cont.expander("More info on these kingdoms", expanded=False, icon="ℹ️"):
            st.info(get_selection_description(selection))
        with cont:
            _st_build_single_existing_kingdom_select(selection)
