import streamlit as st
from ...constants import PATH_ASSETS, QUALITIES_AVAILABLE
from ...utils import get_quality_icon_fpath
from ..randomizer_util import load_config


def _toggle_all_qualities(value: bool, value_to_set_to: int | None = None):
    for quality in QUALITIES_AVAILABLE:
        st.session_state[f"disable {quality} selection"] = value
        if value_to_set_to is not None:
            st.session_state[f"{quality} count"] = value_to_set_to


def _build_quality_row(quality: str):
    config = load_config()
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.15, 0.55, 0.3])
        with col1:
            st.write(quality.capitalize())
            fpath = "./static/" + str(
                get_quality_icon_fpath(quality).relative_to(PATH_ASSETS)
            )
            st.image(fpath, width=60)
        with col3:
            default = config.getboolean(
                "Qualities", f"forbid_{quality}", fallback=False
            )
            st.checkbox(
                f"No {quality.capitalize()} quality",
                value=default,
                key=f"disable {quality} selection",
                help=f"If enabled, the randomizer will exclude all cards with any {quality} quality.",
            )
        with col2:
            default = config.getint("Qualities", f"requested_{quality}", fallback=0)
            st.slider(
                f"Minimum {quality} quality",
                0,
                3,
                value=default,
                key=f"{quality} count",
                disabled=st.session_state[f"disable {quality} selection"],
                help=f"Select the minimum amount of {quality} quality you desire to have in the kingdom.",
            )


@st.fragment
def build_quality_selection():
    st.write(
        "Select the minimum amount of a quality you desire to have in the kingdom, or exclude some completely."
    )
    cols = st.columns(3)
    with cols[0]:
        st.button(
            "Reset",
            on_click=lambda: _toggle_all_qualities(False, 0),
            use_container_width=True,
            help="Reset everything such that the randomization is not influenced.",
        )
    with cols[1]:
        st.button(
            "Enable all",
            on_click=lambda: _toggle_all_qualities(False, 2),
            use_container_width=True,
            help="Enable all qualities to be required for the randomized kingdom. This usually results in a kingdom suitable for engines.",
        )
    with cols[2]:
        st.button(
            "Exclude all",
            on_click=lambda: _toggle_all_qualities(True),
            use_container_width=True,
            help="Have the randomizer consider only CSOs that do not have any qualities.",
        )
    for quality in QUALITIES_AVAILABLE:
        _build_quality_row(quality)
