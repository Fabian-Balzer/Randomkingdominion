from typing import Literal

import streamlit as st
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ...constants import QUALITIES_AVAILABLE
from ...kingdom import Kingdom
from ...utils import (
    annotate_buy_icon,
    get_kingdom_quality_fig,
    plot_quality_polygon,
    set_up_ax_for_quality_plot,
)
from ...utils.plotting import DOM_BLUE


def st_display_full_kingdom_fig(k: Kingdom, with_border=False):
    """Display a kingdom's engine qualities in a polar plot using streamlit."""
    # fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig = get_kingdom_quality_fig(k, add_buy_str=True)
    # plot_normalized_polygon(k.total_qualities, ax=ax)
    # add_kingdom_info_to_plot(ax, k)
    # if with_border:
    #     with st.columns([0.2, 0.5, 0.2])[1]:
    #         with st.container(border=True):
    #             placeholder.pyplot(fig, width="stretch")
    #             return
    st.pyplot(fig, True, width="content")


# @st.cache_resource  # Doesn't work because Figure is consumed on display
def _st_set_up_kingdom_quality_plot(
    qual_keys: list[str],
) -> tuple[Figure, Axes]:
    """Set up and return a kingdom quality plot figure for the given kingdom."""
    return set_up_ax_for_quality_plot(keys=qual_keys)


def st_plot_kingdom_qualities(
    data: dict[str, float] | dict[str, int],
    ax: Axes | None = None,
    buy_str: Literal["yes", "maybe", "no"] | None = None,
    linecolor: str = DOM_BLUE,
) -> Figure:
    """
    Plots the kingdom qualities in a radar/spider plot.
    """

    data = {
        k: max(data[k], 0)
        for k in QUALITIES_AVAILABLE
        if k in data and k != "interactivity"
    }  # Ensure consistent order
    if ax is not None:
        fig: Figure = ax.get_figure()  # type: ignore
    else:
        fig, ax = _st_set_up_kingdom_quality_plot(list(data.keys()))

    if buy_str is not None:
        annotate_buy_icon(ax, buy_str)
    plot_quality_polygon(ax, list(data.values()), linecolor=linecolor)

    return fig
