from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal
from uuid import uuid4

QUIZ_SCORING_VERSION = "1"
QUIZ_RUN_RECORD_KEY = "quiz_run_record"
BuyAvailability = Literal["yes", "maybe", "no"]


class QuizMode(StrEnum):
    PRACTICE = "practice"
    RUN = "run"


class QuizPhase(StrEnum):
    NOT_STARTED = "not_started"
    ANSWERING = "answering"
    SOLUTION = "solution"
    FINISHED = "finished"


@dataclass(frozen=True)
class QuizAnswers:
    quality_values: dict[str, float]
    buy_availability: BuyAvailability


@dataclass(frozen=True)
class CompletedQuizRound:
    round_index: int
    kingdom: str
    submitted_answers: QuizAnswers
    score: float


@dataclass
class QuizRunState:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    mode: QuizMode = QuizMode.PRACTICE
    phase: QuizPhase = QuizPhase.NOT_STARTED
    round_count: int = 1
    current_round_index: int = 0
    current_kingdom: str = ""
    submitted_answers: QuizAnswers | None = None
    round_score: float | None = None
    cumulative_score: float = 0.0
    completed_rounds: list[CompletedQuizRound] = field(default_factory=list)
    scoring_version: str = QUIZ_SCORING_VERSION

    def __post_init__(self) -> None:
        if self.round_count < 1:
            raise ValueError("Round count must be at least 1.")
        if not 0 <= self.current_round_index < self.round_count:
            raise ValueError("Current round index must be within the run's rounds.")

    @classmethod
    def start(
        cls,
        round_count: int,
        kingdom: str,
        mode: QuizMode | None = None,
    ) -> "QuizRunState":
        return cls(
            mode=mode or (QuizMode.PRACTICE if round_count == 1 else QuizMode.RUN),
            phase=QuizPhase.ANSWERING,
            round_count=round_count,
            current_kingdom=kingdom,
        )

    def submit_round(self, answers: QuizAnswers, score: float) -> bool:
        if self.phase is not QuizPhase.ANSWERING:
            return False

        completed_round = CompletedQuizRound(
            round_index=self.current_round_index,
            kingdom=self.current_kingdom,
            submitted_answers=answers,
            score=score,
        )
        self.submitted_answers = answers
        self.round_score = score
        self.cumulative_score += score
        self.completed_rounds.append(completed_round)
        self.phase = QuizPhase.SOLUTION
        return True

    def advance_round(self, kingdom: str) -> None:
        if self.phase is not QuizPhase.SOLUTION:
            raise ValueError("Only a scored round can be advanced.")
        if self.current_round_index + 1 >= self.round_count:
            self.phase = QuizPhase.FINISHED
            return

        self.current_round_index += 1
        self.current_kingdom = kingdom
        self.submitted_answers = None
        self.round_score = None
        self.phase = QuizPhase.ANSWERING

    @property
    def average_score(self) -> float:
        if not self.completed_rounds:
            return 0.0
        return self.cumulative_score / len(self.completed_rounds)

    @property
    def perfect_round_count(self) -> int:
        return sum(round_result.score == 15 for round_result in self.completed_rounds)

    @property
    def maximum_score(self) -> int:
        return self.round_count * 15
