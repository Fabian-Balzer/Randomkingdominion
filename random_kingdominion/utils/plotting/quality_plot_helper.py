from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image

from ...constants import PATH_ASSETS
from ..utils import get_quality_icon_fpath, get_version
from .constants import DOM_BEIGE, DOM_BLUE, XKCD_FONT
from .image_handling import crop_img_by_percentage, load_cso_img_by_key
from .util import annotate_icon

if TYPE_CHECKING:
    from ...kingdom import Kingdom

def _annotate_buy_icon(ax: Axes, buy_type: Literal["Buys", "Buys*", "Nothing"], position: tuple[float, float]):
    fname_dict = {
        "Buys": "yes",
        "Buys*": "maybe",
        "Nothing": "no",}
    fpath = PATH_ASSETS.joinpath(f"icons/qualities/buys_icon_{fname_dict[buy_type]}.png")
    annotate_icon(fpath, ax, 0.8*np.pi, 1, 0.25, 240)
    # icon_dict = {
    #     "Buys": {"cso": "market", "color": "darkgreen", "text": "Yes!"},
    #     "Buys*": {"cso": "city", "color": "sandybrown", "text": "Finicky."},
    #     "Nothing": {"cso": "bandit", "color": "darkred", "text": "No :/"},
    # }
    # icon_to_use = icon_dict[buy_type]
    # img = load_cso_img_by_key(icon_to_use["cso"])
    # crop_rect = [0.15, 0.11, 0.85, 0.51]
    # zoom = 0.17
    # icon = crop_img_by_percentage(img, crop_rect)
    # ab = AnnotationBbox(
    #     OffsetImage(icon, zoom=zoom, transform=ax.transAxes),  # type: ignore
    #     (0.8*np.pi, 0.8),
    #     frameon=True,
    #     box_alignment=(0.5, 1),
    #     pad=0.2,
    #     bboxprops=dict(facecolor="k", edgecolor="k", linewidth=1),
    #     transform=ax.transAxes
    # )
    # fdict = {"size": 10, "color": "white", "weight": "bold", "fontproperties": XKCD_FONT}
    # ax.text(position[0], position[1]+0.035, "Buys?", bbox=dict(facecolor=icon_to_use["color"]), ha="center", transform=ax.transAxes, fontdict=fdict)
    # ax.text(position[0], position[1]-0.125, icon_to_use["text"], bbox=dict(facecolor=icon_to_use["color"]), ha="center", transform=ax.transAxes, fontdict=fdict)
    # ax.add_artist(ab)


def plot_kingdom_qualities(
    data: dict[str, float] | dict[str, int],
    ax: Axes | None = None,
    max_val: int = 4,
    add_pics: bool = True,
    skip_interactivity: bool = True,
    buy_str: Literal["Buys", "Buys*", "Nothing"] | None = None
) -> Figure:
    """
    Plots an N-sided polygon (radar chart) where each side represents a fraction of the maximum value from the input dictionary.

    Parameters
    ----------
    data : dict[str, float] | dict[str, int]
        A dictionary with the quality names as keys and the corresponding values as values.
    ax : Axes | None, optional
        The Matplotlib axes to plot the figure on. If None, a new figure is created. Default is None.
    max_val : int, optional
        The maximum value for the qualities. Default is 4.
    add_pics : bool, optional
        Whether to add icons (for draw, village, etc.) to the plot. Default is True.
    skip_interactivity : bool, optional
        Whether to skip the "interactivity" quality when plotting. Default is True.

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
    normalized_data = [value / max_val for value in data.values()]

    # Number of variables (sides of the polygon)
    num_vars = len(data)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The plot is circular, so we need to "complete the loop" and append the start value to the end.
    normalized_data += normalized_data[:1]
    angles += angles[:1]
    # Create the figure
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    else:
        fig: Figure = ax.get_figure()  # type: ignore

    fontprops = {"fontproperties": XKCD_FONT, "color": "black", "size": 18}
    ax.fill(angles, normalized_data, color=DOM_BLUE, alpha=0.25)
    ax.plot(angles, normalized_data, color=DOM_BLUE, linewidth=2, alpha=0.9)
    ax.set_facecolor(DOM_BEIGE)

    # Set radial ticks and labels
    ax.grid(color="gray", linestyle="--", linewidth=1)
    yticks = np.linspace(0, 1, max_val + 1)
    ax.set_yticks(yticks)
    for spine in ax.spines.values():
        spine.set_linewidth(2)  # Set the desired thickness

    # Labels for each point
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_xticks(angles[:-1])

    if buy_str is not None:
        _annotate_buy_icon(ax, buy_str, (0.177, 0.725))

    if not add_pics:
        return fig
    # Add icons to the plot
    for angle, label in zip(angles[:-1], data.keys()):
        # Load and resize icon
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
        ax.text(
            angle,
            0.35,
            label.capitalize(),
            horizontalalignment=ha,
            verticalalignment=va,
            rotation_mode="anchor",
            rotation=rot,
            fontdict=fontprops,
            # bbox=dict(
            #     facecolor="none",
            #     alpha=0.5,
            #     edgecolor="none",
            #     boxstyle="round,pad=0.2",
            # ),
        )
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
