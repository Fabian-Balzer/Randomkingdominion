import streamlit as st

from ...kingdom import Kingdom
from ..common_widgets import st_build_kingdom_input_warning, st_build_kingdom_text_input
from ..constants import ST_ICONS


def _navigate_to_randomizer(k: Kingdom):
    """Navigate to the randomizer page with the current kingdom."""
    st.session_state["partial_kingdom_input"] = k.get_dombot_csv_string()
    st.switch_page("streamlit_pages/randomizer.py")


def _build_randomizer_button(k: Kingdom):
    if st.button(
        "To Randomizer",
        icon=ST_ICONS["randomizer"],
        help="Start randomization from this selection",
        width="content",
        disabled=k.is_empty,
    ):
        _navigate_to_randomizer(k)


def st_build_oracle_kingdom_input_display() -> Kingdom:
    flex = st.container(horizontal=True, horizontal_alignment="left")
    with flex:
        k = st_build_kingdom_text_input("oracle_kingdom_input")
        _build_randomizer_button(k)
    st_build_kingdom_input_warning(k, ref_to_randomizer=True)
    return k
