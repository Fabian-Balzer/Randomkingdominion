import pandas as pd
import streamlit as st

from ..kingdom import Kingdom, sanitize_cso_name
from .cso_df_display import display_stylysed_cso_df
from .helpers import display_image_with_tooltip
from .plot_display import display_kingdom_plot
from .randomizer_util import reroll_cso, reroll_selected_csos


def display_card_image(cso: pd.Series, full_image: bool = False):
    """Display the card image of a CSO with a tooltip containing the card's name, expansion, and text."""
    img_fpath = "./static/card_pictures/" + cso["ImagePath"]
    crop_rect = None if full_image else [0, 0, 1, 16 / 30]
    first_tt = (
        cso["Name"] + f"<br>(from the <b><em>{cso['Expansion']}</b></em> expansion)"
    )
    first_tt += f"<br>Click to open the Dominion Strategy Wiki page"
    display_image_with_tooltip(
        img_fpath,
        first_tt,
        cso["WikiLink"],
        crop_rect=crop_rect,
    )
    if full_image:
        return
    display_image_with_tooltip(
        img_fpath,
        cso["Text"].replace("\n", "<br>"),
        cso["WikiLink"],
        crop_rect=[0, 62 / 70, 1, 1],
    )


def display_landscape_image(cso: pd.Series, full_image: bool = False):
    """Display the landscape image of a CSO with a tooltip containing the landscape's name and expansion."""
    img_fpath = "./static/card_pictures/" + cso["ImagePath"]
    crop_rect = None if full_image else [0, 0, 1, 22 / 30]
    first_tt = (
        cso["Name"] + f"<br>(from the <b><em>{cso['Expansion']}</b></em> expansion)"
    )
    if not full_image:
        first_tt += "<br>" + cso["Text"].replace("\n", "<br>")
    first_tt += f"<br>Click to open the Dominion Strategy Wiki page"
    display_image_with_tooltip(
        img_fpath,
        first_tt,
        "https://wiki.dominionstrategy.com/index.php/" + cso["Name"].replace(" ", "_"),
        crop_rect=crop_rect,
    )


def _build_single_reroll_button(cso_name: str):
    if st.button(
        "Reroll",
        on_click=lambda c=cso_name: reroll_cso(sanitize_cso_name(c)),
        key=f"reroll_{cso_name}",
        use_container_width=True,
    ):
        st.rerun()


def _build_reroll_selection_button(key: str):
    if st.button(
        "Reroll selected CSOs",
        help="Reroll the CSOs you selected to generate a new kingdom.",
        on_click=reroll_selected_csos,
        use_container_width=True,
        key=key,
    ):
        st.rerun()


def display_full_kingdom_images(k: Kingdom, show_reroll=True):
    """Display the images of the cards and landscapes in the kingdom."""

    cols = st.columns([0.3, 0.5, 0.2])
    sorting_options = {
        "Alphabetical": ["Name"],
        "Cost": ["CostSort", "Name"],
        "Expansion": ["Expansion", "Name"],
    }
    with cols[0]:
        st.write("Sorting options")
    with cols[1]:
        st.radio(
            "Sorting options",
            list(sorting_options.keys()),
            index=1,
            key="Kingdom sorting",
            horizontal=True,
            label_visibility="collapsed",
        )
    with cols[2]:
        st.checkbox("Show full images", False, key="kingdom_view_full_image")
    cards = k.kingdom_card_df
    cards["CostSort"] = cards["Cost"].str.replace("$", "Z")
    cards = cards.sort_values(sorting_options[st.session_state["Kingdom sorting"]])
    # First, build the card display
    for i, (card_index, card) in enumerate(cards.iterrows()):
        if i % 5 == 0:
            cols = st.columns(5)
        with cols[i % 5]:
            display_card_image(
                card, full_image=st.session_state["kingdom_view_full_image"]
            )
            if show_reroll:
                _build_single_reroll_button(card["Name"])
    # Now, build the landscape display
    for i, (_, ls) in enumerate(k.kingdom_landscape_df.iterrows()):
        if i % 4 == 0:
            cols = st.columns(4)
        with cols[i % 4]:
            display_landscape_image(
                ls, full_image=st.session_state["kingdom_view_full_image"]
            )
            if show_reroll:
                _build_single_reroll_button(ls["Name"])


def display_kingdom(k: Kingdom, show_reroll=True):
    df = k.full_kingdom_df.set_index("Name")
    tabs = st.tabs(["Compact View", "Data View", "Plot View"])
    with tabs[0]:
        with st.expander("Kingdom Image Display", expanded=False):
            display_full_kingdom_images(k, show_reroll=show_reroll)
        cols = st.columns(2)
        with cols[0]:
            display_stylysed_cso_df(
                df[["Expansion", "Cost"]],
                with_reroll=show_reroll,
                use_container_width=True,
            )
            if show_reroll:
                _build_reroll_selection_button("Reroll all")
        with cols[1]:
            display_kingdom_plot(k)
    with tabs[1]:
        # Don't add reroll here as it can lead to confusing behavior between the two tabs
        display_stylysed_cso_df(df)
    with tabs[2]:
        with st.columns([0.2, 0.5, 0.2])[1]:
            with st.container(border=True):
                display_kingdom_plot(k)


@st.fragment
def display_current_kingdom():
    k = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    display_kingdom(k)
