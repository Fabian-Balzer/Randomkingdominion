from dataclasses import dataclass
from enum import StrEnum


class QuizPhase(StrEnum):
    NOT_STARTED = "not_started"
    ANSWERING = "answering"
    SOLUTION = "solution"
    FINISHED = "finished"


@dataclass
class QuizRunState:
    phase: QuizPhase = QuizPhase.NOT_STARTED
