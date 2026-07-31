from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal
from uuid import uuid4


QUIZ_SCORING_VERSION = "1"
BuyAvailability = Literal["yes", "maybe", "no"]


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
