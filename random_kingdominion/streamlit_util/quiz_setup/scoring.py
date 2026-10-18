"""Scoring rules for the quiz. Kept free of Streamlit so that it can be used
(and tested) without a running app."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Literal

from ...kingdom import Kingdom
from ...utils.kingdom_helper_funcs import explain_total_quality

BuyAvailability = Literal["yes", "maybe", "no"]

QUIZ_QUALITY_NAMES = ("gain", "thinning", "draw", "village", "altvp", "attack")

EXACT_QUALITY_POINTS = 2
BUY_POINTS = 3
MAX_ROUND_SCORE = EXACT_QUALITY_POINTS * len(QUIZ_QUALITY_NAMES) + BUY_POINTS

# Round scores strictly above these are considered good/impressive.
GOOD_SCORE_THRESHOLD = 8
IMPRESSIVE_SCORE_THRESHOLD = 11


@dataclass(frozen=True)
class ScoreBand:
    color: str
    bar_start: float
    message: str


CHEEKY_BAND = ScoreBand(
    "red",
    0,
    "Cheeky! Did you deliberately go for a low score? It's genuinely not that easy to achieve! :)",
)
OKAY_BAND = ScoreBand(
    "orange",
    1,
    "Off by quite a bit, I know you'll get there if you think about the kingdoms a bit more! There were probably one or two important CSOs you missed.",
)
GOOD_BAND = ScoreBand(
    "gold", GOOD_SCORE_THRESHOLD, "Not bad, you got the general idea :)"
)
IMPRESSIVE_BAND = ScoreBand(
    "lightgreen",
    IMPRESSIVE_SCORE_THRESHOLD,
    "Great job, you really know your way around Dominion kingdoms!\nI wouldn't be surprised if the offsets are due to subjective subtleties in my quality assessments.",
)
# The perfect band starts half a point below the maximum so that it is visible in the score bar.
PERFECT_BAND = ScoreBand(
    "green",
    MAX_ROUND_SCORE - 0.5,
    "Wow, congrats, perfect score!\nYou really know your Dominion (and my way of quality assessments)!",
)
SCORE_BANDS = (CHEEKY_BAND, OKAY_BAND, GOOD_BAND, IMPRESSIVE_BAND, PERFECT_BAND)


def get_score_band(score: float) -> ScoreBand:
    if score >= MAX_ROUND_SCORE:
        return PERFECT_BAND
    if score > IMPRESSIVE_SCORE_THRESHOLD:
        return IMPRESSIVE_BAND
    if score > GOOD_SCORE_THRESHOLD:
        return GOOD_BAND
    if score >= OKAY_BAND.bar_start:
        return OKAY_BAND
    return CHEEKY_BAND


def get_quality_points(user_val: float, real_val: float) -> float:
    diff = abs(real_val - user_val)
    if diff == 0:
        return EXACT_QUALITY_POINTS
    if diff == 0.5:
        return 1.5
    if diff == 1:
        return 1
    return 0


def get_buy_points(buy_str_user: str, buy_str_kingdom: str) -> float:
    return BUY_POINTS if buy_str_user.lower() == buy_str_kingdom else 0


def calc_quiz_score(
    user_vals: Mapping[str, float],
    real_vals: Mapping[str, float],
    buy_str_user: str,
    buy_str_kingdom: str,
) -> float:
    score = get_buy_points(buy_str_user, buy_str_kingdom)
    for qual, user_val in user_vals.items():
        if qual not in real_vals:
            raise ValueError(f"Quality {qual!r} is not available in the kingdom.")
        score += get_quality_points(user_val, real_vals[qual])
    return score


@dataclass(frozen=True)
class KingdomSolution:
    quality_values: Mapping[str, float]
    buy_availability: BuyAvailability
    # Per quality: the (name, value) of each contributing CSO, highest first
    contributions: Mapping[str, tuple[tuple[str, float], ...]]
    # Per quality: how the total was combined from the CSO values
    aggregation_steps: Mapping[str, tuple[str, ...]]
    # The (name, is_conditional) of each CSO providing +Buy
    buy_sources: tuple[tuple[str, bool], ...]
    card_names: tuple[str, ...]
    landscape_names: tuple[str, ...]


@lru_cache(maxsize=256)
def get_kingdom_solution(kingdom_str: str) -> KingdomSolution:
    """Return the real quiz qualities and Buy availability of the given kingdom string,
    plus everything needed to explain them.
    Cached, as building a kingdom is comparatively expensive and happens on every rerun.
    """
    kingdom = Kingdom.from_dombot_csv_string(kingdom_str)
    # The totals are calculated from the full kingdom, including extra CSOs (e.g. a Bane)
    df = kingdom.full_kingdom_df
    quality_values = {q: float(kingdom.total_qualities[q]) for q in QUIZ_QUALITY_NAMES}
    contributions = {}
    aggregation_steps = {}
    for q in QUIZ_QUALITY_NAMES:
        col = f"{q}_quality"
        contributing = df[df[col] > 0].sort_values([col, "Name"], ascending=[False, True])
        contributions[q] = tuple(
            (str(name), float(val))
            for name, val in zip(contributing["Name"], contributing[col])
        )
        aggregation_steps[q] = tuple(explain_total_quality(df[col].to_list())[1])
    buy_sources = tuple(
        (str(name), "Buys" not in gain_types)
        for name, gain_types in zip(df["Name"], df["gain_types"])
        if "Buys" in gain_types or "Buys*" in gain_types
    )
    return KingdomSolution(
        quality_values=MappingProxyType(quality_values),
        buy_availability=kingdom.buy_availability,
        contributions=MappingProxyType(contributions),
        aggregation_steps=MappingProxyType(aggregation_steps),
        buy_sources=buy_sources,
        card_names=tuple(kingdom.kingdom_card_df["Name"]),
        landscape_names=tuple(kingdom.kingdom_landscape_df["Name"]),
    )


def score_quiz_round(
    quality_values: Mapping[str, float], buy_availability: str, kingdom_str: str
) -> float:
    solution = get_kingdom_solution(kingdom_str)
    return calc_quiz_score(
        quality_values,
        solution.quality_values,
        buy_availability,
        solution.buy_availability,
    )
