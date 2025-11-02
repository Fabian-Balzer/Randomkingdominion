from datetime import datetime

from yt_dlp import YoutubeDL

from ....logger import LOGGER
from .util import yml_load_entries, yml_save_entries


def load_yt_info(playlist_dict_entry: dict) -> list[dict]:
    playlist_url = playlist_dict_entry["url"]
    key = playlist_dict_entry["key"]
    existing_entries = yml_load_entries(key)
    LOGGER.info(f"{key}: Loaded {len(existing_entries)} existing entries.")

    def _skip_if_seen(info_dict, *args, **kwargs):
        """Skip if the entry has already been processed."""
        existing_ids = [e["id"] for e in existing_entries]
        existing_ids.append("WWMUBY8e_rI")  # This one was deleted
        if info_dict.get("id") in existing_ids:
            return "Skipping (already processed)"
        return None  # None means keep

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "match_filter": _skip_if_seen,
        "format": "bestaudio/best",  # dummy format so it doesn’t probe
        "ignoreerrors": True,
        "nocheckcertificate": True,
        "force_generic_extractor": True,  # stops fancy format logic
    }
    if playlist_dict_entry.get("flat", False):
        ydl_opts["extract_flat"] = "in_playlist"

    with YoutubeDL(ydl_opts) as ydl:  # type: ignore
        info = ydl.extract_info(playlist_url, download=False)

    good_cols = playlist_dict_entry["cols"]

    new_entries = [
        {k: v for k, v in entry.items() if k in good_cols}
        for entry in info.get("entries", [])
        if isinstance(entry, dict)
    ]
    if len(new_entries) == 0:
        LOGGER.info(f"{key}: No new entries found")
        return existing_entries
    LOGGER.info(f"{key}: Adding {len(new_entries)} new entries")

    for entry in new_entries:
        entry["retrieval_time"] = datetime.now().isoformat()
    try:
        entries = existing_entries + new_entries  # type: ignore
        yml_save_entries(entries, playlist_dict_entry["key"])
    except Exception as e:
        LOGGER.error("Error occurred while saving entries:", e)
    return entries
