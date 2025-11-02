from math import ceil
from typing import Callable

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageOps

from ....kingdom import Kingdom
from ....utils import (
    crop_img_by_percentage,
    get_cropped_card_img_without_text,
    get_cso_quality_description,
    invert_dict,
    load_cso_img_by_key,
    overlay_cutout,
    sanitize_cso_name,
)
from ...constants import ALL_CACHED_CSOS, ST_ICONS
from ...image_util import display_image_with_tooltip
from .extra_components_display import st_build_small_extra_component_display


def round_corners(img: Image.Image, radius: int, padding_px: int = 10) -> Image.Image:
    img = img.convert("RGBA")
    img = ImageOps.expand(img, border=padding_px, fill=(0, 0, 0, 0))
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    img.putalpha(mask)
    return img


def display_cso_image(cso: pd.Series, kingdom: Kingdom, full_image: bool = False):
    """Display the card image of a CSO with a tooltip containing the card's name, expansion, and text."""
    cso_key = str(cso.name)
    name = kingdom.get_cso_name_with_extra(cso_key)
    full_image = full_image or cso["IsExtendedLandscape"]
    img = (
        load_cso_img_by_key(cso_key)
        if full_image
        else get_cropped_card_img_without_text(cso_key)
    )
    # TODO: Add support for the full image positioning, currently it's ugly.
    if cso_key == "young_witch" and kingdom.bane_pile != "":
        bane_img = get_cropped_card_img_without_text(kingdom.bane_pile)
        img = overlay_cutout(img, bane_img, 0.4, (0.05, 0.4))
    elif cso_key == "ferryman" and kingdom.ferryman_pile != "":
        ferry_img = get_cropped_card_img_without_text(kingdom.ferryman_pile)
        img = overlay_cutout(img, ferry_img, 0.4, (0.55, 0.4))
    elif cso_key == "riverboat" and kingdom.riverboat_card != "":
        riv_img = get_cropped_card_img_without_text(kingdom.riverboat_card)
        img = overlay_cutout(img, riv_img, 0.35, (0.05, 0.4))
    elif cso_key == "druid" and len(kingdom.druid_boons) > 0:
        for i, boon in enumerate(kingdom.druid_boons):
            boon_img = load_cso_img_by_key(boon)
            boon_img = crop_img_by_percentage(boon_img, [0, 0, 1, 0.74])
            boon_img = ImageOps.expand(boon_img, border=3, fill="white")
            height_offset = 0.15 * i
            img = overlay_cutout(img, boon_img, 0.24, (0.56, 0.3 + height_offset))
    elif cso_key == "way_of_the_mouse" and kingdom.mouse_card != "":
        mouse_img = get_cropped_card_img_without_text(kingdom.mouse_card)
        img = overlay_cutout(img, mouse_img, 0.45, (0.65, 0.2))
    elif cso_key == "obelisk" and kingdom.obelisk_pile != "":
        obelisk_img = get_cropped_card_img_without_text(kingdom.obelisk_pile)
        img = overlay_cutout(img, obelisk_img, 0.45, (0.65, 0.2))
    elif cso_key == "approaching_army" and kingdom.army_pile != "":
        army_img = get_cropped_card_img_without_text(kingdom.army_pile)
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
        target_img = get_cropped_card_img_without_text(kingdom.trait_dict[cso_key])
        img = overlay_cutout(img, target_img, 0.45, (0.65, 0.2))
    if cso_key in kingdom.trait_dict.values():
        trait_key = invert_dict(kingdom.trait_dict)[cso_key]
        trait_img = load_cso_img_by_key(trait_key)
        trait_img = crop_img_by_percentage(trait_img, [0, 0.12, 0.063, 0.88])
        img = overlay_cutout(img, trait_img, 0.95, (0.01, 0.15))
    img = round_corners(img, 15)
    if st.session_state["kingdom_view_tooltips"]:
        tooltip = name + f"<br>(from the <b><em>{cso['Expansion']}</b></em> expansion)"
        quals = get_cso_quality_description(cso_key)
        if len(quals) > 0:
            tooltip += (
                f"<br><div style='text-align: left;'><b>Qualities</b><br>{quals}</div>"
            )
    else:
        tooltip = ""
    display_image_with_tooltip(
        img,
        tooltip,
        cso["WikiLink"],
    )


def _build_single_reroll_button(cso_name: str, reroll_callback: Callable[[str], None]):
    if st.button(
        "Reroll",
        on_click=lambda c=cso_name: reroll_callback(sanitize_cso_name(c)),
        key=f"reroll_{cso_name}",
        use_container_width=True,
        type="primary",
    ):
        st.rerun()


def _display_shelter_use(k: Kingdom):
    with st.container(border=True):
        st.write("Use Shelters.")
        cols = st.columns(3)
        for cso_name, col in zip(["hovel", "necropolis", "overgrown_estate"], cols):
            cso: pd.Series = ALL_CACHED_CSOS.loc[cso_name]  # type: ignore
            with col:
                display_cso_image(
                    cso, k, full_image=st.session_state["kingdom_view_full_image"]
                )


def _display_colony_use(k: Kingdom):
    with st.container(border=True):
        st.write("Use Colony/Platinum.")
        cols = st.columns(2)
        for cso_name, col in zip(["colony", "platinum"], cols):
            cso: pd.Series = ALL_CACHED_CSOS.loc[cso_name]  # type: ignore
            with col:
                display_cso_image(
                    cso, k, full_image=st.session_state["kingdom_view_full_image"]
                )


def st_build_kingdom_image_display(
    k: Kingdom, single_reroll_callback: Callable[[str], None] | None = None
):
    """Display the images of the cards and landscapes in the kingdom."""

    flex = st.container(horizontal=True, horizontal_alignment="center")
    sorting_options = {
        "Alphabetical": ["Name"],
        "Cost": ["CostSort", "Name"],
        "Expansion": ["Expansion", "Name"],
    }
    flex.radio(
        "Sorting options",
        list(sorting_options.keys()),
        index=1,
        key="Kingdom sorting",
        horizontal=True,
        width="stretch",
        help="Select how to sort the cards in the kingdom display.",
    )
    flex.checkbox("Show full images", False, key="kingdom_view_full_image")
    flex.checkbox(
        "Show Tooltips",
        False,
        key="kingdom_view_tooltips",
        help="Whether to show tooltips upon hovering over the card images, containing the card name, expansion, and qualities.",
    )
    if single_reroll_callback is not None:
        flex.checkbox("Show reroll buttons", True, key="show_reroll_buttons")
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
            if (
                single_reroll_callback is not None
                and st.session_state["show_reroll_buttons"]
            ):
                _build_single_reroll_button(card["Name"], single_reroll_callback)
    num_cols = max(4, len(k.kingdom_landscape_df))
    # Now, build the landscape display
    for i, (_, ls) in enumerate(k.kingdom_landscape_df.iterrows()):
        if i % num_cols == 0:
            cols = st.columns(num_cols)
        with cols[i % num_cols]:
            display_cso_image(ls, k)
            if (
                single_reroll_callback is not None
                and st.session_state["show_reroll_buttons"]
            ):
                _build_single_reroll_button(ls["Name"], single_reroll_callback)
    # Now, build display for col/plat and/or shelters:
    num_extra = np.array([k.use_shelters, k.use_colonies], dtype="bool").sum()
    if num_extra > 0:
        cols = st.columns(int(num_extra))
        if k.use_shelters:
            with cols[0]:
                _display_shelter_use(k)
            if k.use_colonies:
                with cols[1]:
                    _display_colony_use(k)
        else:
            with cols[0]:
                _display_colony_use(k)
    # Extra components:
    with st.expander(
        "Extra setup components", expanded=False, icon=ST_ICONS["components"]
    ):
        st_build_small_extra_component_display(k)
