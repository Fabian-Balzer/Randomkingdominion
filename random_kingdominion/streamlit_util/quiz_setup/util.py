from collections.abc import MutableMapping, Sequence
from typing import Any

import streamlit as st

from ...constants import QUALITIES_AVAILABLE
from ...kingdom import KingdomRandomizer


def st_calc_quiz_score(
    user_vals: dict[str, float],
    real_vals: dict[str, float],
    buy_str_user: str,
    buy_str_kingdom: str,
) -> float:
    score = 0.0
    if buy_str_user.lower() == buy_str_kingdom:
        score += 3
    for qual, user_val in user_vals.items():
        if qual not in real_vals:
            raise ValueError(f"Quality {qual!r} is not available in the kingdom.")
        diff = abs(real_vals[qual] - user_val)
        if diff == 0:
            score += 2
        elif diff == 0.5:
            score += 1.5
        elif diff == 1:
            score += 1
    return score


def reset_quiz_answers(
    state: MutableMapping[str, Any], quality_names: Sequence[str]
) -> None:
    state["quiz_show_solution"] = False
    state.pop("quiz_quality_buy_str", None)
    for quality in quality_names:
        state[f"quiz_quality_slider_{quality}"] = -1


def reset_quiz_workflow(
    state: MutableMapping[str, Any], quality_names: Sequence[str]
) -> None:
    state.pop("quiz_run_state", None)
    state.pop("quiz_current_kingdom", None)
    state.pop("quiz_has_started", None)
    for key in list(state):
        if key.startswith("_quiz_quality_"):
            state.pop(key, None)
    reset_quiz_answers(state, quality_names)


def load_quiz_widget_value(state: MutableMapping[str, Any], answer_key: str) -> str:
    widget_key = f"_{answer_key}"
    if answer_key in state:
        state[widget_key] = state[answer_key]
    else:
        state.pop(widget_key, None)
    return widget_key


def save_quiz_widget_value(state: MutableMapping[str, Any], answer_key: str) -> None:
    widget_value = state.get(f"_{answer_key}")
    if widget_value is None:
        state.pop(answer_key, None)
    else:
        state[answer_key] = widget_value


def generate_random_quiz_kingdom(quality_names: Sequence[str]) -> None:
    st.session_state["quiz_current_kingdom"] = generate_random_quiz_kingdom_string()
    reset_quiz_answers(st.session_state, quality_names)


def generate_random_quiz_kingdom_string() -> str:
    kingdom = KingdomRandomizer().randomize_new_kingdom()
    return kingdom.get_dombot_csv_string()


def get_quiz_quality_names() -> list[str]:
    quality_names = [q for q in QUALITIES_AVAILABLE if q != "interactivity"]
    quality_names = quality_names[3::-1] + quality_names[:3:-1]
    return quality_names
