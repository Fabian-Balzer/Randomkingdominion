import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.grid import grid

from ....utils import get_expansion_icon_path
from ...constants import ALL_EXPANSIONS, NUM_EXPS
from ...image_util import st_build_expansion_icon_with_tt
from ...image_util.image_handling import img_to_bytes
from ..randomizer_util import get_or_initialize_key, load_config


# @st.fragment (can't be fragment due to sidebar stuff)
def _build_exp_num_row():
    flex = st.container(horizontal=True, horizontal_alignment="left")
    enable_max = flex.checkbox(
        "Limit number of expansions",
        value=load_config().getboolean("Expansions", "enable_max", fallback=False),
        key="enable_max_num_expansions",
        help="When checked, the maximum number of expansions to randomize from can be set.",
    )

    val = max(
        1, load_config().getint("Expansions", "max_num_expansions", fallback=NUM_EXPS)
    )

    flex.number_input(
        "Max. number of expansions",
        min_value=1,
        max_value=NUM_EXPS,
        value=val,
        disabled=not enable_max,
        help="The maximum number of expansions to randomize from.",
        key="max_num_expansions",
    )


def _select_non_1e():
    st.session_state["selected_expansions"] = [
        exp for exp in ALL_EXPANSIONS if "1E" not in exp
    ]


def _toggle_all_expansions(value: bool):
    st.session_state["selected_expansions"] = ALL_EXPANSIONS.copy() if value else []


def _build_toggle_row():
    cols = st.columns(3)
    cols[0].button(
        "Select all",
        on_click=lambda: _toggle_all_expansions(True),
        width="stretch",
        type="primary",
        icon="✅",
    )
    cols[1].button(
        "Clear selection",
        on_click=lambda: _toggle_all_expansions(False),
        width="stretch",
        type="primary",
        icon="❌",
    )
    cols[2].button(
        "Select all except 1E",
        on_click=_select_non_1e,
        width="stretch",
        type="primary",
        icon="☑️",
    )


def _build_sorting_options():
    flex = st.container(
        horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"
    )
    flex.write("Sorting options")
    flex.radio(
        "Expansion sorting",
        ["Alphabetical", "Release"],
        index=1,
        key="Exp sorting",
        horizontal=True,
        label_visibility="collapsed",
        width="stretch",
    )
    flex.checkbox("Move 1st Edition", True, key="Exp move 1e")
    flex.checkbox("Move deselected", False, key="Exp move deselected")


def get_sorted_expansions() -> list[str]:
    """Retrieve the expansions sorted by the user's preference."""
    exps = (
        sorted(ALL_EXPANSIONS)
        if st.session_state.get("Exp sorting", "") == "Alphabetical"
        else ALL_EXPANSIONS
    )
    if st.session_state.get("Exp move 1e", True):
        non_first_ed = [exp for exp in exps if "1E" not in exp]
        first_ed = [exp for exp in exps if "1E" in exp]
        exps = non_first_ed + first_ed
    if st.session_state.get("Exp move deselected", False):
        selected = get_selected_expansions(sort=True)
        unselected = [exp for exp in exps if exp not in selected]
        exps = selected + unselected
    return exps


def _toggle_exp(exp: str):
    sel_expansions = get_selected_expansions()
    if exp in sel_expansions:
        sel_expansions.remove(exp)
    else:
        sel_expansions.append(exp)
    st.session_state["selected_expansions"] = sel_expansions


def build_exp_checkbox(exp: str):
    sel_expansions = get_selected_expansions()
    is_sel = exp in sel_expansions
    fpath = "./static/" + get_expansion_icon_path(exp, relative_only=True)
    bytes = img_to_bytes(fpath)
    label = f"![exp_icon](data:image/png;base64,{bytes})\\\n{exp}"
    st.button(
        label,
        key=f"color button {exp}",
        width="stretch",
        on_click=lambda: _toggle_exp(exp),
        type="primary" if is_sel else "secondary",
    )


def _build_selection_grid():
    exps = get_sorted_expansions()
    num_cols = 5
    num_rows = len(exps) // num_cols + 1
    my_grid = grid([num_cols] * num_rows, vertical_align="bottom", gap="small")
    # for _ in range(num_rows):
    #     with st.container(horizontal=True, vertical_alignment="top"):
    #         row_exps = exps[_ * num_cols : (_ + 1) * num_cols]
    #         for exp in row_exps:
    #             build_exp_checkbox(exp)
    for exp in exps:
        with my_grid.container(border=False):
            # with st.container(horizontal=True, horizontal_alignment="center"):
            build_exp_checkbox(exp)


def get_selected_expansions(sort=False) -> list[str]:
    """Retrieve the selected expansions."""
    configured_expansions = load_config().get_expansions()
    selected = get_or_initialize_key("selected_expansions", configured_expansions)
    if not sort:
        return selected
    exps = (
        sorted(ALL_EXPANSIONS)
        if st.session_state.get("Exp sorting", "") == "Alphabetical"
        else ALL_EXPANSIONS
    )
    return [sel for sel in exps if sel in selected]


def _build_exp_selection_overview():
    exps = get_selected_expansions(sort=True)
    num_cols = 3
    num_rows = len(exps) // num_cols + 1
    configured_max_num = load_config().get("Expansions", "max_num_expansions")
    num_max = get_or_initialize_key("max_num_expansions", configured_max_num)
    exp_limit_enabled = get_or_initialize_key("enable_max_num_expansions", False)
    exp_limit_str = (
        f"At most {num_max} different expansions"
        if exp_limit_enabled
        else "No limit to number of expansions"
    )
    with st.expander("🗃️Selected Expansions", expanded=True):
        if len(exps) == 0:
            st.warning("No expansions selected! Please select at least one expansion.")
        else:
            my_grid = grid([num_rows] * num_cols, vertical_align="bottom", gap="small")
            add_vertical_space(1)
        st.write(exp_limit_str)
    for exp in exps:
        with my_grid.container():
            st_build_expansion_icon_with_tt(exp, icon_size=40, tooltip=exp)


@st.fragment
def build_expansion_selection():
    st.write(
        "Select the expansions you want to include in the randomization. You can also set the maximum number of expansions to randomize from."
    )
    with st.expander("Individual Selection", expanded=False):
        _build_toggle_row()
        _build_sorting_options()
        _build_selection_grid()
    current_exps = get_selected_expansions()
    if len(current_exps) == 0:
        st.warning("No expansions selected! Please select at least one expansion.")

    _build_exp_num_row()
    with st.sidebar:
        _build_exp_selection_overview()
