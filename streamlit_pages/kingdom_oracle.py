import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "Kingdom Oracle",
    "This page allows you to easily input a kingdom to visualize its engine qualities and take a more detailed look on its CSOs. The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form.",
    "Learn more about the CSO and kingdom qualities on the about page.",
)


@st.cache_data
def load_recommended():
    recommended = rk.KingdomManager()
    recommended.load_recommended_kingdoms()
    recommended.load_expansions()
    df = recommended.dataframe_repr
    return df


df = load_recommended()

with st.expander("Choose from recommended kingdoms", expanded=False):
    exps = [
        exp for exp in rk.get_cached_expansions() if "1E" not in exp and exp != "Promo"
    ]
    exp_filters = st.multiselect("Allowed expansions", exps)
    df = df[
        df["expansions"]
        .fillna("")
        .apply(lambda x: any([exp in x for exp in exp_filters]))
    ]
    df["name_with_exps"] = (
        df["name"] + " (" + df["expansions"].fillna("").str.join(", ") + ")"
    )
    cols = st.columns([0.9, 0.1])
    with cols[0]:
        sel = st.selectbox("Recommended Kingdoms", [""] + df["name_with_exps"].tolist())
    if sel != "" and type(sel) == str:
        series = df[df["name_with_exps"] == sel].iloc[0].fillna("")
        kingdom = rk.Kingdom.from_dict(series.to_dict())
        st.session_state["kingdom_input"] = kingdom.get_dombot_csv_string()
        st.session_state["kingdom_name"] = kingdom.name
    else:
        st.session_state["kingdom_name"] = ""
    with cols[1]:
        st.link_button(
            "More sets 🔗",
            "https://kieranmillar.github.io/extra-recommended-sets/",
            help="Huge thanks to Kieran Millar whose [Extra Recommended Kingdoms page](https://kieranmillar.github.io/extra-recommended-sets/) I got the data for the recommended kingdoms from! Be sure to check out his additional recommended sets!",
        )

kingdom_input = st.text_input(
    "Enter a kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN'. You may specify the bane card with 'Young Witch: card' or 'Young Witch(Card)'.",
    value=st.session_state.get("kingdom_input", ""),
    key="kingdom_input",
)
kingdom = rk.Kingdom.from_dombot_csv_string(kingdom_input)
kingdom.name = st.session_state.get("kingdom_name", "")
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


st.warning(
    "Be aware that this is a very superficial view of the kingdom and does not take into account special card interactions, and that some of my takes on individual cards' qualities might seem surprising. Check out the about page for more information on those."
)
