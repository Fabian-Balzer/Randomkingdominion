import streamlit as st

from ...constants import QUALITIES_AVAILABLE
from ...utils import plot_kingdom_qualities
from ..constants import ST_ICONS
from ..quality_display import construct_short_qual_desc


def _get_cso_qual_desc_text() -> str:

    qual_desc = "\n  - ".join(
        [construct_short_qual_desc(qual) for qual in QUALITIES_AVAILABLE]
    )
    cso_qual_text = f"""A core concept underlying the randomizer and my kingdom assessment is the idea of the qualities of Card-Shaped Objects (i.e., landscapes, cards, and I've decided to even include campaign twists).

These qualities are a way to quantify the strength of a CSO considering a certain main Dominion engine aspect.\\\n
Qualities are normalized to a scale from 0 to 3, where 0 implies the non-existence of a feature and 3 is the best a CSO can have.\\
The aspects I have come up with are the ability to...
- {qual_desc}

You may visit their individual pages to get a more detailed description of each quality. Also, all CSOs labelled with the given quality are listed there.\\
I have manually assigned these to each CSO, and use them to easily evaluate a given kingdom. You can even filter for certain qualities in the randomizer!"""
    return cso_qual_text


def _get_kingdom_qual_desc_text() -> str:
    kingdom_qual_text = """
To calculate the total qualities of a given kingdom (which are e.g. displayed in the kingdom plots), I use the following weird iterative formula, which considers the individual qualities of all CSOs included in the kingdom:

**As described above, each CSO has a single value from 0 to 3 in each category (e.g., Village).**

For the total given quality in category:

- four cards with qualities of **1** equal to a single quality of **2**, while 
- three cards (or combined ones in the above step) with qualities of **2** equal to a single quality of **3**, and 
- two with a quality of **3** equal to a single quality of **4**.

**The total kingdom quality value is just the maximum reached this way.**

### Example

$\\implies$ As an example, a kingdom with four CSOs with a Draw quality of **1** and **2** CSOs of quality **2** would have a total quality of **3**, as there would virtually be three of quality **2**.

### Visualization and Buy indicator

The resulting qualities are visualized plots that look like the one on the right.

Additionally, the plot contains a buy indicator above the 'Gain' quality, which indicates whether the kingdom contains cards that allow for extra buys. The three categories for this are 'No Buys', 'Maybe?', and 'Buys', where 'Maybe?' indicates that there are cards that can provide extra buys, but only under certain conditions (e.g., City or Animal Fair).
    """
    return kingdom_qual_text


def st_build_cso_description_tabs():
    cso_qual_text = _get_cso_qual_desc_text()
    kingdom_qual_text = _get_kingdom_qual_desc_text()
    tab_names = [
        f"{ST_ICONS['cso_qualities']} CSO Qualities",
        f"{ST_ICONS['kingdom_qualities']} Kingdom Qualities",
    ]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        st.write(cso_qual_text, unsafe_allow_html=True)

    cols = tabs[1].columns([0.6, 0.4])
    cols[0].write(kingdom_qual_text)
    with cols[1]:
        fig = plot_kingdom_qualities(
            {
                "village": 4,
                "draw": 3,
                "thinning": 2,
                "gain": 1,
                "attack": 0,
                "altvp": 2,
            },
            buy_str="Buys",
        )
        fig.set_facecolor("none")
        st.pyplot(fig)
        st.write(
            "<div align='center'>Example kingdom quality plot.</div>",
            unsafe_allow_html=True,
        )
