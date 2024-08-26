import pandas as pd
import streamlit as st

import random_kingdominion as rk

rk.build_page_header(
    "Kingdom Oracle",
    "This page allows you to easily input a kingdom to visualize its engine qualities and take a more detailed look on its CSOs. The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form.",
    "Learn more about the CSO and kingdom qualities on the about page.",
)


@st.cache_data
def load_existing_kingdoms(selection_type: str) -> pd.DataFrame:
    manager = rk.KingdomManager()
    if selection_type == "TGG Dailies":
        manager.load_tgg_dailies()
    elif selection_type == "Recommended":
        manager.load_recommended_kingdoms()
    elif selection_type == "Reddit's KOTW":
        manager.load_kingdoms_from_yaml(rk.FPATH_KINGDOMS_KOTW_REDDIT)
    elif selection_type == "Fabi's Recommendations":
        manager.load_custom_kingdoms()
    df = manager.dataframe_repr

    # Register a name that includes the expansions
    exp_repr = df["expansions"].apply(
        lambda x: ", ".join(x) if len(x) < 4 else f"{len(x)} expansions"
    )
    df["name_with_exps"] = df["name"] + " (" + exp_repr + ")"
    if selection_type == "TGG Dailies":
        sani_wr = df["winrate"].apply(
            lambda x: f" [{x*100:.1f} %]" if x != "" else " [N/A]"
        )
        df["name_with_exps"] = df["name_with_exps"] + sani_wr
    df["csos"] = df.apply(lambda x: x["cards"] + x["landscapes"], axis=1)
    return df


import numpy as np


def _build_kingdom_select_box(df: pd.DataFrame):
    """Build the selection box that also sets the kingdom input and the kingdom name in the select box"""
    sel = st.selectbox(
        f"Choose from {len(df)} Kingdoms", [""] + df["name_with_exps"].tolist()
    )
    if sel != "" and type(sel) == str:
        series = df[df["name_with_exps"] == sel].iloc[0]
        kingdom = rk.Kingdom.from_dict(series.to_dict())
        st.session_state["kingdom_input"] = kingdom.get_dombot_csv_string()
        st.session_state["kingdom_name"] = kingdom.name
    else:
        st.session_state["kingdom_name"] = ""


def _build_reference_widget():
    """Build a widget to reference where the kingdoms are from."""
    selected_stuff = st.session_state.get("kingdom_select_group", "Recommended")
    if selected_stuff == "Recommended":
        st.link_button(
            "More sets 🔗",
            "https://kieranmillar.github.io/extra-recommended-sets/",
            help="Huge thanks to Kieran Millar whose [Extra Recommended Kingdoms page](https://kieranmillar.github.io/extra-recommended-sets/) I got the data for the recommended kingdoms from! Be sure to check out his additional recommended sets!",
        )
    elif selected_stuff == "TGG Dailies":
        st.link_button(
            "TGG Dailies 🔗",
            "https://store.steampowered.com/app/1131620/Dominion/",
            help="The TGG Dailies are a set of daily kingdoms provided in the [Temple Gates Games Client](https://store.steampowered.com/app/1131620/Dominion/), where you compete against the Hard AI.\nThanks to the amazing people on the TGG discord I managed to collect these (most notably ``probably-lost``, ``igorbone`` and ``Diesel Pioneer``).",
        )
    elif selected_stuff == "Reddit's KOTW":
        st.link_button(
            "Reddit's KOTW 🔗",
            "https://www.reddit.com/r/dominion/search/?q=flair%3Akotw&sort=new",
            help="The Kingdom of the Week is a weekly event on the [Dominion subreddit](https://www.reddit.com/r/dominion/) with a special kingdom being covered each week.",
        )


def _get_short_info(selected_stuff: str) -> str:
    if selected_stuff == "Recommended":
        return "The kingdoms recommended by DXV himself, found in the rulebooks of the Dominion expansions, and mixing two expansions at max. Shoutout to Kieran Millar's [Extra Recommended Kingdoms page](https://kieranmillar.github.io/extra-recommended-sets/) where these these kingdoms are conveniently provided."
    elif selected_stuff == "TGG Dailies":
        return "The TGG Dailies are kingdoms provided each day in the Temple Gates Games Client, where you compete against the Hard AI.\\\nShoutout to the amazing people on the TGG discord who helped me collect these (most notably ``probably-lost``, ``igorbone`` and ``Diesel Pioneer``)."
    elif selected_stuff == "Fabi's Recommendations":
        return "My personal recommendations of kingdoms I randomly stumbled upon, played in the TGG client against the Hard AI, and deemed to be interesting.\\\nHave fun with them! They usually contain a large amount of expansions, so they might be more suited for online play."
    elif selected_stuff == "Reddit's KOTW":
        return "The Kingdom of the Week (KOTW) is a weekly event on the Dominion subreddit, where a curated kingdom is covered. These usually offer especially interesting interactions.\\\nCheck out the [Dominion subreddit](https://www.reddit.com/r/dominion/) for more information."
    else:
        return "Unknown"


def _build_exps_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    available_exps = np.unique(
        [exp for exp_list in df["expansions"] for exp in exp_list]
    )
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        require_all_exps = st.checkbox(
            "Require all",
            help="If checked, all selected expansions need to be in the sets, otherwise, any of them will do.",
        )
    with cols[0]:
        placeholder = (
            "Choose expansions (all required)"
            if require_all_exps
            else "Choose expansions (any required)"
        )
        exp_filters = st.multiselect(
            "Allowed expansions",
            available_exps,
            default=st.session_state.get("kingdom_select_exp_filters", []),
            key="kingdom_select_exp_filters",
            placeholder=placeholder + " to filter for",
            help="If no expansions are provided, no filters are applied.",
        )

    # If no expansion is selected, allow for all sets
    if len(exp_filters) > 0:
        filt_func = all if require_all_exps else any
        exp_mask = df["expansions"].apply(
            lambda x: filt_func([exp in x for exp in exp_filters])
        )
        df = df[exp_mask]
    return df


def _build_csos_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    available_csos = np.unique([cso for cso_list in df["csos"] for cso in cso_list])
    available_csos = sorted(rk.ALL_CSOS.loc[available_csos]["Name"])
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        require_all_csos = st.checkbox(
            "Require all",
            help="If checked, all selected CSOs need to be in the sets, otherwise, any of them will do.",
            key="kingdom_select_require_all_csos",
        )
    with cols[0]:
        placeholder = (
            "Choose CSOs (all required)"
            if require_all_csos
            else "Choose CSOs (any required)"
        )
        cso_filters = st.multiselect(
            "Allowed CSOs",
            available_csos,
            default=st.session_state.get("kingdom_select_cso_filters", []),
            key="kingdom_select_cso_filters",
            placeholder=placeholder + " to filter for",
            help="If no CSOs are provided, no filters are applied.",
        )

    # If no CSO is selected, allow for all CSOs
    if len(cso_filters) > 0:
        filt_func = all if require_all_csos else any
        cso_mask = df["csos"].apply(
            lambda x: filt_func([rk.sanitize_cso_name(cso) in x for cso in cso_filters])
        )
        df = df[cso_mask]
    return df


def _build_random_selection_button(df: pd.DataFrame):
    if st.button(
        "Random\nSelection",
        key="kingdom_select_random_selection",
        use_container_width=True,
        type="primary",
        help="Select a random kingdom from those currently eligible.",
    ):
        if len(df) > 0:
            series = df.sample().iloc[0]
            kingdom = rk.Kingdom.from_dict(series.to_dict())
            st.session_state["kingdom_input"] = kingdom.get_dombot_csv_string()
            st.session_state["kingdom_name"] = kingdom.name


def _build_tgg_winrate_filter_widget(df: pd.DataFrame) -> pd.DataFrame:
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        apply_winrate_filter = st.checkbox(
            "Filter by winrate",
            help="If checked, you can filter the kingdoms by the winrate of the TGG Hard AI. The winrate is an approximation and might not be accurate.",
            key="kingdom_select_winrate_filter_checkbox",
        )
    with cols[0]:
        winrate_slider = st.slider(
            "Winrate",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.01,
            key="kingdom_select_winrate_filter",
            help="Filter kingdoms by the winrate of the TGG Hard AI. The winrate is an approximation and might not be accurate.",
            disabled=not apply_winrate_filter,
        )
    if apply_winrate_filter:
        st.info(
            f"The winrate of the TGG Hard AI was kindly provided to me by Jeff - thanks a lot!\\\nThe winrate $\\eta$ is defined as $\\eta = \\frac{{N_{{\\rm First Wins}}}}{{N_{{\\rm First Wins}} + N_{{\\rm First Losses}}}}$ where $N_{{\\rm First Wins}}$ and $N_{{\\rm First Losses}}$ are the number of games the players won or lost against the AI on their first playthrough. It is only available for kingdoms played after mid December 2023 (when AI difficulty settings were introduced to the Daily).\\\nIf you're filtering for it, all kingdoms where it's unavailable are excluded."
        )
    if apply_winrate_filter:
        df = df[df["winrate"] != ""]
        df = df[df["winrate"].between(*winrate_slider)]
    return df


def build_existing_kingdom_select(selection_type: str):
    """Build a way for the user to select one of the given existing kingdoms
    provided via the dataframe.
    """
    df = load_existing_kingdoms(selection_type)
    with st.container(border=True):
        st.write("Filtering options")
        df = _build_exps_filter_widget(df)
        df = _build_csos_filter_widget(df)
        if selection_type == "TGG Dailies":
            df = _build_tgg_winrate_filter_widget(df)

    if len(df) == 0:
        st.warning("No kingdoms available for your selection.")
        return

    cols = st.columns([0.75, 0.15, 0.1])
    with cols[0]:
        _build_kingdom_select_box(df)
    with cols[1]:
        _build_random_selection_button(df)
    with cols[2]:
        _build_reference_widget()


with st.expander("Select existing kingdom to visualize", expanded=False):
    selection = st.radio(
        "Which set of kingdoms?",
        ["Recommended", "TGG Dailies", "Reddit's KOTW", "Fabi's Recommendations"],
        index=0,
        horizontal=True,
        key="kingdom_select_group",
    )
    if selection is not None:
        build_existing_kingdom_select(selection)
        st.info(_get_short_info(selection))

cols = st.columns([0.9, 0.1])
with cols[0]:
    kingdom_input = st.text_input(
        "Enter a kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN'. You may specify the bane card with 'Young Witch: card' or 'Young Witch(Card)'.",
        value=st.session_state.get("kingdom_input", ""),
        key="kingdom_input",
        placeholder="e.g. Chapel, Village, Young Witch (Moat), Pious (Poet), Swindler, Growth, ...",
    )
try:
    if kingdom_input != "":
        kingdom = rk.Kingdom.from_dombot_csv_string(kingdom_input)
    else:
        kingdom = rk.Kingdom([])
except ValueError:
    kingdom = rk.Kingdom([], notes="Invalid kingdom input. Please check the format.")
kingdom.name = st.session_state.get("kingdom_name", "")
with cols[1]:
    if not kingdom.is_empty:
        rk.build_clipboard_button("kingdom_input")

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
