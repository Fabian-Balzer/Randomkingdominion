import streamlit as st
from PIL import Image
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.grid import grid
from streamlit_extras.stylable_container import stylable_container

from ...kingdom import sanitize_cso_name
from ...utils import get_expansion_icon_path
from ..constants import ALL_EXPANSIONS, NUM_EXPS
from ..image_handling import display_image_with_tooltip
from ..randomizer_util import load_config


# @st.fragment (can't be fragment due to sidebar stuff)
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


def _select_non_1e():
    st.session_state["selected_expansions"] = [
        exp for exp in ALL_EXPANSIONS if "1E" not in exp
    ]


def display_exp_image(exp: str, icon_size: int = 30, tooltip: str = ""):

    # Green background if enabled, red if disabled
    # bg_color = (
    #     (50, 255, 50, 100)
    #     if exp in st.session_state.get("selected_expansions", [])
    #     else (255, 50, 50, 100)
    # )

    fpath = "./static/" + get_expansion_icon_path(exp, relative_only=True)
    im = Image.open(fpath).convert("RGBA").resize((icon_size, icon_size))
    # bg = Image.new("RGBA", im.size, bg_color)
    # # Paste the original image onto the background
    # im = Image.alpha_composite(bg, im)

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


def _toggle_exp(exp: str):
    sel_expansions = get_selected_expansions()
    if exp in sel_expansions:
        sel_expansions.remove(exp)
    else:
        sel_expansions.append(exp)
    st.session_state["selected_expansions"] = sel_expansions


def build_exp_checkbox(exp: str):
    sel_expansions = get_selected_expansions()
    cols = st.columns([0.3, 0.7])
    with cols[0]:
        display_exp_image(exp, icon_size=40, tooltip=exp)
    with cols[1]:
        color = "green" if exp in sel_expansions else "grey"
        key = sanitize_cso_name(exp).replace(",", "_").replace("&", "_")
        with stylable_container(
            key=f"green_button_{key}",
            css_styles=f"""
                    button {{
                        background-color: {color};
                        color: white;
                        border-radius: 20px;
                    }}
                    """,
        ):
            st.button(
                f"{exp}",
                key=f"color button {exp}",
                use_container_width=True,
                on_click=lambda: _toggle_exp(exp),
            )


def _toggle_all_expansions(value: bool):
    st.session_state["selected_expansions"] = ALL_EXPANSIONS.copy() if value else []


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
    cols = st.columns([0.2, 0.4, 0.2, 0.2])
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
        st.checkbox("Move 1st Edition", True, key="Exp move 1e")
    with cols[3]:
        st.checkbox("Move deselected", False, key="Exp move deselected")


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


def _build_selection_grid():
    exps = get_sorted_expansions()
    num_cols = 5
    num_rows = len(exps) // num_cols + 1
    my_grid = grid([num_cols] * num_rows, vertical_align="bottom", gap="small")
    for exp in exps:
        with my_grid.container(border=True):
            key = sanitize_cso_name(exp).replace(",", "_").replace("&", "_")
            with stylable_container(
                key=f"cont_{key}",
                css_styles=f"""
                        height: 100px;
                        """,
            ):
                build_exp_checkbox(exp)


def get_selected_expansions(sort=False) -> list[str]:
    """Retrieve the selected expansions."""
    configured_expansions = load_config().get_expansions()
    selected = st.session_state.get("selected_expansions", configured_expansions)
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
    num_max = st.session_state.get("max_num_expansions", NUM_EXPS)
    with st.expander("Selected Expansions", expanded=True):
        if len(exps) == 0:
            st.warning("No expansions selected! Please select at least one expansion.")
        else:
            my_grid = grid([num_rows] * num_cols, vertical_align="bottom", gap="small")
            add_vertical_space(1)
        st.write(f"Maximum of {num_max} expansions")
    for exp in exps:
        with my_grid.container():
            display_exp_image(exp, icon_size=40, tooltip=exp)


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
