from io import BytesIO
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image

from ...constants import PATH_ASSETS
from ..utils import get_version
from .constants import DOM_BEIGE, XKCD_FONT
from .quality_plot_helper import plot_kingdom_qualities
from .util import annotate_single_expansion_icon, get_video_title

if TYPE_CHECKING:
    from ...kingdom import Kingdom


def _annotate_kingdom_cards_landscapes(
    k: "Kingdom", ax: Axes, x0=0.5, y0=0.5, shorten=True, **kwargs
):
    card_text = k.card_and_landscape_text.replace("Cards", "CARDS").replace(
        "Landscapes", "LANDSCAPES"
    )
    if shorten:
        card_lines = card_text.split("\n")
        card_lines = [
            line[:24] + "..." if len(line) > 27 else line for line in card_lines
        ]
        card_text = "\n".join(card_lines)
    fontsize = 14 if card_text.count("\n") > 15 else 15.2
    ax.text(
        x0,
        y0,
        card_text,
        fontsize=fontsize,
        **kwargs,
    )


def _annotate_qualities(ax: Axes, k: "Kingdom", text_args: dict):
    yoffset = 0.28
    offset_dist = 0.065
    for i, qual in enumerate(k.total_qualities):
        if qual == "interactivity":
            continue
        xoffset = 0 if i % 2 == 0 else 0.5
        ax.text(
            xoffset,
            yoffset,
            k.get_qualtype_string(qual, 54),
            fontsize=12,
            **text_args,
        )
        if i % 2 != 0:
            yoffset -= offset_dist
    ax.text(
        0,
        yoffset,
        k.get_component_string(108),
        fontsize=12,
        **text_args,
    )
    yoffset -= offset_dist
    watermark = (
        "Generated with randomkingdominion.streamlit.app/oracle, v. " + get_version()
    )
    ax.text(
        0,
        yoffset,
        watermark,
        fontsize=8,
    )


def _annotate_expansion_icons(ax: Axes, k: "Kingdom"):
    num_expansions = len(k.expansions)
    zoom = 0.66 if num_expansions <= 4 else 0.33
    yoff = 0.16 if num_expansions <= 4 else 0.1
    xoff = 0.86 if num_expansions <= 4 else 0.84
    num_rows = num_expansions if num_expansions <= 4 else num_expansions // 2
    for i, expansion in enumerate(k.expansions):
        x = xoff + 0.1 * (i // num_rows)
        y = 1 - yoff * (i % num_rows)
        annotate_single_expansion_icon(expansion, ax, x, y, zoom)


def _fig_to_img(fig):
    """Convert a Matplotlib figure to a numpy array image."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.2, dpi=200)
    buf.seek(0)
    img = Image.open(buf)
    arr = np.asarray(img)
    buf.close()
    return arr


def get_kingdom_quality_fig(k: "Kingdom", save=False, add_buy_str=True) -> Figure:
    fig = plot_kingdom_qualities(
        k.total_qualities, buy_str=k.buy_availability if add_buy_str else None
    )
    fig.set_size_inches(8.5, 6)
    fig.set_facecolor(DOM_BEIGE)
    ax = fig.gca()
    ax.set_position([0, 0.34, 0.52, 0.6])  # type: ignore
    ax2: Axes = fig.add_axes([0.03, 0.01, 1, 0.98], zorder=-1)  # type: ignore
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax2.set_frame_on(False)

    _text_args = dict(
        va="top",
        ha="left",
        fontdict={"fontproperties": XKCD_FONT, "color": "k"},
        bbox={
            "boxstyle": "round,pad=0.4",
            "facecolor": DOM_BEIGE,
            "linewidth": 2,
        },
    )

    _annotate_kingdom_cards_landscapes(k, ax2, 0.55, 1, **_text_args)  # type: ignore
    _annotate_qualities(ax2, k, _text_args)
    _annotate_expansion_icons(ax2, k)

    # If Divine Wind is in the kingdom, add an inset for the DW kingdom.
    if (dw_k := k.divine_wind_subkingdom) is not None:
        extra_fig = get_kingdom_quality_fig(dw_k, save=False, add_buy_str=add_buy_str)
        extra_fig.get_axes()[0].set_title("")
        extra_fig.suptitle(
            "Divine Wind Kingdom", y=1.1, fontsize=20, **_text_args | {"ha": "center"}
        )

        img = _fig_to_img(extra_fig)
        plt.close(extra_fig)
        inset_ax = fig.add_axes([1, 0.01, 0.8, 0.8], zorder=1)  # type: ignore
        inset_ax.xaxis.set_visible(False)
        inset_ax.yaxis.set_visible(False)
        inset_ax.set_frame_on(True)
        inset_ax.imshow(img)

    title = get_video_title(k)
    ax.set_title(
        title, **(_text_args | {"ha": "center"}), y=1.078, fontsize=15  # type: ignore
    )
    if save:
        fname = f'{k.name.replace(" ", "_")}_thumbnail.png'
        fpath = PATH_ASSETS.joinpath(f"other/youtube/{fname}")
        fig.savefig(str(fpath), pad_inches=0.2, bbox_inches="tight", dpi=300)
    return fig
