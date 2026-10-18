import json
import pickle
from datetime import datetime

import pytest

from random_kingdominion.kingdom import Kingdom
from random_kingdominion.streamlit_util.quiz_setup.persistence import (
    QuizPersistenceError,
    deserialize_quiz_run,
    persist_quiz_run,
    restore_persisted_quiz_run,
    serialize_quiz_run,
)
from random_kingdominion.streamlit_util.quiz_setup.run_state import (
    QUIZ_SCORING_VERSION,
    CompletedQuizRound,
    QuizAnswers,
    QuizDifficulty,
    QuizMode,
    QuizPhase,
    QuizRunState,
)
from random_kingdominion.streamlit_util.quiz_setup.scoring import (
    MAX_ROUND_SCORE,
    PERFECT_BAND,
    SCORE_BANDS,
    calc_quiz_score,
    get_buy_points,
    get_kingdom_solution,
    get_quality_points,
    get_score_band,
)
from random_kingdominion.streamlit_util.quiz_setup.util import (
    load_quiz_widget_value,
    reset_quiz_answers,
    reset_quiz_workflow,
    save_quiz_widget_value,
)


@pytest.mark.parametrize(
    ("user_value", "expected_score"),
    [(2, 2), (1.5, 1.5), (1, 1), (0.5, 0)],
)
def test_quiz_quality_score_offsets(user_value: float, expected_score: float) -> None:
    assert (
        calc_quiz_score({"draw": user_value}, {"draw": 2}, "", "no")
        == expected_score
    )


def test_quiz_buy_score_is_case_insensitive() -> None:
    assert calc_quiz_score({}, {}, "YES", "yes") == 3
    assert calc_quiz_score({}, {}, "maybe", "yes") == 0


def test_quiz_score_rejects_unknown_quality() -> None:
    with pytest.raises(ValueError, match="'draw'"):
        calc_quiz_score({"draw": 2}, {}, "no", "no")


def test_reset_quiz_answers_clears_current_round_only() -> None:
    state = {
        "quiz_quality_buy_str": "yes",
        "quiz_quality_slider_draw": 3,
        "quiz_quality_slider_gain": 2,
        "quiz_total_score": 12.5,
    }

    reset_quiz_answers(state, ["draw", "gain"])

    assert "quiz_quality_buy_str" not in state
    assert "quiz_quality_slider_draw" not in state
    assert "quiz_quality_slider_gain" not in state
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
    start_time = datetime(2026, 1, 1)
    end_time = datetime(2026, 1, 1, 1)
    completed_round = CompletedQuizRound(
        0, "Village, Smithy", answers, 13.5, start_time=start_time, end_time=end_time
    )
    run_state = QuizRunState(round_count=10, completed_rounds=[completed_round])

    assert run_state.completed_rounds == [completed_round]
    assert run_state.completed_rounds[0].submitted_answers.quality_values == {"draw": 2}


def test_quiz_run_state_uses_independent_ids_and_history() -> None:
    first_run = QuizRunState()
    second_run = QuizRunState()
    start_time = datetime(2026, 1, 1)
    end_time = datetime(2026, 1, 1, 1)

    first_run.completed_rounds.append(
        CompletedQuizRound(
            0,
            "Village, Smithy",
            QuizAnswers({}, "no"),
            3,
            start_time=start_time,
            end_time=end_time,
        )
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


def test_quiz_run_submission_is_idempotent() -> None:
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, "Village, Smithy", QuizMode.PRACTICE
    )
    answers = QuizAnswers({"draw": 2}, "yes")

    assert run_state.submit_round(answers, 12.5) is True
    assert run_state.submit_round(answers, 12.5) is False
    assert run_state.phase is QuizPhase.SOLUTION
    assert run_state.cumulative_score == 12.5
    assert len(run_state.completed_rounds) == 1


def test_quiz_run_start_selects_mode_and_is_serializable() -> None:
    practice = QuizRunState.start(
        1, QuizDifficulty.OPEN_BOOK, "Practice Kingdom", QuizMode.PRACTICE
    )
    multi_run = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, "Run Kingdom", QuizMode.RUN
    )

    assert practice.mode is QuizMode.PRACTICE
    assert multi_run.mode is QuizMode.RUN
    assert pickle.loads(pickle.dumps(multi_run)) == multi_run


def test_quiz_run_advances_and_resets_current_round() -> None:
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, "Village, Smithy", QuizMode.RUN
    )
    run_state.submit_round(QuizAnswers({"draw": 2}, "yes"), 12.5)

    run_state.advance_round("Market, Chapel")

    assert run_state.phase is QuizPhase.ANSWERING
    assert run_state.current_round_index == 1
    assert run_state.current_kingdom == "Market, Chapel"
    assert run_state.submitted_answers is None
    assert run_state.round_score is None
    assert run_state.cumulative_score == 12.5


def test_quiz_run_finishes_after_last_scored_round() -> None:
    run_state = QuizRunState.start(
        1, QuizDifficulty.OPEN_BOOK, "Village, Smithy", QuizMode.PRACTICE
    )
    run_state.submit_round(QuizAnswers({"draw": 2}, "yes"), 15)

    run_state.advance_round("")

    assert run_state.phase is QuizPhase.FINISHED
    assert run_state.cumulative_score == 15
    assert run_state.average_score == 15
    assert run_state.perfect_round_count == 1
    assert run_state.maximum_score == 15


def test_quiz_run_summary_metrics_cover_multiple_rounds() -> None:
    run_state = QuizRunState.start(10, QuizDifficulty.OPEN_BOOK, "First", QuizMode.RUN)
    run_state.submit_round(QuizAnswers({}, "yes"), 15)
    run_state.advance_round("Second")
    run_state.submit_round(QuizAnswers({}, "no"), 10)

    assert run_state.cumulative_score == 25
    assert run_state.average_score == 12.5
    assert run_state.perfect_round_count == 1
    assert run_state.maximum_score == 150


def test_reset_quiz_workflow_clears_run_and_preserves_unrelated_state() -> None:
    state = {
        "quiz_run_record": "saved record",
        "quiz_quality_buy_str": "yes",
        "_quiz_quality_buy_str": "yes",
        "quiz_quality_slider_draw": 2,
        "_quiz_quality_slider_draw": 2,
        "unrelated": "keep me",
    }

    reset_quiz_workflow(state, ["draw"])

    assert "quiz_run_record" not in state
    assert "quiz_quality_buy_str" not in state
    assert "_quiz_quality_buy_str" not in state
    assert "quiz_quality_slider_draw" not in state
    assert "_quiz_quality_slider_draw" not in state
    assert state["unrelated"] == "keep me"


def test_quiz_run_persistence_restores_scored_progress() -> None:
    kingdom = Kingdom(cards=["Village", "Smithy"])
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, kingdom.get_dombot_csv_string(), QuizMode.RUN
    )
    quality_values = {
        quality: value
        for quality, value in kingdom.total_qualities.items()
        if quality != "interactivity"
    }
    answers = QuizAnswers(quality_values, kingdom.buy_availability)
    trusted_score = calc_quiz_score(
        quality_values,
        kingdom.total_qualities,
        kingdom.buy_availability,
        kingdom.buy_availability,
    )
    run_state.submit_round(answers, trusted_score)

    restored_run = deserialize_quiz_run(serialize_quiz_run(run_state))

    assert restored_run == run_state
    assert restored_run.submit_round(answers, 15) is False


def test_quiz_run_persistence_recomputes_tampered_scores() -> None:
    kingdom = Kingdom(cards=["Village", "Smithy"])
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, kingdom.get_dombot_csv_string(), QuizMode.RUN
    )
    quality_values = {
        quality: value
        for quality, value in kingdom.total_qualities.items()
        if quality != "interactivity"
    }
    answers = QuizAnswers(quality_values, kingdom.buy_availability)
    trusted_score = calc_quiz_score(
        quality_values,
        kingdom.total_qualities,
        kingdom.buy_availability,
        kingdom.buy_availability,
    )
    run_state.submit_round(answers, trusted_score)
    record = json.loads(serialize_quiz_run(run_state))
    record["completed_rounds"][0]["score"] = 999

    restored_run = deserialize_quiz_run(json.dumps(record))

    assert restored_run.round_score == trusted_score
    assert restored_run.cumulative_score == trusted_score


def test_quiz_run_persistence_rejects_unknown_scoring_version() -> None:
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, "Village, Smithy", QuizMode.RUN
    )
    record = json.loads(serialize_quiz_run(run_state))
    record["scoring_version"] = "future"

    with pytest.raises(QuizPersistenceError, match="scoring version"):
        deserialize_quiz_run(json.dumps(record))


def test_quiz_run_persistence_restores_from_session_mapping() -> None:
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, "Village, Smithy", QuizMode.RUN
    )
    state = {}

    persist_quiz_run(state, run_state)
    restored_run = restore_persisted_quiz_run(state)

    assert restored_run == run_state


def test_quiz_run_persistence_restores_finished_cumulative_score() -> None:
    kingdom = Kingdom(cards=["Village", "Smithy"])
    quality_values = {
        quality: value
        for quality, value in kingdom.total_qualities.items()
        if quality != "interactivity"
    }
    answers = QuizAnswers(quality_values, kingdom.buy_availability)
    trusted_score = calc_quiz_score(
        quality_values,
        kingdom.total_qualities,
        kingdom.buy_availability,
        kingdom.buy_availability,
    )
    run_state = QuizRunState.start(
        1, QuizDifficulty.OPEN_BOOK, kingdom.get_dombot_csv_string(), QuizMode.RUN
    )
    run_state.submit_round(answers, trusted_score)
    run_state.advance_round("")

    restored_run = deserialize_quiz_run(serialize_quiz_run(run_state))

    assert restored_run.phase is QuizPhase.FINISHED
    assert restored_run.cumulative_score == trusted_score
    assert restored_run.average_score == trusted_score


def test_max_round_score_matches_scoring_rules() -> None:
    assert MAX_ROUND_SCORE == 15
    perfect_answers = {q: 1.0 for q in ("gain", "thinning", "draw", "village", "altvp", "attack")}
    assert calc_quiz_score(perfect_answers, perfect_answers, "yes", "yes") == MAX_ROUND_SCORE


@pytest.mark.parametrize(
    ("score", "expected_color"),
    [
        (0, "red"),
        (0.5, "red"),
        (1, "orange"),
        (8, "orange"),
        (8.5, "gold"),
        (11, "gold"),
        (11.5, "lightgreen"),
        (14.5, "lightgreen"),
        (15, "green"),
    ],
)
def test_score_bands_use_good_above_8_and_impressive_above_11(
    score: float, expected_color: str
) -> None:
    assert get_score_band(score).color == expected_color


def test_score_bar_bands_are_ordered_and_end_with_perfect() -> None:
    starts = [band.bar_start for band in SCORE_BANDS]
    assert starts == sorted(starts)
    assert SCORE_BANDS[-1] is PERFECT_BAND
    assert PERFECT_BAND.bar_start < MAX_ROUND_SCORE


@pytest.mark.parametrize("enum_cls", [QuizMode, QuizDifficulty])
def test_quiz_enums_use_stable_ids_and_separate_labels(enum_cls) -> None:
    for member in enum_cls:
        assert member.value.isascii()
        assert member.label != member.value
        assert enum_cls(member.value) is member
        assert member.label in member.get_description()


def test_quiz_mode_round_counts() -> None:
    assert QuizMode.PRACTICE.round_count == 1
    assert QuizMode.RUN.round_count == 10


def test_only_open_book_shows_hints_and_only_hard_hides_text() -> None:
    assert [d for d in QuizDifficulty if d.shows_hints] == [QuizDifficulty.OPEN_BOOK]
    assert [d for d in QuizDifficulty if not d.shows_card_text] == [QuizDifficulty.HARD]


def test_kingdom_solution_is_cached_and_uses_plain_floats() -> None:
    kingdom_str = Kingdom(cards=["Village", "Smithy", "Chapel"]).get_dombot_csv_string()
    solution = get_kingdom_solution(kingdom_str)

    assert get_kingdom_solution(kingdom_str) is solution
    assert "interactivity" not in solution.quality_values
    assert all(type(v) is float for v in solution.quality_values.values())
    assert solution.quality_values["thinning"] == 3


def test_quiz_run_persistence_rejects_old_schema_version() -> None:
    run_state = QuizRunState.start(
        10, QuizDifficulty.OPEN_BOOK, "Village, Smithy", QuizMode.RUN
    )
    record = json.loads(serialize_quiz_run(run_state))
    record["schema_version"] = 1

    with pytest.raises(QuizPersistenceError, match="schema"):
        deserialize_quiz_run(json.dumps(record))


def test_quiz_run_record_stores_stable_ids() -> None:
    run_state = QuizRunState.start(1, QuizDifficulty.HARD, "Village", QuizMode.PRACTICE)
    record = json.loads(serialize_quiz_run(run_state))

    assert record["mode"] == "practice"
    assert record["difficulty"] == "hard"


def test_total_elapsed_time_does_not_count_the_scored_round_twice() -> None:
    start = datetime(2026, 1, 1, 12, 0, 0)
    run_state = QuizRunState.start(10, QuizDifficulty.EASY, "First", QuizMode.RUN)
    run_state.completed_rounds.append(
        CompletedQuizRound(
            0, "First", QuizAnswers({}, "no"), 0, start, datetime(2026, 1, 1, 12, 0, 5)
        )
    )
    run_state.phase = QuizPhase.SOLUTION

    assert run_state.get_elapsed_time_of_current_round() == 5
    assert run_state.get_total_elapsed_time_so_far() == 5


@pytest.mark.parametrize(
    ("user_value", "real_value", "expected_points"),
    [(2, 2, 2), (2.5, 2, 1.5), (1, 2, 1), (0, 2, 0), (0.5, 0, 1.5)],
)
def test_quality_points(user_value: float, real_value: float, expected_points: float) -> None:
    assert get_quality_points(user_value, real_value) == expected_points


def test_buy_points() -> None:
    assert get_buy_points("Yes", "yes") == 3
    assert get_buy_points("maybe", "yes") == 0


def test_kingdom_solution_explains_the_totals() -> None:
    kingdom_str = Kingdom(
        cards=["Village", "Smithy", "Laboratory", "Library", "Moat", "Market", "Chapel"]
    ).get_dombot_csv_string()
    solution = get_kingdom_solution(kingdom_str)

    draw = dict(solution.contributions["draw"])
    assert draw["Smithy"] == 2 and draw["Moat"] == 1
    # Contributions are sorted by value, highest first
    values = [v for _, v in solution.contributions["draw"]]
    assert values == sorted(values, reverse=True)
    # Three 2s (Smithy, Laboratory, Library) combine into a 3
    assert "3×2 → 1×3" in solution.aggregation_steps["draw"]
    assert solution.quality_values["draw"] == 3
    assert solution.aggregation_steps["altvp"] == ("no contributions: 0",)
    assert ("Market", False) in solution.buy_sources
    assert solution.buy_availability == "yes"
    assert "Chapel" in solution.card_names
    assert solution.landscape_names == ()


def test_landscape_text_crop_keeps_the_upper_part() -> None:
    from PIL import Image

    from random_kingdominion.utils.plotting.image_handling import (
        LANDSCAPE_TEXT_BOX_TOP,
        TRAIT_TEXT_BOX_TOP,
        crop_landscape_text,
    )

    img = Image.new("RGB", (367, 224))
    assert crop_landscape_text(img).size == (367, round(224 * LANDSCAPE_TEXT_BOX_TOP))
    assert crop_landscape_text(img, is_trait=True).size == (
        367,
        round(224 * TRAIT_TEXT_BOX_TOP),
    )
