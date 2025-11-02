from typing import Literal

import streamlit as st

from ....kingdom import Kingdom
from ....utils import (
    filter_combo_or_inter_df_for_csos,
    get_video_title,
    plot_kingdom_qualities,
)
from ...constants import ST_ICONS, get_cached_combo_df, get_cached_inter_df
from .. import st_display_combo_md, st_display_inter_md


def _display_more_info_tt(text: str):
    st.markdown(
        f"""<div style='text-align:center'><span class="tooltip">More info ℹ️<span class="tooltiptext">
    {text}
  </span></span>
</div>
""",
        unsafe_allow_html=True,
    )


def _build_kingdom_csv_display(
    k: Kingdom, loc: Literal["randomizer", "oracle"] = "oracle"
):
    code = k.get_dombot_csv_string()
    if k.name != "":
        st.markdown(f"#### {k.name}")
    st.code(code, wrap_lines=loc == "randomizer")
    text = "You can copy this to your clipboard and paste it into the interface of your preferred digital Dominion client.\\\nShould work both for [Dominion Online](https://dominion.games/) and the [TGG implementation](https://store.steampowered.com/app/1131620/Dominion/)."
    _display_more_info_tt(text)


def _build_kingdom_miniplot_display(k: Kingdom):
    """Display a small plot of the kingdom's card qualities."""
    fig = plot_kingdom_qualities(k.total_qualities, buy_str=k.buy_availability)
    if k.name != "":
        fig.axes[0].set_title(
            get_video_title(k),
            fontsize=14,
            pad=10,
        )
    fig.set_facecolor("none")
    st.pyplot(fig)
    text = "The kingdom quality plot gives you a quick overview of the distribution of CSO qualities in this kingdom.\nHover over the CSOs in the card view to see which qualities they contribute.\nFor more information about kingdom qualities, visit the About page."
    _display_more_info_tt(text)


def _build_kingdom_interactions_display(k: Kingdom):
    inter = filter_combo_or_inter_df_for_csos(
        get_cached_inter_df(), k.full_kingdom_df.index, True
    )
    label = "Interactions" if len(inter) != 1 else "Interaction"
    icon = ST_ICONS["interactions"]
    with st.expander(f"{len(inter)} Rules {label}", expanded=False, icon=icon):
        if len(inter) == 0:
            st.info("No interactions available for this kingdom.")
        else:
            st_display_inter_md(inter, include_images=False)
        text = f"These quirky, sometimes not-obvious rules interactions might come up when playing this kingdom. For more information visit the {icon} CSO interactions page."
        _display_more_info_tt(text)


def _build_kingdom_combos_display(k: Kingdom):
    combos = filter_combo_or_inter_df_for_csos(
        get_cached_combo_df(), k.full_kingdom_df.index, True
    )
    icon = ST_ICONS["combos"]
    with st.expander(f"??? (Spoilers!)", expanded=False, icon=icon):
        st.warning("Please don't use this to analyze kingdoms for competitive play.")
        if len(combos) == 0:
            st.info("No synergies/combos/counters available for this kingdom.")
        else:
            st_display_combo_md(combos, include_images=False)
        text = f"These synergies, combos or counters might be present in this kingdom. For more information visit the {icon} CSO Combos page."
        _display_more_info_tt(text)


@st.fragment
def st_build_kingdom_sidebar_display(
    k: Kingdom, loc: Literal["randomizer", "oracle"] = "oracle"
):
    with st.container(gap=None):
        with st.expander("Descriptive string to copy", expanded=False, icon="📋"):
            _build_kingdom_csv_display(k, loc=loc)
        st.container(height=2, border=False)
        with st.expander("Kingdom plot", expanded=loc == "oracle", icon="🧭"):
            _build_kingdom_miniplot_display(k)
        st.container(height=2, border=False)
        _build_kingdom_interactions_display(k)
        st.container(height=2, border=False)
        _build_kingdom_combos_display(k)
