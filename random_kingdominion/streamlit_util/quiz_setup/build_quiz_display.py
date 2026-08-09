from time import sleep, time
from typing import Literal, cast

import matplotlib.pyplot as plt
import streamlit as st

from ...constants import PATH_ASSETS
from ...kingdom import Kingdom
from ...utils import DOM_BEIGE, DOM_BLUE, get_quality_icon_fpath
from ..common_widgets import st_build_kingdom_csv_display, st_display_kingdom_images
from ..image_util import st_plot_kingdom_qualities
from .persistence import (
    QuizPersistenceError,
    persist_quiz_run,
    restore_persisted_quiz_run,
)
from .run_state import (
    BuyAvailability,
    QuizAnswers,
    QuizDifficulty,
    QuizMode,
    QuizPhase,
    QuizRunState,
)
from .util import (
    generate_random_quiz_kingdom_string,
    get_quiz_quality_names,
    load_quiz_widget_value,
    reset_quiz_answers,
    reset_quiz_workflow,
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
    return c.segmented_control(
        "Buy Availability",
        ["yes", "maybe", "no"],
        selection_mode="single",
        default=None,
        key=load_quiz_widget_value(st.session_state, answer_key),
        disabled=solution_is_shown,
        format_func=str.capitalize,
        on_change=save_quiz_widget_value,
        args=(st.session_state, answer_key),
        width="stretch",
    )


def _st_build_qualities_selection(
    quality_names: list[str], solution_is_shown: bool
) -> None:
    for quality in quality_names:
        answer_key = f"quiz_quality_slider_{quality}"
        st.session_state.setdefault(answer_key, -1)
        cols = st.columns([1, 8])
        with cols[0]:
            st.image(get_quality_icon_fpath(quality), width="stretch")

        with cols[1]:
            st.segmented_control(
                f"{quality.capitalize()}",
                ["0", ":star:", "1", "2", "3", "4"],
                key=load_quiz_widget_value(st.session_state, answer_key),
                default=None,
                disabled=solution_is_shown,
                on_change=save_quiz_widget_value,
                args=(st.session_state, answer_key),
                width="stretch",
                label_visibility="collapsed",
                help=f"Select {quality.capitalize()} quality value",
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


def _to_val(s: str | None) -> float:
    if s == ":star:":
        return 0.5
    if s is None:
        return -1.0
    return float(s)


def _get_selected_user_values() -> dict[str, float]:
    """Returns a dictionary of the selected user values for each quality, with -1.0 for unselected qualities."""
    selected_values = {
        q: st.session_state.get(f"quiz_quality_slider_{q}", None)
        for q in get_quiz_quality_names()
    }
    selected_values = {q: _to_val(v) for q, v in selected_values.items()}
    return selected_values


def plot_qualities(
    solution_possible: bool,
    solution_is_shown: bool,
    k: Kingdom,
) -> None:
    linecolor = "darkred" if solution_possible else "gray"
    selected_values = _get_selected_user_values()
    fig = st_plot_kingdom_qualities(selected_values, linecolor=linecolor)
    if solution_is_shown:
        fig = st_plot_kingdom_qualities(
            k.total_qualities, fig.axes[0], buy_str=k.buy_availability
        )
    st.text(
        "Your Estimated Qualities",
        help="The qualities you selected for this kingdom in gray (as long as you aren't finished), then in red. Once the solution is shown, the actual qualities are shown in blue.",
    )
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


def show_solution_button(
    run_state: QuizRunState,
    k: Kingdom,
    solution_possible: bool = False,
) -> None:
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
            selected_values = _get_selected_user_values()
            buy_str = cast(BuyAvailability, _get_buy_availability())
            answers = QuizAnswers(selected_values, buy_str)
            score = st_calc_quiz_score(
                selected_values,
                k.total_qualities,
                buy_str,
                k.buy_availability,
            )
            if run_state.submit_round(answers, score):
                persist_quiz_run(st.session_state, run_state)
            st.session_state["quiz_show_solution"] = True
            st.rerun()


def _get_buy_availability() -> str:
    return st.session_state.get("quiz_quality_buy_str", "")


def solution_section(score: float) -> None:
    # If .5 points, show one decimal place, otherwise show no decimal places
    score_str = f"{score:.1f}" if score % 1 != 0 else f"{int(score)}"
    with st.container():
        # Color depending on score achieved
        msg = ""
        if score < 1:
            color = "red"
            msg = "Cheeky! Did you deliberately go for a low score? It's genuinely not that easy to achieve! :)"
        elif score <= 8:
            color = "orange"
            msg = "Off by a quite a bit, I know you'll get there if you think about the kingdoms a bit more! There were probably one or two important CSOs you missed."
        elif score <= 11:
            color = "gold"
            msg = "Not bad, you got the general idea :)"
        elif score < 15:
            color = "lightgreen"
            msg = "Great job, you really know your way around Dominion kingdoms!\nI wouldn't be surprised if the offsets are due to subjective subtleties in my quality assessments."
        elif score == 15:
            color = "green"
            msg = "Wow, congrats, perfect score!\nYou really know your Dominion (and my way of quality assessments)!"

        st.markdown(
            f"<h2 style='color: {color};'>Score: {score_str}/15</h2>{msg}",
            unsafe_allow_html=True,
        )
        fig = plot_score_bar(score)
        with st.container(horizontal=True, horizontal_alignment="center"):
            st.pyplot(fig, True, width="content")
        plt.close(fig)


def _get_current_run_mode() -> QuizMode:
    mode_label = st.session_state.get("quiz_run_mode", QuizMode.PRACTICE)
    return QuizMode.from_display_key(mode_label)


def _get_current_difficulty() -> QuizDifficulty:
    difficulty_label = st.session_state.get(
        "quiz_difficulty_selection", QuizDifficulty.PRACTICE
    )
    return QuizDifficulty.from_display_key(difficulty_label)


def _build_run_mode_selection() -> None:
    st.segmented_control(
        "Quiz Mode",
        list(QuizMode),
        default=_get_current_run_mode(),
        width="stretch",
        key="quiz_run_mode",
        help="\\\n".join([m.get_description() for m in QuizMode]),
    )


def _build_difficulty_selection() -> None:
    st.segmented_control(
        "Difficulty",
        list(QuizDifficulty),
        default=_get_current_difficulty(),
        width="stretch",
        selection_mode="single",
        required=True,
        key="quiz_difficulty_selection",
        help="\\\n".join([m.get_description() for m in QuizDifficulty]),
    )


def _build_mode_navigation(quality_names: list[str]) -> None:
    col0, col1 = st.container(border=True).columns([1, 2])
    with col0:
        _build_run_mode_selection()
    with col1:
        _build_difficulty_selection()
    selected_mode = _get_current_run_mode()
    if selected_mode is QuizMode.PRACTICE:
        st.caption("Explore one kingdom at a time without a cumulative score.")
        button_label = "Start Practice"
        round_count = 1
    else:
        st.caption("Score ten kingdoms in a row and review your combined result.")
        button_label = "Start 10 Kingdom Run"
        round_count = 10

    if st.button(button_label, type="primary", width="stretch"):
        kingdom = generate_random_quiz_kingdom_string()
        run_state = QuizRunState.start(
            round_count,
            difficulty=_get_current_difficulty(),
            kingdom=kingdom,
            mode=selected_mode,
        )
        persist_quiz_run(st.session_state, run_state)
        reset_quiz_answers(st.session_state, quality_names)
        st.rerun()


@st.fragment(run_every=0.5)
def _build_timer_display(run_state: QuizRunState) -> None:
    with st.container(horizontal=True, horizontal_alignment="left"):
        if st.checkbox("Hide Timer", value=True, key="quiz_show_timer"):
            return

        elapsed_seconds = int(run_state.get_elapsed_time_of_current_round())
        minutes, seconds = divmod(elapsed_seconds, 60)
        if run_state.mode is QuizMode.PRACTICE:
            st.text(f"Time: {minutes:02d}:{seconds:02d}")
            return
        elapsed_seconds_tot = int(run_state.get_total_elapsed_time_so_far())
        total_minutes, total_seconds = divmod(elapsed_seconds_tot, 60)
        st.text(
            f"Round Time: {minutes:02d}:{seconds:02d}, Total time: {total_minutes:02d}:{total_seconds:02d}"
        )


def _build_run_header(run_state: QuizRunState, quality_names: list[str]) -> None:
    header = st.container(horizontal=True, horizontal_alignment="distribute")
    if run_state.mode is QuizMode.RUN:
        diff = run_state.difficulty
        header.text(
            f"Difficulty: {diff.value}",
            help=f"The difficulty level you selected for this run: {diff.get_description(include_name=False)}",
        )
        header.markdown(
            f"**Round {run_state.current_round_index + 1} of {run_state.round_count}**"
        )
        header.markdown(
            f"**Score: {run_state.cumulative_score:g}/{run_state.maximum_score}**"
        )
        st.progress(
            len(run_state.completed_rounds) / run_state.round_count,
            text="Run progress",
        )
    else:
        header.markdown("**Practice**")
    with header:
        _build_timer_display(run_state)

    if header.button("Stop / Reset", type="secondary"):
        reset_quiz_workflow(st.session_state, quality_names)
        st.rerun()


def _build_finished_summary(run_state: QuizRunState) -> None:
    st.subheader("10 Kingdom Run Complete")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Total Score",
        f"{run_state.cumulative_score:g}/{run_state.maximum_score}",
    )
    col2.metric("Average", f"{run_state.average_score:.1f}/15")
    col3.metric(
        "Perfect Rounds",
        f"{run_state.perfect_round_count}/{run_state.round_count}",
    )


def _advance_or_restart(run_state: QuizRunState, quality_names: list[str]) -> None:
    if run_state.mode is QuizMode.PRACTICE:
        label = "Practice Another Kingdom"
    elif run_state.current_round_index + 1 == run_state.round_count:
        label = "View Run Summary"
    else:
        label = "Next Kingdom"

    if st.button(label, type="primary", width="stretch"):
        if run_state.mode is QuizMode.PRACTICE:
            run_state = QuizRunState.start(
                1,
                _get_current_difficulty(),
                generate_random_quiz_kingdom_string(),
                QuizMode.PRACTICE,
            )
        else:
            next_kingdom = (
                ""
                if run_state.current_round_index + 1 == run_state.round_count
                else generate_random_quiz_kingdom_string()
            )
            run_state.advance_round(next_kingdom)
        persist_quiz_run(st.session_state, run_state)
        reset_quiz_answers(st.session_state, quality_names)
        st.rerun()


def st_build_full_quiz_display() -> None:
    quality_names = get_quiz_quality_names()
    try:
        run_state = restore_persisted_quiz_run(st.session_state)
    except QuizPersistenceError:
        st.session_state.pop("quiz_run_record", None)
        st.warning("The saved quiz run could not be restored and was reset.")
        run_state = None

    if not isinstance(run_state, QuizRunState):
        _build_mode_navigation(quality_names)
        return

    _build_run_header(run_state, quality_names)
    if run_state.phase is QuizPhase.FINISHED:
        _build_finished_summary(run_state)
        return

    solution_is_shown = run_state.phase is QuizPhase.SOLUTION
    k_str = run_state.current_kingdom
    k = Kingdom.from_dombot_csv_string(k_str)

    selection_cont = st.container(border=True)

    checkbox_large_view = st.sidebar.checkbox(
        "Large Kingdom View",
        value=st.session_state.get("quiz_kingdom_view_large", False),
        key="quiz_kingdom_view_large",
    )
    if checkbox_large_view:
        col0 = selection_cont.expander("The Kingdom", expanded=True)
        col1, col2 = selection_cont.columns(2)
    else:
        col0, col1, col2 = selection_cont.columns(3)
        col0 = col0.container(border=True)
        col0.write("The Kingdom")
    with col0:
        full_img = run_state.difficulty != QuizDifficulty.HARD
        exclude_qualities = (
            not solution_is_shown and run_state.difficulty != QuizDifficulty.PRACTICE
        )
        _fragmented_kingdom_display(
            k_str,
            exclude_qualities=exclude_qualities,
            checkbox_full_image=full_img,
        )
        if solution_is_shown:
            st.info(
                "By hovering over the images, you can now see the individual qualities."
            )

    with col2.container(border=True):
        if not solution_is_shown:
            st.write("Adjust Qualities")
            _st_build_buy_selection(solution_is_shown)
            _st_build_qualities_selection(quality_names, solution_is_shown)
        else:
            solution_section(run_state.round_score or 0.0)

    selected_values = _get_selected_user_values()
    buy_str = _get_buy_availability()
    solution_possible = all(v != -1 for v in selected_values.values()) and buy_str != ""

    with col1.container(border=True):
        plot_qualities(solution_possible, solution_is_shown, k)

    if solution_is_shown:
        _advance_or_restart(run_state, quality_names)
    else:
        show_solution_button(run_state, k, solution_possible)
