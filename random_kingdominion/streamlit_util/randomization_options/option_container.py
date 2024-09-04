"""The container for the randomization options."""

import streamlit as st

from ..kingdom_readout import build_kingdom_text_input
from .expansion_select import build_expansion_selection
from .landscape_options import build_landscape_option_selection
from .likes_and_bans import build_like_ban_selection
from .mechanics import build_mechanics_options
from .quality_options import build_quality_selection


def build_randomization_options():
    """Build the randomization options."""

    with st.container(border=True):
        st.write("### Randomization Options")
        TABS = st.tabs(
            ["Expansions", "Mechanics", "Landscapes", "Engine Qualities", "Likes/Bans"]
        )
        build_kingdom_text_input(
            key="partial_random_kingdom",
            description_text="Enter a (partial) kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN' to start the randomization from.\\\nTakes precedence over the other options (e.g. will force [No] Shelters and cards even if they are banned or not in the selected expansions).",
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
