from typing import TYPE_CHECKING

from matplotlib.axes import Axes

from ....constants import ALL_CSOS
from ..constants import CAMPAIGN_COLOR, DOM_BEIGE, XKCD_FONT
from .config import TitleConfig
from .icons import annotate_campaign_seal

if TYPE_CHECKING:
    from ....kingdom import Kingdom


def annotate_title(
    ax: Axes,
    title: str,
    config: TitleConfig,
    is_video_type: bool = False,
    **kwargs,
):
    """Annotate the main title using config positioning."""
    fontsize = config.fontsize if len(title) <= 30 else config.fontsize_long
    x, y = (
        (config.video_type_x, config.video_type_y)
        if is_video_type
        else (config.title_x, config.title_y)
    )
    ha = "right" if is_video_type else "left"
    ax.text(
        x,
        y,
        title,
        va="bottom",
        fontsize=fontsize,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": config.facecolor},
        fontdict={"fontproperties": XKCD_FONT, "color": config.textcolor},
        clip_on=True,
        ha=ha,
        **kwargs,
    )


def annotate_subtitle(ax: Axes, k: "Kingdom", config: TitleConfig):
    """Annotate the subtitle if present in kingdom notes."""
    text = k.unpacked_notes.get("subtitle", "")
    if text == "":
        return
    ax.text(
        config.subtitle_x,
        config.subtitle_y,
        "\n" + text,
        va="bottom",
        fontsize=config.subtitle_fontsize,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": config.facecolor},
        fontdict={"fontproperties": XKCD_FONT, "color": config.textcolor},
        clip_on=True,
        zorder=0,
    )


def annotate_single_twist(
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
    annotate_campaign_seal(ax, x0 - 0.033, y0 + 0.0227, 0.3)
    new_x0 = x0
    new_y0 = y0 - 0.07
    return new_x0, new_y0


def annotate_twists(ax: Axes, k: "Kingdom", x0: float, y0: float):
    for i, effect in enumerate(k.campaign_effects):
        x0, y0 = annotate_single_twist(ax, effect, k, x0, y0)
        if y0 < 0.7:
            x0 += 0.15
            y0 += 0.14
    extra_twists = k.unpacked_notes.get("extra_twists", [])
    for i, twist in enumerate(extra_twists):
        x0, y0 = annotate_single_twist(ax, twist, k, x0, y0)
