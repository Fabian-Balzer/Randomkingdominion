"""Regression tests that drive the quiz page through Streamlit's AppTest."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from random_kingdominion.kingdom import Kingdom
from random_kingdominion.streamlit_util.quiz_setup.persistence import (
    serialize_quiz_run,
)
from random_kingdominion.streamlit_util.quiz_setup.run_state import (
    QUIZ_RUN_RECORD_KEY,
    QuizAnswers,
    QuizDifficulty,
    QuizMode,
    QuizPhase,
    QuizRunState,
)
from random_kingdominion.streamlit_util.quiz_setup.scoring import QUIZ_QUALITY_NAMES

REPO_ROOT = Path(__file__).resolve().parents[1]
QUIZ_PAGE = REPO_ROOT / "streamlit_pages" / "quiz.py"
TEST_KINGDOM = Kingdom(
    cards=[
        "Village",
        "Smithy",
        "Chapel",
        "Market",
        "Witch",
        "Moat",
        "Cellar",
        "Workshop",
        "Gardens",
        "Laboratory",
    ]
).get_dombot_csv_string()


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    monkeypatch.chdir(REPO_ROOT)
    at = AppTest.from_file(str(QUIZ_PAGE), default_timeout=120)
    at.run()
    return at


def _segmented(at: AppTest, key: str):
    return next(s for s in at.get("button_group") if s.key == key)


def _button(at: AppTest, label: str):
    return next(b for b in at.button if b.label == label)


def _run_record(at: AppTest) -> dict:
    return json.loads(at.session_state[QUIZ_RUN_RECORD_KEY])


def _answer_everything(at: AppTest, value: str = "2", buy: str = "yes") -> None:
    _segmented(at, "_quiz_quality_buy_str").set_value(buy).run()
    for quality in QUIZ_QUALITY_NAMES:
        _segmented(at, f"_quiz_quality_slider_{quality}").set_value(value).run()


def test_start_screen_renders_with_defaults(app: AppTest) -> None:
    assert not app.exception
    assert _segmented(app, "_quiz_run_mode").value == QuizMode.PRACTICE
    assert _segmented(app, "_quiz_difficulty_selection").value == QuizDifficulty.OPEN_BOOK


@pytest.mark.parametrize("stale_value", [None, "🧪 Practice"])
def test_missing_or_stale_mode_selection_falls_back_to_default(
    app: AppTest, stale_value
) -> None:
    """B1: a deselected (None) or outdated value used to raise a ValueError."""
    app.session_state["quiz_run_mode"] = stale_value
    app.run()

    assert not app.exception
    assert _segmented(app, "_quiz_run_mode").value == QuizMode.PRACTICE


def test_practice_keeps_difficulty_for_next_kingdom_and_after_reset(
    app: AppTest,
) -> None:
    """B2: 'Practice Another Kingdom' used to fall back to the default difficulty."""
    _segmented(app, "_quiz_difficulty_selection").set_value(QuizDifficulty.HARD).run()
    _button(app, "Start Practice").click().run()
    assert _run_record(app)["difficulty"] == "hard"

    _answer_everything(app)
    _button(app, "Click here to show Solution").click().run()
    _button(app, "Practice Another Kingdom").click().run()

    assert not app.exception
    record = _run_record(app)
    assert record["difficulty"] == "hard"
    assert record["phase"] == "answering"

    _button(app, "Stop / Reset").click().run()
    assert _segmented(app, "_quiz_difficulty_selection").value == QuizDifficulty.HARD


def test_deselected_quality_blocks_the_solution(app: AppTest) -> None:
    """B4: deselecting removes the answer; nothing may write an invalid sentinel."""
    _button(app, "Start Practice").click().run()
    _answer_everything(app)
    assert any(b.label == "Click here to show Solution" for b in app.button)

    # What save_quiz_widget_value does when a segmented control gets deselected:
    del app.session_state["quiz_quality_slider_draw"]
    app.run()

    assert not app.exception
    assert "quiz_quality_slider_draw" not in app.session_state
    assert any("Please select all qualities" in i.value for i in app.info)


def test_solution_view_uses_submitted_answers(app: AppTest) -> None:
    """B5: the solution plot no longer depends on the answer widgets' state."""
    _button(app, "Start Practice").click().run()
    _answer_everything(app)
    _button(app, "Click here to show Solution").click().run()
    for quality in QUIZ_QUALITY_NAMES:
        del app.session_state[f"quiz_quality_slider_{quality}"]
    app.run()

    assert not app.exception
    assert _run_record(app)["phase"] == "solution"
    assert any("Score:" in m.value for m in app.markdown)


def test_last_run_round_leads_to_summary(app: AppTest) -> None:
    run_state = QuizRunState.start(
        10, QuizDifficulty.EASY, TEST_KINGDOM, QuizMode.RUN
    )
    answers = QuizAnswers({q: 1.0 for q in QUIZ_QUALITY_NAMES}, "no")
    for _ in range(9):
        run_state.submit_round(answers, 0)
        run_state.advance_round(TEST_KINGDOM)
    app.session_state[QUIZ_RUN_RECORD_KEY] = serialize_quiz_run(run_state)
    app.run()

    _answer_everything(app)
    _button(app, "Click here to show Solution").click().run()
    _button(app, "View Run Summary").click().run()

    assert not app.exception
    assert _run_record(app)["phase"] == QuizPhase.FINISHED.value
    metrics = {m.label: m.value for m in app.metric}
    assert set(metrics) == {"Total Score", "Average", "Perfect Rounds", "Total Time"}
    assert metrics["Total Score"].endswith("/150")
