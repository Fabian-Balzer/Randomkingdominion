import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "What is this site about?",
    "Here, I'll try to shed some light on the ideas concerning my approach to the randomizer, the individual and kingdom-wide CSO (short for Card-Shaped Object, including landscapes) qualities.",
)
st.write(
    "Click on any tab below to learn more about the respective topic.\\\nFeel free to reach out with feedback, suggestions, or bug reports (preferable on GitHub or the Discord), and be sure to check out my [YouTube channel](https://www.youtube.com/@fabyy5713) for Dominion content!"
)

segmented_options = [
    f"{rk.ST_ICONS['video']} Introduction Video",
    f"🃏 About CSOs",
    f"📝 Description of subsites",
    f"ℹ️ Miscellaneous",
    "⚠️ Affiliations",
]

control_container = st.container(border=True)
control = control_container.segmented_control(
    "What would you like to learn more about?",
    segmented_options,
    default=segmented_options[0],
    width="stretch",
)

if control == segmented_options[0]:
    with control_container:
        rk.st_build_introduction_video_showcase()

if control == segmented_options[1]:
    with control_container:
        st.write(
            "Card-Shaped Objects (CSOs) are the central elements in Dominion, representing various game components such as landscapes and cards."
        )
        rk.st_build_cso_description_tabs()

if control == segmented_options[2]:
    with control_container:
        st.write("More details about the different pages of this site:")
        rk.st_build_site_desc_tabs()

if control == segmented_options[3]:
    with control_container:
        rk.st_build_more_info_tabs()

affiliation_text = """Dominion is a game by Donald X. Vaccarino and published by Rio Grande Games.
This project has no affiliation with either party, it is merely a fan-made tool.
Card names, card text and card art are © Rio Grande Games / Donald X. Vaccarino.

Card images were taken from the [Dominion Strategy Wiki](https://wiki.dominionstrategy.com) and might be outdated (let me know!).

They are available under the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0) license](https://creativecommons.org/licenses/by-nc-sa/3.0/).

Card data (names, expansions, types, costs and card text) is based on the [List of cards](https://wiki.dominionstrategy.com/index.php/List_of_cards) of the Dominion Strategy Wiki by its contributors, used under CC BY-NC-SA 3.0.
It was reformatted and extended with my own qualities and types; the resulting card table is shared under the same license.

Random KingDominion © 2021–2026 Fabian Balzer. The source code is available on [GitHub](https://github.com/Fabian-Balzer/Randomkingdominion) under the [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0.html), and comes without any warranty.
"""

if control == segmented_options[4]:
    with control_container:
        st.write(affiliation_text)
