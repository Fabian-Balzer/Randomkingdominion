import math

import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "Dominion Pairwise Rules Interactions",
    "On this page, you can explore interactions between Card-Shaped Objects (CSOs) that might catch you off-guard rules-wise. The project was initiated on discord by `nave`; while there are lot of different combinations, these do not cover the straight-forward interactions like your typical Village/Smithy. The interactions have been gathered with the assumption that those using it have a base knowledge of the rules of Dominion and are looking for edge-cases and things that are not 100 % intuitive.\\\nYou can either filter the interactions for certain expansions, or post a comma-separated list from which the site will try to filter for any relevant interactions.\\\nIf you want to see the full list of CSOs, you can visit the [CSO Database](/cso_overview).",
    "Learn more about the CSO and kingdom qualities on the about page.",
)


def _get_pairwise_comb_str(n: int):
    num_comb = math.comb(n, 2)
    return f"${{{n}\\choose{{2}}}} = {num_comb}$"


N_CSOS = len(
    rk.ALL_CACHED_CSOS[
        ~rk.listlike_contains_any(
            rk.ALL_CACHED_CSOS["Types"], ["Stamp", "Twist", "Setup Effect"]
        )
    ]
)
expander_text = f"""
The interactions below are meant to cover finicky pairwise rules interactions between Card-Shaped Objects (CSOs) that might not be immediately obvious.

The interactions have been gathered under the assumption that those reading them have a base knowledge of the rules of Dominion and are looking for edge-cases and things that might not be 100 % intuitive.

### What kind of interactions can you *not* find here?

While there are ton of different combinations (actually, considering that by now there exist $\\sim{N_CSOS}$ CSOs, there'd be {_get_pairwise_comb_str(N_CSOS)} possible pairwise combinations), the ones showcased here do **not** cover straight-forward interactions like Village/Smithy.

More specifically, the following general interactions are omitted here:

- **Basic strategy**:\\\nCommon synergies to e.g. build engines, e.g. typical Village-Smithy-like interactions.
- **Two-CSO combos**:\\\nAny powerful two-CSO combos like Lurker/Hunting Grounds, Collection/Stampede, Beggar/Guildhall, etc.. These are omitted here as this tool's intent is to cover shady rules interactions and not strategies. You can however find those at the [CSO combos](/combos) subpage of this website.
- **Shadows interacting with Ways**:\\\nSpeaking of shady; while Shadow cards can be played as Ways even from your deck, I decided to omit specifying for each Shadow card that they can be played as a given Way from your deck.

### Contribution

The project was initiated by `nave` on the [Dominion Discord](https://discord.gg/dominiongame).

If you have any suggestions for interactions that are not covered here but you think would fit in, feel free to visit the `#rules-lookup-project` channel on the discord.
"""
with st.expander("About these rules interactions", expanded=False, icon="💡"):
    st.markdown(expander_text, unsafe_allow_html=True)
    st.warning(
        "These interactions are for sure not exhaustive, and mistakes are possible - let me know if you have additional interactions to add, or find a mistake!"
    )

rk.st_display_combo_or_inter_page("inter")
