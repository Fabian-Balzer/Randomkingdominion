import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "About this page",
    "Here, I'll try to shed some light on the ideas concerning my approach to the randomizer, the individual and kingdom-wide CSO (short for Card-Shaped Object, including landscapes) qualities.",
)
st.write(
    "Click on any expander below to learn more about the respective topic.\\\nFeel free to reach out with feedback, suggestions, or bug reports, and be sure to check out my [YouTube channel](https://www.youtube.com/@fabyy5713) for Dominion content!"
)

qual_desc = "\n  - ".join(
    [rk.construct_short_qual_desc(qual) for qual in rk.QUALITIES_AVAILABLE]
)
cso_qual_text = f"""A core concept underlying the randomizer and my kingdom assessment is the idea of the qualities of Card-Shaped Objects (i.e., landscapes, cards, and I've decided to even include campaign twists).

These qualities are a way to quantify the strength of a CSO considering a certain main Dominion engine aspect.\\\n
Qualities are normalized to a scale from 0 to 3, where 0 implies the non-existence of a feature and 3 is the best a CSO can have.\\
The aspects I have come up with are the ability to...
  - {qual_desc}

You may visit their individual pages to get a more detailed description of each quality. Also, all CSOs labelled with the given quality are listed there.\\
I have manually assigned these to each CSO, and use them to easily evaluate a given kingdom. You can even filter for certain qualities in the randomizer!"""

with st.expander("CSO Qualities", expanded=False, icon=rk.ST_ICONS["cso_qualities"]):
    st.write(cso_qual_text, unsafe_allow_html=True)

kingdom_qual_text = """
### Kingdom Quality Calculation

To calculate the total qualities of a given kingdom (which are e.g. displayed in the kingdom plots), I use the following weird iterative formula, which considers the individual qualities of all CSOs included in the kingdom:

**As described above, each CSO has a single value from 0 to 3 in each category (e.g., Village).**

For the total given quality in category:

- four cards with qualities of 1 equal to a single quality of 2, while 
- three cards (or combined ones in the above step) with qualities of 2 equal to a single quality of 4, and 
- two of 3 equal to a single quality of 4.

**The total kingdom quality value is just the maximum reached this way.**

### Example

$\\implies$ As an example, a kingdom with 4 CSOs of quality 1 and 2 cards of quality 2 would have a total quality of 3, as there would virtually be three of quality 2.

### Visualization and Buy indicator

The resulting qualities are visualized plots that look like the one on the right.

Additionally, the plot contains a buy indicator above the 'Gain' quality, which indicates whether the kingdom contains cards that allow for extra buys. The three categories for this are 'No Buys', 'Maybe?', and 'Buys', where 'Maybe?' indicates that there are cards that can provide extra buys, but only under certain conditions (e.g., City or Animal Fair).

"""

with st.expander(
    "Kingdom Qualities", expanded=False, icon=rk.ST_ICONS["kingdom_qualities"]
):
    cols = st.columns([0.6, 0.4])
    cols[0].write(kingdom_qual_text, unsafe_allow_html=True)
    with cols[1]:
        fig = rk.plot_kingdom_qualities(
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

randomizer_link = f'<a href="randomizer" target="_self">randomizer</a>'
randomizer_desc_text = f"""The {randomizer_link} is a tool to quickly generate a random kingdom for our Dominion games with a few clicks. It allows for a lot of customization, including the ability to exclude or require specific cards, landscapes, or card types. In detail, these are the options you can set:

- {rk.ST_ICONS["expansions"]} **Expansions**:\\
You can select which expansions you want to include in the randomization, and also limit the randomization to a maximum amount of expansions you want to occur.
- {rk.ST_ICONS["mechanics"]} **Mechanics**:\\
You can currently exclude certain card Types, such as Attack, Duration, or Reserve cards. In the future, you might be able to force the inclusion of certain mechanics or themes (depending on whether I get my hands on the #two-themes tournament data, or alternatively find the time to categorize them myself :D). This section also contains customization options for the inclusion of Colony/Platinum and Shelters.
- {rk.ST_ICONS["landscapes"]} **Landscape options**:\\
You can choose the amount of allowed landscapes and specify the allowed landscape types.
- {rk.ST_ICONS["cso_qualities"]} **Engine Qualities**:\\
This part is based on the idea of CSO qualities (see the description above).\\
The randomizer then allows to exclude or require specific qualities, which can be useful if you want to play a kingdom with a certain focus.\\
For this task, upon each step of randomization, the randomizer will pick a random quality that in total is not fulfilled by the partially randomized kingdom, and limit the subset of remaining CSOs to those that fulfill this quality. This means that if you're requesting a kingdom with all qualities at the highest level, it can occur that they aren't perfectly fulfilled.
- {rk.ST_ICONS["bans"]} **Banning, Forcing, Liking or Disliking CSOs**:\\
You can specify CSOs that you want to exclude, require, like, or dislike. The randomizer will then try to include or exclude these CSOs to its best abilities, where the liked and disliked CSOs are assigned weights relative to the other CSOs. In the future, I aim to implement pasting CSO names here - sorry that you currently have to do this manually!"""


with st.expander(
    "Details on the Randomizer", expanded=False, icon=rk.ST_ICONS["randomizer"]
):
    st.write(randomizer_desc_text, unsafe_allow_html=True)

oracle_text = """The kingdom oracle allows you to easily input a kingdom to visualize its engine qualities derived from the included CSOs, and to take a more detailed look on its cards. The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form, and can also provide information on special combos or rules interactions that are present in the kingdom."""

with st.expander("Kingdom Oracle", expanded=False, icon=rk.ST_ICONS["oracle"]):
    st.write(oracle_text)

with st.expander("CSO Database", expanded=False, icon=rk.ST_ICONS["cso_overview"]):
    st.write(
        "The CSO Database page provides an overview of all available CSOs and the qualities I have associated with them. You can filter and sort the CSOs by their properties, qualities, and other fun stuff."
    )
with st.expander("CSO Interactions", expanded=False, icon=rk.ST_ICONS["interactions"]):
    st.write(
        "The interactions page allows you to explore interactions between CSOs that might catch you off-guard rules-wise. The project was initiated on discord by `nave`; while there are lot of different combinations, these do not cover the straight-forward interactions like your typical Village/Smithy. The interactions have been gathered with the assumption that those using it have a base knowledge of the rules of Dominion and are looking for edge-cases and things that are not 100 % intuitive."
    )

with st.expander("CSO Combos", expanded=False, icon=rk.ST_ICONS["combos"]):
    st.write(
        "The combos page allows you to explore pairwise CSO synergies, rushes, counters, and more."
    )

future_development_text = """
In the future, the following features might find their way into the randomizer:
- **Cookies**:
    - Save your preferences for future visits, and maybe download the configuration as well as the generated kingdoms.
- **Themes**:
  - Allow for the inclusion of certain themes or mechanics, such as "extra turn enablers" or "cost reducers".
- **Pastable CSO names**:
    - Allow for pasting CSO names to exclude, require, like, or dislike them, or even starting a kingdom with a partial DomBot string.
- **Extra component limitations**:
    - Some cards require extra setup or components, such as tokens or mats. Maybe I'll add a feature to limit them (relevant for IRL play).
- **Kingdom history**:
    - Save the kingdoms you've generated to look at them later.

### Already implemented

I'm proud to say that the following features have already been implemented recently:

- ✅ **Exploring two-card combos**:
    - On the combos page, you can explore pairwise synergies, rushes, counters, and more between CSOs.
- ✅ **Exploring rules interactions**:
    - On the interactions page, you can explore pairwise rules interactions between CSOs that might not be immediately obvious.
- ✅ **Kingdom analysis of recommended sets**:
    - Recommended (and TGG Daily) sets can be loaded into the kingdom oracle for analysis.
"""

with st.expander(
    "Future Development", expanded=False, icon=rk.ST_ICONS["future_development"]
):
    st.write(future_development_text)

with st.expander("Changelog", expanded=False, icon=rk.ST_ICONS["changelog"]):
    log = rk.get_changelog()
    for version, changes in log.items():
        st.write(f"#### Version {version}")
        st.write("- " + "\n- ".join(changes))

feedback_text = """
I hope you enjoy this randomizer and find it useful for your Dominion games.\\
If you have any feedback (especially concerning my quality assessments, they are certainly arguable), suggestions, or bug reports, feel free to contact me via the [GitHub repository](https://github.com/Fabian-Balzer/Randomkingdominion) or on the dominion discord."""

with st.expander("Feedback", expanded=False, icon=rk.ST_ICONS["feedback"]):
    st.write(feedback_text, unsafe_allow_html=True)

final_text = """
### ⚠️ Affiliations

Dominion is a game by Donald X. Vaccarino and published by Rio Grande Games.
This project has no affiliation with either party, it is merely a fan-made tool.\\
Card images were taken from the Dominion Strategy Wiki and might be outdated (let me know!).

#### 🔗 Links

Here are some links to relevant Dominion pages:

- [Dominion Strategy Wiki](https://wiki.dominionstrategy.com/)
- [Dominion Online Implementation](https://dominion.games/)
- [Dominion by Temple Gates Games](https://store.steampowered.com/app/1131620/Dominion/)
- [The Dominion Discord](https://discord.gg/dominiongame)
- [The Dominion Subreddit](https://www.reddit.com/r/dominion/)
- [Kieran Millar's Extra Recommended Sets](https://kieranmillar.github.io/extra-recommended-sets/)
"""

st.write(final_text)
