
import streamlit as st

from ..constants import ALL_CSOS
from .image_handling import img_to_html


def toggle_showing_info():
    st.session_state["show_further_info"] = not st.session_state.get(
        "show_further_info", False
    )

@st.fragment
def _build_page_info(desc: str, link_help: str = ""):
    if link_help == "":
        st.info(desc)
        return
    cols = st.columns([0.9, 0.1], vertical_alignment="top")
    with cols[0]:
        st.info(desc)
    with cols[1]:
        st.page_link(
            "streamlit_pages/about.py",
            label="More details",
            icon="❓",
            use_container_width=True,
            help=link_help,
        )


def build_page_header(title: str, desc: str, link_help: str = ""):
    """Build the header of a page with a title, description, and a button to show more info which reveals the description."""
    cols = st.columns([0.9, 0.1], vertical_alignment="top")
    with cols[0]:
        st.write("# " + title, unsafe_allow_html=True)
    button_text = "➖\tℹ️" if st.session_state.get("show_further_info") else "➕\tℹ️"
    cols[1].button(
        button_text,
        on_click=toggle_showing_info,
        use_container_width=True,
        key="show_more_info",
        help="Show more info about the page.",
    )
    if st.session_state.get("show_further_info", False):
        _build_page_info(desc, link_help)



@st.cache_data
def load_main_df():
    """Cache the CSOs for streamlit (Not sure this is the correct way)"""
    ALL_CSOS["Name and Expansion"] = ALL_CSOS.apply(
        lambda x: f"{x['Name']} ({x['Expansion']})", axis=1
    )
    return ALL_CSOS


MAIN_DF = load_main_df()


@st.cache_data
def get_cached_unique_types():
    unique_types = set()
    MAIN_DF["Types"].apply(lambda x: unique_types.update(x))
    return sorted(unique_types)


def _get_card_cost_fpaths(card_cost: str) -> list[str]:
    repl_dict = {"*": "star", "+": "plus", "P": " 74px-Potion", "$": "120px-Coin"}
    for key, value in repl_dict.items():
        card_cost = card_cost.replace(key, value)
    substrings = card_cost.split()
    if "D" in substrings[-1]:
        substrings[-1] = "Debt" + substrings[-1].replace("D", "")
    return [f"{sub}.png" for sub in substrings]


def get_cost_html(cost_str: str) -> str:
    """Convert a card cost string to an HTML string with images of the cost components."""
    costs = _get_card_cost_fpaths(cost_str)
    cost_img_str = ""
    for cost_str in costs:
        cost_img_str += img_to_html(f"./static/icons/{cost_str}")
    return cost_img_str
