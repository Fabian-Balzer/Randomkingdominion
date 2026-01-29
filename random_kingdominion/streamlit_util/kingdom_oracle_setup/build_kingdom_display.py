import streamlit as st

from ...kingdom import Kingdom
from ..common_widgets import (
    st_build_full_kingdom_display,
    st_build_kingdom_sidebar_display,
)
from ..constants import ST_ICONS
from .data_preparation import get_link_dataframe, get_links_for_kingdom


@st.fragment
def _build_link_video_display(k: Kingdom):
    link = k.unpacked_notes.get("link", "")
    recovered_name = k.name.split(" [")[0]
    other_links = get_links_for_kingdom(
        recovered_name, get_link_dataframe(), youtubify=True
    )
    if link == "" and len(other_links) == 0:
        return
    if len(other_links) == 0:
        other_links["Fabi"] = link
    exp = st.expander("Playthrough Videos", expanded=True, icon=ST_ICONS["video"])
    if "occasion" in k.unpacked_notes:
        exp.write("Check out the video where I played this kingdom!")
    else:
        exp.write("Check out videos of people explaining and playing this kingdom!")
    if len(other_links) > 1:
        tabs_names = sorted(other_links)
        control = exp.segmented_control(
            "Select a video to watch:",
            options=tabs_names,
            key="kingdom_video_select",
            default=tabs_names[0],
            width="stretch",
        )
        if control not in other_links:
            return
    else:
        control = list(other_links.keys())[0]
        if "occasion" not in k.unpacked_notes:
            exp.write(f"Video by {control}:")
    link = other_links[control]
    _, container, _ = exp.columns([20, 60, 20])
    with container:
        with st.container(border=True):
            st.video(link)


@st.fragment
def st_build_oracle_kingdom_display(k: Kingdom):
    if k.is_empty:
        st.write("No kingdom selected")
    else:
        with st.container(border=True):
            st_build_full_kingdom_display(k)

        with st.sidebar:
            st_build_kingdom_sidebar_display(k, loc="oracle")

    _build_link_video_display(k)

    # if (link := k.unpacked_notes.get("link", "")) != "":
    #     with st.expander("Playthroughs", expanded=True, icon=ST_ICONS["video"]):
    #         st.write("Check out videos where people explain and play this kingdom!")
    #         avail_links = st.session_state.get("kingdom_links", {})
    #         tabs = st.tabs([k.split("_")[0].capitalize() for k in avail_links.keys()])
    #         for tab, (col, link_id) in zip(tabs, avail_links.items()):
    #             with tab:
    #                 if link_id == "":
    #                     continue
    #                 link = f"https://www.youtube.com/watch?v={link_id}"
    #                 _, container, _ = st.columns([20, 60, 20])
    #                 with container:
    #                     with st.container(border=True):
    #                         st.video(link)
