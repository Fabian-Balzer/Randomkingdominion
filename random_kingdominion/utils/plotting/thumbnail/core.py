from typing import TYPE_CHECKING, Literal

from ..constants import (
    CAMPAIGN_COLOR,
    DAILY_COLOR,
    FIRST_PLAYER_COLOR,
    FTW_COLOR,
    SECOND_PLAYER_COLOR,
)
from ..util import get_video_title, plot_gradient_image, set_up_fig_and_ax_for_img
from .annotations import annotate_subtitle, annotate_title
from .config import ThumbnailConfig
from .kingdom_display import annotate_cards_landscapes

if TYPE_CHECKING:
    from ....kingdom import Kingdom


def create_thumbnail(
    k: "Kingdom",
    config: ThumbnailConfig | None = None,
):
    """Create a standardized thumbnail for a YouTube video."""
    if config is None:
        config = ThumbnailConfig(video_type="Daily Dominion")
    fig, ax = set_up_fig_and_ax_for_img()
    plot_gradient_image(ax, extent=(0, 1, 0, 1), direction="horizontal", cmap="gray_r")

    is_match = config.video_type == "Match"
    title = get_video_title(k, is_match=is_match)
    if not is_match:
        annotate_title(ax, config.video_type, config.title, True)
    annotate_title(ax, " " + title, config.title, False)
    annotate_subtitle(ax, k, config.title)
    annotate_cards_landscapes(ax, k, config.kingdom_display)

    # Video-type specific extras
    handler = config.video_type_handler
    fpath = handler(ax, k, config)

    fig.savefig(fpath, pad_inches=0.2, bbox_inches="tight", dpi=200)
