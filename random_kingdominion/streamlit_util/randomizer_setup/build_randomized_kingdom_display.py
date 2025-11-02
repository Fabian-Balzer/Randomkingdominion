import streamlit as st

from ...kingdom import Kingdom
from ..common_widgets import (
    st_build_full_kingdom_display,
    st_build_kingdom_sidebar_display,
)
from .randomizer_util import load_config
from .reroll_callbacks import reroll_cso, reroll_selected_csos


def _get_invalidity_issues_text(k: Kingdom) -> str:
    warn_text = k.notes
    if not k.is_valid:
        warn_text += "\nThis kingdom is invalid for the following reasons:\n- "
        warn_text += "\n- ".join(
            [f"{r.name}: {r.get_description()}" for r in k.invalidity_reasons]
        )
    return warn_text


def _build_incomplete_randomization_warning(k: Kingdom):
    """Build a warning if the current kingdom in the randomizer is incomplete."""
    if k.is_empty:
        st.warning(
            "**You have managed to randomize an empty kingdom! Please adjust the randomization options to allow for a valid kingdom.**"
        )
    elif not k.is_valid:
        amount_wrong = len(k.invalidity_reasons)
        pl_suffix = "s" if amount_wrong > 1 else ""
        expander_label = f"Randomization failed ({amount_wrong} issue{pl_suffix})"
        with st.expander(expander_label, expanded=True):
            rerolled = load_config().get("General", "rerolled_csos", fallback=[])
            rr_str = ""
            if len(rerolled) > 0:
                rr_str = ", ".join(rerolled)
                rr_str = (
                    f"\\\nYou might also have rerolled too often:\\\n**{rr_str}**\n\n"
                )
            pretext = f"**The Randomization was only partially successful.**\\\nMaybe the constraints were too strict.{rr_str}\\\nTry adjusting/loosening them below.\n\n"
            st.warning(pretext + _get_invalidity_issues_text(k))


@st.fragment
def st_build_current_randomized_kingdom_display():
    k = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    with st.container(border=True):
        st.write("### Current Kingdom (scroll down for new randomization)")
        with st.sidebar:
            st_build_kingdom_sidebar_display(k, loc="randomizer")
        st_build_full_kingdom_display(k, reroll_selected_csos, reroll_cso)
        _build_incomplete_randomization_warning(k)
