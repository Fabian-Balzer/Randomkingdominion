from pathlib import Path
from typing import TYPE_CHECKING, Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch
from scipy.ndimage import zoom as zoom_image

from ...constants import ALL_CSOS, EXPANSION_LIST, PATH_ASSETS, PATH_CARD_PICS
from ...logger import LOGGER
from .constants import (CAMPAIGN_COLOR, DAILY_COLOR, DOM_BEIGE, DOM_BLUE,
                        FIRST_PLAYER_COLOR, SECOND_PLAYER_COLOR, XKCD_FONT)
from .image_handling import crop_img_by_percentage, load_cso_img_by_key
from .quality_plot_helper import plot_kingdom_qualities
from .util import (annotate_dominion_logo, annotate_icon,
                   annotate_single_expansion_icon, get_video_title,
                   plot_gradient_image, set_up_fig_and_ax_for_img)

if TYPE_CHECKING:
    from ...kingdom import Kingdom




def _annotate_title(
    ax: Axes,
    title: str,
    x0: float,
    y0: float,
    fc=DOM_BEIGE,
    tc="k",
    fontsize=28,
    **kwargs,
):
    ax.text(
        x0,
        y0,
        title,
        va="bottom",
        fontsize=fontsize,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": fc},
        fontdict={"fontproperties": XKCD_FONT, "color": tc},
        clip_on=True,
        **kwargs,
    )


def _annotate_subtitle(ax: Axes, k: "Kingdom", fc=DOM_BEIGE):
    text = k.unpacked_notes.get("subtitle", "")
    if text == "":
        return
    _annotate_title(ax, "\n" + text, 0.015, 0.85, fc=fc, tc="k", fontsize=13, zorder=0)


def _annotate_hard_ai(ax: Axes, x0: float, y0: float, final_zoom=0.4, ec="k"):

    icon_path = PATH_ASSETS.joinpath("icons/hard_ai_pfp.png")
    img = plt.imread(icon_path)
    height, width = img.shape[:2]
    new_height, new_width = 100, 100
    zoom_factors = (new_height / height, new_width / width, 1)
    # Resize the image
    img_resized = zoom_image(img, zoom_factors)
    # Convert back to array for matplotlib
    image_rgb = np.clip(img_resized, 0, 1)
    img = OffsetImage(image_rgb, zoom=final_zoom)
    ab = AnnotationBbox(
        img,
        (x0, y0),
        frameon=True,
        xycoords="data",
        box_alignment=(0, 1),
        bboxprops=dict(facecolor=ec, edgecolor="k", linewidth=1),
    )
    ax.add_artist(ab)
    return ab


def _annotate_expansion_icons(
    expansions: Sequence[str], ax: Axes, x0: float, y0: float
):
    """Annotate the used expansions in one or two rows (depending on number)"""
    num_expansions = len(expansions)
    zoom = 0.68 if num_expansions <= 4 else 0.32
    xoff = 0.12 if num_expansions <= 4 else 0.07
    num_cols = num_expansions if num_expansions <= 4 else np.ceil(num_expansions / 2)
    for i, expansion in enumerate(expansions):
        x = x0 + xoff * (i % num_cols)
        y = y0 - 0.085 * (i // num_cols)
        annotate_single_expansion_icon(expansion, ax, x, y, zoom)


def _annotate_kingdom_plot(
    ax: Axes, k: "Kingdom", x0, y0, zoom=0.75, fc="none", fc_ax="white"
):
    """Annotate the kingdom plot by temporarily saving it."""
    inset_fig = plot_kingdom_qualities(k.total_qualities, buy_str=k.buy_availability)
    inset_fig.set_facecolor(fc)
    inset_fig.gca().set_facecolor(fc_ax)
    p = PATH_ASSETS.joinpath("other/youtube/current_kingdom_plot.png")
    inset_fig.savefig(p, bbox_inches="tight")
    plt.close()
    img = plt.imread(p)
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(
        imagebox, (x0, y0), frameon=False, box_alignment=(1, 1), pad=0.1
    )
    ax.add_artist(ab)


def _annotate_campaign_progress(ax: Axes, fpath: Path, x0, y0, zoom=0.75):
    """Annotate the kingdom plot by temporarily saving it."""
    img = plt.imread(fpath)
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(
        imagebox, (x0, y0), frameon=False, box_alignment=(1, 0), pad=0.1
    )
    ax.add_artist(ab)


def _annotate_single_twist(
    ax: Axes, effect: str, k: "Kingdom", x0: float, y0: float
) -> tuple[float, float]:
    if effect not in ALL_CSOS.index:
        text = effect
    else:
        entry = ALL_CSOS.loc[effect]
        type_ = entry["Types"][0]
        if type_ == "Stamp":
            return x0, y0
        text = entry["Name"]
    ax.text(
        x0,
        y0,
        "  " + text,  # type: ignore
        ha="left",
        va="top",
        fontsize=13,
        fontdict={"fontproperties": XKCD_FONT, "color": "black"},
        bbox={"boxstyle": "round,pad=0.4", "facecolor": CAMPAIGN_COLOR, "linewidth": 2},
    )
    _annotate_campaign_seal(ax, x0 - 0.033, y0 + 0.0227, 0.3)
    new_x0 = x0  # + 0.17
    new_y0 = y0 - 0.07
    return new_x0, new_y0


def _annotate_twists(
    ax: Axes,
    k: "Kingdom",
    x0,
    y0,
):
    for i, effect in enumerate(k.campaign_effects):
        x0, y0 = _annotate_single_twist(ax, effect, k, x0, y0)
        if y0 < 0.7:
            x0 += 0.15
            y0 += 0.14
    extra_twists = k.unpacked_notes.get("extra_twists", [])
    for i, twist in enumerate(extra_twists):
        x0, y0 = _annotate_single_twist(ax, twist, k, x0, y0)


def _annotate_kingdom_cards_landscapes(
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
        card_text = "\n".join(card_lines)
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


def _annotate_single_card_img(
    ax: Axes,
    card: str,
    x0: float,
    y0: float,
    index: int = 0,
    zoom=0.8,
    stamps: list[str] = [],
):
    position = x0 + 0.19 * (index % 2), y0 - 0.32 * (index // 2)
    img = load_cso_img_by_key(card)
    crop_rect = [0.15, 0.11, 0.85, 0.51]
    entry = ALL_CSOS.loc[card]
    if (
        entry["IsExtendedLandscape"]
        or entry["IsOtherThing"]
        and not "Loot" in entry["Types"]
    ):  # type: ignore
        crop_rect = [0.31, 0.13, 0.69, 0.692]
        zoom = 0.9
    if card in [
        "copper",
        "silver",
        "gold",
        "platinum",
        "potion",
        "estate",
        "duchy",
        "province",
        "colony",
        "curse",
    ]:
        crop_rect = [0.15, 0.15, 0.85, 0.55]
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
    if len(stamps) > 0:
        for i, stamp in enumerate(stamps):
            s = ALL_CSOS.loc[stamp]
            ax.text(
                position[0] + 0.026,
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
            annotate_icon(
                PATH_CARD_PICS.joinpath(s["ImagePath"]),  # type: ignore
                ax,
                position[0],
                position[1] - 0.218 + i * 0.07,
                0.26,
            )


def _annotate_cards_landscapes(ax: Axes, k: "Kingdom"):

    if "crucial_cards" not in k.unpacked_notes:
        _annotate_kingdom_cards_landscapes(
            k,
            ax,
            0.024,
            0.635,
            bbox={"boxstyle": "round,pad=0.4", "facecolor": DOM_BEIGE, "linewidth": 2},
            shorten=False,
        )
        return

    if "turns" in k.unpacked_notes and len(k.unpacked_notes["turns"]) > 0:
        turns = max(k.unpacked_notes["turns"])
        turns = f"{turns} Turns"
        if "tries" in k.unpacked_notes:
            turns += f" [{k.unpacked_notes['tries']} Tries]"
        ax.text(
            0.55,
            0.664,
            f"{turns}",
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
                bbox={
                    "boxstyle": "round,pad=0.4",
                    "facecolor": DOM_BLUE,
                    "linewidth": 2,
                },
                color="white",
                fontsize=15,
                zorder=0,
            )
        if k.unpacked_notes.get("find_the_win", False):
            ax.text(
                0.55,
                0.78,
                "+ Find-The-Win!",
                ha="right",
                bbox={
                    "boxstyle": "round,pad=0.4",
                    "facecolor": DOM_BLUE,
                    "linewidth": 2,
                },
                color="white",
                fontsize=15,
                zorder=0,
            )
    rect = FancyBboxPatch(
        (0, 0),
        0.508,
        0.605,
        boxstyle="round,pad=0.05,rounding_size=0.01",
        edgecolor="black",
        lw=2,
        facecolor=DOM_BEIGE,
        clip_on=True,
    )
    ax.add_patch(rect)
    _annotate_kingdom_cards_landscapes(k, ax, 0.385, 0.635)
    crucial_cards: list = k.unpacked_notes["crucial_cards"]
    from ...kingdom import sanitize_cso_list

    crucial_cards = sanitize_cso_list(crucial_cards, sort=False)
    for i, cso in enumerate(crucial_cards):
        stamps = [
            s
            for s in k.campaign_effects
            if k.stamp_and_effects_dict.get(s, "_") == cso
        ]
        _annotate_single_card_img(ax, cso, 0.01, 0.63, i, stamps=stamps)



def _annotate_campaign_seal(ax: Axes, x0=0.01, y0=0.87, zoom=0.4):
    annotate_icon(
        PATH_ASSETS.joinpath("icons/campaign_seal.png"), ax, x0, y0, final_zoom=zoom
    )


def do_daily_extras(ax: Axes, k: "Kingdom") -> Path:
    _annotate_expansion_icons(k.expansions, ax, 0.01, 0.83)
    if len(k.campaign_effects) > 0:
        _annotate_campaign_seal(ax, 0.518, 0.655, 0.3)
    _annotate_kingdom_plot(ax, k, 1, 0.707, 0.68, fc_ax=DOM_BEIGE)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    twist_y0 = 0.75 if k.unpacked_notes.get("bonus_game", False) else 0.825
    _annotate_twists(ax, k, 0.4, twist_y0)
    fname = f"{k.name.replace(" ", "_")}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/dailies/{fname}")

def _annotate_ftw_img(ax: Axes, ftw_num: int, x0: float, y0: float, zoom=0.3):
    """Annotate the Find-the-win image."""
    fpath = PATH_ASSETS.joinpath(f"other/youtube/ftw/ftw_{ftw_num}.png")
    img = plt.imread(PATH_ASSETS.joinpath(fpath))  # type: ignore
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(imagebox, (x0, y0), frameon=False, box_alignment=(1, 1), pad=0)
    ax.add_artist(ab)

def _annotate_difficulty(ax: Axes, difficulty: str, x0: float, y0: float):
    """Annotate the difficulty of the Find-the-win."""
    if difficulty == "medium":
        color = "#FF8C00"  # Dark Orange
    elif difficulty == "hard":
        color = "#A30808"  # Red
    else:
        color = "#32CD32"  # Lime Green
    ax.text(
        x0,
        y0,
        f"Difficulty: {difficulty.capitalize()}",
        ha="left",
        va="bottom",
        fontsize=13,
        fontdict={"fontproperties": XKCD_FONT, "color": "black"},
        bbox={
            "boxstyle": "round,pad=0.4",
            "facecolor": color,
            "linewidth": 2,
        },
    )

def do_ftw_extras(ax: Axes, k: "Kingdom") -> Path:
    ftw_num = k.unpacked_notes["ftw_num"]
    _annotate_expansion_icons(k.expansions, ax, 0.01, 0.83)
    if len(k.campaign_effects) > 0:
        _annotate_campaign_seal(ax, 0.518, 0.655, 0.3)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    _annotate_ftw_img(ax, ftw_num, 0.965, 0.65, 0.4)
    _annotate_twists(ax, k, 0.4, 0.75)
    _annotate_difficulty(ax, k.unpacked_notes["difficulty"], 0.72, 0.1)
    fname = f"ftw_{ftw_num}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/ftw/{fname}")

def do_recset_extras(ax: Axes, k: "Kingdom") -> Path:
    _annotate_expansion_icons(k.expansions, ax, 0.01, 0.83)
    _annotate_kingdom_plot(ax, k, 1, 0.707, 0.68, fc_ax=DOM_BEIGE)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    fname = f"{k.name.replace(" ", "_")}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/recsets/{fname}")


def do_campaign_extras(ax: Axes, k: "Kingdom") -> Path:
    if (
        "expansion" not in k.unpacked_notes
        and (e := k.name.split(" ")[0]) in EXPANSION_LIST
    ):
        k.notes = r'{"expansion": "' + e + '"}'
        LOGGER.info(f"Set notes to {k.notes}")
    expansions = (
        k.expansions
        if "expansion" not in k.unpacked_notes
        else [k.unpacked_notes["expansion"]]
    )
    _annotate_expansion_icons(
        expansions,
        ax,
        0.01,
        0.83,
    )
    _annotate_twists(ax, k, 0.17, 0.8)
    if "expansion" in k.unpacked_notes:
        from ...kingdom import sanitize_cso_name

        exp = sanitize_cso_name(k.unpacked_notes["expansion"])
        fname = f"{k.name.replace(" ", "_")}_thumbnail.png"
        fpath = PATH_ASSETS.joinpath(f"other/youtube/campaigns/{exp}/{fname}")
        map_fpath = fpath.parent.joinpath(f"dominion{k.name.split()[1]}.png")
    else:
        fname = f"{k.name.split(" ")[0].lower().replace(" ", "_").replace(", ", "_")}_thumbnail.png"
        fpath = PATH_ASSETS.joinpath(
            f"other/youtube/campaigns/{k.name.split(":")[0].lower().replace(" ", "_")}/{fname}"
        )
        map_fpath = fpath.parent.joinpath(f"dominion{k.name.split()[1]}.png")
    try:
        _annotate_campaign_progress(ax, map_fpath, 0.99, 0.01, 0.2)
    except FileNotFoundError:
        LOGGER.warning(f"Could not find map for {k.name}")
    _annotate_kingdom_plot(ax, k, 0.925, 0.89, 0.44, fc_ax=DOM_BEIGE)

    if not fpath.parent.exists():
        fpath.parent.mkdir(parents=False)
    return fpath


def create_thumbnail(
    k: "Kingdom",
    video_type: Literal[
        "Daily Dominion", "Dominion RecSets", "Dominion Campaigns", "Find-the-win"
    ] = "Daily Dominion",
):
    """Create a standardized thumnail for a yt video"""
    fig, ax = set_up_fig_and_ax_for_img()

    # Generate a simple gradient as the background
    plot_gradient_image(ax, extent=(0, 1, 0, 1), direction="horizontal", cmap="gray_r")
    video_type_dict = {
        "Daily Dominion": DAILY_COLOR,
        "Dominion RecSets": "#90EE90",
        "Dominion Campaigns": CAMPAIGN_COLOR,
        "Find-the-win": "#089308",
    }
    assert video_type in video_type_dict, f"Unknown video type {video_type}"
    title = get_video_title(k)
    # _annotate_title(ax, video_type, 0.066, 0.91, fc=video_type_dict[video_type])
    # _annotate_title(ax, title, 0.99, 0.91, ha="right", fc=DOM_BEIGE)
    _annotate_title(
        ax, video_type, 0.935, 0.91, ha="right", fc=video_type_dict[video_type]
    )
    _annotate_hard_ai(
        ax,
        0.944,
        0.99,
        0.36,
        ec=(
            FIRST_PLAYER_COLOR
            if k.unpacked_notes.get("second_player", False)
            else SECOND_PLAYER_COLOR
        ),
    )
    _annotate_title(
        ax, " " + title, 0.0, 0.91, ha="left", fc=video_type_dict[video_type]
    )
    _annotate_subtitle(ax, k, fc=video_type_dict[video_type])

    _annotate_cards_landscapes(ax, k)

    special = {
        "Daily Dominion": do_daily_extras,
        "Dominion RecSets": do_recset_extras,
        "Dominion Campaigns": do_campaign_extras,
        "Find-the-win": do_ftw_extras,
    }[video_type]
    fpath = special(ax, k)
    fig.savefig(fpath, pad_inches=0.2, bbox_inches="tight", dpi=200)
