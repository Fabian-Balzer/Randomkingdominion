from math import ceil

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
from PIL import Image

import random_kingdominion as rk

st.title("RandomKingDominion - Randomizer")

cols = st.columns([0.7, 0.3])
with cols[0]:
    st.write(
        "Just another randomizer for the card game of [Dominion](https://wiki.dominionstrategy.com/index.php).\\\nShipped with loads of options to randomize brand-new kingdoms to your liking."
    )
with cols[1]:
    st.page_link(
        "streamlit_pages/about.py",
        label="More details",
        icon="❓",
        use_container_width=True,
        help="Learn more about the Kingdom Randomizer and its features on the about page.",
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


rk.build_randomization_options()

if st.button(
    label="Randomize Kingdom with the selected options! 🔀",
    use_container_width=True,
    on_click=rk.randomize_kingdom,
):
    st.rerun()

if "randomized_kingdom" not in st.session_state:
    rk.randomize_kingdom()


@st.fragment
def _build_clipboard_button():
    csv_str = rk.Kingdom.from_dombot_csv_string(
        st.session_state["randomized_kingdom"]
    ).get_dombot_csv_string()
    st.button(
        "🔼To clipboard",
        help="Copy the kingdom's DomBot string to your clipboard",
        on_click=lambda: rk.copy_to_clipboard(csv_str),
        use_container_width=True,
    )


cols = st.columns([0.85, 0.15])
with cols[0]:
    st.write(
        rk.Kingdom.from_dombot_csv_string(
            st.session_state["randomized_kingdom"]
        ).get_dombot_csv_string()
    )
with cols[1]:
    _build_clipboard_button()

rk.display_current_kingdom()

# import numpy as np

# for cost in np.unique(rk.ALL_CSOS["Cost"].fillna("$1")):
#     html = get_cost_html(cost)
#     st.write(f"{html} {cost}", unsafe_allow_html=True)
