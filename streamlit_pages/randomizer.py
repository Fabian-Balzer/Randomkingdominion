import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "RandomKingDominion - Domionion Randomizer",
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


# # Remove spacing between columns:
# st.markdown(
#     """
#     <style>
#     [data-testid=column] [data-testid=stVerticalBlock]{
#         gap: 0rem;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


if "randomized_kingdom" in st.session_state:
    st.toast("Randomization successful!", icon="🎉")
    rk.display_current_kingdom()

rk.build_randomization_options()

if st.button(
    label="🔀 Randomize new Kingdom with the options selected above!",
    use_container_width=True,
    on_click=rk.randomize_kingdom,
):
    st.rerun()
