import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "RandomKingDominion - Dominion Randomizer",
    "This page contains just another randomizer for the card game of [Dominion](https://wiki.dominionstrategy.com/index.php).\\\nShipped with loads of options to randomize brand-new kingdoms to your liking.",
    "Learn more about the Kingdom Randomizer and its features on the about page.",
)


def load_history():
    if "history" in st.session_state:
        return st.session_state["history"]
    hist = rk.KingdomManager()
    # TODO: Load history from file
    return []


HISTORY = load_history()


if st.session_state.get("show_randomization_toast", False):
    st.toast("Randomization successful!", icon="🎉")
    del st.session_state["show_randomization_toast"]
if st.session_state.get("randomized_kingdom", "") != "":
    rk.display_current_kingdom()

if st.button(
    label="🔀 Randomize new Kingdom with the options selected below!",
    use_container_width=True,
    on_click=rk.randomize_kingdom,
):
    st.session_state["show_randomization_toast"] = True
    st.rerun()

rk.build_randomization_options()
