import json
from datetime import datetime
from typing import Any, cast

from streamlit.runtime.state import SessionStateProxy

from ...kingdom import Kingdom
from .run_state import (
    QUIZ_RUN_RECORD_KEY,
    QUIZ_SCORING_VERSION,
    BuyAvailability,
    CompletedQuizRound,
    QuizAnswers,
    QuizDifficulty,
    QuizMode,
    QuizPhase,
    QuizRunState,
)
from .util import st_calc_quiz_score

QUIZ_RUN_SCHEMA_VERSION = 1


class QuizPersistenceError(ValueError):
    pass


def persist_quiz_run(state: SessionStateProxy, run_state: QuizRunState) -> None:
    state[QUIZ_RUN_RECORD_KEY] = serialize_quiz_run(run_state)


def restore_persisted_quiz_run(
    state: SessionStateProxy,
) -> QuizRunState | None:
    serialized_run = state.get(QUIZ_RUN_RECORD_KEY)
    if serialized_run is None:
        return None
    if not isinstance(serialized_run, str):
        raise QuizPersistenceError("The saved quiz run is not text.")
    return deserialize_quiz_run(serialized_run)


def _serialize_completed_round(round_result: CompletedQuizRound) -> dict[str, Any]:
    return {
        "round_index": round_result.round_index,
        "kingdom": round_result.kingdom,
        "submitted_answers": {
            "quality_values": {
                quality: float(value)
                for quality, value in round_result.submitted_answers.quality_values.items()
            },
            "buy_availability": round_result.submitted_answers.buy_availability,
        },
        "score": round_result.score,
        "start_time": round_result.start_time.isoformat(),
        "end_time": round_result.end_time.isoformat(),
    }


def serialize_quiz_run(run_state: QuizRunState) -> str:
    record = {
        "schema_version": QUIZ_RUN_SCHEMA_VERSION,
        "run_id": run_state.run_id,
        "mode": run_state.mode.value,
        "phase": run_state.phase.value,
        "round_count": run_state.round_count,
        "difficulty": run_state.difficulty.value,
        "current_round_index": run_state.current_round_index,
        "current_kingdom": run_state.current_kingdom,
        "scoring_version": run_state.scoring_version,
        "last_round_start": run_state.last_round_start.isoformat(),
        "completed_rounds": [
            _serialize_completed_round(round_result)
            for round_result in run_state.completed_rounds
        ],
    }
    return json.dumps(record, separators=(",", ":"), sort_keys=True)


def deserialize_quiz_run(serialized_run: str) -> QuizRunState:
    try:
        record = json.loads(serialized_run)
        if not isinstance(record, dict):
            raise TypeError("Quiz run record must be an object.")
        return _restore_quiz_run(record)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, QuizPersistenceError):
            raise
        raise QuizPersistenceError("The saved quiz run is invalid.") from exc


def _restore_quiz_run(record: dict[str, Any]) -> QuizRunState:
    if record["schema_version"] != QUIZ_RUN_SCHEMA_VERSION:
        raise QuizPersistenceError("The saved quiz schema is not supported.")
    if record["scoring_version"] != QUIZ_SCORING_VERSION:
        raise QuizPersistenceError("The saved quiz scoring version is not supported.")

    completed_rounds = [
        _restore_completed_round(round_record)
        for round_record in record["completed_rounds"]
    ]
    run_state = QuizRunState(
        run_id=str(record["run_id"]),
        mode=QuizMode(record["mode"]),
        phase=QuizPhase(record["phase"]),
        difficulty=QuizDifficulty(record["difficulty"]),
        round_count=int(record["round_count"]),
        current_round_index=int(record["current_round_index"]),
        current_kingdom=str(record["current_kingdom"]),
        completed_rounds=completed_rounds,
        cumulative_score=sum(round_result.score for round_result in completed_rounds),
        scoring_version=str(record["scoring_version"]),
        last_round_start=datetime.fromisoformat(record["last_round_start"]),
    )
    _validate_restored_progress(run_state)
    if run_state.phase is QuizPhase.SOLUTION:
        current_round = completed_rounds[-1]
        run_state.submitted_answers = current_round.submitted_answers
        run_state.round_score = current_round.score
    return run_state


def _restore_completed_round(record: dict[str, Any]) -> CompletedQuizRound:
    answer_record = record["submitted_answers"]
    quality_values = {
        str(quality): float(value)
        for quality, value in answer_record["quality_values"].items()
    }
    buy_availability = cast(BuyAvailability, str(answer_record["buy_availability"]))
    if buy_availability not in ("yes", "maybe", "no"):
        raise QuizPersistenceError("The saved Buy answer is invalid.")

    answers = QuizAnswers(quality_values, buy_availability)
    kingdom_string = str(record["kingdom"])
    kingdom = Kingdom.from_dombot_csv_string(kingdom_string)
    trusted_score = st_calc_quiz_score(
        quality_values,
        kingdom.total_qualities,
        buy_availability,
        kingdom.buy_availability,
    )
    start_time = record.get("start_time")
    end_time = record.get("end_time")
    if start_time is None or end_time is None:
        raise QuizPersistenceError(
            "The saved quiz round has an unsupported start time."
        )
    start_time = datetime.fromisoformat(start_time)
    end_time = datetime.fromisoformat(end_time)
    return CompletedQuizRound(
        round_index=int(record["round_index"]),
        kingdom=kingdom_string,
        submitted_answers=answers,
        score=trusted_score,
        start_time=start_time,
        end_time=end_time,
    )


def _validate_restored_progress(run_state: QuizRunState) -> None:
    expected_indices = list(range(len(run_state.completed_rounds)))
    actual_indices = [
        round_result.round_index for round_result in run_state.completed_rounds
    ]
    if actual_indices != expected_indices:
        raise QuizPersistenceError("Saved quiz rounds are not sequential.")

    completed_count = len(run_state.completed_rounds)
    if run_state.phase is QuizPhase.ANSWERING:
        valid_progress = completed_count == run_state.current_round_index
    elif run_state.phase is QuizPhase.SOLUTION:
        valid_progress = completed_count == run_state.current_round_index + 1
    elif run_state.phase is QuizPhase.FINISHED:
        valid_progress = (
            completed_count == run_state.round_count
            and run_state.current_round_index == run_state.round_count - 1
        )
    else:
        valid_progress = completed_count == 0
    if not valid_progress:
        raise QuizPersistenceError("Saved quiz progress is inconsistent.")
