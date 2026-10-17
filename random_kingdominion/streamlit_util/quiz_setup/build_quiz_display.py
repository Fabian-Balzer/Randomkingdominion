from collections.abc import Mapping
from typing import TypeVar, cast

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
    QUIZ_RUN_RECORD_KEY,
    QuizAnswers,
    QuizDifficulty,
    QuizMode,
    QuizPhase,
    QuizRunState,
)
from .scoring import (
    MAX_ROUND_SCORE,
    QUIZ_QUALITY_NAMES,
    SCORE_BANDS,
    BuyAvailability,
    get_kingdom_solution,
    get_score_band,
    score_quiz_round,
)
from .util import (
    QUIZ_BUY_ANSWER_KEY,
    QUIZ_DIFFICULTY_KEY,
    QUIZ_HIDE_TIMER_KEY,
    QUIZ_LARGE_VIEW_KEY,
    QUIZ_MODE_KEY,
    generate_random_quiz_kingdom_string,
    get_quality_answer_key,
    load_quiz_widget_value,
    reset_quiz_answers,
    reset_quiz_workflow,
    save_quiz_widget_value,
)

_QUALITY_OPTIONS = ["0", ":star:", "1", "2", "3", "4"]

_E = TypeVar("_E", QuizMode, QuizDifficulty)


@st.fragment
def _fragmented_kingdom_display(
    k: Kingdom, exclude_qualities: bool, checkbox_full_image: bool = False
):
    st_display_kingdom_images(
        k,
        show_full_image=checkbox_full_image,
        show_tooltips=True,
        exclude_tooltip_qualities=exclude_qualities,
    )
    st_build_kingdom_csv_display(k)


def _st_build_buy_selection() -> None:
    c = st.container(border=True)
    c.segmented_control(
        "Buy Availability",
        ["yes", "maybe", "no"],
        selection_mode="single",
        key=load_quiz_widget_value(st.session_state, QUIZ_BUY_ANSWER_KEY),
        format_func=str.capitalize,
        on_change=save_quiz_widget_value,
        args=(st.session_state, QUIZ_BUY_ANSWER_KEY),
        width="stretch",
    )


def _st_build_qualities_selection() -> None:
    for quality in QUIZ_QUALITY_NAMES:
        answer_key = get_quality_answer_key(quality)
        cols = st.columns([1, 8])
        with cols[0]:
            st.image(get_quality_icon_fpath(quality), width="stretch")

        with cols[1]:
            st.segmented_control(
                f"{quality.capitalize()}",
                _QUALITY_OPTIONS,
                key=load_quiz_widget_value(st.session_state, answer_key),
                on_change=save_quiz_widget_value,
                args=(st.session_state, answer_key),
                width="stretch",
                label_visibility="collapsed",
                help=f"Select {quality.capitalize()} quality value",
            )


def _show_selected_buy_icon(buy_str: BuyAvailability | None) -> None:
    if not buy_str:
        st.caption("No buy option selected")
        return
    cont = st.container(horizontal=True, horizontal_alignment="center")
    fpath = PATH_ASSETS.joinpath(f"icons/qualities/buys_icon_{buy_str}.png")
    cont.image(fpath, caption="Selected", width=60)


def _to_val(s: str | None) -> float | None:
    if s is None:
        return None
    if s == ":star:":
        return 0.5
    return float(s)


def _get_selected_quality_values() -> dict[str, float | None]:
    """Returns the selected value for each quality, with None for unselected qualities."""
    return {
        q: _to_val(st.session_state.get(get_quality_answer_key(q)))
        for q in QUIZ_QUALITY_NAMES
    }


def _get_selected_buy_availability() -> BuyAvailability | None:
    return st.session_state.get(QUIZ_BUY_ANSWER_KEY)


def _get_complete_answers() -> QuizAnswers | None:
    """Returns the current answers, or None if anything is still unanswered."""
    quality_values = _get_selected_quality_values()
    buy_str = _get_selected_buy_availability()
    if buy_str is None or any(v is None for v in quality_values.values()):
        return None
    return QuizAnswers(cast(dict[str, float], quality_values), buy_str)


def _plot_qualities(run_state: QuizRunState) -> None:
    submitted = run_state.submitted_answers
    if run_state.phase is QuizPhase.SOLUTION and submitted is not None:
        user_values: Mapping[str, float | None] = submitted.quality_values
        buy_str = submitted.buy_availability
        linecolor = "darkred"
    else:
        user_values = _get_selected_quality_values()
        buy_str = _get_selected_buy_availability()
        linecolor = "darkred" if _get_complete_answers() is not None else "gray"
    fig = st_plot_kingdom_qualities(
        {q: v or 0.0 for q, v in user_values.items()}, linecolor=linecolor
    )
    if run_state.phase is QuizPhase.SOLUTION:
        solution = get_kingdom_solution(run_state.current_kingdom)
        fig = st_plot_kingdom_qualities(
            dict(solution.quality_values),
            fig.axes[0],
            buy_str=solution.buy_availability,
        )
    st.text(
        "Your Estimated Qualities",
        help="The qualities you selected for this kingdom in gray (as long as you aren't finished), then in red. Once the solution is shown, the actual qualities are shown in blue.",
    )
    st.pyplot(fig, True)
    plt.close(fig)
    _show_selected_buy_icon(buy_str)


def plot_score_bar(score: float):
    fig, ax = plt.subplots(figsize=(0.2, 1))
    band_ends = [band.bar_start for band in SCORE_BANDS[1:]] + [MAX_ROUND_SCORE]
    ranges = [
        (band.bar_start, end, band.color) for band, end in zip(SCORE_BANDS, band_ends)
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
    ax.bar(
        0, MAX_ROUND_SCORE, color="none", edgecolor=DOM_BLUE, width=0.5, linewidth=0.5
    )
    ax.axhline(score, color=DOM_BLUE, linewidth=3)
    ax.set_ylim(0, MAX_ROUND_SCORE)
    ax.set_xticks([])
    ax.set_yticks(list(range(0, MAX_ROUND_SCORE + 1, 3)), minor=False)
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


def show_solution_button(run_state: QuizRunState, answers: QuizAnswers | None) -> None:
    f = st.container(horizontal=True, horizontal_alignment="left")
    if answers is None:
        f.info(
            "Please select all qualities and buy availability to unlock the solution."
        )
        return
    if f.button("Click here to show Solution", width="stretch", type="primary"):
        score = score_quiz_round(
            answers.quality_values, answers.buy_availability, run_state.current_kingdom
        )
        if run_state.submit_round(answers, score):
            persist_quiz_run(st.session_state, run_state)
        st.rerun()


def solution_section(score: float) -> None:
    band = get_score_band(score)
    with st.container():
        st.markdown(
            f"<h2 style='color: {band.color};'>Score: {score:g}/{MAX_ROUND_SCORE}</h2>{band.message}",
            unsafe_allow_html=True,
        )
        fig = plot_score_bar(score)
        with st.container(horizontal=True, horizontal_alignment="center"):
            st.pyplot(fig, True, width="content")
        plt.close(fig)


def _get_durable_selection(key: str, enum_cls: type[_E], default: _E) -> _E:
    try:
        return enum_cls(st.session_state.get(key, default))
    except ValueError:
        return default


def _get_selected_mode() -> QuizMode:
    return _get_durable_selection(QUIZ_MODE_KEY, QuizMode, QuizMode.PRACTICE)


def _get_selected_difficulty() -> QuizDifficulty:
    return _get_durable_selection(
        QUIZ_DIFFICULTY_KEY, QuizDifficulty, QuizDifficulty.OPEN_BOOK
    )


def _get_option_label(option: QuizMode | QuizDifficulty) -> str:
    # Module-level instead of a lambda, as session state has to stay picklable
    return option.label


def _build_enum_selection(
    label: str, enum_cls: type[_E], durable_key: str, default: _E
) -> None:
    """Build a required segmented control whose choice survives the widget not being
    rendered (e.g. during a round)."""
    st.session_state[durable_key] = _get_durable_selection(
        durable_key, enum_cls, default
    )
    st.segmented_control(
        label,
        list(enum_cls),
        format_func=_get_option_label,
        selection_mode="single",
        required=True,
        width="stretch",
        key=load_quiz_widget_value(st.session_state, durable_key),
        on_change=save_quiz_widget_value,
        args=(st.session_state, durable_key),
        help="\\\n".join([option.get_description() for option in enum_cls]),
    )


def _start_new_run(mode: QuizMode, difficulty: QuizDifficulty) -> None:
    run_state = QuizRunState.start(
        mode.round_count,
        difficulty=difficulty,
        kingdom=generate_random_quiz_kingdom_string(),
        mode=mode,
    )
    persist_quiz_run(st.session_state, run_state)
    reset_quiz_answers(st.session_state, QUIZ_QUALITY_NAMES)
    st.rerun()


def _build_mode_navigation() -> None:
    col0, col1 = st.container(border=True).columns([1, 2])
    with col0:
        _build_enum_selection("Quiz Mode", QuizMode, QUIZ_MODE_KEY, QuizMode.PRACTICE)
    with col1:
        _build_enum_selection(
            "Difficulty",
            QuizDifficulty,
            QUIZ_DIFFICULTY_KEY,
            QuizDifficulty.OPEN_BOOK,
        )
    mode = _get_selected_mode()
    st.caption(mode.get_description(include_name=False))
    if mode is QuizMode.PRACTICE:
        button_label = "Start Practice"
    else:
        button_label = f"Start {mode.round_count} Kingdom Run"

    if st.button(button_label, type="primary", width="stretch"):
        _start_new_run(mode, _get_selected_difficulty())


def _format_duration(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def _show_timer_text(run_state: QuizRunState) -> None:
    round_time = _format_duration(run_state.get_elapsed_time_of_current_round())
    if run_state.mode is QuizMode.PRACTICE:
        st.text(f"Time: {round_time}")
        return
    total_time = _format_duration(run_state.get_total_elapsed_time_so_far())
    st.text(f"Round Time: {round_time}, Total time: {total_time}")


def _build_timer_display(run_state: QuizRunState) -> None:
    st.session_state.setdefault(QUIZ_HIDE_TIMER_KEY, True)
    hide_timer = st.checkbox(
        "Hide Timer",
        key=load_quiz_widget_value(st.session_state, QUIZ_HIDE_TIMER_KEY),
        on_change=save_quiz_widget_value,
        args=(st.session_state, QUIZ_HIDE_TIMER_KEY),
    )
    if hide_timer:
        return
    if run_state.phase is QuizPhase.ANSWERING:
        # Only keep refreshing while the clock is actually running
        st.fragment(_show_timer_text, run_every=1.0)(run_state)
    else:
        _show_timer_text(run_state)


def _build_run_header(run_state: QuizRunState) -> None:
    header = st.container(horizontal=True, horizontal_alignment="distribute")
    if run_state.mode is QuizMode.RUN:
        diff = run_state.difficulty
        header.text(
            f"Difficulty: {diff.label}",
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
    if run_state.phase is not QuizPhase.FINISHED:
        with header:
            _build_timer_display(run_state)

    if header.button("Stop / Reset", type="secondary"):
        reset_quiz_workflow(st.session_state, QUIZ_QUALITY_NAMES)
        st.rerun()


def _build_finished_summary(run_state: QuizRunState) -> None:
    st.subheader(f"{run_state.round_count} Kingdom Run Complete")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Total Score",
        f"{run_state.cumulative_score:g}/{run_state.maximum_score}",
    )
    col2.metric("Average", f"{run_state.average_score:.1f}/{MAX_ROUND_SCORE}")
    col3.metric(
        "Perfect Rounds",
        f"{run_state.perfect_round_count}/{run_state.round_count}",
    )
    col4.metric("Total Time", _format_duration(run_state.total_elapsed_time))


def _advance_or_restart(run_state: QuizRunState) -> None:
    is_last_round = run_state.current_round_index + 1 == run_state.round_count
    if run_state.mode is QuizMode.PRACTICE:
        label = "Practice Another Kingdom"
    elif is_last_round:
        label = "View Run Summary"
    else:
        label = "Next Kingdom"

    if not st.button(label, type="primary", width="stretch"):
        return
    if run_state.mode is QuizMode.PRACTICE:
        _start_new_run(QuizMode.PRACTICE, run_state.difficulty)
        return
    next_kingdom = "" if is_last_round else generate_random_quiz_kingdom_string()
    run_state.advance_round(next_kingdom)
    persist_quiz_run(st.session_state, run_state)
    reset_quiz_answers(st.session_state, QUIZ_QUALITY_NAMES)
    st.rerun()


def st_build_full_quiz_display() -> None:
    try:
        run_state = restore_persisted_quiz_run(st.session_state)
    except QuizPersistenceError:
        st.session_state.pop(QUIZ_RUN_RECORD_KEY, None)
        st.warning("The saved quiz run could not be restored and was reset.")
        run_state = None

    if run_state is None:
        _build_mode_navigation()
        return

    _build_run_header(run_state)
    if run_state.phase is QuizPhase.FINISHED:
        _build_finished_summary(run_state)
        return

    solution_is_shown = run_state.phase is QuizPhase.SOLUTION
    k = Kingdom.from_dombot_csv_string(run_state.current_kingdom)

    selection_cont = st.container(border=True)

    st.session_state.setdefault(QUIZ_LARGE_VIEW_KEY, False)
    checkbox_large_view = st.sidebar.checkbox(
        "Large Kingdom View",
        key=load_quiz_widget_value(st.session_state, QUIZ_LARGE_VIEW_KEY),
        on_change=save_quiz_widget_value,
        args=(st.session_state, QUIZ_LARGE_VIEW_KEY),
    )
    if checkbox_large_view:
        col0 = selection_cont.expander("The Kingdom", expanded=True)
        col1, col2 = selection_cont.columns(2)
    else:
        col0, col1, col2 = selection_cont.columns(3)
        col0 = col0.container(border=True)
        col0.write("The Kingdom")
    with col0:
        difficulty = run_state.difficulty
        _fragmented_kingdom_display(
            k,
            exclude_qualities=not solution_is_shown and not difficulty.shows_hints,
            checkbox_full_image=difficulty.shows_card_text,
        )
        if solution_is_shown:
            st.info(
                "By hovering over the images, you can now see the individual qualities."
            )

    with col2.container(border=True):
        if solution_is_shown:
            solution_section(run_state.round_score or 0.0)
        else:
            st.write("Adjust Qualities")
            _st_build_buy_selection()
            _st_build_qualities_selection()

    with col1.container(border=True):
        _plot_qualities(run_state)

    if solution_is_shown:
        _advance_or_restart(run_state)
    else:
        show_solution_button(run_state, _get_complete_answers())
