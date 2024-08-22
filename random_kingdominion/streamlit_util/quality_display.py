import streamlit as st

from ..constants import PATH_ASSETS, QUALITIES_AVAILABLE
from .constants import ALL_CACHED_CSOS, STATIC_FPATH
from .cso_df_display import display_stylysed_cso_df
from .helpers import build_page_header, img_to_html


def get_qual_image_html(qual: str, size: int | None = None):
    img = img_to_html(STATIC_FPATH.joinpath(f"icons/qualities/{qual}.jpg"))
    if size is not None:
        img = img.replace("auto", f"{size}px")
    return img


def build_quality_page(qual: str):
    assert qual in QUALITIES_AVAILABLE, f"Quality '{qual}' not valid."
    fpath = PATH_ASSETS.joinpath(f"../card_info/quality_descriptions/{qual}.md")
    with fpath.open() as f:
        desc_lines = f.readlines()
    qual_string = qual.capitalize().replace("Altvp", "Alternative VP")
    desc = f"The {qual_string} quality is one of the core engine qualities of Dominion Card-Shaped Objects (CSOs) I have identified, and is used both to randomize and to visualize kingdoms (see the *randomizer* or the *oracle*). This page provides a brief explanation as well as a summary of all CSOs with that quality."
    if qual == "interactivity":
        desc = desc.replace("core engine qualities", "qualities")
    build_page_header(
        f"{get_qual_image_html(qual)} {qual_string}",
        desc,
        "Look here for a general overview of what this website offers.",
    )
    desc_lines = [line for line in desc_lines if not line.startswith("## ")]
    desc = "".join(desc_lines).replace("##", "#")
    parts = desc.split("##")
    st.write(parts[0])
    part1_header = f"{qual_string}: Quality assessments"
    part1 = parts[1].replace(f"{qual_string} Quality", "")
    with st.expander(part1_header, expanded=False):
        st.write(part1)
    if len(parts) > 2:
        part2_header = f"{qual_string}: Type classification"
        part2 = parts[2].replace(f"{qual_string} Types", "")
        with st.expander(part2_header, expanded=False):
            st.write(part2)
    else:
        st.write("No types information assigned for this quality.")
    df = ALL_CACHED_CSOS[ALL_CACHED_CSOS[f"{qual}_quality"] > 0].set_index("Name")
    st.write(
        f"## All {len(df)} CSOs with any {qual} quality\n\nHint: *Click on the column headers to sort the table.*"
    )
    display_stylysed_cso_df(df)


EMOJI_DICT = {
    "village": "🏘️",
    "draw": "🎨",
    "thinning": "🗑️",
    "gain": "💰",
    "attack": "⚔️",
    "altvp": "🏆",
    "interactivity": "💑",
}

SHORT_DESCS = {
    "village": "...play more than one terminal per turn.",
    "draw": "...increase your handsize.",
    "thinning": "...remove cards from your deck.",
    "gain": "...gain more than one card per turn.",
    "attack": "...attack other players, directly or indirectly.",
    "altvp": "...give access to VP in alternative ways than just Provinces/Duchies/Estates (therefore includes Cursing).",
    "interactivity": "...foster player interactions.",
}


def get_quality_page_navigation(qual: str):
    return st.Page(
        f"streamlit_pages/qualities/{qual}.py",
        title=qual.capitalize(),
        icon=EMOJI_DICT[qual],
        url_path=f"{qual}_qual",
    )


def construct_short_qual_desc(qual: str) -> str:
    link = f'<a href="{qual}_qual" target="_self">{qual.capitalize()}</a>'
    return f"{get_qual_image_html(qual, 30)} **{link}**: {SHORT_DESCS[qual]}"
    # st.page_link(
    #     f"streamlit_pages/qualities/{qual}.py",
    #     label=f"{header}{SHORT_DESCS[qual]}",
    #     icon=EMOJI_DICT[qual],
    #     help=f"Navigate to the page for the {qual} quality.",
    # )
    # return
    cols = st.columns([0.9, 0.1], vertical_alignment="center")
    with cols[1]:
        img_path = STATIC_FPATH.joinpath(f"icons/qualities/{qual}.jpg")
        st.image(str(img_path), use_column_width=True)
    with cols[0]:
        st.page_link(
            f"streamlit_pages/qualities/{qual}.py",
            label=f"{qual.capitalize()}",
            icon=EMOJI_DICT[qual],
            help=f"Navigate to the page for the {qual} quality.",
        )
    # img = _get_qual_image_html(qual, 40)
    # return f"{img}[{qual.capitalize()}](./{qual}_qual)"
