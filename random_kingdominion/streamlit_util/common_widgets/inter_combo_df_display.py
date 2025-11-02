import pandas as pd
import streamlit as st
from streamlit.elements.lib.column_types import ColumnConfig

from ..constants import COMBO_COLOR_DICT, ST_ICONS


def _get_common_column_config() -> dict[str, ColumnConfig]:
    """Returns the common column config for both combos and interactions."""
    return {
        "img_1": st.column_config.ImageColumn("Img 1", width=22),  # type: ignore
        "img_2": st.column_config.ImageColumn("Img 2", width=22),  # type: ignore
        "CSO 1": st.column_config.TextColumn("CSO 1", width=60),  # type: ignore
        "CSO 2": st.column_config.TextColumn("CSO 2", width=60),  # type: ignore
        "exp_img_1": st.column_config.ImageColumn("Exp 1", width=22),  # type: ignore
        "exp_img_2": st.column_config.ImageColumn("Exp 2", width=22),  # type: ignore
    }


def _highlight_combo_types(df: pd.DataFrame) -> pd.DataFrame:
    """Highlights the combo types in the DataFrame."""
    # Dark yellow, dark green, green, light green, dark red, grey:

    def highlight_type(val: str) -> str:
        return f"background-color: {COMBO_COLOR_DICT.get(val, '')}"

    return df.style.map(highlight_type, subset=["Type"])  # type: ignore


def _highlight_combo_yt_types(df: pd.DataFrame) -> pd.DataFrame:
    """Highlights the combo types in the DataFrame."""
    if not "YTComment" in df.columns:
        return df

    def highlight_yt(val: str) -> str:
        color = ""
        if "showcase" in val.lower():
            color = "#3FAE59"
        elif "playthrough" in val.lower():
            color = "#2e45a8"
        elif "match" in val.lower():
            color = "#a82e4b"
        return f"background-color: {color}70" if color else ""

    return df.map(highlight_yt, subset=["YTComment"])  # type: ignore


def st_display_combo_df(df: pd.DataFrame):
    """Displays the combos DataFrame"""
    col_config = _get_common_column_config()
    col_config.update(
        {
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Description": st.column_config.TextColumn("Description"),
            "YTLink": st.column_config.LinkColumn(
                "YouTube Link",
                help="Link to a YouTube video explaining the combo, or a video where it just occurs.",
                width=22,
                display_text="To YT",
            ),
            # TODO: Once implemented by streamlit, combine those columns to have the link display text be the comment. As of streamlit 1.5.0 this is not possible, it only allows for a fixed display text.
            "YTComment": st.column_config.TextColumn(
                "YouTube Info",
                help="More information about the YouTube link.",
                width=100,
            ),
        }
    )
    columns = [
        "CSO 1",
        "CSO 2",
        "Type",
        "Description",
        "img_1",
        "img_2",
        "exp_img_1",
        "exp_img_2",
    ]
    if (df["YTLink"] != "").any():
        columns.append("YTLink")
        columns.append("YTComment")
    df = _highlight_combo_types(df)
    df = _highlight_combo_yt_types(df)
    with st.container():
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            column_config=col_config,
            column_order=columns,
        )


def st_display_inter_df(df: pd.DataFrame):
    """Displays the interactions DataFrame"""
    col_config = _get_common_column_config()
    col_config.update(
        {
            "Rule": st.column_config.TextColumn("Interaction Description"),
        }
    )
    with st.container():
        st.dataframe(
            df,
            hide_index=True,
            width="stretch",
            column_config=col_config,
            column_order=[
                "CSO 1",
                "CSO 2",
                "Rule",
                "img_1",
                "img_2",
                "exp_img_1",
                "exp_img_2",
            ],
        )


def _get_combo_row_md(row: pd.Series, include_images: bool = True) -> str:
    """Returns the markdown string for a single combo row."""
    images = ""
    if include_images:
        images = f"""
<img src="{row['img_1']}" alt="{row['CSO 1']}" width="32" height="45" style="border-radius:5px; box-shadow:0 0 5px rgba(0,0,0,0.2);"/>
<img src="{row['img_2']}" alt="{row['CSO 2']}" width="32" height="45" style="border-radius:5px; box-shadow:0 0 5px rgba(0,0,0,0.2);"/>"""
    yt_link = ""
    if row["YTLink"] != "":
        yt_link = f"""<br/><a href="{row['YTLink']}" target="_blank" style="text-decoration:none; color:#FF0000; font-weight:bold;">{ST_ICONS['video']} YouTube Video</a>"""
    colored_type = f'<em style="background-color:{COMBO_COLOR_DICT.get(row['Type'], '#000')}">{row['Type']}</em>'
    sanitized_desc = row["Description"].replace("\n", "<br/>").replace("$", r"\$")

    text = f"""{images}
- **{row['CSO 1']} and {row['CSO 2']} ({colored_type})**\\
{sanitized_desc}
{yt_link}"""
    return text


def st_display_combo_md(df: pd.DataFrame, include_images: bool = True):
    """Displays the combos in markdown."""
    for _, row in df.iterrows():
        st.markdown(
            _get_combo_row_md(row, include_images=include_images),
            unsafe_allow_html=True,
        )


def _get_inter_row_md(row: pd.Series, include_images: bool = True) -> str:
    """Returns the markdown string for a single interaction row."""
    images = ""
    if include_images:
        images = f"""
<img src="{row['img_1']}" alt="{row['CSO 1']}" width="32" height="45" style="border-radius:5px; box-shadow:0 0 5px rgba(0,0,0,0.2);"/>
<img src="{row['img_2']}" alt="{row['CSO 2']}" width="32" height="45" style="border-radius:5px; box-shadow:0 0 5px rgba(0,0,0,0.2);"/>"""
    sanitized_rule = row["Rule"].replace("\n", "<br/>").replace("$", r"\$")

    text = f"""{images}
- **{row['CSO 1']} and {row['CSO 2']}**\\
{sanitized_rule}"""
    return text


def st_display_inter_md(df: pd.DataFrame, include_images: bool = True):
    """Displays the interactions in markdown."""
    for _, row in df.iterrows():
        st.markdown(
            _get_inter_row_md(row, include_images=include_images),
            unsafe_allow_html=True,
        )
