from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import uuid4

QUIZ_SCORING_VERSION = "1"
QUIZ_RUN_RECORD_KEY = "quiz_run_record"
BuyAvailability = Literal["yes", "maybe", "no"]


class QuizMode(StrEnum):
    PRACTICE = "🧪 Practice"
    RUN = "🏁 Run"

    @classmethod
    def from_display_key(cls, key: str) -> "QuizMode":
        if key == "🧪 Practice":
            return QuizMode.PRACTICE
        elif key == "🏁 Run":
            return QuizMode.RUN
        else:
            raise ValueError(f"Unknown display key: {key!r}")

    def get_description(self, include_name: bool = True) -> str:
        d = ""
        if self is QuizMode.PRACTICE:
            d = "Explore one kingdom at a time without a cumulative score."
        elif self is QuizMode.RUN:
            d = "Score ten kingdoms in a row and review your combined result."
        else:
            raise ValueError(f"Unknown quiz mode: {self!r}")
        if not include_name:
            return d
        return f"**{self.value}**: {d}"


class QuizDifficulty(StrEnum):
    PRACTICE = "🧪 Practice"
    EASY = "🌱 Easy"
    HARD = "🔥 Hard"

    @classmethod
    def from_display_key(cls, key: str) -> "QuizDifficulty":
        if key == "🧪 Practice":
            return QuizDifficulty.PRACTICE
        elif key == "🌱 Easy":
            return QuizDifficulty.EASY
        elif key == "🔥 Hard":
            return QuizDifficulty.HARD
        else:
            raise ValueError(f"Unknown display key: {key!r}")

    def get_description(self, include_name: bool = True) -> str:
        d = ""
        if self is QuizDifficulty.PRACTICE:
            d = "Full cards including text, hints with quality values shown."
        elif self is QuizDifficulty.EASY:
            d = "Full cards including text, hints with quality values hidden."
        elif self is QuizDifficulty.HARD:
            d = "Card texts hidden, no hints, only pictures."
        else:
            raise ValueError(f"Unknown quiz difficulty: {self!r}")
        if not include_name:
            return d
        return f"**{self.value}**: {d}"


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
    start_time: datetime
    end_time: datetime

    @property
    def elapsed_time(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class QuizRunState:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    mode: QuizMode = QuizMode.PRACTICE
    difficulty: QuizDifficulty = QuizDifficulty.PRACTICE
    phase: QuizPhase = QuizPhase.NOT_STARTED
    round_count: int = 1
    current_round_index: int = 0
    current_kingdom: str = ""
    submitted_answers: QuizAnswers | None = None
    round_score: float | None = None
    cumulative_score: float = 0.0
    completed_rounds: list[CompletedQuizRound] = field(default_factory=list)
    scoring_version: str = QUIZ_SCORING_VERSION
    last_round_start: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.round_count < 1:
            raise ValueError("Round count must be at least 1.")
        if not 0 <= self.current_round_index < self.round_count:
            raise ValueError("Current round index must be within the run's rounds.")

    @classmethod
    def start(
        cls,
        round_count: int,
        difficulty: QuizDifficulty,
        kingdom: str,
        mode: QuizMode,
    ) -> "QuizRunState":
        return cls(
            mode=mode,
            phase=QuizPhase.ANSWERING,
            difficulty=difficulty,
            round_count=round_count,
            current_kingdom=kingdom,
            last_round_start=datetime.now(),
        )

    def submit_round(self, answers: QuizAnswers, score: float) -> bool:
        if self.phase is not QuizPhase.ANSWERING:
            return False

        completed_round = CompletedQuizRound(
            round_index=self.current_round_index,
            kingdom=self.current_kingdom,
            submitted_answers=answers,
            score=score,
            start_time=self.last_round_start,
            end_time=datetime.now(),
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
        self.last_round_start = datetime.now()

    def get_elapsed_time_of_current_round(self) -> float:
        if self.phase is QuizPhase.ANSWERING:
            return (datetime.now() - self.last_round_start).total_seconds()
        elif self.phase is QuizPhase.SOLUTION:
            last_round = self.completed_rounds[-1]
            return last_round.elapsed_time
        else:
            return 0.0

    def get_total_elapsed_time_so_far(self) -> float:
        if self.phase is QuizPhase.FINISHED:
            return self.total_elapsed_time
        return self.total_elapsed_time + self.get_elapsed_time_of_current_round()

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

    @property
    def total_elapsed_time(self) -> float:
        return sum(round_result.elapsed_time for round_result in self.completed_rounds)
