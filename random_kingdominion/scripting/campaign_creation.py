from ..constants import PATH_ASSETS
from ..kingdom.kingdom_manager import KingdomManager
from ..utils.plotting import create_thumbnail


def set_up_campaign_video_assets(
    campaign_name: str, manager: KingdomManager | None = None
) -> None:
    """Set up the video assets for the given campaign kingdom."""
    if manager is None:
        manager = KingdomManager()
        manager.load_campaigns()
    kingdom = manager.get_kingdom_by_name(campaign_name)
    if kingdom is None:
        raise ValueError(f"No kingdom found for campaign '{campaign_name}'.")
    caption_path = PATH_ASSETS.joinpath("other/youtube/campaigns/current_caption.txt")
    caption_path.write_text(f"Dominion Campaigns: {kingdom.name}")
    create_thumbnail(kingdom, "Dominion Campaigns")
