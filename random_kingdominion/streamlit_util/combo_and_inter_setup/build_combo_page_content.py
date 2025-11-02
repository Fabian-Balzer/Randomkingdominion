import streamlit as st

from ..constants import COMBO_COLOR_DICT, ST_ICONS
from .build_combo_or_inter_page import st_build_combo_or_inter_page


def _get_combo_explanation_text() -> str:
    text = """
For the purpose of this page, the following types of pairwise interactions (sometimes overlapping with the [rules interactions](/interactions)) are defined and roughly ranked by strength (although counters don't really fit in here):

!!Rush > !!Combo > !!Synergy > !!Weak Synergy > !!Counter > !!Nombo

These are defined below, although arguably the distinctions tend to be a bit fuzzy at times. Note that I mostly do not include synergies that should be somewhat obvious, f.e. such as Battlefield/Mill or most Trail/VG/Weaver stuff (although I've decided to include a few notable ones).

- !!Rush: A strong and centralizing strategy that usually quickly ends the game if followed, and for which you mostly ignore everything else in the kingdom.
- !!Combo: Strong, centralizing synergies which usually will make you loose if you ignore them.
- !!Synergy: Stuff that very nicely works together but isn't always viable, such as Capitalism/Landing Party.
- !!Weak Synergy: Something that is pleasantly accelerating your build, but can also be skipped if stronger things are around, or stuff that might only be relevant at a specific point in the game (like Castles/Keep).\\\n**<span style="color:darkred">Note that these are filtered out in the dataframe below by default; you may view them by changing that in the 'other' filter tab.</span>**
- !!Counter: Some interaction of an Attack played by an opponent versus a card you might have wanted to use yourself, like Crown/Highwayman.
- !!Nombo: Something that actively anti-synergizes, or does not work as you might expect, like Trail/Improve.

### YouTube Links

#### Showcases

For some of the rushes and combos, I've added YouTube links that provide a dedicated explanation and showcase the combo in action. Especially [tracer](https://www.youtube.com/@tracerdominion) and [ceviri](https://www.youtube.com/@ceviridominion1636) have some great educational content on this!

#### Playthroughs

For synergies or combos for which I couldn't find dedicated showcase videos, I've added links to playthroughs by various content creators (usually TGG Dailies or League matches; heavily biased by my own viewing habits, including stuff by [JNails](https://www.youtube.com/@JacobNails1), [Sharur](https://www.youtube.com/@SharurFoF), [Mic Qsenoch](https://www.youtube.com/@MicQsenoch), [tracer](https://www.youtube.com/@tracerdominion), [RDon](https://www.youtube.com/@RDon40), and [myself](https://www.youtube.com/@fabyy5713)) where the interaction occurs.

Let me know if you find an interesting video that could be added here for things that don't have anything attached!
    """
    for key, color in COMBO_COLOR_DICT.items():
        # We need this so Synergy doesn't also highlight Weak Synergy:
        icon = ST_ICONS["combo_type_" + key.lower().replace(" ", "_")]
        text = text.replace(
            f"!!{key}",
            f'**<span style="background-color:{color}; padding:2px 6px; border-radius:4px;">{key}{icon}</span>**',
        )
    return text


def st_build_combo_page_content():
    expander_text = _get_combo_explanation_text()
    with st.expander(
        "About rushes, combos, synergies, counters and nombos",
        expanded=False,
        icon="💡",
    ):
        st.markdown(expander_text, unsafe_allow_html=True)
        st.warning(
            "These combos are for sure not exhaustive - let me know if you have additional combos to add, or find a mistake!"
        )

    st_build_combo_or_inter_page("combo")
