import pandas as pd

from ....constants import PATH_ASSETS
from ....logger import LOGGER
from ....utils import write_dataframe_to_file
from .constants import PLAYLIST_DICT
from .download_yt_info import load_yt_info
from .process_titles import PROCESSOR_DICT


def perform_full_yt_processing(download: bool = True) -> None:
    """Perform the full processing pipeline for all playlists."""
    idx_dicts = {}
    for playlist_key, playlist_entry in PLAYLIST_DICT.items():
        LOGGER.info(f"Processing playlist: {playlist_key}")
        if download:
            load_yt_info(playlist_entry)
        processor = PROCESSOR_DICT.get(playlist_key)
        if processor:
            LOGGER.info(f"Applying processor for {playlist_key}")
            idx_dicts[playlist_key] = processor()
        else:
            LOGGER.warning(
                f"No processor defined for {playlist_key}, skipping processing step."
            )

    yt_id_df = pd.DataFrame.from_dict(idx_dicts, orient="index").T
    # Insert name column
    yt_id_df.insert(0, "name", yt_id_df.index)
    fpath = PATH_ASSETS / "other" / "yt_dailies_ids.csv"
    write_dataframe_to_file(yt_id_df.sort_values("name", ascending=False), fpath)
