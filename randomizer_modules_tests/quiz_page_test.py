"""Regression tests that drive the quiz page through Streamlit's AppTest."""

import json
from enum import StrEnum
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from random_kingdominion.kingdom import Kingdom
from random_kingdominion.streamlit_util.quiz_setup.kingdom_pool import (
    QUIZ_DEFAULT_EXPANSIONS,
    QUIZ_EXPANSION_OPTIONS,
    QuizKingdomPool,
    QuizPoolSource,
)
from random_kingdominion.streamlit_util.quiz_setup.persistence import serialize_quiz_run
from random_kingdominion.streamlit_util.quiz_setup.run_state import (
    QUIZ_RUN_RECORD_KEY,
    QuizAnswers,
    QuizDifficulty,
    QuizMode,
    QuizPhase,
    QuizRunState,
)
from random_kingdominion.streamlit_util.quiz_setup.scoring import (
    MAX_ROUND_SCORE,
    QUIZ_QUALITY_NAMES,
)

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
    assert (
        _segmented(app, "_quiz_difficulty_selection").value == QuizDifficulty.OPEN_BOOK
    )


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
    assert any("Contributing CSOs" in m.value for m in app.markdown)
    assert any("Open Book" in m.value and "badge" in m.value for m in app.markdown)
    assert any("Quality hints shown" in m.value for m in app.markdown)
    # Where to send feedback on the ratings
    assert any("Fabi_1000" in c.value for c in app.caption)


def test_last_run_round_leads_to_summary(app: AppTest) -> None:
    num_rounds = QuizMode.RUN.round_count
    run_state = QuizRunState.start(
        num_rounds, QuizDifficulty.EASY, TEST_KINGDOM, QuizMode.RUN
    )
    answers = QuizAnswers({q: 1.0 for q in QUIZ_QUALITY_NAMES}, "no")
    for _ in range(num_rounds - 1):
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
    assert metrics["Total Score"].endswith(f"/{num_rounds * MAX_ROUND_SCORE}")
    # F2: an Easy run doesn't get the hints badge
    assert not any("Quality hints shown" in m.value for m in app.markdown)
    # T1: the pool, as scores from different pools aren't comparable
    assert any("🎲 Random · 16 expansions" in m.value for m in app.markdown)
    assert any(c.value.startswith("Kingdoms drawn from: ") for c in app.caption)
    # F3: round table, tendencies table and the round details
    rounds_df, tendencies_df = (d.value for d in app.dataframe)
    assert list(rounds_df["Round"]) == list(range(1, num_rounds + 1))
    assert len(tendencies_df) == len(QUIZ_QUALITY_NAMES) + 1
    assert any("Contributing CSOs" in m.value for m in app.markdown)
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


def _share_expander(at: AppTest):
    return next(e for e in at.expander if e.label == "Share your result as an image")


def test_finished_run_can_be_shared_as_an_image(app: AppTest) -> None:
    run_state = QuizRunState.start(1, QuizDifficulty.HARD, TEST_KINGDOM, QuizMode.RUN)
    run_state.submit_round(QuizAnswers({q: 1.0 for q in QUIZ_QUALITY_NAMES}, "no"), 0)
    run_state.advance_round("")
    app.session_state[QUIZ_RUN_RECORD_KEY] = serialize_quiz_run(run_state)
    app.run()
    # Only drawn once opened, as that takes a few seconds for a full run
    assert not _share_expander(app).proto.expanded
    assert not app.get("download_button")

    # What opening the expander does
    app.session_state["quiz_share_expander"] = True
    app.run()
    app.text_input[0].input("Tester").run()

    assert not app.exception
    assert app.session_state["quiz_player_name"] == "Tester"
    assert len(app.get("download_button")) == 1
    copy_button = app.get("html")[0].proto.body
    assert "Copy image" in copy_button and "data:image/png;base64," in copy_button


def test_solved_practice_kingdom_can_be_shared(app: AppTest) -> None:
    _button(app, "Start Practice").click().run()
    assert not any(e.label == "Share your result as an image" for e in app.expander)

    _answer_everything(app)
    _button(app, "Show Solution").click().run()
    app.session_state["quiz_share_expander"] = True
    app.run()

    assert not app.exception
    assert len(app.get("download_button")) == 1


def test_practice_kingdom_can_be_rerolled_after_confirmation(app: AppTest) -> None:
    _segmented(app, "_quiz_difficulty_selection").set_value(QuizDifficulty.EASY).run()
    _button(app, "Start Practice").click().run()
    _segmented(app, "_quiz_quality_buy_str").set_value("yes").run()
    kingdom_before = _run_record(app)["current_kingdom"]

    _button(app, "🎲 Reroll kingdom").click().run()
    _button(app, "Cancel").click().run()
    assert _run_record(app)["current_kingdom"] == kingdom_before

    _button(app, "🎲 Reroll kingdom").click().run()
    _button(app, "Reroll").click().run()

    assert not app.exception
    record = _run_record(app)
    assert record["current_kingdom"] != kingdom_before
    assert (record["mode"], record["difficulty"]) == ("practice", "easy")
    assert record["phase"] == "answering"
    assert "quiz_quality_buy_str" not in app.session_state


@pytest.mark.parametrize(
    ("mode", "difficulty"),
    [(QuizMode.PRACTICE, QuizDifficulty.HARD), (QuizMode.RUN, QuizDifficulty.EASY)],
)
def test_no_reroll_in_hard_practice_or_runs(
    app: AppTest, mode: QuizMode, difficulty: QuizDifficulty
) -> None:
    _segmented(app, "_quiz_run_mode").set_value(mode).run()
    _segmented(app, "_quiz_difficulty_selection").set_value(difficulty).run()
    start_label = next(b.label for b in app.button if b.label.startswith("Start"))
    _button(app, start_label).click().run()

    assert _run_record(app)["phase"] == "answering"
    assert not any(b.label == "🎲 Reroll kingdom" for b in app.button)


def test_kingdom_string_is_only_shown_with_the_solution(app: AppTest) -> None:
    _button(app, "Start Practice").click().run()
    assert not any(e.label == "Kingdom string to copy" for e in app.expander)

    _answer_everything(app)
    _button(app, "Show Solution").click().run()
    assert any(e.label == "Kingdom string to copy" for e in app.expander)


def test_random_answers_button_only_in_debug_mode(
    app: AppTest, monkeypatch: pytest.MonkeyPatch
) -> None:
    _button(app, "Start Practice").click().run()
    assert not any("random answers" in b.label for b in app.button)

    monkeypatch.setenv("RK_DEBUG", "1")
    app.run()
    _button(app, "🐞 Submit random answers").click().run()

    assert not app.exception
    record = _run_record(app)
    assert record["phase"] == "solution"
    assert len(record["completed_rounds"]) == 1


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
    assert any("How good can you read" in m.value for m in app.markdown)
    _button(app, "Start Practice").click().run()

    assert not any("How good can you read" in m.value for m in app.markdown)
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


# T1: kingdom pools


def _start_button(at: AppTest):
    return next(b for b in at.button if b.label.startswith("Start "))


def test_pool_selection_defaults_to_random_kingdoms_from_default_expansions(
    app: AppTest,
) -> None:
    assert _segmented(app, "_quiz_pool_source").value == QuizPoolSource.RANDOM
    assert _segmented(app, "_quiz_expansions").value == list(QUIZ_DEFAULT_EXPANSIONS)
    assert any(c.value.startswith("✔ Random kingdoms from") for c in app.caption)

    _button(app, "Start Practice").click().run()

    assert not app.exception
    assert _run_record(app)["pool"] == {
        "source": "random",
        "expansions": list(QUIZ_DEFAULT_EXPANSIONS),
    }
    assert any("🎲 Random · 16 expansions" in m.value for m in app.markdown)


def test_too_small_pool_is_explained_before_starting(app: AppTest) -> None:
    _segmented(app, "_quiz_pool_source").set_value(QuizPoolSource.RECOMMENDED).run()
    # Only 2 recommended kingdoms use nothing but this expansion
    _segmented(app, "_quiz_expansions").set_value(["Cornucopia & Guilds, 2E"]).run()
    _segmented(app, "_quiz_run_mode").set_value(QuizMode.RUN).run()

    assert not app.exception
    assert _start_button(app).disabled
    needs = f"but a 🏁 Run needs {QuizMode.RUN.round_count}"
    assert any(needs in w.value for w in app.warning)

    # A single kingdom is enough to practice
    _segmented(app, "_quiz_run_mode").set_value(QuizMode.PRACTICE).run()
    assert not _start_button(app).disabled
    assert not app.warning
    assert any("Recommended kingdoms use only your" in c.value for c in app.caption)


def test_expansion_shortcuts_and_empty_selection(app: AppTest) -> None:
    _button(app, "Clear selection").click().run()

    assert _segmented(app, "_quiz_expansions").value == []
    assert _start_button(app).disabled
    assert any("No expansions selected" in w.value for w in app.warning)

    _button(app, "Select all").click().run()
    assert _segmented(app, "_quiz_expansions").value == list(QUIZ_EXPANSION_OPTIONS)
    assert not _start_button(app).disabled

    _button(app, "Select all except 1E").click().run()
    assert not any("1E" in exp for exp in _segmented(app, "_quiz_expansions").value)
    assert "Promo" in _segmented(app, "_quiz_expansions").value


def test_pool_selection_survives_a_round_and_reset(app: AppTest) -> None:
    _segmented(app, "_quiz_pool_source").set_value(QuizPoolSource.TGG_DAILIES).run()
    _segmented(app, "_quiz_expansions").set_value(["Base, 2E", "Intrigue, 2E"]).run()
    _button(app, "Start Practice").click().run()
    assert _run_record(app)["pool"]["source"] == "tgg_dailies"

    _button(app, "Stop / Reset").click().run()
    _button(app, "Stop quiz").click().run()

    assert not app.exception
    assert _segmented(app, "_quiz_pool_source").value == QuizPoolSource.TGG_DAILIES
    assert _segmented(app, "_quiz_expansions").value == ["Base, 2E", "Intrigue, 2E"]


def test_curated_kingdom_is_named_once_solved(app: AppTest) -> None:
    _segmented(app, "_quiz_pool_source").set_value(QuizPoolSource.RECOMMENDED).run()
    _button(app, "Start Practice").click().run()
    assert not any("Recommended kingdom *" in m.value for m in app.markdown)

    _answer_everything(app)
    _button(app, "Show Solution").click().run()

    assert not app.exception
    assert any("⭐ Recommended · 16 expansions" in m.value for m in app.markdown)
    assert any(m.value.startswith("⭐ Recommended kingdom *") for m in app.markdown)


def test_run_draws_its_next_kingdoms_from_the_pool_without_repeats(
    app: AppTest,
) -> None:
    pool = QuizKingdomPool(QuizPoolSource.RECOMMENDED, ("Base, 2E",))
    # Play the last two rounds of a run
    num_rounds = QuizMode.RUN.round_count
    run_state = QuizRunState.start(
        num_rounds, QuizDifficulty.EASY, TEST_KINGDOM, QuizMode.RUN, pool=pool
    )
    answers = QuizAnswers({q: 1.0 for q in QUIZ_QUALITY_NAMES}, "no")
    for _ in range(num_rounds - 2):
        run_state.submit_round(answers, 0)
        run_state.advance_round(TEST_KINGDOM)
    app.session_state[QUIZ_RUN_RECORD_KEY] = serialize_quiz_run(run_state)
    app.run()

    _answer_everything(app)
    _button(app, "Show Solution").click().run()
    _button(app, "Next Kingdom").click().run()
    _answer_everything(app)
    _button(app, "Show Solution").click().run()
    _button(app, "View Run Summary").click().run()

    assert not app.exception
    record = _run_record(app)
    kingdoms = [r["kingdom"] for r in record["completed_rounds"]]
    assert kingdoms[-1] != kingdoms[-2]
    assert Kingdom.from_dombot_csv_string(kingdoms[-1]).expansions == ["Base, 2E"]
    rounds_df = app.dataframe[0].value
    assert "Name" in rounds_df.columns
    assert rounds_df["Name"].iloc[-1] != "–"


class _ReloadedQuizDifficulty(StrEnum):
    """Stands in for QuizDifficulty after Streamlit reloaded its module: same ids,
    but a different class, so that pickle can't store the old members anymore."""

    HARD = "hard"


def test_selections_are_stored_as_plain_ids(app: AppTest) -> None:
    app.session_state["quiz_difficulty_selection"] = _ReloadedQuizDifficulty.HARD
    app.run()

    assert not app.exception
    assert _segmented(app, "_quiz_difficulty_selection").value == QuizDifficulty.HARD
    for key in [
        "quiz_run_mode",
        "_quiz_run_mode",
        "quiz_difficulty_selection",
        "_quiz_difficulty_selection",
        "quiz_pool_source",
        "_quiz_pool_source",
    ]:
        assert type(app.session_state[key]) is str, key
