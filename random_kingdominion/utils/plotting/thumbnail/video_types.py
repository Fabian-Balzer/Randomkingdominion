from pathlib import Path
from typing import TYPE_CHECKING

from matplotlib.axes import Axes

from ....constants import EXPANSION_LIST, PATH_ASSETS
from ....logger import LOGGER
from ....utils import sanitize_cso_name
from ..constants import DOM_BEIGE
from ..util import annotate_dominion_logo
from .annotations import annotate_twists
from .config import ExpansionIconsConfig, ThumbnailConfig
from .icons import (
    annotate_campaign_seal,
    annotate_difficulty,
    annotate_expansion_icons,
    annotate_opponent,
    annotate_ftw_img,
    annotate_hard_ai,
)
from .kingdom_display import annotate_campaign_progress, annotate_kingdom_plot

if TYPE_CHECKING:
    from ....kingdom import Kingdom


def do_daily_extras(ax: Axes, k: "Kingdom", config: ThumbnailConfig) -> Path:
    annotate_hard_ai(ax, config.ai_icon, k)
    annotate_expansion_icons(k.expansions, ax, config.expansion_icons)
    if len(k.campaign_effects) > 0:
        annotate_campaign_seal(ax, 0.518, 0.655, 0.3)
    annotate_kingdom_plot(ax, k, 1, 0.707, 0.68, fc_ax=DOM_BEIGE)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    twist_y0 = 0.75 if k.unpacked_notes.get("bonus_game", False) else 0.825
    annotate_twists(ax, k, 0.4, twist_y0)
    fname = f"{k.name.replace(' ', '_')}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/dailies/{fname}")


def do_ftw_extras(ax: Axes, k: "Kingdom", config: ThumbnailConfig) -> Path:
    ftw_num = k.unpacked_notes["ftw_num"]
    annotate_hard_ai(ax, config.ai_icon, k)
    annotate_expansion_icons(k.expansions, ax, config.expansion_icons)
    if len(k.campaign_effects) > 0:
        annotate_campaign_seal(ax, 0.518, 0.655, 0.3)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    annotate_ftw_img(ax, ftw_num, 0.965, 0.65, 0.4)
    annotate_twists(ax, k, 0.4, 0.75)
    annotate_difficulty(ax, k.unpacked_notes["ftw_difficulty"], 0.72, 0.1)
    fname = f"ftw_{ftw_num}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/ftw/{fname}")


def do_recset_extras(ax: Axes, k: "Kingdom", config: ThumbnailConfig) -> Path:
    annotate_hard_ai(ax, config.ai_icon, k)
    annotate_expansion_icons(k.expansions, ax, config.expansion_icons)
    annotate_kingdom_plot(ax, k, 1, 0.707, 0.68, fc_ax=DOM_BEIGE)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    fname = f"{k.name.replace(' ', '_')}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/recsets/{fname}")


def do_campaign_extras(ax: Axes, k: "Kingdom", config: ThumbnailConfig) -> Path:
    assert (
        "expansion" in k.unpacked_notes
    ), "Campaign thumbnails require 'expansion' in kingdom notes."
    expansions = k.unpacked_notes.get("expansions", [])
    if not expansions:
        expansions = [sanitize_cso_name(k.unpacked_notes["expansion"])]
    annotate_hard_ai(ax, config.ai_icon, k)
    annotate_expansion_icons(expansions, ax, config.expansion_icons)
    annotate_twists(ax, k, 0.17, 0.8)

    if "expansion" in k.unpacked_notes:
        exp = sanitize_cso_name(k.unpacked_notes["expansion"])
        fname = f"{k.name.replace(' ', '_')}_thumbnail.png"
        fpath = PATH_ASSETS.joinpath(f"other/youtube/campaigns/{exp}/{fname}")
        map_fpath = fpath.parent.joinpath(f"dominion{k.name.split()[-1]}.png")
    else:
        fname = f"{k.name.split(' ')[0].lower().replace(' ', '_').replace(', ', '_')}_thumbnail.png"
        fpath = PATH_ASSETS.joinpath(
            f"other/youtube/campaigns/{k.name.split(':')[0].lower().replace(' ', '_')}/{fname}"
        )
        map_fpath = fpath.parent.joinpath(f"dominion{k.name.split()[-1]}.png")

    try:
        annotate_campaign_progress(ax, map_fpath, 0.99, 0.01, 0.2)
    except FileNotFoundError:
        LOGGER.warning(f"Could not find map for {k.name} at {map_fpath}")
    annotate_kingdom_plot(ax, k, 0.925, 0.89, 0.44, fc_ax=DOM_BEIGE)

    if not fpath.parent.exists():
        fpath.parent.mkdir(parents=True)
    return fpath


def do_match_extras(ax: Axes, k: "Kingdom", config: ThumbnailConfig) -> Path:
    annotate_opponent(ax, k)
    annotate_expansion_icons(k.expansions, ax, config.expansion_icons)
    annotate_kingdom_plot(ax, k, 1, 0.707, 0.68, fc_ax=DOM_BEIGE)
    annotate_dominion_logo(ax, 0.95, 0.67, 0.55)
    fname = f"{k.name.replace(' ', '_')}_thumbnail.png"
    return PATH_ASSETS.joinpath(f"other/youtube/matches/{fname}")
