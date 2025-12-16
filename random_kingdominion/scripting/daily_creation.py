"""Registering Dailies for Random Kingdominion."""

from datetime import datetime, timedelta
from pathlib import Path

from ..constants import PATH_MAIN
from ..kingdom import Kingdom, KingdomManager
from ..logger import LOGGER
from ..utils.plotting import (
    create_opening_hints,
    create_thumbnail,
    get_kingdom_quality_fig,
)
from .constants import CAPTION_PATH
from .util import get_nearest_kingdom_name


def parse_daily_date(date_str: str | None = None) -> str:
    """Parse the provided date string or return today's date in YYYY-MM-DD format."""
    if date_str is None:
        # Offset to get PST date
        today = (datetime.now() - timedelta(0, 3600 * 8)).strftime("%Y-%m-%d")
        LOGGER.info(f"No date provided, using today's date of {today}.")
        return today
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return date.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")


def _parse_existing_kingdoms_in_txt(txt_path: Path) -> dict[str, str]:
    existing_kingdoms = {}
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                date, kingdom_string = line.strip().split("---", maxsplit=1)
                existing_kingdoms[date] = kingdom_string
    return existing_kingdoms


def _validate_kingdom_string(kingdom_str: str):
    k = Kingdom.from_dombot_csv_string(kingdom_str)
    if not k.is_valid:
        raise ValueError(
            f"Kingdom is invalid for the following reasons:\n\t{k.invalidity_reasons}"
        )


def register_daily_kingdom(
    kingdom_str: str,
    date_str: str,
    replace: bool = False,
    validate: bool = True,
    add_yt_note_basics: bool = True,
) -> KingdomManager:
    """Register the kingdom string for the given date in the tgg_dailies.txt file"""
    txt_path = PATH_MAIN.joinpath(f"scripts/data/new_kingdoms/tgg_dailies.txt")
    date = parse_daily_date(date_str)
    existing_kingdoms = _parse_existing_kingdoms_in_txt(txt_path)
    existing = existing_kingdoms.get(date, "").strip()
    if existing:
        if replace:
            LOGGER.info(f"Replacing existing kingdom for {date}:\n\t'{existing}'")
        else:
            raise ValueError(f"A kingdom for {date} already exists:\n\t'{existing}'")
    if validate:
        _validate_kingdom_string(kingdom_str)
    existing_kingdoms[date] = kingdom_str.strip()
    new_text = "\n".join(
        f"{d}---{ks}" for d, ks in sorted(existing_kingdoms.items())[::-1]
    )
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    manager = KingdomManager(add_yt_note_basics=add_yt_note_basics)
    manager.load_tgg_dailies(reload=True)
    return manager


def get_daily_kingdom(
    date_str: str, manager: KingdomManager | None = None, reload=False
) -> tuple[Kingdom, KingdomManager]:
    """Retrieve the kingdom and manager for the given daily date."""
    date = parse_daily_date(date_str)
    if manager is None:
        manager = KingdomManager()
        manager.load_tgg_dailies(reload=reload)
    kingdom = manager.get_kingdom_by_name(date)
    if kingdom is None:
        raise ValueError(f"No kingdom found for date {date}.")
    return kingdom, manager


def set_up_daily_video_assets(
    date_str: str, manager: KingdomManager | None = None
) -> None:
    """Set up the kingdom plot, change the display string, and try to create opening hints."""
    k, manager = get_daily_kingdom(date_str, manager)
    create_thumbnail(k)
    CAPTION_PATH.write_text(f"TGG Daily Challenge {k.name}")

    new_name = k.unpacked_notes.get("name", "")
    LOGGER.info(
        "Dombot Kingdom String:\n\n"
        + k.get_dombot_csv_string()
        + "\nExpansions:\n"
        + ", ".join(k.expansions)
    )

    if new_name != "":
        close_prev = get_nearest_kingdom_name(new_name, k.name, manager)
        LOGGER.warning(
            f"Closest previous kingdom name:\n\t{close_prev} (vs. {new_name})"
        )

    if "openings" in k.unpacked_notes:
        try:
            create_opening_hints(k)
            LOGGER.info("Successfully created opening hints")
        except AssertionError as e:
            LOGGER.error(f"Could not create opening hints:\n\t{e}")


def plot_daily_kingdom(date_str: str, manager: KingdomManager | None = None) -> None:
    """Generate and show the kingdom plot for the given daily date."""
    k, _ = get_daily_kingdom(date_str, manager)
    get_kingdom_quality_fig(k, add_buy_str=True)
    import matplotlib.pyplot as plt

    plt.show()
