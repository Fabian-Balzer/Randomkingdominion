from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Literal

from matplotlib.axes import Axes

from ..constants import (
    CAMPAIGN_COLOR,
    DAILY_COLOR,
    DOM_BEIGE,
    FIRST_PLAYER_COLOR,
    FTW_COLOR,
    SECOND_PLAYER_COLOR,
)

if TYPE_CHECKING:
    from ....kingdom import Kingdom


@dataclass(frozen=True, slots=True)
class TitleConfig:
    """Positioning for title elements."""

    video_type_x: float = 0.935
    video_type_y: float = 0.91
    title_x: float = 0.0
    title_y: float = 0.91
    facecolor: str = DOM_BEIGE
    textcolor: str = "k"
    subtitle_x: float = 0.015
    subtitle_y: float = 0.85
    fontsize: int = 28
    fontsize_long: int = 25  # for titles > 30 chars
    subtitle_fontsize: int = 13


@dataclass(frozen=True, slots=True)
class AIIconConfig:
    """Positioning for the Hard AI icon."""

    x: float = 0.944
    y: float = 0.99
    zoom: float = 0.36
    ec: str = "k"

    def get_color(self, k: "Kingdom") -> str:
        return (
            FIRST_PLAYER_COLOR
            if k.unpacked_notes.get("second_player", False)
            else SECOND_PLAYER_COLOR
        )


@dataclass(frozen=True, slots=True)
class KingdomDisplayConfig:
    """Positioning for kingdom cards/landscapes display."""

    cards_x: float = 0.024
    cards_y: float = 0.635
    crucial_cards_x: float = 0.01
    crucial_cards_y: float = 0.63
    crucial_card_zoom: float = 0.8
    crucial_card_x_offset: float = 0.19
    crucial_card_y_offset: float = 0.32
    text_x: float = 0.39
    text_y: float = 0.635
    box_width: float = 0.508
    box_height: float = 0.605
    box_fc: str = DOM_BEIGE


@dataclass(frozen=True, slots=True)
class ExpansionIconsConfig:
    """Positioning for expansion icons."""

    x: float = 0.01
    y: float = 0.83
    zoom_few: float = 0.68  # <= 4 expansions
    zoom_many: float = 0.32  # > 4 expansions
    x_offset_few: float = 0.12
    x_offset_many: float = 0.07
    y_offset: float = 0.085

    def get_zoom(self, num_expansions: int) -> float:
        return self.zoom_few if num_expansions <= 4 else self.zoom_many

    def get_x_offset(self, num_expansions: int) -> float:
        return self.x_offset_few if num_expansions <= 4 else self.x_offset_many


@dataclass(frozen=True, slots=True)
class KingdomPlotConfig:
    """Positioning for the kingdom quality plot."""

    x: float = 1.0
    y: float = 0.707
    zoom: float = 0.68


@dataclass(frozen=True, slots=True)
class ThumbnailConfig:
    """Central configuration for thumbnail generation."""

    video_type: Literal[
        "Daily Dominion",
        "Dominion RecSets",
        "Dominion Campaigns",
        "Find-the-win",
        "Match",
    ] = "Daily Dominion"

    # Sub-configs
    title: TitleConfig = field(default_factory=TitleConfig)
    ai_icon: AIIconConfig = field(default_factory=AIIconConfig)
    kingdom_display: KingdomDisplayConfig = field(default_factory=KingdomDisplayConfig)
    expansion_icons: ExpansionIconsConfig = field(default_factory=ExpansionIconsConfig)
    kingdom_plot: KingdomPlotConfig = field(default_factory=KingdomPlotConfig)

    # Colors
    background_cmap: str = "gray_r"
    box_color: str = DOM_BEIGE

    def __post_init__(self):
        assert self.video_type in {
            "Daily Dominion",
            "Dominion RecSets",
            "Dominion Campaigns",
            "Find-the-win",
            "Match",
        }, f"Unknown video type {self.video_type}"
        self.set_color(self.video_type_color)

    def set_color(self, color: str):
        object.__setattr__(self.title, "facecolor", color)

    @property
    def video_type_color(self) -> str:
        return {
            "Daily Dominion": DAILY_COLOR,
            "Dominion RecSets": "#90EE90",
            "Dominion Campaigns": CAMPAIGN_COLOR,
            "Find-the-win": FTW_COLOR,
            "Match": "#FF8800",
        }[self.video_type]

    @property
    def video_type_handler(
        self,
    ) -> Callable[[Axes, "Kingdom", "ThumbnailConfig"], Path]:
        from .video_types import (
            do_campaign_extras,
            do_daily_extras,
            do_ftw_extras,
            do_recset_extras,
            do_match_extras,
        )

        return {
            "Daily Dominion": do_daily_extras,
            "Dominion RecSets": do_recset_extras,
            "Dominion Campaigns": do_campaign_extras,
            "Find-the-win": do_ftw_extras,
            "Match": do_match_extras,
        }[self.video_type]


# Pre-built configs for different video types
DAILY_CONFIG = ThumbnailConfig(video_type="Daily Dominion")
CAMPAIGN_CONFIG = ThumbnailConfig(
    video_type="Dominion Campaigns",
    kingdom_plot=KingdomPlotConfig(x=0.925, y=0.89, zoom=0.44),
)
FTW_CONFIG = ThumbnailConfig(video_type="Find-the-win")
RECSET_CONFIG = ThumbnailConfig(video_type="Dominion RecSets")

MATCH_CONFIG = ThumbnailConfig(video_type="Match")
