import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk

st.title("About this page")


qual_desc = "\n  - ".join(
    [rk.construct_short_qual_desc(qual) for qual in rk.QUALITIES_AVAILABLE]
)
st.write(
    f"""
I'll try to shed some light on my ideas concerning my approach to the randomizer, the individual and kingdom-wide CSO (short for Card-Shaped Object, including landscapes) qualities, and excuse myself for the website looking a little funky in some places. 
"""
)

cso_qual_text = f"""A core concept underlying the randomizer and my kingdom assessment is the idea of CSO qualities. These qualities are a way to quantify the strength of a CSO considering a certain main Dominion engine aspect. The qualities are normalized to a scale from 0 to 3, where 0 is the non-existence and 3 is the best a CSO can have.\\
The aspects I have come up with are the ability to...
  - {qual_desc}

I have manually assigned these to each CSO (my thoughts on this can be found in the respective quality pages). From all CSOs in a kingdom, I then use a weird formula to calculate the kingdom's total qualities:\\
The total quality of a kingdom is calculated iteratively, where lower values take a higher amount to be equivalent to a higher value (four cards with a quality of 1 count as one card of quality 2, three cards of quality 2 as one of quality 3, and only if there are two or more cards of quality 3 the highest total quality value is awarded)."""

with st.expander("CSO Qualities", expanded=False):
    st.write(cso_qual_text, unsafe_allow_html=True)

randomizer_link = f'<a href="randomizer" target="_self">randomizer</a>'
randomizer_desc_text = f"""The {randomizer_link} is a tool to quickly generate a random kingdom for our Dominion games with a few clicks. It allows for a lot of customization, including the ability to exclude or require specific cards, landscapes, or card types. In detail, these are the options you can set:

- 📦**Expansions**:\\
You can select which expansions you want to include in the randomization, and also limit the randomization to a maximum amount of expansions you want to occur.
- ⚙️**Mechanics**:\\
You can currently exclude certain card Types, such as Attack, Duration, or Reserve cards. In the future, you might be able to force the inclusion of certain mechanics or themes (depending on whether I get my hands on the #two-themes tournament data, or alternatively find the time to categorize them myself :D).
- 🏞️**Landscape options**:\\
You can choose the amount of allowed landscapes and specify the allowed landscape types.
- 🚂**Engine Qualities**:\\
This part is based on the idea of CSO qualities (see the description above).\\
The randomizer then allows to exclude or require specific qualities, which can be useful if you want to play a kingdom with a certain focus.\\
For this task, upon each step of randomization, the randomizer will pick a random quality that in total is not fulfilled by the partially randomized kingdom, and limit the subset of remaining CSOs to those that fulfill this quality. This means that if you're requesting a kingdom with all qualities at the highest level, it can occur that they aren't perfectly fulfilled.
- 🚫**Banning, Forcing, Liking or Disliking CSOs**:\\
You can specify CSOs that you want to exclude, require, like, or dislike. The randomizer will then try to include or exclude these CSOs to its best abilities, where the liked and disliked CSOs are assigned weights relative to the other CSOs."""


with st.expander("Randomizer", expanded=False):
    st.write(randomizer_desc_text, unsafe_allow_html=True)


final_text = """

I hope you enjoy the randomizer and find it useful for your Dominion games.\\
If you have any feedback (especially concerning my quality assessments, they are certainly arguable), suggestions, or bug reports, feel free to contact me via the [GitHub repository](https://github.com/Fabian-Balzer/Randomkingdominion) or on the dominion discord.


### Affiliations

Dominion is a game by Donald X. Vaccarino and published by Rio Grande Games.
This project has no affiliation with either party. Card images were taken from the Dominion Strategy Wiki.
"""

st.write(final_text)
