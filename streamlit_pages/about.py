import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "About this page",
    "Here, I'll try to shed some light on the ideas concerning my approach to the randomizer, the individual and kingdom-wide CSO (short for Card-Shaped Object, including landscapes) qualities.",
)


qual_desc = "\n  - ".join(
    [rk.construct_short_qual_desc(qual) for qual in rk.QUALITIES_AVAILABLE]
)
cso_qual_text = f"""A core concept underlying the randomizer and my kingdom assessment is the idea of CSO qualities. These qualities are a way to quantify the strength of a CSO considering a certain main Dominion engine aspect. The qualities are normalized to a scale from 0 to 3, where 0 is the non-existence and 3 is the best a CSO can have.\\
The aspects I have come up with are the ability to...
  - {qual_desc}

You may visit their individual pages to get a more detailed description of each quality. Also, all CSOs labelled with the given quality are listed there.\\
I have manually assigned these to each CSO. From all CSOs in a kingdom, I then use a weird formula to calculate the kingdom's total qualities:\\
*The total quality of a kingdom is calculated iteratively, where lower values take a higher amount to be equivalent to a higher value (four cards with a quality of 1 count as one card of quality 2, three cards of quality 2 as one of quality 3, and only if there are two or more cards of quality 3 the highest total quality value is awarded).\\
As an example, a kingdom with 4 cards of quality 1 and 2 cards of quality 2 would have a total quality of 3, as there would virtually be three of quality 2.*"""

with st.expander("CSO Qualities", expanded=False):
    st.write(cso_qual_text, unsafe_allow_html=True)

randomizer_link = f'<a href="randomizer" target="_self">randomizer</a>'
randomizer_desc_text = f"""The {randomizer_link} is a tool to quickly generate a random kingdom for our Dominion games with a few clicks. It allows for a lot of customization, including the ability to exclude or require specific cards, landscapes, or card types. In detail, these are the options you can set:

- 📦**Expansions**:\\
You can select which expansions you want to include in the randomization, and also limit the randomization to a maximum amount of expansions you want to occur.
- ⚙️**Mechanics**:\\
You can currently exclude certain card Types, such as Attack, Duration, or Reserve cards. In the future, you might be able to force the inclusion of certain mechanics or themes (depending on whether I get my hands on the #two-themes tournament data, or alternatively find the time to categorize them myself :D). This section also contains customization options for the inclusion of Colony/Platinum and Shelters.
- 🏞️**Landscape options**:\\
You can choose the amount of allowed landscapes and specify the allowed landscape types.
- 🚂**Engine Qualities**:\\
This part is based on the idea of CSO qualities (see the description above).\\
The randomizer then allows to exclude or require specific qualities, which can be useful if you want to play a kingdom with a certain focus.\\
For this task, upon each step of randomization, the randomizer will pick a random quality that in total is not fulfilled by the partially randomized kingdom, and limit the subset of remaining CSOs to those that fulfill this quality. This means that if you're requesting a kingdom with all qualities at the highest level, it can occur that they aren't perfectly fulfilled.
- 🚫**Banning, Forcing, Liking or Disliking CSOs**:\\
You can specify CSOs that you want to exclude, require, like, or dislike. The randomizer will then try to include or exclude these CSOs to its best abilities, where the liked and disliked CSOs are assigned weights relative to the other CSOs. In the future, I aim to implement pasting CSO names here - sorry that you currently have to do this manually!"""


with st.expander("Details on the Randomizer", expanded=False):
    st.write(randomizer_desc_text, unsafe_allow_html=True)

oracle_text = """The kingdom oracle allows you to easily input a kingdom to visualize its engine qualities derived from the included CSOs, and to take a more detailed look on its cards. The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form."""

with st.expander("Kingdom Oracle", expanded=False):
    st.write(oracle_text)

with st.expander("CSO Database", expanded=False):
    st.write(
        "The CSO Database page provides an overview of all available CSOs and the qualities I have associated with them. You can filter and sort the CSOs by their properties, qualities, and other fun stuff."
    )
with st.expander("CSO Interactions", expanded=False):
    st.write(
        "The interactions page allows you to explore interactions between CSOs that might catch you off-guard rules-wise. The project was initiated on discord by `nave`; while there are lot of different combinations, these do not cover the straight-forward interactions like your typical Village/Smithy. The interactions have been gathered with the assumption that those using it have a base knowledge of the rules of Dominion and are looking for edge-cases and things that are not 100 % intuitive."
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
- ✅ **Kingdom analysis of recommended sets**:
    - I plan to include the recommended (and maybe the TGG Daily) sets as part of the Kingdom Oracle so you'll be able to analyze them there without having to paste them in.
"""

with st.expander("Future Development", expanded=False):
    st.write(future_development_text)

with st.expander("Changelog", expanded=False):
    log = rk.get_changelog()
    for version, changes in log.items():
        st.write(f"#### Version {version}")
        st.write("- " + "\n- ".join(changes))

feedback_text = """
I hope you enjoy this randomizer and find it useful for your Dominion games.\\
If you have any feedback (especially concerning my quality assessments, they are certainly arguable), suggestions, or bug reports, feel free to contact me via the [GitHub repository](https://github.com/Fabian-Balzer/Randomkingdominion) or on the dominion discord."""

with st.expander("Feedback", expanded=False):
    st.write(feedback_text, unsafe_allow_html=True)

final_text = """
### Affiliations

Dominion is a game by Donald X. Vaccarino and published by Rio Grande Games.
This project has no affiliation with either party.\\
Card images were taken from the Dominion Strategy Wiki and might be outdated (let me know!).\\
Here are some links to relevant Dominion pages:

- [Dominion Strategy Wiki](https://wiki.dominionstrategy.com/)
- [Dominion Online Implementation](https://dominion.games/)
- [Dominion by Temple Gates Games](https://store.steampowered.com/app/1131620/Dominion/)
- [The Dominion Discord](https://discord.gg/dominiongame)
- [The Dominion Subreddit](https://www.reddit.com/r/dominion/)
- [Kieran Millar's Extra Recommended Sets](https://kieranmillar.github.io/extra-recommended-sets/)
"""

st.write(final_text)
