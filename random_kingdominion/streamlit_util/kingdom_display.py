from math import ceil
from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageOps

from random_kingdominion.streamlit_util.randomization_options.expansion_select import (
    display_exp_image,
)
from random_kingdominion.utils.plotting.quality_plot_helper import (
    plot_kingdom_qualities,
)

from ..kingdom import Kingdom
from ..utils import (
    crop_img_by_percentage,
    filter_combo_or_inter_df_for_csos,
    get_card_img_without_text,
    get_cso_quality_description,
    invert_dict,
    load_cso_img_by_key,
    overlay_cutout,
    sanitize_cso_name,
)
from .combos_and_interactions import st_display_combo_df, st_display_inter_df
from .constants import (
    ALL_CACHED_CSOS,
    ST_ICONS,
    get_cached_combo_df,
    get_cached_inter_df,
)
from .cso_df_display import display_stylysed_cso_df
from .image_handling import display_image_with_tooltip
from .kingdom_readout import build_incomplete_randomization_warning
from .plot_display import st_display_kingdom_plot
from .randomizer_util import reroll_cso, reroll_selected_csos


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
    img = round_corners(img, 15)
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
        type="primary",
    ):
        st.rerun()


def _build_reroll_selection_button(key: str):
    if st.button(
        "Reroll selected CSOs",
        help="Reroll the CSOs you selected to generate a new kingdom.",
        on_click=reroll_selected_csos,
        use_container_width=True,
        key=key,
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


def _display_extra_components(k: Kingdom, show_exp=False):
    """Display extra components needed for the kingdom."""
    text = k.get_component_string(
        show_exp=show_exp, cutoff_len=None, exclude_trash_mat=False
    ).replace("EXTRAS:", "")
    text = "- " + "\n- ".join(text.split(", "))
    st.write(text)


def _display_all_components(k: Kingdom):
    """Display all components needed for the kingdom, grouped by expansion."""
    tabs = st.tabs(
        ["Cards and Landscapes", "Extra Components"], default="Extra Components"
    )
    exp_groups = k.full_kingdom_df.groupby("Expansion", observed=True)
    for exp, group in exp_groups:
        c = tabs[0].container(border=True)
        cols = c.columns([0.1, 0.9])
        with cols[0]:
            display_exp_image(str(exp), tooltip=str(exp))
        with cols[1]:
            text = ""
            for row in group.itertuples():
                cost = f"({row.Cost})" if pd.notna(row.Cost) else ""
                text += f"- {row.Name} {cost}\n"
            st.write(text)
    tabs[1].write(
        "These extra components might be needed if you set up this kingdom in person:"
    )
    with tabs[1]:
        _display_extra_components(k, True)


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
            st.checkbox("Show reroll buttons", True, key="show_reroll_buttons")
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
        _display_extra_components(k)


def _build_kingdom_csv_display(
    k: Kingdom, loc: Literal["randomizer", "oracle"] = "oracle"
):
    code = k.get_dombot_csv_string()
    if k.name != "":
        st.markdown(f"#### {k.name}")
    st.code(code, wrap_lines=loc == "randomizer")
    st.markdown(
        """<div style='text-align:center'><span class="tooltip">More info ℹ️<span class="tooltiptext">
    You can copy this to your clipboard and paste it into the interface of your preferred digital Dominion client.\\\nShould work both for [Dominion Online](https://dominion.games/) and the [TGG implementation](https://store.steampowered.com/app/1131620/Dominion/).
  </span>
</span>
</div>
""",
        unsafe_allow_html=True,
    )


def _build_kingdom_miniplot_display(k: Kingdom):
    """Display a small plot of the kingdom's card qualities."""
    fig = plot_kingdom_qualities(k.total_qualities, buy_str=k.buy_availability)
    if k.name != "":
        fig.axes[0].set_title(k.name)
    fig.set_facecolor("none")
    st.pyplot(fig)
    st.markdown(
        """<div style='text-align:center'><span class="tooltip">More info ℹ️<span class="tooltiptext">
    The kingdom quality plot gives you a quick overview of the distribution of CSO qualities in this kingdom.\nHover over the CSOs in the card view to see which qualities they contribute.\nFor more information about kingdom qualities, visit the About page.
  </span>
</span>
</div>
""",
        unsafe_allow_html=True,
    )


def display_sidebar_kingdom_info(
    k: Kingdom, loc: Literal["randomizer", "oracle"] = "oracle"
):
    with st.container():
        # st.markdown("""
        # <style>
        # div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        #     gap: 0.4rem !important;
        # }
        # </style>
        # """, unsafe_allow_html=True)

        with st.expander("Descriptive string to copy", expanded=False, icon="📋"):
            _build_kingdom_csv_display(k, loc=loc)
        with st.expander("Kingdom plot", expanded=loc == "oracle", icon="🧭"):
            _build_kingdom_miniplot_display(k)


def display_kingdom(k: Kingdom, is_randomizer_view=True):
    df = k.full_kingdom_df.set_index("Name")
    tab_names = [
        "📜Standard View",
        "📊Data View",
        "🧭Overview Plot",
        f"{ST_ICONS['components']}Components",
        f"{ST_ICONS['interactions']}{ST_ICONS['combos']}Interactions",
    ]
    if is_randomizer_view:
        tab_names.insert(1, "🔁Reroll View")
    selected_tab = st.segmented_control(
        "What to display",
        tab_names,
        label_visibility="hidden",
        default="📜Standard View",
        width="stretch",
    )
    if selected_tab == "📜Standard View":
        display_full_kingdom_images(k, show_reroll=is_randomizer_view)
    if selected_tab == "🔁Reroll View":
        display_stylysed_cso_df(
            df[["ImagePath", "Expansion", "Cost"]],
            with_reroll=is_randomizer_view,
            width="stretch",
        )
        _build_reroll_selection_button("Reroll selection")
    if selected_tab == "📊Data View":
        display_stylysed_cso_df(df)
    if selected_tab == f"{ST_ICONS['components']}Components":
        _display_all_components(k)
    if selected_tab == "🧭Overview Plot":
        st_display_kingdom_plot(k, with_border=True)
        st.info(
            "*Hint: Hover over the images in the kingdom image display in the standard view to directly see the individual cards' qualities.*"
        )
    if selected_tab == f"{ST_ICONS['interactions']}{ST_ICONS['combos']}Interactions":
        interactions = filter_combo_or_inter_df_for_csos(
            get_cached_inter_df(), k.full_kingdom_df.index, require_all=True
        )
        if len(interactions) > 0:
            st.write("#### Special Interactions (rules-wise)")
            st_display_inter_df(interactions)
        else:
            st.info(
                "No special rules interactions found [which doesn't necessarily mean there are none, let me know about any you find!]."
            )
        cols = st.columns([0.7, 0.3])
        cols[1].page_link(
            "streamlit_pages/interactions.py",
            label="More about interactions",
            icon=ST_ICONS["interactions"],
            use_container_width=True,
            help="Visit the page that contains more information on the available interactions in the database.",
        )
        combos = filter_combo_or_inter_df_for_csos(
            get_cached_combo_df(), k.full_kingdom_df.index, require_all=True
        )
        with st.expander(
            "🎊Special pairwise combos, synergies, rushes, or counters in this kingdom (WARNING: Spoilers)",
            expanded=False,
        ):
            if len(combos) > 0:
                st_display_combo_df(combos)
            else:
                st.info("No combos/synergies found for this kingdom")
        cols = st.columns([0.7, 0.3])
        cols[1].page_link(
            "streamlit_pages/combos.py",
            label="More about synergies",
            icon="🎊",
            use_container_width=True,
            help="Visit the page that contains more information on the available combos in the database.",
        )


def display_current_randomized_kingdom():
    k = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    with st.container(border=True):
        st.write("### Current Kingdom (scroll down for new randomization)")
        with st.sidebar:
            display_sidebar_kingdom_info(k, loc="randomizer")
        display_kingdom(k)
        build_incomplete_randomization_warning(k)
