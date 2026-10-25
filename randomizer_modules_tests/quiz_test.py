import json
import pickle
from datetime import datetime
from io import BytesIO

import pytest
from PIL import Image

from random_kingdominion.kingdom import Kingdom, KingdomManager
from random_kingdominion.streamlit_util.quiz_setup import (
    explanations,
    kingdom_pool,
    share_image,
)
from random_kingdominion.streamlit_util.quiz_setup.kingdom_pool import (
    QUIZ_DEFAULT_EXPANSIONS,
    QUIZ_EXPANSION_OPTIONS,
    QuizKingdomPool,
    QuizPoolSource,
    count_available_kingdoms,
    draw_quiz_kingdom,
    get_curated_kingdom_name,
    get_quiz_randomizer_config,
    uses_only_expansions,
)
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
    QUIZ_QUALITY_NAMES,
    SCORE_BANDS,
    calc_quiz_score,
    get_buy_points,
    get_kingdom_solution,
    get_quality_points,
    get_score_band,
)
from random_kingdominion.streamlit_util.quiz_setup.share_image import (
    MAX_PLAYER_NAME_LENGTH,
    get_quiz_share_png,
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


@pytest.mark.parametrize("enum_cls", [QuizMode, QuizDifficulty, QuizPoolSource])
def test_quiz_enums_use_stable_ids_and_separate_labels(enum_cls) -> None:
    for member in enum_cls:
        assert member.value.isascii()
        assert member.label != member.value
        assert enum_cls(member.value) is member
        assert member.label in member.get_description()


def test_quiz_enum_ids_are_unique_across_selections() -> None:
    """The selection widgets look up all labels by id in one dict."""
    ids = [
        option.value
        for enum_cls in (QuizMode, QuizDifficulty, QuizPoolSource)
        for option in enum_cls
    ]

    assert len(ids) == len(set(ids))


def test_quiz_mode_round_counts() -> None:
    assert QuizMode.PRACTICE.round_count == 1
    assert QuizMode.RUN.round_count == 5


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


# T1: kingdom pools


def test_default_pool_is_random_without_first_editions_and_promos() -> None:
    pool = QuizKingdomPool()

    assert pool.source is QuizPoolSource.RANDOM
    assert pool.expansions == QUIZ_DEFAULT_EXPANSIONS
    assert not any("1E" in exp for exp in pool.expansions)
    assert "Promo" not in pool.expansions
    assert set(QUIZ_EXPANSION_OPTIONS) - set(pool.expansions) == {
        "Promo",
        *(exp for exp in QUIZ_EXPANSION_OPTIONS if "1E" in exp),
    }


def test_pool_sorts_expansions_and_rejects_unknown_ones() -> None:
    pool = QuizKingdomPool(QuizPoolSource.RECOMMENDED, ("Seaside, 2E", "Base, 2E"))

    assert pool == QuizKingdomPool(
        QuizPoolSource.RECOMMENDED, ("Base, 2E", "Seaside, 2E")
    )
    assert pool.label == "⭐ Recommended · 2 expansions"
    assert QuizKingdomPool(expansions=("Alchemy",)).expansion_summary == "1 expansion"
    assert (
        QuizKingdomPool(expansions=QUIZ_EXPANSION_OPTIONS).expansion_summary
        == "all expansions"
    )
    with pytest.raises(ValueError, match="Unknown expansions"):
        QuizKingdomPool(expansions=("Base",))


def test_quiz_randomizer_config_is_independent_of_the_default_bans() -> None:
    config = get_quiz_randomizer_config(["Alchemy", "Base, 2E"])

    assert config.getlist("General", "banned_csos") == []
    assert config.get_expansions(add_renewed_bases=False) == ["Alchemy", "Base, 2E"]


@pytest.mark.parametrize(
    ("csos_expansions", "selected", "expected"),
    [
        # Cards in both editions are available with either of them
        ({"Base"}, ["Base, 1E"], True),
        ({"Base"}, ["Base, 2E"], True),
        ({"Base", "Base, 2E"}, ["Base, 1E"], False),
        ({"Base", "Base, 1E"}, ["Base, 1E"], True),
        # The 2E merger of Cornucopia and Guilds
        ({"Cornucopia", "Guilds"}, ["Cornucopia & Guilds, 2E"], True),
        ({"Cornucopia", "Guilds"}, ["Cornucopia, 1E", "Guilds, 1E"], True),
        ({"Cornucopia", "Guilds"}, ["Cornucopia, 1E"], False),
        ({"Cornucopia & Guilds, 2E"}, ["Cornucopia, 1E", "Guilds, 1E"], False),
        ({"Unknown"}, list(QUIZ_EXPANSION_OPTIONS), False),
        (set(), [], True),
    ],
)
def test_expansion_filter_handles_editions(
    csos_expansions: set[str], selected: list[str], expected: bool
) -> None:
    assert uses_only_expansions(csos_expansions, selected) is expected


def test_random_pool_draws_from_the_selected_expansions() -> None:
    pool = QuizKingdomPool(expansions=("Alchemy",))
    kingdom = Kingdom.from_dombot_csv_string(draw_quiz_kingdom(pool))

    assert kingdom.expansions == ["Alchemy"]
    assert count_available_kingdoms(pool) is None
    assert get_curated_kingdom_name(pool, kingdom.get_dombot_csv_string()) is None


def test_random_pool_redraws_kingdoms_of_the_run(monkeypatch) -> None:
    first, second = (
        Kingdom(cards=["Village", "Smithy"]),
        Kingdom(cards=["Market", "Chapel"]),
    )
    draws = [first, first, second]

    class FakeRandomizer:
        def __init__(self, config) -> None:
            pass

        def randomize_new_kingdom(self) -> Kingdom:
            return draws.pop(0)

    monkeypatch.setattr(kingdom_pool, "KingdomRandomizer", FakeRandomizer)

    kingdom_str = draw_quiz_kingdom(QuizKingdomPool(), {first.get_dombot_csv_string()})

    assert kingdom_str == second.get_dombot_csv_string()
    assert draws == []


def test_empty_selection_has_no_kingdoms() -> None:
    for source in QuizPoolSource:
        pool = QuizKingdomPool(source, ())
        assert count_available_kingdoms(pool) == 0
        with pytest.raises(ValueError, match="no expansions"):
            draw_quiz_kingdom(pool)


def test_curated_pool_only_uses_selected_expansions_and_never_repeats() -> None:
    all_recommended = QuizKingdomPool(QuizPoolSource.RECOMMENDED, QUIZ_EXPANSION_OPTIONS)
    pool = QuizKingdomPool(QuizPoolSource.RECOMMENDED, ("Base, 2E",))
    num_available = count_available_kingdoms(pool)
    assert num_available is not None
    assert 0 < num_available < count_available_kingdoms(all_recommended)  # type: ignore

    drawn: list[str] = []
    for _ in range(num_available):
        drawn.append(draw_quiz_kingdom(pool, exclude=drawn))

    assert len(set(drawn)) == num_available
    for kingdom_str in drawn:
        assert Kingdom.from_dombot_csv_string(kingdom_str).expansions == ["Base, 2E"]
        # Each curated kingdom can be named once it's solved
        assert get_curated_kingdom_name(pool, kingdom_str)
    with pytest.raises(ValueError, match="no kingdoms left"):
        draw_quiz_kingdom(pool, exclude=drawn)


def test_tgg_dailies_count_duplicates_once() -> None:
    pool = QuizKingdomPool(QuizPoolSource.TGG_DAILIES, QUIZ_EXPANSION_OPTIONS)
    curated = kingdom_pool._load_curated_kingdoms(QuizPoolSource.TGG_DAILIES)

    assert count_available_kingdoms(pool) == len({k.identity for k in curated})
    assert get_curated_kingdom_name(
        pool, draw_quiz_kingdom(pool)
    ) in {k.name for k in curated}


def test_used_kingdoms_cover_completed_and_current_rounds() -> None:
    run_state = QuizRunState.start(10, QuizDifficulty.EASY, "First", QuizMode.RUN)
    run_state.submit_round(QuizAnswers({}, "no"), 0)
    run_state.advance_round("Second")

    assert run_state.used_kingdoms == {"First", "Second"}


def test_quiz_run_persistence_restores_the_pool() -> None:
    pool = QuizKingdomPool(QuizPoolSource.TGG_DAILIES, ("Base, 2E", "Alchemy"))
    run_state = QuizRunState.start(
        10, QuizDifficulty.HARD, "Village, Smithy", QuizMode.RUN, pool=pool
    )
    record = json.loads(serialize_quiz_run(run_state))

    assert record["pool"] == {
        "source": "tgg_dailies",
        "expansions": ["Base, 2E", "Alchemy"],
    }
    restored_run = deserialize_quiz_run(serialize_quiz_run(run_state))
    assert restored_run.pool == pool
    assert restored_run == run_state


@pytest.mark.parametrize(
    "pool_record",
    [
        {"source": "campaigns", "expansions": ["Base, 2E"]},
        {"source": "random", "expansions": ["Base"]},
        {"source": "random", "expansions": "Base, 2E"},
        {"source": "random"},
    ],
)
def test_quiz_run_persistence_rejects_invalid_pools(pool_record: dict) -> None:
    run_state = QuizRunState.start(1, QuizDifficulty.EASY, "Village", QuizMode.PRACTICE)
    record = json.loads(serialize_quiz_run(run_state))
    record["pool"] = pool_record

    with pytest.raises(QuizPersistenceError):
        deserialize_quiz_run(json.dumps(record))


def test_quiz_run_persistence_rejects_records_without_a_pool() -> None:
    """Records of schema version 2 had no pool; they are rejected and reset."""
    run_state = QuizRunState.start(1, QuizDifficulty.EASY, "Village", QuizMode.PRACTICE)
    record = json.loads(serialize_quiz_run(run_state))
    del record["pool"]
    record["schema_version"] = 2

    with pytest.raises(QuizPersistenceError, match="schema"):
        deserialize_quiz_run(json.dumps(record))


def test_curated_pools_leave_out_kingdoms_with_campaign_effects() -> None:
    """Twists, stamps and setup effects aren't covered by the qualities."""
    manager = KingdomManager()
    manager.load_tgg_dailies()
    with_effects = [k for k in manager.kingdoms if k.get("campaign_effects")]
    curated = kingdom_pool._load_curated_kingdoms(QuizPoolSource.TGG_DAILIES)

    assert with_effects, "the filter isn't tested if no Daily has campaign effects"
    assert not any(k.info.get("campaign_effects") for k in curated)
    assert {k.name for k in curated}.isdisjoint(k["name"] for k in with_effects)


def test_feedback_text_names_discord_and_later_the_video(monkeypatch) -> None:
    assert "Fabi_1000" in explanations.get_feedback_text()
    assert "video" not in explanations.get_feedback_text()

    monkeypatch.setattr(explanations, "QUIZ_FEEDBACK_VIDEO_URL", "https://youtu.be/x")
    assert "[showcase video](https://youtu.be/x)" in explanations.get_feedback_text()


def _finished_run(kingdom_str: str, num_rounds: int, mode: QuizMode) -> QuizRunState:
    run_state = QuizRunState.start(num_rounds, QuizDifficulty.HARD, kingdom_str, mode)
    answers = QuizAnswers({q: 0.5 for q in QUIZ_QUALITY_NAMES}, "yes")
    for i in range(num_rounds):
        run_state.submit_round(answers, 7.5)
        run_state.advance_round(kingdom_str if i + 1 < num_rounds else "")
    return run_state


def test_share_summary_has_plain_labels_and_a_bounded_name() -> None:
    kingdom_str = Kingdom(cards=["Village", "Smithy"]).get_dombot_csv_string()
    run_state = _finished_run(kingdom_str, 2, QuizMode.RUN)

    summary = share_image._get_share_summary(run_state, "  " + "x" * 50 + " ")

    # The font has no emoji and no middle dot
    assert summary.settings == "Hard | Random | 16 expansions"
    assert summary.title == "2 Kingdom Run"
    assert summary.player_name == "x" * MAX_PLAYER_NAME_LENGTH
    assert summary.total_score == 15
    assert summary.maximum_score == 2 * MAX_ROUND_SCORE
    assert [r.quality_values for r in summary.rounds] == [(0.5,) * 6] * 2


def test_share_image_is_a_cached_png_that_grows_with_the_rounds() -> None:
    kingdom_str = Kingdom(
        cards=["Village", "Smithy", "Chapel", "Market", "Witch"],
        landscapes=["Delve"],
        use_colonies=True,
    ).get_dombot_csv_string()
    practice = _finished_run(kingdom_str, 1, QuizMode.PRACTICE)
    run = _finished_run(kingdom_str, 3, QuizMode.RUN)

    practice_png = get_quiz_share_png(practice, "Tester")
    run_png = get_quiz_share_png(run)

    assert practice_png.startswith(b"\x89PNG")
    assert get_quiz_share_png(practice, "Tester") is practice_png
    with Image.open(BytesIO(practice_png)) as practice_img:
        with Image.open(BytesIO(run_png)) as run_img:
            assert run_img.width > practice_img.width
            assert run_img.height == practice_img.height


@pytest.mark.parametrize(
    ("num_cards", "expected"),
    [
        # Cheapest first: the lower row holds the cheaper half, left to right
        (10, [(c, 1) for c in range(5)] + [(c, 0) for c in range(5)]),
        # As in the kingdom view, an odd count leaves the lower left slot empty
        (11, [(c, 1) for c in range(1, 6)] + [(c, 0) for c in range(6)]),
    ],
)
def test_share_image_arranges_cards_like_the_kingdom_view(
    num_cards: int, expected: list[tuple[int, int]]
) -> None:
    assert share_image._get_card_grid_positions(num_cards) == expected
