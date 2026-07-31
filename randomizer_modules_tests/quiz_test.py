import pytest

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
