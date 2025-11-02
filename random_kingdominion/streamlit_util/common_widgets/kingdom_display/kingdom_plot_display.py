import streamlit as st

from ....kingdom import Kingdom
from ...image_util import st_display_kingdom_plot


def st_build_full_kingdom_plot_display(k: Kingdom):
    st_display_kingdom_plot(k, with_border=True)
    st.info(
        "*Hint: Hover over the images in the kingdom image display in the standard view to directly see the individual cards' qualities.*"
    )
    with st.expander("Disclaimer", expanded=False, icon="⚠️"):
        st.warning(
            "Be aware that these plots are a very superficial view of the kingdom and do not take into account special card interactions. Check out the about page for more information on those."
        )
