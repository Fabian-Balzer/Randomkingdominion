import matplotlib.pyplot as plt
import streamlit as st

from ..kingdom import Kingdom
from ..utils import (add_kingdom_info_to_plot, get_kingdom_quality_fig,
                     plot_kingdom_qualities)


def display_kingdom_plot(k: Kingdom, with_border=False):
    """Display a kingdom's engine qualities in a polar plot using streamlit."""

    # fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig = get_kingdom_quality_fig(k)
    # plot_normalized_polygon(k.total_qualities, ax=ax)
    # add_kingdom_info_to_plot(ax, k)
    if with_border:
        with st.columns([0.2, 0.5, 0.2])[1]:
            with st.container(border=True):
                st.pyplot(fig, use_container_width=True)
                return
    st.pyplot(fig, use_container_width=True)
