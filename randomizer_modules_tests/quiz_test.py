import pytest

from random_kingdominion.streamlit_util.quiz_setup.run_state import (
    QUIZ_SCORING_VERSION,
    CompletedQuizRound,
    QuizAnswers,
    QuizPhase,
    QuizRunState,
)
from random_kingdominion.streamlit_util.quiz_setup.util import (
    load_quiz_widget_value,
    reset_quiz_answers,
    save_quiz_widget_value,
    st_calc_quiz_score,
)


@pytest.mark.parametrize(
    ("user_value", "expected_score"),
    [(2, 2), (1.5, 1.5), (1, 1), (0.5, 0)],
)
def test_quiz_quality_score_offsets(user_value: float, expected_score: float) -> None:
    assert (
        st_calc_quiz_score({"draw": user_value}, {"draw": 2}, "", "no")
        == expected_score
    )


def test_quiz_buy_score_is_case_insensitive() -> None:
    assert st_calc_quiz_score({}, {}, "YES", "yes") == 3
    assert st_calc_quiz_score({}, {}, "maybe", "yes") == 0


def test_quiz_score_rejects_unknown_quality() -> None:
    with pytest.raises(ValueError, match="'draw'"):
        st_calc_quiz_score({"draw": 2}, {}, "no", "no")


def test_reset_quiz_answers_clears_current_round_only() -> None:
    state = {
        "quiz_show_solution": True,
        "quiz_quality_buy_str": "yes",
        "quiz_quality_slider_draw": 3,
        "quiz_quality_slider_gain": 2,
        "quiz_total_score": 12.5,
    }

    reset_quiz_answers(state, ["draw", "gain"])

    assert state["quiz_show_solution"] is False
    assert "quiz_quality_buy_str" not in state
    assert state["quiz_quality_slider_draw"] == -1
    assert state["quiz_quality_slider_gain"] == -1
    assert state["quiz_total_score"] == 12.5


def test_quiz_widget_state_sync_preserves_durable_answer() -> None:
    state = {"quiz_quality_slider_draw": 2}

    widget_key = load_quiz_widget_value(state, "quiz_quality_slider_draw")
    assert widget_key == "_quiz_quality_slider_draw"
    assert state[widget_key] == 2

    state[widget_key] = 3
    save_quiz_widget_value(state, "quiz_quality_slider_draw")
    assert state["quiz_quality_slider_draw"] == 3

    state.pop(widget_key)
    load_quiz_widget_value(state, "quiz_quality_slider_draw")
    assert state[widget_key] == 3


def test_quiz_widget_state_sync_keeps_empty_buy_unselected() -> None:
    state = {"_quiz_quality_buy_str": "yes"}

    widget_key = load_quiz_widget_value(state, "quiz_quality_buy_str")

    assert widget_key not in state


def test_quiz_run_state_starts_not_started() -> None:
    run_state = QuizRunState()

    assert run_state.phase is QuizPhase.NOT_STARTED
    assert run_state.phase == "not_started"
    assert run_state.round_count == 1
    assert run_state.current_round_index == 0
    assert run_state.current_kingdom == ""
    assert run_state.submitted_answers is None
    assert run_state.round_score is None
    assert run_state.cumulative_score == 0
    assert run_state.completed_rounds == []
    assert run_state.scoring_version == QUIZ_SCORING_VERSION


@pytest.mark.parametrize("phase", list(QuizPhase))
def test_quiz_run_state_accepts_each_phase(phase: QuizPhase) -> None:
    run_state = QuizRunState(phase=phase)

    assert run_state.phase is phase


def test_quiz_run_state_tracks_run_and_current_round() -> None:
    answers = QuizAnswers({"draw": 2, "gain": 1.5}, "yes")
    run_state = QuizRunState(
        phase=QuizPhase.SOLUTION,
        round_count=10,
        current_round_index=2,
        current_kingdom="Village, Smithy",
        submitted_answers=answers,
        round_score=12.5,
        cumulative_score=37.0,
    )

    assert run_state.run_id
    assert run_state.current_round_index == 2
    assert run_state.current_kingdom == "Village, Smithy"
    assert run_state.submitted_answers is answers
    assert run_state.round_score == 12.5
    assert run_state.cumulative_score == 37.0
    assert run_state.scoring_version == QUIZ_SCORING_VERSION


def test_quiz_run_state_tracks_completed_round_history() -> None:
    answers = QuizAnswers({"draw": 2}, "maybe")
    completed_round = CompletedQuizRound(0, "Village, Smithy", answers, 13.5)
    run_state = QuizRunState(round_count=10, completed_rounds=[completed_round])

    assert run_state.completed_rounds == [completed_round]
    assert run_state.completed_rounds[0].submitted_answers.quality_values == {
        "draw": 2
    }


def test_quiz_run_state_uses_independent_ids_and_history() -> None:
    first_run = QuizRunState()
    second_run = QuizRunState()

    first_run.completed_rounds.append(
        CompletedQuizRound(0, "Village, Smithy", QuizAnswers({}, "no"), 3)
    )

    assert first_run.run_id != second_run.run_id
    assert second_run.completed_rounds == []


@pytest.mark.parametrize(
    ("round_count", "current_round_index"),
    [(0, 0), (10, -1), (10, 10)],
)
def test_quiz_run_state_rejects_invalid_round_position(
    round_count: int, current_round_index: int
) -> None:
    with pytest.raises(ValueError):
        QuizRunState(
            round_count=round_count,
            current_round_index=current_round_index,
        )
