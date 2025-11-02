import streamlit as st

from ...constants import ALL_CACHED_CSOS, LIKE_BAN_OPTIONS
from ..randomizer_util import load_config


def _build_like_ban_option(option: str):
    config = load_config()
    default = config.getlist("General", f"{option.lower()}_csos")
    default_transl = [ALL_CACHED_CSOS.loc[name]["Name"] for name in default]
    st.multiselect(
        f"{option} CSOs",
        ALL_CACHED_CSOS[
            ALL_CACHED_CSOS["IsInSupply"] | ALL_CACHED_CSOS["IsExtendedLandscape"]
        ]["Name"].tolist(),
        default=default_transl,
        key=f"{option.lower()}_csos",
        placeholder=f"Select the CSOs you want to have {option.lower()} during randomization.",
        help=LIKE_BAN_OPTIONS[option],
    )


def _build_like_ban_extra_wid(option: str):
    config = load_config()
    if option == "Banned":
        st.write("These CSOs will never appear in any randomized kingdom.")
    elif option == "Required":
        st.write(
            "These CSOs will always appear in any randomized kingdom, unless you really only want to include cards of your selected expansions."
        )
        default = config.getboolean(
            "General", "allow_required_csos_of_other_exps", fallback=False
        )
        st.checkbox(
            "Allow required CSOs of unselected expansions",
            value=default,
            key="allow_required_csos_of_other_exps",
            help="When enabled, required CSOs can be from any expansion, not just the selected ones. Otherwise, only CSOs from the selected expansions are considered.",
        )
    elif option == "Disliked":
        st.write(
            "These CSOs will have a lower probability of showing up. You can select the weight factor (relative to all other CSOs) here."
        )
        default = config.getfloat("General", "dislike_factor", fallback=0.5)
        st.number_input(
            label="Weight",
            value=default,
            min_value=0.1,
            max_value=0.9,
            step=0.1,
            key="dislike_factor",
            format="%.1f",
        )
    elif option == "Liked":
        default = config.getfloat("General", "like_factor", fallback=2.0)
        st.write(
            "These CSOs will have a higher probability of showing up. You can select the weight factor here. Will have no effect if the card is banned or disliked."
        )
        st.number_input(
            "Weight",
            value=default,
            min_value=1.5,
            max_value=10.0,
            step=0.5,
            key="like_factor",
            format="%.1f",
        )


@st.fragment
def build_like_ban_selection():
    st.write(
        "Select the cards you like, dislike, ban or want to force during randomization."
    )
    for option in LIKE_BAN_OPTIONS:
        with st.container(border=True):
            cols = st.columns(2)
            with cols[0]:
                _build_like_ban_option(option)
            with cols[1]:
                _build_like_ban_extra_wid(option)
