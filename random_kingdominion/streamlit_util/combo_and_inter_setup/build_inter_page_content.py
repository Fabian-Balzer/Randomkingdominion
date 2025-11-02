import math

import numpy as np
import streamlit as st

from ...cso_series_utils import listlike_contains_any
from ..constants import ALL_CACHED_CSOS, COMBO_COLOR_DICT, ST_ICONS
from .build_combo_or_inter_page import st_build_combo_or_inter_page


@st.cache_data
def _get_cso_count() -> int:
    return np.sum(
        ~listlike_contains_any(
            ALL_CACHED_CSOS["Types"], ["Stamp", "Twist", "Setup Effect"]
        )
    )


def _get_pairwise_comb_str(n: int):
    num_comb = math.comb(n, 2)
    return f"${{{n}\\choose{{2}}}} = {num_comb}$"


def _get_inter_explanation_text() -> str:
    n_csos = _get_cso_count()
    text = f"""
The interactions below are meant to cover finicky pairwise rules interactions between Card-Shaped Objects (CSOs) that might not be immediately obvious.

The interactions have been gathered under the assumption that those reading them have a base knowledge of the rules of Dominion and are looking for edge-cases and things that might not be 100 % intuitive.

### What kind of interactions can you *not* find here?

While there are ton of different combinations (actually, considering that by now there exist $\\sim{n_csos}$ CSOs, there'd be {_get_pairwise_comb_str(n_csos)} possible pairwise combinations), the ones showcased here do **not** cover straight-forward interactions like Village/Smithy.

More specifically, the following general interactions are omitted here:

- **Basic strategy**:\\\nCommon synergies to e.g. build engines, e.g. typical Village-Smithy-like interactions.
- **Two-CSO combos**:\\\nAny powerful two-CSO combos like Lurker/Hunting Grounds, Collection/Stampede, Beggar/Guildhall, etc.. These are omitted here as this tool's intent is to cover shady rules interactions and not strategies. You can however find those at the [CSO combos](/combos) subpage of this website.
- **Shadows interacting with Ways**:\\\nSpeaking of shady; while Shadow cards can be played as Ways even from your deck, I decided to omit specifying for each Shadow card that they can be played as a given Way from your deck.

### Contribution

The project was initiated by `nave` on the [Dominion Discord](https://discord.gg/dominiongame).

If you have any suggestions for interactions that are not covered here but you think would fit in, feel free to visit the `#rules-lookup-project` channel on the discord.
"""
    for key, color in COMBO_COLOR_DICT.items():
        # We need this so Synergy doesn't also highlight Weak Synergy:
        icon = ST_ICONS["combo_type_" + key.lower().replace(" ", "_")]
        text = text.replace(
            f"!!{key}",
            f'**<span style="background-color:{color}; padding:2px 6px; border-radius:4px;">{key}{icon}</span>**',
        )
    return text


def st_build_inter_page_content():
    inter_text = _get_inter_explanation_text()
    with st.expander("About these rules interactions", expanded=False, icon="💡"):
        st.markdown(inter_text, unsafe_allow_html=True)
        st.warning(
            "These interactions are for sure not exhaustive, and mistakes are possible - let me know if you have additional interactions to add, or find a mistake!"
        )

    st_build_combo_or_inter_page("inter")
