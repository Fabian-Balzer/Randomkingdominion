import streamlit as st

from ..common_widgets import st_display_combo_df, st_display_inter_df
from ..constants import get_cached_combo_df, get_cached_inter_df
from .constants import PAIR_TYPE
from .df_filtering import st_build_combo_inter_filters
from .util import get_name


def st_build_combo_or_inter_page(pair_type: PAIR_TYPE):
    """Displays the combos or interactions page."""
    name = get_name(pair_type)
    if pair_type == "inter":
        df = get_cached_inter_df()
    else:
        df = get_cached_combo_df()
    num_initial = len(df)
    df = st_build_combo_inter_filters(df, pair_type)
    filt_indicator = st.session_state.get(f"{pair_type}_filter_str", "")
    st.write(
        f"#### {filt_indicator}Filtering for {len(df)}/{num_initial} available pairwise {name}s of Card-Shaped Objects (CSOs)."
    )
    if pair_type == "inter":
        st_display_inter_df(df)
    else:
        st_display_combo_df(df)
    st.info("Hint: You can also sort by expansion in the expansion column.")
    if pair_type == "inter":
        st.info(
            "Note that the [Kingdom Oracle](/oracle) and the [Randomizer](/randomizer) will also display all relevant interactions for any given kingdom."
        )
