"""Registering Dailies for Random Kingdominion."""

from ..constants import FPATH_KINGDOMS_MATCHES
from ..kingdom import KingdomManager


def register_match(
    kingdom_str: str,
    opponent: str,
    occasion: str,
    game_num: int,
    is_second_player: bool,
    replace: bool = False,
    validate: bool = True,
) -> KingdomManager:
    """Register the kingdom string for the given date in the tgg_dailies.txt file"""

    manager = KingdomManager()
    manager.load_matches()
    match_key = f"{occasion}_{opponent}_g{game_num}"
    if match_key in manager.kingdoms and not replace:
        raise ValueError(
            f"Match '{match_key}' already exists. To replace it, set replace=True."
        )
    notes = {
        "opponent": opponent,
        "occasion": occasion,
        "game_num": game_num,
        "second_player": is_second_player,
        "crucial_cards": [],
        "name": "",
        "subtitle": "",
        "ending": [],
        "points": [],
        "turns": [],
        "link": "",
    }
    manager.add_kingdom_from_string(
        match_key, kingdom_str, notes=notes, do_assertion=validate
    )
    manager.save_kingdoms_to_yaml(FPATH_KINGDOMS_MATCHES)
    return manager
