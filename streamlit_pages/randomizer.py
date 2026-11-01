import streamlit as st

import random_kingdominion.streamlit_util as rks

rks.build_page_header(
    "RandomKingDominion - Dominion Randomizer",
    "This page contains just another randomizer for the card game of [Dominion](https://wiki.dominionstrategy.com/index.php).\\\nShipped with loads of options to randomize brand-new kingdoms to your liking.",
    "Learn more about the Kingdom Randomizer and its features on the about page.",
)

if st.session_state.get("randomized_kingdom", "") != "":
    rks.st_build_current_randomized_kingdom_display()

# Randomizes and shows the toast in its callback, so that one rerun is enough
st.button(
    label="Randomize a new Kingdom with the options selected below!",
    width="stretch",
    on_click=rks.randomize_new_kingdom,
    icon=rks.ST_ICONS["randomizer"],
    type="primary",
)

rks.st_build_full_randomization_options()
