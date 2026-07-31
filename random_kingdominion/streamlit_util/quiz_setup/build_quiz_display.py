from typing import Literal

import matplotlib.pyplot as plt
import streamlit as st

from ...constants import PATH_ASSETS
from ...kingdom import Kingdom
from ...utils import DOM_BEIGE, DOM_BLUE, get_quality_icon_fpath
from ..common_widgets import st_build_kingdom_csv_display, st_display_kingdom_images
from ..image_util import st_plot_kingdom_qualities
from .util import (
    generate_random_quiz_kingdom,
    get_quiz_quality_names,
    load_quiz_widget_value,
    save_quiz_widget_value,
    st_calc_quiz_score,
)


@st.fragment
def _fragmented_kingdom_display(
    k_str: str, exclude_qualities: bool, checkbox_full_image: bool = False
):
    k = Kingdom.from_dombot_csv_string(k_str)
    st_display_kingdom_images(
        k,
        show_full_image=checkbox_full_image,
        show_tooltips=True,
        exclude_tooltip_qualities=exclude_qualities,
    )
    st_build_kingdom_csv_display(k)


def _st_build_buy_selection(
    solution_is_shown: bool,
) -> Literal["yes", "no", "maybe"] | None:
    c = st.container(border=True)
    answer_key = "quiz_quality_buy_str"
    return c.radio(
        "Buy Availability",
        ["yes", "maybe", "no"],
        index=None,
        horizontal=True,
        key=load_quiz_widget_value(st.session_state, answer_key),
        disabled=solution_is_shown,
        format_func=str.capitalize,
        on_change=save_quiz_widget_value,
        args=(st.session_state, answer_key),
    )


def qualities_selection(quality_names: list[str], solution_is_shown: bool) -> None:
    for quality in quality_names:
        answer_key = f"quiz_quality_slider_{quality}"
        st.session_state.setdefault(answer_key, -1)
        cols = st.columns([1, 8])
        with cols[0]:
            st.image(
                get_quality_icon_fpath(quality),
                width="stretch",
            )
        with cols[1]:
            st.select_slider(
                f"{quality.capitalize()}",
                help=quality.capitalize(),
                options=[-1, 0, 0.5, 1, 2, 3, 4],
                key=load_quiz_widget_value(st.session_state, answer_key),
                format_func=lambda x: (
                    "Select please" if x == -1 else str(x if x % 1 != 0 else int(x))
                ),
                label_visibility="collapsed",
                disabled=solution_is_shown,
                on_change=save_quiz_widget_value,
                args=(st.session_state, answer_key),
            )


@st.fragment
def _show_selected_buy_icon(
    buy_str: Literal["", "yes", "no", "maybe"] | None,
) -> None:
    if not buy_str:
        st.caption("No buy option selected")
        return
    cont = st.container(horizontal=True, horizontal_alignment="center")
    fpath = PATH_ASSETS.joinpath(f"icons/qualities/buys_icon_{buy_str}.png")
    cont.image(fpath, caption="Selected", width=60)


def plot_qualities(
    solution_possible: bool,
    solution_is_shown: bool,
    k: Kingdom,
) -> None:
    linecolor = "darkred" if solution_possible else "gray"
    selected_values = {
        q: st.session_state.get(f"quiz_quality_slider_{q}", -1)
        for q in get_quiz_quality_names()
    }
    fig = st_plot_kingdom_qualities(selected_values, linecolor=linecolor)
    if solution_is_shown:
        fig = st_plot_kingdom_qualities(
            k.total_qualities, fig.axes[0], buy_str=k.buy_availability
        )
    st.write("Your Estimated Qualities")
    st.pyplot(fig, True)
    plt.close(fig)
    _show_selected_buy_icon(st.session_state.get("quiz_quality_buy_str", ""))


def plot_score_bar(score: float):
    fig, ax = plt.subplots(figsize=(0.2, 1))
    # Color ranges
    ranges = [
        (0, 1, "red"),
        (1, 8, "orange"),
        (8, 11, "gold"),
        (11, 14.5, "lightgreen"),
        (14.5, 15, "green"),
    ]
    for start, end, color in ranges:
        ax.bar(
            0,
            end - start,
            bottom=start,
            color=color,
            edgecolor="k",
            width=0.5,
            alpha=0.7,
            linewidth=0.3,
        )
    for start, end, color in ranges:
        if score < start:
            continue
        end = min(end, score)
        ax.bar(
            0,
            end - start,
            bottom=start,
            color=color,
            edgecolor="k",
            width=0.5,
            linewidth=0.3,
        )
    ax.bar(0, score, color="none", edgecolor=DOM_BLUE, width=0.5, linewidth=2)
    ax.bar(0, score, color=DOM_BLUE, edgecolor="none", width=0.5, alpha=0.4)
    ax.bar(0, 15, color="none", edgecolor=DOM_BLUE, width=0.5, linewidth=0.5)
    ax.axhline(score, color=DOM_BLUE, linewidth=3)
    ax.set_ylim(0, 15)
    ax.set_xticks([])
    ax.set_yticks(list(range(0, 16, 3)), minor=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(
        axis="y", which="minor", direction="in", length=6, color="black", reset=True
    )
    fig.subplots_adjust(left=0.05, right=0.95, top=1, bottom=0)
    fig.set_facecolor(DOM_BEIGE)
    ax.set_facecolor(DOM_BEIGE)
    return fig


def show_solution_button(solution_possible: bool = False) -> None:
    f = st.container(horizontal=True, horizontal_alignment="left")
    if not solution_possible:
        f.info(
            "Please select all qualities and buy availability to unlock the solution."
        )
    else:
        if f.button(
            "Click here to show Solution",
            disabled=not solution_possible,
            width="stretch",
            type="primary",
        ):
            st.session_state["quiz_show_solution"] = True
            st.session_state["quiz_has_started"] = False
            st.rerun()


def _get_selected_values() -> dict[str, float]:
    quality_names = get_quiz_quality_names()
    selected_values: dict[str, float] = {}
    for q in quality_names:
        selected_values[q] = st.session_state.get(f"quiz_quality_slider_{q}", -1)
    return selected_values


def _get_buy_availability() -> str:
    return st.session_state.get("quiz_quality_buy_str", "")


def solution_section(k: Kingdom) -> None:
    selected_values = _get_selected_values()
    buy_str = _get_buy_availability()
    score = st_calc_quiz_score(
        selected_values, k.total_qualities, buy_str, k.buy_availability
    )
    # If .5 points, show one decimal place, otherwise show no decimal places
    score_str = f"{score:.1f}" if score % 1 != 0 else f"{int(score)}"
    with st.container():
        # Color depending on score achieved
        # 0-5 points: red, 5-10 points: orange, 10-13 points: light green, 13-15 points: green
        msg = ""
        if score <= 1:
            color = "red"
            msg = "Did you deliberately go for a low score? :)"
        elif score <= 8:
            color = "orange"
            msg = "Off by a quite a bit, I know you'll get better after thinking a bit more! There were probably one or two important CSOs you missed."
        elif score <= 11:
            color = "gold"
            msg = "Not bad, you got the general idea :)"
        elif score < 15:
            color = "lightgreen"
            msg = "Great job, you really know your way around in Dominion! The offsets might be due to my subjective quality assessments."
        elif score == 15:
            color = "green"
            msg = "Wow, perfect score! You really know your Dominion!"

        st.markdown(
            f"<h2 style='color: {color};'>Score: {score_str}/15</h2>{msg}",
            unsafe_allow_html=True,
        )
        # TODO: 1D bar plot:
        fig = plot_score_bar(score)
        with st.container(horizontal=True, horizontal_alignment="center"):
            st.pyplot(fig, True, width="content")
        plt.close(fig)


def st_build_kingdom_display_options() -> tuple[bool, bool]:
    col1, col2 = st.columns(2)
    with col1:
        checkbox_large_view = st.checkbox(
            "Large Kingdom View",
            value=st.session_state.get("quiz_kingdom_view_large", False),
            key="quiz_kingdom_view_large",
        )
    with col2:
        checkbox_full_image = st.checkbox(
            "Show Full Images",
            value=st.session_state.get("quiz_kingdom_view_full_image", True),
            key="quiz_kingdom_view_full_image",
        )
    return checkbox_large_view, checkbox_full_image


def st_build_full_quiz_display() -> None:

    quality_names = get_quiz_quality_names()
    solution_is_shown = st.session_state.get("quiz_show_solution", False)
    quiz_has_started = st.session_state.get("quiz_has_started", False)
    randomize_button = st.container()

    k_str = st.session_state.get("quiz_current_kingdom", "")
    if k_str == "":
        st.info("Click the button to generate a random kingdom to start the quiz.")
    else:
        k = Kingdom.from_dombot_csv_string(k_str)

        large_kingdom_view, checkbox_full_image = st_build_kingdom_display_options()
        selection_cont = st.container(border=True)
        if large_kingdom_view:
            col0 = selection_cont.expander("The Kingdom", expanded=True)
            col1, col2 = selection_cont.columns(2)
        else:
            col0, col1, col2 = selection_cont.columns(3)
            col0 = col0.container(border=True)
            col0.write("The Kingdom")

        with col0:
            _fragmented_kingdom_display(
                k_str,
                exclude_qualities=not solution_is_shown,
                checkbox_full_image=checkbox_full_image,
            )
            if solution_is_shown:
                st.info(
                    "By hovering over the images, you can now see the individual qualities."
                )

        with col2.container(border=True):
            if not solution_is_shown:
                st.write("Adjust Qualities")
                _st_build_buy_selection(solution_is_shown)
                qualities_selection(quality_names, solution_is_shown)
            else:
                solution_section(k)

        selected_values = _get_selected_values()
        buy_str = _get_buy_availability()
        solution_possible = (
            all(v != -1 for v in selected_values.values()) and buy_str != ""
        )

        with col1.container(border=True):
            plot_qualities(solution_possible, solution_is_shown, k)

        if not solution_is_shown:
            show_solution_button(solution_possible)

    if randomize_button.button(
        "Generate New Random Kingdom",
        help="Generate a new random kingdom for the quiz.",
        width="stretch",
        type="secondary" if quiz_has_started else "primary",
    ):
        generate_random_quiz_kingdom(quality_names)
        solution_is_shown = False
        quiz_has_started = True
        st.session_state["quiz_show_solution"] = False
        st.session_state["quiz_has_started"] = True
        st.rerun()
