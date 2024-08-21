from math import ceil

import streamlit as st
from PIL import Image

from ...utils import get_expansion_icon_path
from ..constants import ALL_EXPANSIONS, NUM_EXPS
from ..image_handling import display_image_with_tooltip
from ..randomizer_util import load_config


def _select_non_1e():
    for exp in ALL_EXPANSIONS:
        st.session_state[f"{exp} enabled"] = "1E" not in exp


def display_exp_image(exp: str, icon_size: int = 30, tooltip: str = ""):

    # Green background if enabled, red if disabled
    bg_color = (
        (50, 255, 50, 100) if st.session_state[f"{exp} enabled"] else (255, 50, 50, 100)
    )

    fpath = "./static/" + get_expansion_icon_path(exp, relative_only=True)
    im = Image.open(fpath).convert("RGBA").resize((icon_size, icon_size))
    bg = Image.new("RGBA", im.size, bg_color)
    # Paste the original image onto the background
    im = Image.alpha_composite(bg, im)

    display_image_with_tooltip(im, tooltip)

    # A try to set it up as a nice checkbox, but doesn't work as I cannot interact with session_state....
    # checkbox_id = f"{exp} enabled"
    # if checkbox_id not in st.session_state:
    #     st.session_state[checkbox_id] = True
    # Convert the RGBA tuple to a CSS-compatible rgba string
    # bg_color_css = (
    #     f"rgba({bg_color[0]}, {bg_color[1]}, {bg_color[2]}, {bg_color[3] / 255})"
    # )
    # image_base64 = get_image_as_base64(fpath)
    # md_text = f"""
    # <style>
    #     .rounded-box {{
    #         display: flex;
    #         align-items: center;
    #         border: 1px solid #ccc;
    #         border-radius: 5px;
    #         padding: 5px;
    #         margin-bottom: 5px;
    #         overflow: hidden;  /* Prevent content overflow */
    #         justify-content: space-between;  /* Distribute space between text and image */
    #     }}
    #     .rounded-box img {{
    #         width: 50px;
    #         height: 50px;
    #         border-radius: 5px;
    #         margin-right: 10px;
    #     }}
    #     .rounded-box input {{
    #         margin-right: 10px;
    #     }}
    #     .rounded-box label {{
    #         display: flex;
    #         align-items: left;
    #         width: 100%;
    #     }}
    # </style>
    # <div class="rounded-box">
    #     <input type="checkbox" id="{checkbox_id}" name="{exp}">
    #     <label for="{checkbox_id}">
    #         {exp}
    #         <img src="data:image/png;base64,{image_base64}" alt="{exp}">
    #     </label>
    # </div>"""
    # st.markdown(md_text, unsafe_allow_html=True)


def build_exp_checkbox(exp: str):
    """Build a single row to display an expansion and its weights."""
    configured_expansions = load_config().get_expansions()
    with st.container(border=True):
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.checkbox(
                exp,
                exp in configured_expansions,
                key=f"{exp} enabled",
            )
        with col2:
            display_exp_image(exp)
    # with col3:
    #     if use_counts:
    #         st.number_input("Minimum", 0, 10, key=f"{exp} count")
    #     else:
    #         st.number_input("Weight", 1, 100, key=f"{exp} weight")


@st.fragment
def _build_exp_num_row():
    val = max(
        1, load_config().getint("Expansions", "max_num_expansions", fallback=NUM_EXPS)
    )
    st.number_input(
        "Max. number of expansions",
        min_value=1,
        max_value=NUM_EXPS,
        value=val,
        help="The maximum number of expansions to randomize from.",
        key="max_num_expansions",
    )


def _toggle_all_expansions(value: bool):
    for exp in ALL_EXPANSIONS:
        st.session_state[f"{exp} enabled"] = value


def _build_toggle_row():
    cols = st.columns(3)
    with cols[0]:
        st.button(
            "Deselect all",
            on_click=lambda: _toggle_all_expansions(False),
            use_container_width=True,
        )
    with cols[1]:
        st.button(
            "Select all",
            on_click=lambda: _toggle_all_expansions(True),
            use_container_width=True,
        )
    with cols[2]:
        st.button(
            "Select all except 1E",
            on_click=_select_non_1e,
            use_container_width=True,
        )


def _build_sorting_options():
    cols = st.columns(3)
    with cols[0]:
        st.write("Sorting options")
    with cols[1]:
        st.radio(
            "Expansion sorting",
            ["Alphabetical", "Release"],
            index=1,
            key="Exp sorting",
            horizontal=True,
            label_visibility="collapsed",
        )
    with cols[2]:
        st.checkbox("Move deselected", True, key="Exp move deselected")


def get_currently_selected_expansions() -> list[str]:
    """Retrieve the expansions that are currently selected by the user."""
    sorted_expansions = (
        sorted(ALL_EXPANSIONS)
        if st.session_state["Exp sorting"] == "Alphabetical"
        else ALL_EXPANSIONS
    )
    configured_expansions = load_config().get_expansions()
    return [
        exp
        for exp in sorted_expansions
        if st.session_state.get(f"{exp} enabled", exp in configured_expansions)
    ]


def _build_selection_grid():
    # st.multiselect(
    #     "Selected Expansions",
    #     options=ALL_EXPANSIONS,
    #     default=selected_expansions,
    #     key="expansionSelectForFilter",
    #     help="Select the expansions you want to include in the filtered results.",
    # )
    # st.write(
    #     "Currently not selected: "
    #     + ", ".join([exp for exp in ALL_EXPANSIONS if exp not in selected_expansions])
    # )
    selected_expansions = get_currently_selected_expansions()
    col_num = 5
    row_num = ceil(NUM_EXPS / col_num)
    cols = st.columns(col_num)
    if st.session_state.get("Exp move deselected", True):
        unsel = [exp for exp in ALL_EXPANSIONS if exp not in selected_expansions]
        sorted_expansions = selected_expansions + unsel
    for i, col in enumerate(cols):
        start = i * row_num
        stop = min((i + 1) * row_num, NUM_EXPS)
        exp_subset = sorted_expansions[start:stop]
        with col:
            for exp in exp_subset:
                build_exp_checkbox(exp)


@st.fragment
def build_expansion_selection():
    st.write(
        "Select the expansions you want to include in the randomization. You can also set the maximum number of expansions to randomize from."
    )
    _build_exp_num_row()
    with st.expander("Individual Selection", expanded=False):
        _build_toggle_row()
        _build_sorting_options()
        _build_selection_grid()
    current_exps = get_currently_selected_expansions()
    if len(current_exps) == 0:
        st.warning("No expansions selected! Please select at least one expansion.")
    else:
        with st.container(border=True):
            st.write("Current selection")
            cols = st.columns(len(current_exps))
            st.write(" ")
        for col, exp in zip(cols, current_exps):
            with col:
                display_exp_image(exp, icon_size=20, tooltip=exp)

    st.warning(
        "Sorry for this selection looking absolutely atrocious, streamlit doesn't really let you customize checkboxes. I wasted way too much time trying to improve it, for now I'll leave it be."
    )
