import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg

from ..kingdom import Kingdom
from ..utils import add_kingdom_info_to_plot, plot_normalized_polygon


def display_kingdom_plot(k: Kingdom):
    """Display a kingdom's engine qualities in a polar plot using streamlit."""
    with RendererAgg.lock:
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        plot_normalized_polygon(k.total_qualities, ax=ax)
        add_kingdom_info_to_plot(ax, k)

        st.pyplot(fig, use_container_width=True)
