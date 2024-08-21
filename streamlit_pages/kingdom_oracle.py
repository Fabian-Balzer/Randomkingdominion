import streamlit as st

import random_kingdominion as rk

st.title("Kingdom Oracle")

cols = st.columns([0.8, 0.2])
with cols[0]:
    st.write(
        "This page allows you to input a kingdom to visualize its engine qualities.\\\n Be aware that this is a very superficial view of the kingdom and does not take into account special card interactions, and that some of my takes on individual cards' qualities might seem weird at first."
    )
with cols[1]:
    st.page_link(
        "streamlit_pages/about.py",
        label="More details",
        icon="❓",
        use_container_width=True,
        help="Learn more about how the card and kingdom qualities are obtained.",
    )
df = rk.ALL_CSOS

kingdom_input = st.text_input(
    "Enter a kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN'. You may specify the bane card with 'Young Witch: card' or 'Young Witch(Card)'.",
)
kingdom = rk.Kingdom.from_dombot_csv_string(kingdom_input)
if kingdom.notes != "" and "['']" not in kingdom.notes:
    notes = kingdom.notes.replace("\n", "<br>").removesuffix("<br>")
    red_background_message = f"""
    <div style='background-color: #ffcccc; padding: 10px; border-radius: 5px;'>
        <p style='color: black; font-size: 16px;'>{notes}</p>
    </div>
    """
    st.write(red_background_message, unsafe_allow_html=True)

if kingdom.is_empty:
    st.write("No kingdom selected")
else:
    rk.display_kingdom(kingdom, is_randomizer_view=False)
