import pandas as pd
import streamlit as st

from ...constants import (
    FPATH_KINGDOMS_KOTW_REDDIT,
    FPATH_KINGDOMS_TGG_DAILIES,
    PATH_ASSETS,
)
from ...kingdom import KingdomManager
from ...utils import get_modification_timestamp
from ..combo_and_inter_setup.util import add_combo_inter_info_for_kingdoms
from ..constants import ST_ICONS
from .constants import OracleSelectionType


@st.cache_data
def load_link_dataframe(mod_time: int) -> pd.DataFrame:
    """Load the link DataFrame for existing kingdoms."""
    fpath = PATH_ASSETS / "other" / "yt_dailies_ids.csv"
    df = pd.read_csv(fpath, dtype=str, sep=";").fillna("").set_index("name")
    return df


def get_link_dataframe() -> pd.DataFrame:
    """Get the streamlit-cached link DataFrame."""
    fpath = PATH_ASSETS / "other" / "yt_dailies_ids.csv"
    mod_time = get_modification_timestamp(fpath)
    return load_link_dataframe(mod_time)


def get_links_for_kingdom(
    name: str, link_df: pd.DataFrame, youtubify: bool = False
) -> dict[str, str]:
    """Get all links for the given kingdom name from the link DataFrame."""
    if name not in link_df.index:
        return {}
    row: pd.Series = link_df.loc[name]  # type: ignore
    links = {col: row[col] for col in link_df.columns if row[col] != ""}
    if not youtubify:
        return links
    for k, v in links.items():
        links[k] = f"https://www.youtube.com/watch?v={v}"
    return links


def _get_display_name(row: pd.Series, seltype: OracleSelectionType) -> str:
    """Get the display name for the given kingdom row."""
    exps = row["expansions"]
    exp_repr = ", ".join(exps) if len(exps) < 4 else f"{len(exps)} expansions"
    notes = row["notes"]
    has_notes = isinstance(notes, dict)
    vid_icon = ST_ICONS["video"]
    has_video = row["has_video_link"]
    sani_wr = ""
    link_str = ""
    if seltype == "TGG Dailies":
        wr = row["winrate"] if "winrate" in row else ""
        sani_wr = f" [WR: {wr*100:.1f} %]" if wr else " [WR: N/A]"
        if (avail := row["avail_links"]) != "":
            link_str = f"[{vid_icon}{avail}]"
    special_name = f"[{vid_icon}{notes.get('name', '')}]" if has_notes else ""
    extra_name = " - "
    if has_video:
        extra_name += f"{link_str}{special_name}"
    display_name = f"{row['name']}{sani_wr}{extra_name} ({exp_repr})"
    return display_name


@st.cache_data
def _load_existing_kingdoms(
    selection_type: OracleSelectionType, mod_time: int
) -> pd.DataFrame:
    """Load kingdoms from the given selection type and return them as a DataFrame."""
    _ = mod_time + 1  # Dummy calculation to trigger cache invalidation
    manager = KingdomManager()
    if selection_type == "TGG Dailies":
        manager.load_tgg_dailies()
    elif selection_type == "TGG Campaigns":
        manager.load_campaigns(curated_only=True)
    elif selection_type == "Recommended":
        manager.load_recommended_kingdoms()
    elif selection_type == "Reddit's KOTW":
        manager.load_kingdoms_from_yaml(FPATH_KINGDOMS_KOTW_REDDIT)
    elif selection_type == "Fabi's Rec's":
        manager.load_fabi_recsets_kingdoms()
    elif selection_type == "Fabi's Matches":
        manager.load_matches()
    else:
        raise ValueError(f"Unknown selection type: {selection_type}")
    df = manager.dataframe_repr
    df = add_combo_inter_info_for_kingdoms(df)
    if "notes" not in df.columns:
        df["notes"] = ""

    df["link_fabi"] = df["notes"].apply(
        lambda x: "" if not isinstance(x, dict) else x.get("link", "")
    )
    df["has_video_link"] = df["link_fabi"] != ""
    link_df = get_link_dataframe()
    if selection_type == "TGG Dailies":
        df["avail_links"] = df["name"].apply(
            lambda x: ", ".join(
                [s[0] for s in sorted(get_links_for_kingdom(x, link_df))]
            )
        )
        df["has_video_link"] = df["avail_links"] != ""
    df["name_with_exps"] = df.apply(
        lambda x: _get_display_name(x, selection_type), axis=1
    )
    df["csos"] = df.apply(lambda x: x["cards"] + x["landscapes"], axis=1)
    return df


def get_existing_kingdoms(
    selection_type: OracleSelectionType,
) -> pd.DataFrame:
    """Get the streamlit-cached existing kingdoms DataFrame for the given selection type."""
    mod_time = get_modification_timestamp(FPATH_KINGDOMS_TGG_DAILIES)
    return _load_existing_kingdoms(selection_type, mod_time)
