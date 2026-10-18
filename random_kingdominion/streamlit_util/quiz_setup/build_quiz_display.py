from collections.abc import Mapping
from typing import TypeVar, cast

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from ...constants import PATH_ASSETS
from ...kingdom import Kingdom
from ...utils import DOM_BEIGE, get_quality_icon_fpath
from ..common_widgets import st_build_kingdom_csv_display, st_display_kingdom_images
from ..image_util import st_plot_kingdom_qualities
from ..quality_display import EMOJI_DICT
from .explanations import (
    get_feedback_text,
    st_build_explanation_section,
    st_build_explanation_selector,
)
from .kingdom_pool import (
    QUIZ_DEFAULT_EXPANSIONS,
    QUIZ_EXPANSION_OPTIONS,
    QuizKingdomPool,
    QuizPoolSource,
    count_available_kingdoms,
    draw_quiz_kingdom,
    get_curated_kingdom_name,
    sort_expansions,
)
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
    BUY_POINTS,
    EXACT_QUALITY_POINTS,
    MAX_ROUND_SCORE,
    QUIZ_QUALITY_NAMES,
    SCORE_BANDS,
    BuyAvailability,
    get_buy_points,
    get_kingdom_solution,
    get_quality_points,
    get_score_band,
    score_quiz_round,
)
from .util import (
    QUIZ_BUY_ANSWER_KEY,
    QUIZ_DIFFICULTY_KEY,
    QUIZ_EXPANSIONS_KEY,
    QUIZ_HIDE_TIMER_KEY,
    QUIZ_MODE_KEY,
    QUIZ_POOL_SOURCE_KEY,
    get_quality_answer_key,
    load_quiz_widget_value,
    reset_quiz_answers,
    reset_quiz_workflow,
    save_quiz_widget_value,
)

_QUALITY_OPTIONS = ["0", ":star:", "1", "2", "3", "4"]

_E = TypeVar("_E", QuizMode, QuizDifficulty, QuizPoolSource)


_BUY_EXPLANATIONS = {
    "yes": "unconditional +Buy available",
    "maybe": "only conditional +Buy",
    "no": "no +Buy",
}


def _get_quality_label(quality: str) -> str:
    return "Alt-VP" if quality == "altvp" else quality.capitalize()


@st.fragment
def _fragmented_kingdom_display(
    k: Kingdom, exclude_qualities: bool, show_card_text: bool = True
):
    st_display_kingdom_images(
        k,
        show_full_image=show_card_text,
        show_tooltips=True,
        exclude_tooltip_qualities=exclude_qualities,
        hide_landscape_text=not show_card_text,
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
                _get_quality_label(quality),
                _QUALITY_OPTIONS,
                key=load_quiz_widget_value(st.session_state, answer_key),
                on_change=save_quiz_widget_value,
                args=(st.session_state, answer_key),
                width="stretch",
                label_visibility="collapsed",
                help=f"Select {_get_quality_label(quality)} quality value",
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
        (
            "Your Estimate [RED] vs. Solution [BLUE]"
            if run_state.phase is QuizPhase.SOLUTION
            else "Your Estimated Qualities"
        ),
        help="The qualities you selected for this kingdom in gray (as long as you aren't finished), then in red. Once the solution is shown, the actual qualities are shown in blue.",
    )
    with st.container(horizontal=True, horizontal_alignment="center"):
        st.pyplot(fig, True, width=320)
    plt.close(fig)
    # While answering, the Buy selection itself shows the choice already
    if run_state.phase is QuizPhase.SOLUTION:
        _show_selected_buy_icon(buy_str)


def plot_score_bar(score: float):
    """A vertical bar of the score bands: the achieved part in full colour, the rest
    faded, and a marker at the score."""
    fig, ax = plt.subplots(figsize=(0.2, 1))
    band_ends = [band.bar_start for band in SCORE_BANDS[1:]] + [MAX_ROUND_SCORE]
    for band, end in zip(SCORE_BANDS, band_ends):
        start = band.bar_start
        ax.bar(0, end - start, bottom=start, color=band.color, width=0.5, alpha=0.25)
        if score > start:
            ax.bar(
                0, min(end, score) - start, bottom=start, color=band.color, width=0.5
            )
    ax.bar(
        0, MAX_ROUND_SCORE, color="none", edgecolor="#333333", width=0.5, linewidth=0.6
    )
    # Not clipped, so that the marker stays fully visible for a perfect score
    ax.plot(
        [-0.4, 0.4],
        [score, score],
        color="#222222",
        linewidth=5,
        solid_capstyle="butt",
        clip_on=False,
    )
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0, MAX_ROUND_SCORE)
    ax.set_xticks([])
    ax.set_yticks(list(range(0, MAX_ROUND_SCORE + 1, 3)))
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(left=0.05, right=0.95, top=1, bottom=0)
    fig.set_facecolor(DOM_BEIGE)
    ax.set_facecolor(DOM_BEIGE)
    return fig


def _build_submit_button(run_state: QuizRunState) -> None:
    answers = _get_complete_answers()
    num_answered = sum(v is not None for v in _get_selected_quality_values().values())
    num_answered += _get_selected_buy_availability() is not None
    num_questions = len(QUIZ_QUALITY_NAMES) + 1
    label = "Show Solution"
    if answers is None:
        label += f" ({num_answered}/{num_questions} answered)"
    clicked = st.button(
        label,
        type="primary",
        width="stretch",
        disabled=answers is None,
        help="Select Buy availability and one value for all qualities to unlock the solution.",
    )
    if clicked and answers is not None:
        score = score_quiz_round(
            answers.quality_values, answers.buy_availability, run_state.current_kingdom
        )
        if run_state.submit_round(answers, score):
            persist_quiz_run(st.session_state, run_state)
        st.rerun(scope="app")


def _build_settings_badges(run_state: QuizRunState) -> None:
    """Show the mode, difficulty and kingdom pool, and flag whether quality hints
    were shown."""
    with st.container(horizontal=True):
        st.badge(run_state.mode.label, color="gray")
        st.badge(run_state.difficulty.label, color="gray")
        st.badge(run_state.pool.label, color="gray")
        if run_state.difficulty.shows_hints:
            st.badge("Quality hints were shown", icon="💡", color="orange")


def solution_section(run_state: QuizRunState) -> None:
    score = run_state.round_score or 0.0
    band = get_score_band(score)
    text_col, bar_col = st.columns([3, 1], vertical_alignment="center")
    with text_col:
        st.markdown(
            f"<h2 style='color: {band.color};'>Score: {score:g}/{MAX_ROUND_SCORE}</h2>{band.message}",
            unsafe_allow_html=True,
        )
        _build_settings_badges(run_state)
        if title := _get_kingdom_title(run_state, run_state.current_kingdom):
            st.markdown(title)
    fig = plot_score_bar(score)
    bar_col.pyplot(fig, True, width="content")
    plt.close(fig)


def _get_points_icon(points: float, max_points: float) -> str:
    if points == max_points:
        return "✅"
    return "🟡" if points > 0 else "❌"


def _build_solution_breakdown(answers: QuizAnswers, kingdom_str: str) -> None:
    """Show a table of how each quality's total came together, next to the answers."""
    solution = get_kingdom_solution(kingdom_str)
    header = [
        "",
        "Quality",
        "You",
        "Solution",
        "Points",
        "Contributing CSOs",
        "Calculation",
    ]
    rows = [header, [":-:", "---", ":-:", ":-:", ":-:", "---", "---"]]
    for q in QUIZ_QUALITY_NAMES:
        user_val = answers.quality_values[q]
        real_val = solution.quality_values[q]
        points = get_quality_points(user_val, real_val)
        contributions = ", ".join(
            f"{name} ({val:g})" for name, val in solution.contributions[q]
        )
        rows.append(
            [
                _get_points_icon(points, EXACT_QUALITY_POINTS),
                f"{EMOJI_DICT[q]} {_get_quality_label(q)}",
                f"{user_val:g}",
                f"**{real_val:g}**",
                f"{points:g}/{EXACT_QUALITY_POINTS}",
                contributions or "–",
                "; ".join(solution.aggregation_steps[q]),
            ]
        )
    buy_points = get_buy_points(answers.buy_availability, solution.buy_availability)
    buy_sources = ", ".join(
        name + (" (conditional)" if is_conditional else "")
        for name, is_conditional in solution.buy_sources
    )
    rows.append(
        [
            _get_points_icon(buy_points, BUY_POINTS),
            "🛒 Buy",
            answers.buy_availability.capitalize(),
            f"**{solution.buy_availability.capitalize()}**",
            f"{buy_points:g}/{BUY_POINTS}",
            buy_sources or "–",
            _BUY_EXPLANATIONS[solution.buy_availability],
        ]
    )
    st.markdown("\n".join("| " + " | ".join(row) + " |" for row in rows))
    st.caption(
        "A value of 0.5 corresponds to :star: in the selection.\n'4×1 → 1×2' means that four CSOs with a value of 1 count as one with a value of 2; see *Quality Calculation Details* at the top for the full rules.\n"
        + get_feedback_text()
    )


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


# The ids are unique across the enums, so one lookup serves all selections
_OPTION_LABELS = {
    option.value: option.label
    for enum_cls in (QuizMode, QuizDifficulty, QuizPoolSource)
    for option in enum_cls
}


def _get_option_label(option_id: str) -> str:
    # Module-level instead of a lambda, as session state has to stay picklable
    return _OPTION_LABELS[option_id]


def _build_enum_selection(
    label: str, enum_cls: type[_E], durable_key: str, default: _E
) -> None:
    """Build a required segmented control whose choice survives the widget not being
    rendered (e.g. during a round)."""
    # Only the plain ids go into session state: pickle stores enum members by
    # reference, which fails once Streamlit reloads their module after a code change
    # (the member in session state then belongs to the old class).
    st.session_state[durable_key] = _get_durable_selection(
        durable_key, enum_cls, default
    ).value
    st.segmented_control(
        label,
        [option.value for option in enum_cls],
        format_func=_get_option_label,
        selection_mode="single",
        required=True,
        width="stretch",
        key=load_quiz_widget_value(st.session_state, durable_key),
        on_change=save_quiz_widget_value,
        args=(st.session_state, durable_key),
        help="\\\n".join([option.get_description() for option in enum_cls]),
    )


def _get_selected_pool_source() -> QuizPoolSource:
    return _get_durable_selection(
        QUIZ_POOL_SOURCE_KEY, QuizPoolSource, QuizPoolSource.RANDOM
    )


def _get_selected_expansions() -> tuple[str, ...]:
    selected = st.session_state.get(QUIZ_EXPANSIONS_KEY, QUIZ_DEFAULT_EXPANSIONS)
    if not isinstance(selected, (list, tuple)):
        return QUIZ_DEFAULT_EXPANSIONS
    return sort_expansions(selected)


def _get_selected_pool() -> QuizKingdomPool:
    return QuizKingdomPool(_get_selected_pool_source(), _get_selected_expansions())


_EXPANSION_SHORTCUTS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Select all", "✅", QUIZ_EXPANSION_OPTIONS),
    ("Clear selection", "❌", ()),
    (
        "Select all except 1E",
        "☑️",
        tuple(exp for exp in QUIZ_EXPANSION_OPTIONS if "1E" not in exp),
    ),
)


def _build_expansion_toggle_row() -> None:
    """The same shortcuts as in the randomizer's expansion selection."""
    # Handled inline instead of in on_click callbacks: those can fire on the first
    # rerun of a round in AppTest, which keeps the start screen's buttons from the
    # run interrupted by st.rerun() (see the conftest of the tests).
    for col, (label, icon, expansions) in zip(st.columns(3), _EXPANSION_SHORTCUTS):
        if col.button(label, width="stretch", icon=icon):
            st.session_state[QUIZ_EXPANSIONS_KEY] = list(expansions)
            # Rerun, so that the count in the expander's label is updated as well
            st.rerun(scope="app")


def _build_expansion_selection() -> None:
    """The expansions the kingdoms may use, for random and curated pools alike.
    Independent of the randomizer's expansion selection."""
    selected = _get_selected_expansions()
    st.session_state[QUIZ_EXPANSIONS_KEY] = list(selected)
    label = f"Your expansions ({len(selected)} of {len(QUIZ_EXPANSION_OPTIONS)} selected)"
    # A key, so that the expander stays open when the count in its label changes
    with st.expander(label, key="quiz_expansions_expander"):
        _build_expansion_toggle_row()
        st.pills(
            "Expansions",
            QUIZ_EXPANSION_OPTIONS,
            selection_mode="multi",
            key=load_quiz_widget_value(st.session_state, QUIZ_EXPANSIONS_KEY),
            on_change=save_quiz_widget_value,
            args=(st.session_state, QUIZ_EXPANSIONS_KEY),
            label_visibility="collapsed",
            width="stretch",
        )


def _build_pool_availability(pool: QuizKingdomPool, mode: QuizMode) -> bool:
    """Show how many kingdoms the pool has, and whether that's enough for the mode.
    Returns whether the quiz can be started."""
    if not pool.expansions:
        st.warning("No expansions selected! Please select at least one expansion.")
        return False
    # Only shown if it takes a while, i.e. the first time a curated pool is loaded on
    # this server; afterwards the pool is cached for all sessions
    with st.spinner(f"Loading the {pool.source.label} kingdoms..."):
        num_available = count_available_kingdoms(pool)
    if num_available is None:
        st.caption(f"✔ Random kingdoms from {pool.expansion_summary}.")
        return True
    if num_available >= mode.round_count:
        st.caption(
            f"✔ {num_available} {pool.source.label} kingdoms use only your expansions."
        )
        return True
    kingdoms = "kingdom uses" if num_available == 1 else "kingdoms use"
    advice = "select more expansions or choose another pool."
    if mode is QuizMode.RUN:
        advice = "select more expansions, switch to Practice, or choose another pool."
    st.warning(
        f"Only {num_available} {pool.source.label} {kingdoms} only your expansions, "
        f"but a {mode.label} needs {mode.round_count}. Please {advice}"
    )
    return False


def _get_kingdom_title(run_state: QuizRunState, kingdom_str: str) -> str | None:
    """The name of a curated kingdom, to be shown once it's solved."""
    name = get_curated_kingdom_name(run_state.pool, kingdom_str)
    if name is None:
        return None
    return run_state.pool.source.get_kingdom_name_label(name)


def _start_new_run(
    mode: QuizMode, difficulty: QuizDifficulty, pool: QuizKingdomPool
) -> None:
    run_state = QuizRunState.start(
        mode.round_count,
        difficulty=difficulty,
        kingdom=draw_quiz_kingdom(pool),
        mode=mode,
        pool=pool,
    )
    persist_quiz_run(st.session_state, run_state)
    reset_quiz_answers(st.session_state, QUIZ_QUALITY_NAMES)
    st.rerun(scope="app")


def _build_mode_navigation() -> None:
    st_build_explanation_section()
    settings = st.container(border=True)
    col0, col1 = settings.columns([1, 2])
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
    with settings:
        st.caption(mode.get_description(include_name=False))
        _build_enum_selection(
            "Kingdom Pool", QuizPoolSource, QUIZ_POOL_SOURCE_KEY, QuizPoolSource.RANDOM
        )
        _build_expansion_selection()
        pool = _get_selected_pool()
        can_start = _build_pool_availability(pool, mode)
    if mode is QuizMode.PRACTICE:
        button_label = "Start Practice"
    else:
        button_label = f"Start {mode.round_count} Kingdom Run"

    if st.button(
        button_label, type="primary", width="stretch", disabled=not can_start
    ):
        _start_new_run(mode, _get_selected_difficulty(), pool)


def _format_duration(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def _get_timer_label(run_state: QuizRunState) -> str:
    round_time = _format_duration(run_state.get_elapsed_time_of_current_round())
    if run_state.mode is QuizMode.PRACTICE:
        return f"⏱ {round_time}"
    total_time = _format_duration(run_state.get_total_elapsed_time_so_far())
    return f"⏱ {round_time} / {total_time}"


def _build_timer_button(run_state: QuizRunState) -> None:
    """A single button that shows the time (or offers to show it) and toggles it."""
    hidden = st.session_state[QUIZ_HIDE_TIMER_KEY]
    clicked = st.button(
        "⏱ Show time" if hidden else _get_timer_label(run_state),
        # A fixed key, as the label changes every second
        key="quiz_timer_button",
        width="stretch",
        help=(
            "Show the elapsed time."
            if hidden
            else "Elapsed time of this round (and of the whole run). Click to hide."
        ),
    )
    if clicked:
        st.session_state[QUIZ_HIDE_TIMER_KEY] = not hidden
        # Whether the timer refreshes every second is decided in the full run
        st.rerun(scope="app")


def _build_timer(run_state: QuizRunState) -> None:
    st.session_state.setdefault(QUIZ_HIDE_TIMER_KEY, True)
    # Only keep refreshing while the clock is actually running and visible
    is_ticking = (
        not st.session_state[QUIZ_HIDE_TIMER_KEY]
        and run_state.phase is QuizPhase.ANSWERING
    )
    st.fragment(_build_timer_button, run_every=1.0 if is_ticking else None)(run_state)


def _build_run_header(run_state: QuizRunState) -> None:
    # Fixed slots, so that nothing moves when e.g. the timer is shown or hidden
    settings_col, progress_col, timer_col, actions_col = st.columns(
        [3, 2, 2, 3], vertical_alignment="center"
    )
    with settings_col:
        _build_settings_badges(run_state)
    if run_state.mode is QuizMode.RUN:
        progress_col.markdown(
            f"**Round {run_state.current_round_index + 1} of {run_state.round_count}** · Score {run_state.cumulative_score:g}/{run_state.maximum_score}"
        )
    if run_state.phase is not QuizPhase.FINISHED:
        with timer_col:
            _build_timer(run_state)

    actions = actions_col.container(horizontal=True, horizontal_alignment="right")
    with actions.popover("❓ Rules & Tips"):
        st_build_explanation_selector()
    if run_state.phase is QuizPhase.FINISHED:
        # Nothing to lose anymore, so no confirmation needed
        actions.button("Back to Start", on_click=_reset_quiz)
    elif actions.button("Stop / Reset", type="secondary"):
        _confirm_reset_dialog(run_state)

    if run_state.mode is QuizMode.RUN:
        st.progress(len(run_state.completed_rounds) / run_state.round_count)


def _reset_quiz() -> None:
    reset_quiz_workflow(st.session_state, QUIZ_QUALITY_NAMES)


@st.dialog("Stop this quiz?")
def _confirm_reset_dialog(run_state: QuizRunState) -> None:
    if run_state.mode is QuizMode.RUN:
        st.write(
            f"You are in round {run_state.current_round_index + 1} of {run_state.round_count} with {run_state.cumulative_score:g} points so far. This progress will be lost."
        )
    else:
        st.write("The current kingdom will be discarded.")
    buttons = st.container(horizontal=True, horizontal_alignment="right")
    if buttons.button("Cancel"):
        st.rerun()
    # Resetting in a callback, as the dialog's own rerun only reruns the dialog
    if buttons.button("Stop quiz", type="primary", on_click=_reset_quiz):
        st.rerun()


def _get_kingdom_summary(kingdom_str: str) -> str:
    solution = get_kingdom_solution(kingdom_str)
    summary = ", ".join(solution.card_names)
    if solution.landscape_names:
        summary += " | " + ", ".join(solution.landscape_names)
    return summary


def _build_round_table(run_state: QuizRunState) -> None:
    rows = [
        {
            "Round": r.round_index + 1,
            "Score": r.score,
            "Time": _format_duration(r.elapsed_time),
            "Kingdom": _get_kingdom_summary(r.kingdom),
            **(
                {"Name": get_curated_kingdom_name(run_state.pool, r.kingdom) or "–"}
                if run_state.pool.source.is_curated
                else {}
            ),
        }
        for r in run_state.completed_rounds
    ]
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        column_config={
            "Round": st.column_config.NumberColumn("Round", width="small"),
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=0, max_value=MAX_ROUND_SCORE, format="%g"
            ),
            "Time": st.column_config.TextColumn("Time", width="small"),
            "Kingdom": st.column_config.TextColumn("Kingdom (cards | landscapes)"),
        },
    )


def _build_quality_tendencies(run_state: QuizRunState) -> None:
    """Show per quality how often the answer was exact, and whether the user tends
    to over- or underestimate it."""
    rounds = run_state.completed_rounds
    rows = []
    for q in QUIZ_QUALITY_NAMES:
        offsets = [
            r.submitted_answers.quality_values[q]
            - get_kingdom_solution(r.kingdom).quality_values[q]
            for r in rounds
        ]
        rows.append(
            {
                "Quality": f"{EMOJI_DICT[q]} {_get_quality_label(q)}",
                "Exact": f"{sum(o == 0 for o in offsets)}/{len(rounds)}",
                "Avg. points": sum(get_quality_points(o, 0) for o in offsets)
                / len(rounds),
                "Avg. offset": f"{sum(offsets) / len(rounds):+.1f}",
            }
        )
    buy_correct = sum(
        get_buy_points(
            r.submitted_answers.buy_availability,
            get_kingdom_solution(r.kingdom).buy_availability,
        )
        > 0
        for r in rounds
    )
    rows.append(
        {
            "Quality": "🛒 Buy",
            "Exact": f"{buy_correct}/{len(rounds)}",
            "Avg. points": buy_correct / len(rounds) * EXACT_QUALITY_POINTS,
            "Avg. offset": "–",
        }
    )
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        column_config={
            "Avg. points": st.column_config.ProgressColumn(
                "Avg. points",
                min_value=0,
                max_value=EXACT_QUALITY_POINTS,
                format="%.1f",
                help=f"Average points per round, scaled to {EXACT_QUALITY_POINTS} (the Buy row is scaled down from {BUY_POINTS}).",
            ),
            "Avg. offset": st.column_config.TextColumn(
                "Avg. offset",
                help="Your answer minus the real value, on average. Positive values mean you tend to overestimate the quality, negative ones that you underestimate it.",
            ),
        },
    )


def _format_round_option(round_index: int) -> str:
    # Module-level instead of a lambda, as session state has to stay picklable
    return str(round_index + 1)


@st.fragment
def _build_round_details(run_state: QuizRunState) -> None:
    round_index = st.segmented_control(
        "Show the details of round",
        list(range(len(run_state.completed_rounds))),
        format_func=_format_round_option,
        default=0,
        required=True,
        key="quiz_summary_round",
        width="stretch",
    )
    completed_round = run_state.completed_rounds[round_index or 0]
    if title := _get_kingdom_title(run_state, completed_round.kingdom):
        st.markdown(title)
    st.markdown(f"**Kingdom:** {_get_kingdom_summary(completed_round.kingdom)}")
    _build_solution_breakdown(
        completed_round.submitted_answers, completed_round.kingdom
    )


def _build_finished_summary(run_state: QuizRunState) -> None:
    st.subheader(f"{run_state.round_count} Kingdom Run Complete")
    _build_settings_badges(run_state)
    st.caption(f"Kingdoms drawn from: {', '.join(run_state.pool.expansions)}")
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

    with st.container(border=True):
        st.markdown("#### 📋 Rounds")
        _build_round_table(run_state)
    with st.container(border=True):
        st.markdown("#### 🎯 Your tendencies per quality")
        _build_quality_tendencies(run_state)
    with st.container(border=True):
        st.markdown("#### 🔎 Round details")
        _build_round_details(run_state)
    if st.button("Play again with the same settings", type="primary", width="stretch"):
        _start_new_run(run_state.mode, run_state.difficulty, run_state.pool)


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
        _start_new_run(QuizMode.PRACTICE, run_state.difficulty, run_state.pool)
        return
    next_kingdom = (
        ""
        if is_last_round
        else draw_quiz_kingdom(run_state.pool, exclude=run_state.used_kingdoms)
    )
    run_state.advance_round(next_kingdom)
    persist_quiz_run(st.session_state, run_state)
    reset_quiz_answers(st.session_state, QUIZ_QUALITY_NAMES)
    st.rerun(scope="app")


@st.fragment
def _build_side_column(run_state: QuizRunState) -> None:
    """The answers (or the score) with the submit (or next) button, and the plot.
    A fragment, so that answer clicks only rerun this column instead of the whole page
    with all its card images; submitting and advancing rerun the whole page."""
    solution_is_shown = run_state.phase is QuizPhase.SOLUTION
    # The button right below the inputs/score, so it stays above the fold
    with st.container(border=True):
        if solution_is_shown:
            solution_section(run_state)
            _advance_or_restart(run_state)
        else:
            st.write("Adjust Qualities")
            _st_build_buy_selection()
            _st_build_qualities_selection()
            _build_submit_button(run_state)
    with st.container(border=True):
        _plot_qualities(run_state)


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

    kingdom_col, side_col = st.container(border=True).columns([2, 1])
    with kingdom_col.container(border=True):
        st.write("The Kingdom")
        difficulty = run_state.difficulty
        _fragmented_kingdom_display(
            k,
            exclude_qualities=not solution_is_shown and not difficulty.shows_hints,
            # Once solved, reveal the card texts to make the solution easier to follow
            show_card_text=difficulty.shows_card_text or solution_is_shown,
        )
        if solution_is_shown:
            st.info(
                "By hovering over the images, you can now see the individual qualities."
            )

    with side_col:
        _build_side_column(run_state)

    if solution_is_shown and run_state.submitted_answers is not None:
        with st.container(border=True):
            st.markdown("#### 🔎 How the values are calculated")
            _build_solution_breakdown(
                run_state.submitted_answers, run_state.current_kingdom
            )
