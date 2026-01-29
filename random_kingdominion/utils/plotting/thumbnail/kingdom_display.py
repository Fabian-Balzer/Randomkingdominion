from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch

from ....constants import ALL_CSOS, PATH_ASSETS, PATH_CARD_PICS
from ...utils import sanitize_cso_list
from ..constants import CAMPAIGN_COLOR, DOM_BEIGE, DOM_BLUE, FTW_COLOR, XKCD_FONT
from ..image_handling import get_square_cutout
from ..quality_plot_helper import plot_kingdom_qualities
from ..util import annotate_icon
from .config import KingdomDisplayConfig

if TYPE_CHECKING:
    from ....kingdom import Kingdom


def save_temporary_kingdom_plot(k: "Kingdom", fc="none", fc_ax=DOM_BEIGE) -> Path:
    """Save the kingdom qualities plot temporarily and return the path."""
    inset_fig = plot_kingdom_qualities(k.total_qualities, buy_str=k.buy_availability)
    inset_fig.set_facecolor(fc)
    inset_fig.gca().set_facecolor(fc_ax)
    p = PATH_ASSETS.joinpath("other/youtube/current_kingdom_plot.png")
    inset_fig.savefig(p, bbox_inches="tight", dpi=200)
    plt.close()
    return p


def annotate_kingdom_plot(
    ax: Axes, k: "Kingdom", x0, y0, zoom=0.75, fc="none", fc_ax=DOM_BEIGE
):
    """Annotate the kingdom plot by temporarily saving it."""
    p = save_temporary_kingdom_plot(k, fc, fc_ax)
    img = plt.imread(p)
    imagebox = OffsetImage(img, zoom=zoom / 2)
    ab = AnnotationBbox(
        imagebox, (x0, y0), frameon=False, box_alignment=(1, 1), pad=0.1
    )
    ax.add_artist(ab)


def annotate_campaign_progress(ax: Axes, fpath: Path, x0, y0, zoom=0.75):
    """Annotate the kingdom plot by temporarily saving it."""
    img = plt.imread(fpath)
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(
        imagebox, (x0, y0), frameon=False, box_alignment=(1, 0), pad=0.1
    )
    ax.add_artist(ab)


def annotate_kingdom_cards_landscapes(
    k: "Kingdom", ax: Axes, x0=0.5, y0=0.5, tc="black", shorten=True, **kwargs
):
    card_text = (
        k.card_and_landscape_text.replace("Cards", "CARDS")
        .replace("Landscapes", "LANDSCAPES")
        .replace("Stamps and Twists", "STAMPS & TWISTS")
    )
    if shorten:
        card_lines = card_text.split("\n")
        card_lines = [
            line[:16] + "..." if len(line) > 19 else line for line in card_lines
        ]
        card_text = "\n".join(card_lines[:19])
    cc = card_text.count("\n")
    fontsize = 12 if cc > 16 else 13 if cc >= 15 else 15
    ax.text(
        x0,
        y0,
        card_text,
        va="top",
        ha="left",
        fontdict={"fontproperties": XKCD_FONT, "color": tc},
        fontsize=fontsize,
        **kwargs,
    )


def annotate_single_crucial_cso(
    ax: Axes,
    cso_key: str,
    x0: float,
    y0: float,
    index: int = 0,
    zoom=0.8,
    stamps_traits: list[str] = [],
):
    position = x0 + 0.19 * (index % 2), y0 - 0.32 * (index // 2)
    icon = get_square_cutout(cso_key)
    entry = ALL_CSOS.loc[cso_key]
    if (
        entry["IsExtendedLandscape"]
        or entry["IsOtherThing"]
        and not "Loot" in entry["Types"]
    ):  # type: ignore
        zoom = 0.9
    ab = AnnotationBbox(
        OffsetImage(icon, zoom=zoom),  # type: ignore
        position,
        frameon=True,
        box_alignment=(0, 1),
        pad=0.1,
        bboxprops=dict(facecolor="darkgray", edgecolor="white", linewidth=4),
    )
    ax.add_artist(ab)
    if len(stamps_traits) == 0:
        return
    for i, stamp_or_trait in enumerate(stamps_traits):
        s = ALL_CSOS.loc[stamp_or_trait]
        ax.text(
            position[0] + 0.028,
            position[1] - 0.27 + i * 0.07,
            "  " + s["Name"],  # type: ignore
            ha="left",
            va="bottom",
            fontsize=13,
            fontdict={"fontproperties": XKCD_FONT, "color": "black"},
            bbox={
                "boxstyle": "round,pad=0.4",
                "facecolor": CAMPAIGN_COLOR,
                "linewidth": 2,
            },
        )
        if "Trait" in s["Types"]:
            t_icon = get_square_cutout(stamp_or_trait)
            t_pos = position[0] + 0.005, position[1] - 0.231 + i * 0.07
            ab = AnnotationBbox(
                OffsetImage(t_icon, zoom=0.14),  # type: ignore
                t_pos,
                frameon=True,
                box_alignment=(0, 1),
                pad=0.1,
                bboxprops=dict(facecolor="darkgray", edgecolor="black", linewidth=2),
            )
            ax.add_artist(ab)
        else:
            annotate_icon(
                PATH_CARD_PICS.joinpath(s["ImagePath"]),  # type: ignore
                ax,
                position[0],
                position[1] - 0.218 + i * 0.07,
                0.26,
            )


def _annotate_turns_info(ax: Axes, k: "Kingdom"):
    """Annotate turns and bonus game info."""
    from .icons import annotate_difficulty

    turns = max(k.unpacked_notes["turns"])
    assert (
        np.diff(k.unpacked_notes["turns"])[0] <= 1
    ), "Turns should only differ by 1 at most."
    turns_text = f"{turns} Turns"
    if "tries" in k.unpacked_notes:
        turns_text += f" [{k.unpacked_notes['tries']} Tries]"
    ax.text(
        0.55,
        0.664,
        turns_text,
        ha="right",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": DOM_BLUE, "linewidth": 2},
        color="white",
        fontsize=15,
        zorder=0,
    )
    if k.unpacked_notes.get("bonus_game", False):
        ax.text(
            0.55,
            0.78,
            "+ Bonus Game!",
            ha="right",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": DOM_BLUE, "linewidth": 2},
            color="white",
            fontsize=15,
            zorder=0,
        )
    if k.unpacked_notes.get("find_the_win", False):
        ax.text(
            0.382,
            0.78,
            "+ Find-The-Win!",
            ha="left",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": FTW_COLOR, "linewidth": 2},
            color="white",
            fontsize=15,
            zorder=0,
        )
        annotate_difficulty(ax, k.unpacked_notes["ftw_difficulty"], 0.382, 0.715)


def annotate_cards_landscapes(ax: Axes, k: "Kingdom", config: KingdomDisplayConfig):

    if "crucial_cards" not in k.unpacked_notes:
        annotate_kingdom_cards_landscapes(
            k,
            ax,
            config.cards_x,
            config.cards_y,
            bbox={"boxstyle": "round,pad=0.4", "facecolor": DOM_BEIGE, "linewidth": 2},
            shorten=False,
        )
        return

    if "turns" in k.unpacked_notes and len(k.unpacked_notes["turns"]) > 0:
        _annotate_turns_info(ax, k)

    rect = FancyBboxPatch(
        (0, 0),
        config.box_width,
        config.box_height,
        boxstyle="round,pad=0.05,rounding_size=0.01",
        edgecolor="black",
        lw=2,
        facecolor=config.box_fc,
        clip_on=True,
    )
    ax.add_patch(rect)
    annotate_kingdom_cards_landscapes(k, ax, config.text_x, config.text_y)
    crucial_cards: list = k.unpacked_notes["crucial_cards"]
    crucial_cards = sanitize_cso_list(crucial_cards, sort=False)
    for i, cso in enumerate(crucial_cards):
        stamps_traits = [
            s for s in k.campaign_effects if k.stamp_and_effects_dict.get(s, "_") == cso
        ]
        stamps_traits += [s for s in k.trait_dict if k.trait_dict.get(s, "_") == cso]
        annotate_single_crucial_cso(
            ax,
            cso,
            config.crucial_cards_x,
            config.crucial_cards_y,
            i,
            stamps_traits=stamps_traits,
        )
