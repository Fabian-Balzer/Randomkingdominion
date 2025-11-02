import pandas as pd
import streamlit as st

from ....utils import filter_combo_or_inter_df_for_csos
from ...constants import ST_ICONS, get_cached_combo_df, get_cached_inter_df
from .. import st_display_combo_df, st_display_inter_df


def st_build_combo_and_inter_display(csos: list[str]):

    interactions = filter_combo_or_inter_df_for_csos(
        get_cached_inter_df(), csos, require_all=True
    )
    if len(interactions) > 0:
        st.write("#### Special Interactions (rules-wise)")
        st_display_inter_df(interactions)
    else:
        st.info(
            "No special rules interactions found [which doesn't necessarily mean there are none, let me know about any you find!]."
        )
    cols = st.columns([0.7, 0.3])
    cols[1].page_link(
        "streamlit_pages/interactions.py",
        label="More about interactions",
        icon=ST_ICONS["interactions"],
        use_container_width=True,
        help="Visit the page that contains more information on the available interactions in the database.",
    )
    combos = filter_combo_or_inter_df_for_csos(
        get_cached_combo_df(), csos, require_all=True
    )
    with st.expander(
        "🎊Special pairwise combos, synergies, rushes, or counters in this kingdom (WARNING: Spoilers)",
        expanded=False,
    ):
        if len(combos) > 0:
            st_display_combo_df(combos)
        else:
            st.info("No combos/synergies found for this kingdom")
    cols = st.columns([0.7, 0.3])
    cols[1].page_link(
        "streamlit_pages/combos.py",
        label="More about synergies",
        icon="🎊",
        use_container_width=True,
        help="Visit the page that contains more information on the available combos in the database.",
    )
