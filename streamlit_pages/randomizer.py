import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "RandomKingDominion - Dominion Randomizer",
    "This page contains just another randomizer for the card game of [Dominion](https://wiki.dominionstrategy.com/index.php).\\\nShipped with loads of options to randomize brand-new kingdoms to your liking.",
    "Learn more about the Kingdom Randomizer and its features on the about page.",
)

if st.session_state.get("show_randomization_toast", False):
    msg = st.session_state.get("randomization_toast", "Randomization successful!")
    icon = "🎉" if "successful" in msg else "⚠️" if "invalid" in msg else "❌"
    st.toast(msg, icon=icon, duration=7)
    del st.session_state["show_randomization_toast"]
if st.session_state.get("randomized_kingdom", "") != "":
    rk.st_build_current_randomized_kingdom_display()

if st.button(
    label="Randomize a new Kingdom with the options selected below!",
    width="stretch",
    on_click=rk.randomize_new_kingdom,
    icon=rk.ST_ICONS["randomizer"],
    type="primary",
):
    st.session_state["show_randomization_toast"] = True
    st.rerun()

rk.st_build_full_randomization_options()
