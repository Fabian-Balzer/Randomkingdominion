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

# Each test renders the page several times, which takes seconds
pytestmark = pytest.mark.slow

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
    _button(app, "Show Solution").click().run()
    _button(app, "Practice Another Kingdom").click().run()

    assert not app.exception
    record = _run_record(app)
    assert record["difficulty"] == "hard"
    assert record["phase"] == "answering"

    _button(app, "Stop / Reset").click().run()
    _button(app, "Stop quiz").click().run()
    assert _segmented(app, "_quiz_difficulty_selection").value == QuizDifficulty.HARD


def test_deselected_quality_blocks_the_solution(app: AppTest) -> None:
    """B4: deselecting removes the answer; nothing may write an invalid sentinel."""
    _button(app, "Start Practice").click().run()
    _answer_everything(app)
    assert not _button(app, "Show Solution").disabled

    # What save_quiz_widget_value does when a segmented control gets deselected:
    del app.session_state["quiz_quality_slider_draw"]
    app.run()

    assert not app.exception
    assert "quiz_quality_slider_draw" not in app.session_state
    # UI 4: the submit button stays in place, disabled, and counts the answers
    submit = next(b for b in app.button if b.label.startswith("Show Solution"))
    assert submit.disabled
    assert submit.label == "Show Solution (6/7 answered)"


def test_solution_view_uses_submitted_answers(app: AppTest) -> None:
    """B5: the solution plot no longer depends on the answer widgets' state."""
    _button(app, "Start Practice").click().run()
    _answer_everything(app)
    _button(app, "Show Solution").click().run()
    for quality in QUIZ_QUALITY_NAMES:
        del app.session_state[f"quiz_quality_slider_{quality}"]
    app.run()

    assert not app.exception
    assert _run_record(app)["phase"] == "solution"
    assert any("Score:" in m.value for m in app.markdown)
    # F1: the breakdown table, F2: the settings badges
    assert any("How it adds up" in m.value for m in app.markdown)
    assert any("Open Book" in m.value and "badge" in m.value for m in app.markdown)
    assert any("Quality hints were shown" in m.value for m in app.markdown)


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
    _button(app, "Show Solution").click().run()
    _button(app, "View Run Summary").click().run()

    assert not app.exception
    assert _run_record(app)["phase"] == QuizPhase.FINISHED.value
    metrics = {m.label: m.value for m in app.metric}
    assert set(metrics) == {"Total Score", "Average", "Perfect Rounds", "Total Time"}
    assert metrics["Total Score"].endswith("/150")
    # F2: an Easy run doesn't get the hints badge
    assert not any("Quality hints were shown" in m.value for m in app.markdown)
    # F3: round table, tendencies table and the round details
    rounds_df, tendencies_df = (d.value for d in app.dataframe)
    assert list(rounds_df["Round"]) == list(range(1, 11))
    assert len(tendencies_df) == len(QUIZ_QUALITY_NAMES) + 1
    assert any("How it adds up" in m.value for m in app.markdown)
    assert any(b.label == "Play again with the same settings" for b in app.button)


def test_play_again_keeps_mode_and_difficulty(app: AppTest) -> None:
    run_state = QuizRunState.start(1, QuizDifficulty.HARD, TEST_KINGDOM, QuizMode.RUN)
    run_state.submit_round(QuizAnswers({q: 1.0 for q in QUIZ_QUALITY_NAMES}, "no"), 0)
    run_state.advance_round("")
    app.session_state[QUIZ_RUN_RECORD_KEY] = serialize_quiz_run(run_state)
    app.run()

    _button(app, "Play again with the same settings").click().run()

    assert not app.exception
    record = _run_record(app)
    assert (record["mode"], record["difficulty"]) == ("run", "hard")
    assert record["phase"] == "answering"
    assert record["completed_rounds"] == []


def test_reset_needs_confirmation_and_cancel_keeps_the_run(app: AppTest) -> None:
    """UI 7: Stop / Reset only asks; cancelling keeps the run."""
    _button(app, "Start Practice").click().run()
    record_before = _run_record(app)

    _button(app, "Stop / Reset").click().run()
    assert QUIZ_RUN_RECORD_KEY in app.session_state
    _button(app, "Cancel").click().run()

    assert not app.exception
    assert _run_record(app) == record_before


def test_layout_has_kingdom_and_side_column_without_toggle(app: AppTest) -> None:
    """U1/U6: layout A (kingdom 2/3, answers + plot 1/3), no sidebar, no view toggle."""
    _button(app, "Start Practice").click().run()

    assert not app.exception
    assert len(app.sidebar.children) == 0
    assert not any(t.label == "Large view" for t in app.toggle)
    widths = [round(c.weight, 3) for c in app.columns]
    # Listed depth-first, so the card columns of the kingdom come in between
    assert {0.667, 0.333} <= set(widths)


def test_explanations_move_into_a_popover_during_a_round(app: AppTest) -> None:
    """UI 5: intro and explanations only on the start screen, a popover during a round."""
    assert any("Are you able to infer" in m.value for m in app.markdown)
    _button(app, "Start Practice").click().run()

    assert not any("Are you able to infer" in m.value for m in app.markdown)
    assert any(p.proto.popover.label == "❓ Rules & Tips" for p in app.get("popover"))


def test_timer_is_one_fixed_button_that_toggles(app: AppTest) -> None:
    """The timer is a single button with a fixed key (no layout jumps), hidden by default."""
    _button(app, "Start Practice").click().run()
    timer = next(b for b in app.button if b.key == "quiz_timer_button")
    assert timer.label == "⏱ Show time"

    timer.click().run()

    timer = next(b for b in app.button if b.key == "quiz_timer_button")
    assert not app.exception
    assert timer.label.startswith("⏱ 00:")
    assert app.session_state["quiz_hide_timer"] is False
