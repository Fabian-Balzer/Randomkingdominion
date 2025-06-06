from math import ceil

import pandas as pd
import streamlit as st
from PIL import ImageOps
from st_copy_to_clipboard import st_copy_to_clipboard

from ..constants import ALL_CSOS
from ..kingdom import Kingdom, sanitize_cso_name
from ..utils import (
    crop_img_by_percentage,
    get_card_img_without_text,
    get_cso_quality_description,
    invert_dict,
    load_cso_img_by_key,
    overlay_cutout,
)
from .cso_df_display import display_stylysed_cso_df
from .image_handling import display_image_with_tooltip
from .plot_display import display_kingdom_plot
from .randomizer_util import reroll_cso, reroll_selected_csos


@st.fragment
def build_clipboard_button(state_key: str):
    csv_str = Kingdom.from_dombot_csv_string(
        st.session_state[state_key]
    ).get_dombot_csv_string()
    st_copy_to_clipboard(
        csv_str,
        before_copy_label="📋Copy to clipboard",
        after_copy_label="Copied! Ready to be pasted in your favorite client.",
        key=csv_str,
    )
    # st.button(
    #     "🔼To clipboard",
    #     help="Copy the kingdom's DomBot string to your clipboard",
    #     on_click=lambda: copy_to_clipboard(csv_str),
    #     use_container_width=True,
    # )


def display_cso_image(cso: pd.Series, kingdom: Kingdom, full_image: bool = False):
    """Display the card image of a CSO with a tooltip containing the card's name, expansion, and text."""
    cso_key = str(cso.name)
    name = kingdom.get_cso_name_with_extra(cso_key)
    tooltip = name + f"<br>(from the <b><em>{cso['Expansion']}</b></em> expansion)"
    quals = get_cso_quality_description(cso_key)
    if len(quals) > 0:
        tooltip += (
            f"<br><div style='text-align: left;'><b>Qualities</b><br>{quals}</div>"
        )
    full_image = full_image or cso["IsExtendedLandscape"]
    img = (
        load_cso_img_by_key(cso_key)
        if full_image
        else get_card_img_without_text(cso_key)
    )
    # TODO: Add support for the full image positioning, currently it's ugly.
    if cso_key == "young_witch" and kingdom.bane_pile != "":
        bane_img = get_card_img_without_text(kingdom.bane_pile)
        img = overlay_cutout(img, bane_img, 0.4, (0.05, 0.4))
    elif cso_key == "ferryman" and kingdom.ferryman_pile != "":
        ferry_img = get_card_img_without_text(kingdom.ferryman_pile)
        img = overlay_cutout(img, ferry_img, 0.4, (0.55, 0.4))
    elif cso_key == "riverboat" and kingdom.riverboat_card != "":
        riv_img = get_card_img_without_text(kingdom.riverboat_card)
        img = overlay_cutout(img, riv_img, 0.35, (0.05, 0.4))
    elif cso_key == "druid" and len(kingdom.druid_boons) > 0:
        for i, boon in enumerate(kingdom.druid_boons):
            boon_img = load_cso_img_by_key(boon)
            boon_img = crop_img_by_percentage(boon_img, [0, 0, 1, 0.74])
            boon_img = ImageOps.expand(boon_img, border=3, fill="white")
            height_offset = 0.15 * i
            img = overlay_cutout(img, boon_img, 0.24, (0.56, 0.3 + height_offset))
    elif cso_key == "way_of_the_mouse" and kingdom.mouse_card != "":
        mouse_img = get_card_img_without_text(kingdom.mouse_card)
        img = overlay_cutout(img, mouse_img, 0.45, (0.65, 0.2))
    elif cso_key == "obelisk" and kingdom.obelisk_pile != "":
        obelisk_img = get_card_img_without_text(kingdom.obelisk_pile)
        img = overlay_cutout(img, obelisk_img, 0.45, (0.65, 0.2))
    elif cso_key == "approaching_army" and kingdom.army_pile != "":
        army_img = get_card_img_without_text(kingdom.army_pile)
        img = overlay_cutout(img, army_img, 0.45, (0.65, 0.2))
    if cso_key == kingdom.obelisk_pile:
        obelisk_img = load_cso_img_by_key("obelisk")
        obelisk_img = crop_img_by_percentage(obelisk_img, [0.28, 0, 0.72, 0.1])
        img = overlay_cutout(img, obelisk_img, 0.67, (0.28, 0.78))
    if cso_key == kingdom.bane_pile:
        witch = load_cso_img_by_key("young_witch")
        witch = crop_img_by_percentage(witch, [0.5, 0.1, 0.9, 0.5])
        witch = ImageOps.expand(witch, border=3, fill="white")
        img = overlay_cutout(img, witch, 0.5, (0.77, 0.18))
    if cso_key == kingdom.army_pile:
        army = load_cso_img_by_key("approaching_army")
        army = crop_img_by_percentage(army, [0.3, 0.1, 0.65, 0.65])
        army = ImageOps.expand(army, border=3, fill="white")
        img = overlay_cutout(img, army, 0.45, (0.08, 0.18))
    if cso_key in kingdom.trait_dict:
        target_img = get_card_img_without_text(kingdom.trait_dict[cso_key])
        img = overlay_cutout(img, target_img, 0.45, (0.65, 0.2))
    if cso_key in kingdom.trait_dict.values():
        trait_key = invert_dict(kingdom.trait_dict)[cso_key]
        trait_img = load_cso_img_by_key(trait_key)
        trait_img = crop_img_by_percentage(trait_img, [0, 0.12, 0.063, 0.88])
        img = overlay_cutout(img, trait_img, 0.95, (0.01, 0.15))
    display_image_with_tooltip(
        img,
        tooltip,
        cso["WikiLink"],
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

    col_proportions = [0.3, 0.5, 0.2]
    if show_reroll:
        col_proportions.append(0.2)
    cols = st.columns(col_proportions)
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
    if show_reroll:
        with cols[3]:
            st.checkbox("Show reroll buttons", False, key="show_reroll_buttons")
    cards = k.kingdom_card_df
    cards["CostSort"] = cards["Cost"].str.replace("$", "Z")
    cards = cards.sort_values(sorting_options[st.session_state["Kingdom sorting"]])
    num_cols = ceil(len(cards) / 2)
    # First, build the card display
    has_cost_sort = st.session_state["Kingdom sorting"] == "Cost"
    iterable = reversed(list(cards.iterrows())) if has_cost_sort else cards.iterrows()
    for i, (card_index, card) in enumerate(iterable):
        if i % num_cols == 0:
            cols = st.columns(num_cols)
        index = num_cols - i % num_cols - 1 if has_cost_sort else i % num_cols
        with cols[index]:
            display_cso_image(
                card, k, full_image=st.session_state["kingdom_view_full_image"]
            )
            if show_reroll and st.session_state["show_reroll_buttons"]:
                _build_single_reroll_button(card["Name"])
    num_cols = max(4, len(k.kingdom_landscape_df))
    # Now, build the landscape display
    for i, (_, ls) in enumerate(k.kingdom_landscape_df.iterrows()):
        if i % num_cols == 0:
            cols = st.columns(num_cols)
        with cols[i % num_cols]:
            display_cso_image(ls, k)
            if show_reroll and st.session_state["show_reroll_buttons"]:
                _build_single_reroll_button(ls["Name"])


def build_csv_display():
    cols = st.columns([0.85, 0.15], vertical_alignment="top")
    with cols[0]:
        with st.expander("Descriptive string", expanded=False):
            st.code(
                Kingdom.from_dombot_csv_string(
                    st.session_state["randomized_kingdom"]
                ).get_dombot_csv_string()
            )
            st.write(
                "You can copy this to your clipboard and paste it into the interface of your preferred digital Dominion client.\\\nShould work both for [Dominion Online](https://dominion.games/) and the [TGG implementation](https://store.steampowered.com/app/1131620/Dominion/).",
                unsafe_allow_html=True,
            )
    with cols[1]:
        build_clipboard_button("randomized_kingdom")


def display_kingdom(k: Kingdom, is_randomizer_view=True):
    df = k.full_kingdom_df.set_index("Name")
    tab_names = ["Compact View", "Data View"]
    if is_randomizer_view:
        tab_names.append("Plot View")
    tabs = st.tabs(tab_names)
    with tabs[0]:
        with st.expander("Kingdom Image Display", expanded=is_randomizer_view):
            display_full_kingdom_images(k, show_reroll=is_randomizer_view)
        expander_label = "Shortened Info" if is_randomizer_view else "Overview plot"
        with st.expander(expander_label, expanded=not is_randomizer_view):
            if is_randomizer_view:
                cols = st.columns(2)
                with cols[0]:
                    display_stylysed_cso_df(
                        df[["ImagePath", "Expansion", "Cost"]],
                        with_reroll=is_randomizer_view,
                        use_container_width=True,
                    )
                    if is_randomizer_view:
                        _build_reroll_selection_button("Reroll selection")
                with cols[1]:
                    display_kingdom_plot(k)
            else:
                display_kingdom_plot(k, with_border=True)
                st.info(
                    "*Hint: Hover over the images in the kingdom image display (above) to directly see the individual cards' qualities.*"
                )
    with tabs[1]:
        # Don't add reroll here as it can lead to confusing behavior between the two tabs
        display_stylysed_cso_df(df)
    if is_randomizer_view:
        with tabs[2]:
            display_kingdom_plot(k, with_border=True)
        build_csv_display()
    if len(inter := k.get_interactions()) > 0:
        st.write("#### Special Interactions (rules-wise)")
        for _, (c1, c2, rule) in inter.iterrows():
            c1 = ALL_CSOS.loc[c1]["Name"]
            c2 = ALL_CSOS.loc[c2]["Name"]
            st.write(f"- **{c1} and {c2}**: {rule}")
    else:
        st.write(
            "No special rules interactions found [which doesn't mean there are none, let me know about any you find!]."
        )


def display_current_kingdom():
    k = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    with st.container(border=True):
        st.write("### Current Kingdom (scroll down for new randomization)")
        display_kingdom(k)
