from typing import TYPE_CHECKING, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from scipy.ndimage import zoom as zoom_image

from ....constants import PATH_ASSETS
from ..constants import FIRST_PLAYER_COLOR, SECOND_PLAYER_COLOR, XKCD_FONT
from ..util import annotate_icon, annotate_single_expansion_icon
from .config import AIIconConfig, ExpansionIconsConfig

if TYPE_CHECKING:
    from ....kingdom import Kingdom


def annotate_hard_ai(ax: Axes, config: AIIconConfig, k: "Kingdom") -> AnnotationBbox:
    icon_path = PATH_ASSETS.joinpath("icons/hard_ai_pfp.png")
    img = plt.imread(icon_path)
    height, width = img.shape[:2]
    new_height, new_width = 100, 100
    zoom_factors = (new_height / height, new_width / width, 1)
    img_resized = zoom_image(img, zoom_factors)
    image_rgb = np.clip(img_resized, 0, 1)  # type: ignore
    img = OffsetImage(image_rgb, zoom=config.zoom)
    ab = AnnotationBbox(
        img,
        (config.x, config.y),
        frameon=True,
        xycoords="data",
        box_alignment=(0, 1),
        bboxprops=dict(facecolor=config.get_color(k), edgecolor="k", linewidth=1),
    )
    ax.add_artist(ab)
    return ab


def annotate_opponent(ax: Axes, k: "Kingdom") -> None:
    """Annotate the opponent name on the thumbnail."""
    opponent_name = k.unpacked_notes.get("opponent", "Opponent")
    color = (
        SECOND_PLAYER_COLOR
        if k.unpacked_notes.get("second_player", False)
        else FIRST_PLAYER_COLOR
    )
    game_num = k.unpacked_notes.get("game_num", None)
    if game_num is not None:
        opponent_name = f"Game {game_num} vs. {opponent_name}"
    ax.text(
        0.989,
        0.978,
        opponent_name,
        ha="right",
        va="top",
        fontsize=25,
        fontdict={"fontproperties": XKCD_FONT, "color": "black"},
        bbox={"boxstyle": "round,pad=0.4", "facecolor": color, "linewidth": 2},
    )


def annotate_expansion_icons(
    expansions: Sequence[str], ax: Axes, config: ExpansionIconsConfig
):
    """Annotate the used expansions in one or two rows (depending on number)"""
    num_expansions = len(expansions)
    zoom = config.get_zoom(num_expansions)
    xoff = config.get_x_offset(num_expansions)
    num_cols = num_expansions if num_expansions <= 4 else np.ceil(num_expansions / 2)
    for i, expansion in enumerate(expansions):
        x = config.x + xoff * (i % num_cols)
        y = config.y - 0.085 * (i // num_cols)
        annotate_single_expansion_icon(expansion, ax, x, y, zoom)


def annotate_campaign_seal(ax: Axes, x0=0.01, y0=0.87, zoom=0.4):
    annotate_icon(
        PATH_ASSETS.joinpath("icons/campaign_seal.png"), ax, x0, y0, final_zoom=zoom
    )


def annotate_ftw_img(ax: Axes, ftw_num: int, x0: float, y0: float, zoom=0.3):
    """Annotate the Find-the-win image."""
    fpath = PATH_ASSETS.joinpath(f"other/youtube/ftw/ftw_{ftw_num}.png")
    img = plt.imread(fpath)
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(imagebox, (x0, y0), frameon=False, box_alignment=(1, 1), pad=0)
    ax.add_artist(ab)


def annotate_difficulty(ax: Axes, difficulty: str, x0: float, y0: float):
    """Annotate the difficulty of the Find-the-win."""
    color_map = {
        "medium": "#FF8C00",  # Dark Orange
        "hard": "#A30808",  # Red
    }
    color = color_map.get(difficulty, "#32CD32")  # Default: Lime Green
    ax.text(
        x0,
        y0,
        f"Difficulty: {difficulty.capitalize()}",
        ha="left",
        va="bottom",
        fontsize=13,
        fontdict={"fontproperties": XKCD_FONT, "color": "black"},
        bbox={"boxstyle": "round,pad=0.4", "facecolor": color, "linewidth": 2},
    )
