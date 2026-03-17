from datetime import datetime

import requests
from yt_dlp import YoutubeDL

from random_kingdominion.constants import PATH_ASSETS

from ....logger import LOGGER
from .util import yml_load_entries, yml_save_entries


def _process_subtitles(subtitles_dict: dict, key):
    """Process the subtitles dict to extract the English automatic subtitles."""
    if "en" not in subtitles_dict:
        return
    url = subtitles_dict["en"].get("url")
    if not url:
        return
    vtt_text = requests.get(url).text

    fpath = PATH_ASSETS / f"other/yt_stats/fabyy_transcriptions/{key}.vtt"
    fpath.write_text(vtt_text, encoding="utf-8")


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
    if playlist_dict_entry["key"] == "fabyy_dailies":
        ydl_opts["writesubtitles"] = True
        ydl_opts["writeautomaticsub"] = True
        ydl_opts["subtitleslangs"] = ["en"]

    with YoutubeDL(ydl_opts) as ydl:  # type: ignore
        info = ydl.extract_info(playlist_url, download=False)
    good_cols = playlist_dict_entry["cols"].copy()
    for entry in info.get("entries", []):
        req_sub = entry.get("requested_subtitles", None)
        if isinstance(entry, dict) and req_sub is not None:
            _process_subtitles(req_sub, entry["id"])

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
