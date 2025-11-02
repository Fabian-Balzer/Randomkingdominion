"""The container for the randomization options."""

import streamlit as st

from ...common_widgets import (
    st_build_kingdom_input_warning,
    st_build_kingdom_text_input,
)
from ...constants import ST_ICONS
from ..randomizer_util import load_config
from .expansion_select import build_expansion_selection
from .landscape_options import build_landscape_option_selection
from .likes_and_bans import build_like_ban_selection
from .mechanics import build_mechanics_options
from .quality_options import build_quality_selection


@st.fragment
def build_partial_kingdom_input():
    config = load_config()
    initial_val = config.get("General", "partial_kingdom_input", fallback="")
    expanded = initial_val != ""
    with st.expander("Starting from...", expanded=expanded, icon=ST_ICONS["changelog"]):
        k = st_build_kingdom_text_input(
            key="partial_kingdom_input",
            initial_value=initial_val,
            description_text="Enter a (partial) kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN' to start the randomization from.\\\nTakes precedence over the other options (e.g. will force cards even if they are banned or not in the selected expansions).",
        )
        s = k.get_dombot_csv_string(ignore_col_shelt=True)
        st_build_kingdom_input_warning(k, ref_to_randomizer=False)
        if s == "":
            st.write("Starting from an empty kingdom.")
        else:
            st.info(
                f"Starting from: {s}.\\\nNote that Colony, Shelter and also Ruins usage listed here will be ignored."
            )


def _build_randomization_sidebar():
    """Build the sidebar for the randomization options."""

    st.sidebar.write("### Randomizer Option Overview")
    # The rest has to be done inside the fragments for the sidebar to be updated correctly


def st_build_full_randomization_options():
    """Build the randomization options."""
    _build_randomization_sidebar()

    with st.container(border=True):
        st.write("### Randomization Options")
        build_partial_kingdom_input()
        TABS = st.tabs(
            [
                f"{ST_ICONS['expansions']}Expansions",
                f"{ST_ICONS['mechanics']}Mechanics",
                f"{ST_ICONS['landscapes']}Landscapes",
                f"{ST_ICONS['cso_qualities']}Engine Qualities",
                f"{ST_ICONS['bans']}Likes/Bans",
            ]
        )
    with TABS[0]:
        build_expansion_selection()
    with TABS[1]:
        build_mechanics_options()
    with TABS[2]:
        build_landscape_option_selection()
    with TABS[3]:
        build_quality_selection()
    with TABS[4]:
        build_like_ban_selection()
