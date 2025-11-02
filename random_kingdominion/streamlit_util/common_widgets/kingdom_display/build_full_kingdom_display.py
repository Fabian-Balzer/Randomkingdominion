from typing import Callable

import streamlit as st

from ....kingdom import Kingdom
from ....utils import get_video_title
from ...constants import ST_ICONS
from .. import display_stylysed_cso_df
from .combo_and_inter_display import st_build_combo_and_inter_display
from .extra_components_display import st_build_big_extra_component_display
from .kingdom_as_images import st_build_kingdom_image_display
from .kingdom_plot_display import st_build_full_kingdom_plot_display
from .reroll_view import st_build_reroll_kingdom_display


def st_build_full_kingdom_display(
    k: Kingdom,
    reroll_selection_callback: Callable[[], None] | None = None,
    single_reroll_callback: Callable[[str], None] | None = None,
):
    is_randomizer_view = (
        reroll_selection_callback is not None and single_reroll_callback is not None
    )
    df = k.full_kingdom_df
    csos = df.index.tolist()
    df = df.set_index("Name")
    tab_names = [
        "📜Standard View",
        "📊Data View",
        "🧭Overview Plot",
        f"{ST_ICONS['components']}Components",
        f"{ST_ICONS['interactions']}{ST_ICONS['combos']}Interactions",
    ]
    if is_randomizer_view:
        tab_names.insert(1, "🔁Reroll View")
    label = t if (t := get_video_title(k)) != "" else "Custom Kingdom"
    selected_tab = st.segmented_control(
        label,
        tab_names,
        label_visibility="collapsed" if is_randomizer_view else "visible",
        default="📜Standard View",
        width="stretch",
    )
    if selected_tab == "📜Standard View":
        st_build_kingdom_image_display(k, single_reroll_callback)
    if selected_tab == "🔁Reroll View" and reroll_selection_callback is not None:
        st_build_reroll_kingdom_display(df, reroll_selection_callback)
    if selected_tab == "📊Data View":
        display_stylysed_cso_df(df)
    if selected_tab == f"{ST_ICONS['components']}Components":
        st_build_big_extra_component_display(k)
    if selected_tab == "🧭Overview Plot":
        st_build_full_kingdom_plot_display(k)
    if selected_tab == f"{ST_ICONS['interactions']}{ST_ICONS['combos']}Interactions":
        df = k.full_kingdom_df
        st_build_combo_and_inter_display(csos)
