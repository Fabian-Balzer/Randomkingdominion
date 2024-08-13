from pathlib import Path

import streamlit as st
from streamlit_cookies_controller import CookieController

from ..constants import EXPANSION_LIST, RENEWED_EXPANSIONS


@st.cache_data
def get_cached_expansions():
    return [exp for exp in EXPANSION_LIST if exp not in RENEWED_EXPANSIONS]


COOKIES = CookieController()

STATIC_FPATH = Path("./static")
ALL_EXPANSIONS = get_cached_expansions()
NUM_EXPS = len(ALL_EXPANSIONS)
LIKE_BAN_OPTIONS = {
    "Banned": "These CSOs are excluded from the draw pool during randomization.",
    "Required": "These CSOs will be included in the kingdom (unless they are from different expansions than the selected ones, in that case it depends on whether you want to allow that). This overrides any bans.",
    "Disliked": "These CSOs will have a lower probability of showing up.",
    "Liked": "These CSOs will have a higher probability of showing up.",
}


@st.cache_data
def _load_csos():
    from random_kingdominion import ALL_CSOS

    return ALL_CSOS


ALL_CACHED_CSOS = _load_csos()
