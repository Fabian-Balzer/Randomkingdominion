from collections.abc import Sequence
from typing import cast

from streamlit.runtime.state import SessionStateProxy

from ...kingdom import KingdomRandomizer
from .run_state import QUIZ_RUN_RECORD_KEY

QUIZ_BUY_ANSWER_KEY = "quiz_quality_buy_str"
# Durable keys for settings whose widgets are not rendered during a round
QUIZ_MODE_KEY = "quiz_run_mode"
QUIZ_DIFFICULTY_KEY = "quiz_difficulty_selection"
QUIZ_HIDE_TIMER_KEY = "quiz_hide_timer"


def get_quality_answer_key(quality: str) -> str:
    return f"quiz_quality_slider_{quality}"


def reset_quiz_answers(state: SessionStateProxy, quality_names: Sequence[str]) -> None:
    state.pop(QUIZ_BUY_ANSWER_KEY, None)
    for quality in quality_names:
        state.pop(get_quality_answer_key(quality), None)


def reset_quiz_workflow(state: SessionStateProxy, quality_names: Sequence[str]) -> None:
    state.pop(QUIZ_RUN_RECORD_KEY, None)
    for key in list(state):
        if cast(str, key).startswith("_quiz_quality_"):
            state.pop(key, None)
    reset_quiz_answers(state, quality_names)


def load_quiz_widget_value(state: SessionStateProxy, answer_key: str) -> str:
    """Copy the durable value of `answer_key` into the state of its widget, which
    Streamlit forgets whenever the widget isn't rendered. Returns the widget key."""
    widget_key = f"_{answer_key}"
    if answer_key in state:
        state[widget_key] = state[answer_key]
    else:
        state.pop(widget_key, None)
    return widget_key


def save_quiz_widget_value(state: SessionStateProxy, answer_key: str) -> None:
    widget_value = state.get(f"_{answer_key}")
    if widget_value is None:
        state.pop(answer_key, None)
    else:
        state[answer_key] = widget_value


def generate_random_quiz_kingdom_string() -> str:
    kingdom = KingdomRandomizer().randomize_new_kingdom()
    return kingdom.get_dombot_csv_string()
