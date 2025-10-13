import textwrap
from typing import TYPE_CHECKING, Any, Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch

from ...constants import ALL_CSOS, PATH_ASSETS
from .constants import DOM_BEIGE, DOM_BLUE, XKCD_FONT
from .image_handling import crop_img_by_percentage, load_cso_img_by_key
from .util import (annotate_dominion_logo, annotate_icon, plot_gradient_image,
                   set_up_fig_and_ax_for_img)

if TYPE_CHECKING:
    from ...kingdom import Kingdom

def _annotate_title(ax: Axes, name: str):
    ax.text(0.5, 0.98, f"Openings for {name}", ha="center",
            va="top", fontsize=18, color="black", 
            bbox={"boxstyle": "round,pad=0.3", "facecolor": DOM_BEIGE},
            fontdict={"weight": "bold", "fontproperties": XKCD_FONT})

def _annotate_disclaimer_text(ax: Axes):
    disclaimer_text = "Disclaimer: These openings are of course just recommendations - maybe other variations might be better suited for your game plan!\nThe grades are a bit arbitrary, just fitting my personal vibe on a range from A to F, also in terms of speed compared to other kingdoms."
    ax.text(0.5, 0, disclaimer_text, ha="center", va="top", fontsize=12, color="black",
            fontdict={"fontproperties": XKCD_FONT},
            bbox={"boxstyle": "round,pad=0.2", "facecolor": DOM_BEIGE})
    
def _set_background_gradient(ax: Axes):
    gradient1 = np.linspace(120, 190, 500)
    gradient = np.vstack((gradient1, gradient1))
    plot_gradient_image(ax, extent=(0, 1, 0, 1), direction="horizontal", cmap="copper", gradient=gradient, alpha=0.7)

def _annotate_vertical_line(ax: Axes, x0: float, y1: float):
    line = Line2D([x0, x0], [0, y1+0.011], color=DOM_BLUE, linewidth=3, linestyle=":")
    ax.add_line(line)  # Using ax.plot would change axes limits


def _annotate_single_coin(ax: Axes, coin_type: str, ycoord: float, x_offset=0.):
    fpath = PATH_ASSETS.joinpath(f"icons/120px-Coin{coin_type}.png")
    annotate_icon(fpath, ax, x_offset, ycoord, 0.8, 30)

def _annotate_coin_icons(ax: Axes, open_type: str, y0: float):
    is_double_open = "|" in open_type
    box_x = -0.01
    box_y = y0 - 0.07
    xwidth = 0.09
    yheight = 0.079
    if is_double_open:
        box_y -= 0.08
        yheight *= 2
    rect = FancyBboxPatch(
        (box_x, box_y),
        xwidth,
        yheight,
        boxstyle="round,pad=0.001,rounding_size=0.01",
        edgecolor="black",
        lw=2,
        facecolor=DOM_BEIGE,
        clip_on=True,
    )
    ax.add_patch(rect)
    line = Line2D([box_x + xwidth/2*0.95, box_x + xwidth/2*1.15], [box_y, box_y + yheight], color='black', linewidth=2)
    ax.add_line(line)  # Using ax.plot would change axes limits
    
    # Actually annotate the coins
    if is_double_open:
        o1, o2 = open_type.split("|")
        c1, c2 = o1.split("/")
        _annotate_single_coin(ax, c1, y0)
        _annotate_single_coin(ax, c2, y0, 0.04)
        c1, c2 = o2.split("/")
        _annotate_single_coin(ax, c1, y0-0.07)
        _annotate_single_coin(ax, c2, y0-0.07, 0.04)
    else:
        c1, c2 = open_type.split("/")
        _annotate_single_coin(ax, c1, y0)
        _annotate_single_coin(ax, c2, y0, 0.04)

def _get_grade_color(grade: str):
    grades = "ABCEDF"
    sanitized_grade = grade.upper()[0]
    # Get the RdYlGn colormap
    cmap = plt.get_cmap('RdYlGn_r')
    colors = cmap(np.linspace(0, 1, len(grades)))
    color = colors[grades.index(sanitized_grade)]
    return color

def _annotate_grade(ax: Axes, grade: str, y0: float, num_openings: int):
    # - Annotate the grade in a circular patch
    grade_color = _get_grade_color(grade)
    fontsize = 25 * (4/(2+num_openings))
    ax.text(0.04, y0, grade, ha="center", va="center", fontsize=fontsize, color="black",
            fontdict={"weight": "bold", "fontproperties": XKCD_FONT},
            bbox={"boxstyle": "circle", "facecolor": grade_color, "alpha": 0.8})

def _annotate_cso_imgs(ax: Axes, x0: float, y0: float, csos: list[str], num_openings: int):
    csos = csos[:5]  # We cannot show more than 5 due to space constraints
    for i, cso_name in enumerate(csos):
        # Size and position depend on the number of openings because the
        # available space is influenced by the number of openings
        position = x0 + 0.3/num_openings * i, y0
        zoom = 1.5/(num_openings+3)

        cso = ALL_CSOS.loc[cso_name]
        img = load_cso_img_by_key(cso.name)  # type: ignore
        crop_rect = [0.15, 0.11, 0.85, 0.51]
        if cso["IsExtendedLandscape"]:  # type: ignore
            crop_rect = [0.31, 0.12, 0.69, 0.692]
            zoom = zoom*1.2
        icon = crop_img_by_percentage(img, crop_rect)
        ab = AnnotationBbox(
            OffsetImage(icon, zoom=zoom),  # type: ignore
            position,
            frameon=True,
            box_alignment=(0, 1),
            pad=0.1,
            bboxprops=dict(facecolor="darkgray", edgecolor="white", linewidth=4),
        )
        ax.add_artist(ab)

def _annotate_text_and_imgs_for_turn(ax: Axes, x0: float, y0: float, turn: Literal[1, 2], opening_info: dict[str, Any], num_openings: int):
    from ...kingdom import sanitize_cso_list

    # First, unpack the turn information
    turn_desc = opening_info[f"t{turn}"]
    turn_desc = "\n".join(textwrap.wrap(turn_desc, 41))
    csos = sanitize_cso_list(opening_info.get(f"t{turn}_csos", []), sort=False)

    fdict = {"weight": "bold", "fontproperties": XKCD_FONT}
    bbox = {"boxstyle": "round,pad=0.3", "facecolor": DOM_BEIGE}
    bbox_title = bbox.copy()
    bbox_title["facecolor"] = DOM_BLUE
    text_x0 = x0 + 0.07 if turn == 1 else x0 + 0.075
    ax.text(text_x0, y0, turn_desc, ha="left", va="top", fontsize=14, color="black",
            fontdict=fdict, bbox=bbox)
    ax.text(x0, y0, f"Turn {turn}", ha="left", va="top", fontsize=14, color="white",
            fontdict=fdict, bbox=bbox_title)
    _annotate_cso_imgs(ax, x0, y0 - 0.4/num_openings, csos, num_openings=num_openings)


def _annotate_separator_line(ax: Axes, ycoord: float):
    line = Line2D([0, 1], [ycoord, ycoord], color='black', linewidth=3)
    ax.add_line(line)  # Using ax.plot would change axes limits

def _annotate_single_opening(ax: Axes, opening_info: dict[str, Any], ycoord: float, x1: float, x2: float, num_openings: int):
    open_type = opening_info["type"]  # e.g. 3/4|4/3, or 5/2
    _annotate_coin_icons(ax, open_type, ycoord)
    grade_y = ycoord - 0.185 if "|" in open_type else ycoord - 0.14
    _annotate_grade(ax, opening_info["grade"], grade_y, num_openings)

    _annotate_text_and_imgs_for_turn(ax, x1, ycoord-0.01, 1, opening_info, num_openings)
    _annotate_text_and_imgs_for_turn(ax, x2, ycoord-0.01, 2, opening_info, num_openings)

    _annotate_separator_line(ax, ycoord + 0.011)

def create_opening_hints(k: "Kingdom"):
    openings = k.unpacked_notes.get("openings", [])
    assert all([all([x in subdict.keys() for x in ["grade", "type", "t1", "t2"]]) for subdict in openings]), f"Some part of the openings are missing information ({openings})"
    assert all([subdict.get("grade") != "" for subdict in openings]), "Some openings are missing a grade"

    fig, ax = set_up_fig_and_ax_for_img()

    _set_background_gradient(ax)
    _annotate_title(ax, k.name)
    _annotate_disclaimer_text(ax)

    y0, x1, x2 = 0.9, 0.1, 0.54
    _annotate_vertical_line(ax, x1 - 0.013, y0)
    _annotate_vertical_line(ax, x2 - 0.013, y0)

    for open_info in openings:
        _annotate_single_opening(ax, open_info, y0, x1, x2, len(openings))
        y0 -= 0.23*4/len(openings)

    annotate_dominion_logo(ax, 0.99, 0.91, 0.24)
    fig.savefig(PATH_ASSETS.joinpath("other/youtube/current_openings.png"), dpi=300, bbox_inches="tight")
