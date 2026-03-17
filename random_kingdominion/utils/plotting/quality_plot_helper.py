from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

from ...constants import PATH_ASSETS, QUALITIES_AVAILABLE
from ..utils import get_quality_icon_fpath, get_version
from .constants import DOM_BEIGE, DOM_BLUE, XKCD_FONT
from .util import annotate_icon

if TYPE_CHECKING:
    from ...kingdom import Kingdom


def annotate_buy_icon(
    ax: Axes,
    buy_type: Literal["yes", "maybe", "no"],
    pos_angle=0.8 * np.pi,
):
    fpath = PATH_ASSETS.joinpath(f"icons/qualities/buys_icon_{buy_type}.png")
    annotate_icon(fpath, ax, pos_angle, 1, 0.25, 240)


def calculate_quality_angles(num_keys) -> list[float]:
    """Calculates the angles for the given quality keys."""
    # The plot is circular, so we need to "complete the loop" and append the start value to the end.
    angles = np.linspace(0, 2 * np.pi, num_keys, endpoint=False).tolist()
    angles += angles[:1]
    return angles


def set_up_ax_for_quality_plot(
    keys: list[str], ax: Axes | None = None, max_val: int = 4, add_pics: bool = True
) -> tuple[Figure, Axes]:
    """Sets up the given Axes for a quality plot."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    else:
        fig: Figure = ax.get_figure()  # type: ignore

    angles = calculate_quality_angles(len(keys))

    # Set radial ticks and labels
    ax.grid(color="gray", linestyle="--", linewidth=1)
    yticks = np.linspace(0, 1, max_val + 1)
    ax.set_yticks(yticks)
    for spine in ax.spines.values():
        spine.set_linewidth(2)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_facecolor(DOM_BEIGE)
    ax.set_ylim(0, 1.049)
    fig.set_facecolor("none")
    if not add_pics:
        return fig, ax

    fontprops = {
        "fontproperties": XKCD_FONT,
        "color": "black",
        "size": 18,
        "fontweight": "bold",
    }
    for angle, label in zip(angles[:-1], keys):
        icon_path = get_quality_icon_fpath(label)
        icon = Image.open(icon_path)
        im_size = 100
        icon = np.array(icon.resize((im_size, im_size), resample=Image.LANCZOS))  # type: ignore
        ab = AnnotationBbox(
            OffsetImage(icon, zoom=0.4), (angle, 1), frameon=False, xycoords="data"
        )
        ax.add_artist(ab)
        rot = (
            np.degrees(angle)
            if angle < np.pi / 2 or angle > 3 * np.pi / 2
            else np.degrees(angle) - 180
        )
        va = "center"
        ha = "left" if angle < np.pi / 2 or angle > 3 * np.pi / 2 else "right"
        angle_offset = np.pi / 15 if ha == "left" else -np.pi / 15
        ax.text(
            angle + angle_offset,
            0.35,
            label.capitalize(),
            horizontalalignment=ha,
            verticalalignment=va,
            rotation_mode="anchor",
            rotation=rot,
            fontdict=fontprops,
        )

    return fig, ax


def _annotate_hexagon_icons(
    ax: Axes, angles: list[float], data: list[float], linecolor: str
) -> None:
    """Annotates hexagon icons for non-zero qualities."""
    mask = np.array([d >= 0.025 for d in data])
    ax.scatter(
        np.array(angles)[mask],
        np.array(data)[mask],
        color=linecolor,
        s=100,
        marker="H",
        fc="none",
        lw=3,
        alpha=0.8,
    )


def _annotate_star_icons(ax: Axes, angles: list[float], data: list[float]) -> None:
    """Annotates star icons for luck- or limit-based qualities."""
    mask = np.array([d == 0.125 for d in data])
    if not any(mask):
        return
    ax.scatter(
        np.array(angles)[mask],
        np.array(data)[mask],
        color="orange",
        s=150,
        marker="*",
        fc="none",
        lw=1.5,
        alpha=0.9,
    )


def plot_quality_polygon(
    ax: Axes,
    values: list[float],
    max_val: int = 4,
    linecolor: str = DOM_BLUE,
) -> None:
    """Plots the polygon on the given Axes."""
    normalized_data = [value / max_val for value in values]
    normalized_data = [
        d if d != 0 else 0.02 for d in normalized_data
    ]  # Avoid zero values
    angles = calculate_quality_angles(len(normalized_data))
    # The plot is circular, so we need to "complete the loop" and append the start value to the end. This has already been done for angles.
    normalized_data += normalized_data[:1]
    ax.fill(angles, normalized_data, color=linecolor, alpha=0.25)
    ax.plot(angles, normalized_data, color=linecolor, linewidth=3, alpha=0.8)
    _annotate_hexagon_icons(ax, angles, normalized_data, linecolor)
    _annotate_star_icons(ax, angles, normalized_data)


def plot_kingdom_qualities(
    data: dict[str, float],
    ax: Axes | None = None,
    max_val: int = 4,
    add_pics: bool = True,
    skip_interactivity: bool = True,
    buy_str: Literal["yes", "maybe", "no"] | None = None,
    linecolor: str = DOM_BLUE,
) -> Figure:
    """
    Plots an N-sided polygon (radar chart) where each side represents a fraction of the maximum value from the input dictionary.

    Parameters
    ----------
    data : dict[str, float]
        A dictionary with the quality names as keys and the corresponding values as values.
    ax : Axes | None, optional
        The Matplotlib axes to plot the figure on. If None, a new figure is created. Default is None.
    max_val : int, optional
        The maximum value for the qualities. Default is 4.
    add_pics : bool, optional
        Whether to add icons (for draw, village, etc.) to the plot. Default is True.
    skip_interactivity : bool, optional
        Whether to skip the "interactivity" quality when plotting. Default is True.
    buy_str : Literal["yes", "maybe", "no"] | None, optional
        A string indicating the buy availability to annotate on the plot. Default is None.
    linecolor : str, optional
        The color of the polygon line. Default is DOM_BLUE.

    The function normalizes the values in the dictionary to fractions of the maximum value, calculates the angles for the polygon vertices,
    and plots the resulting figure using Matplotlib.

    Returns:

    - fig (Figure): The resulting Matplotlib figure.

    Example usage:
    >>> data = {'A': 0.6, 'B': 0.8, 'C': 0.5, 'D': 0.9, 'E': 0.7}
    >>> plot_normalized_polygon(data)
    """
    if skip_interactivity:
        data = {key: value for key, value in data.items() if key != "interactivity"}
    data = {
        k: data[k] for k in QUALITIES_AVAILABLE if k in data
    }  # Ensure consistent order
    fig, ax = set_up_ax_for_quality_plot(
        list(data.keys()), ax=ax, max_val=max_val, add_pics=add_pics
    )
    if buy_str is not None:
        annotate_buy_icon(ax, buy_str)
    plot_quality_polygon(ax, list(data.values()), max_val, linecolor=linecolor)

    return fig


def add_kingdom_info_to_plot(ax: Axes, kingdom: "Kingdom"):
    """Add information about the kingdom to the plot, just outside the boundaries."""

    bbox = dict(
        facecolor="white",
        alpha=0.5,
        edgecolor="k",
        boxstyle="round,pad=0.2",
    )
    offset = 0
    for qual in kingdom.total_qualities:
        if qual == "interactivity":
            continue
        ax.text(
            0,
            -0.05 - offset,
            kingdom.get_qualtype_string(qual),
            transform=ax.transAxes,
            fontdict=dict(font="monospace"),
            va="top",
            bbox=bbox,
        )
        offset += 0.05
    ax.text(
        0,
        -0.05 - offset,
        kingdom.get_component_string(),
        transform=ax.transAxes,
        va="top",
        fontdict=dict(font="monospace"),
        bbox=bbox,
    )
    watermark = (
        "Generated with randomkingdominion.streamlit.app/oracle, v. " + get_version()
    )
    ax.text(
        0,
        -0.05 - offset - 0.05,
        watermark,
        transform=ax.transAxes,
        va="top",
        fontdict=dict(font="monospace", size=7),
        bbox=bbox | dict(facecolor="lightgray", edgecolor="none"),
    )

    card_text = kingdom.card_and_landscape_text
    ax.text(
        1.1,
        0.95,
        card_text,
        va="top",
        ha="left",
        transform=ax.transAxes,
        fontdict=dict(font="monospace"),
        bbox=bbox,
    )
    expansion_text = "Expansions:\n " + "\n ".join(
        [c.title().replace("_", " ") for c in sorted(kingdom.expansions)]
    )
    ax.text(
        1.1,
        0.9 - card_text.count("\n") * 0.05,
        expansion_text,
        va="top",
        ha="left",
        transform=ax.transAxes,
        fontdict=dict(font="monospace"),
        bbox=bbox,
    )
    title = "Kingdom Overview"
    if kingdom.name != "":
        title += f": {kingdom.name}"
    ax.set_title(title, y=1.01)
