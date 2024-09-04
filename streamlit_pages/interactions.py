import pandas as pd
import streamlit as st

import random_kingdominion as rk


@st.cache_data
def get_interactions() -> pd.DataFrame:
    """Loads the available interactions and adds some
    streamlit-relevant columns to them."""
    df = rk.ALL_INTERACTIONS.copy()
    name_dict = rk.ALL_CSOS["Name"].to_dict()
    img_dict = rk.ALL_CSOS["ImagePath"].to_dict()
    exp_dict = rk.ALL_CSOS["Expansion"].to_dict()
    df["CSO 1"] = df["Card1"].apply(name_dict.get)
    df["CSO 2"] = df["Card2"].apply(name_dict.get)
    df["img_1"] = df["Card1"].apply(lambda x: "app/static/card_pictures/" + img_dict[x])
    df["img_2"] = df["Card2"].apply(lambda x: "app/static/card_pictures/" + img_dict[x])
    df["exp_1"] = df["Card1"].apply(exp_dict.get)
    df["exp_2"] = df["Card2"].apply(exp_dict.get)

    df["exp_img_1"] = df["exp_1"].apply(
        lambda x: "app/static/" + rk.get_expansion_icon_path(x, relative_only=True)
    )
    df["exp_img_2"] = df["exp_2"].apply(
        lambda x: "app/static/" + rk.get_expansion_icon_path(x, relative_only=True)
    )
    return df


INTERACTIONS = get_interactions()

rk.build_page_header(
    "Domionion Card and Landscape Rules Interactions",
    "On this page, you can explore interactions between Card-Shaped Objects (CSOs) that might catch you off-guard rules-wise. The project was initiated on discord by `nave`; while there are lot of different combinations, these do not cover the straight-forward interactions like your typical Village/Smithy. The interactions have been gathered with the assumption that those using it have a base knowledge of the rules of Dominion and are looking for edge-cases and things that are not 100 % intuitive.\\\nYou can either filter the interactions for certain expansions, or post a comma-separated list from which the site will try to filter for any relevant interactions.\\\nIf you want to see the full list of CSOs, you can visit the [CSO Database](/cso_overview).",
    "Learn more about the CSO and kingdom qualities on the about page.",
)


def build_interactions_filter_expansions(df: pd.DataFrame) -> pd.DataFrame:
    """Builds the filter for the interactions.
    df: pd.DataFrame: The interactions dataframe to filter"""
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        require_all = st.checkbox(
            "Require all CSOs",
            value=st.session_state.get("inter_require_all_exps", False),
            key="inter_require_all_exps",
            help="If checked, only interactions that include all CSOs provided here are shown.",
        )
    with cols[0]:
        relevant_expansions = [
            exp
            for exp in rk.get_cached_expansions()
            if exp in df["exp_1"].unique() or exp in df["exp_2"].unique()
        ]
        expansions = st.multiselect(
            "Expansions",
            relevant_expansions,
            default=st.session_state.get("inter_expansion_filter", []),
            key="inter_expansion_filter",
            help="Filter for interactions from the selected expansions. If left empty, all expansions are included.",
            placeholder="Select expansions to filter for",
        )
    if len(expansions) > 0:
        if require_all:
            df = df[df["exp_1"].isin(expansions) & df["exp_2"].isin(expansions)]
        else:
            df = df[df["exp_1"].isin(expansions) | df["exp_2"].isin(expansions)]
    return df


def build_interactions_filter_other(df: pd.DataFrame) -> pd.DataFrame:
    """Builds the filter for the interactions.
    df: pd.DataFrame: The interactions dataframe to filter"""
    st.write("Here you might apply additional filters to the interactions.")
    exclude_ways = st.checkbox(
        "Exclude Ways",
        value=st.session_state.get("inter_exclude_ways", False),
        key="inter_exclude_ways",
        help="Exclude interactions that include Ways, as most of these are generic.",
    )
    if exclude_ways:
        df = df[~df.index.str.contains("way_of_the_")]
    exclude_first_edition = st.checkbox(
        "Exclude 1E CSOs",
        value=st.session_state.get("inter_exclude_first_edition", True),
        key="inter_exclude_first_edition",
        help="Exclude interactions revolving around CSOs from first editions.",
    )
    if exclude_first_edition:
        df = df[~df["exp_1"].str.contains("1E") & ~df["exp_2"].str.contains("1E")]
    return df


def build_interactions_filter_for_csos(df: pd.DataFrame) -> pd.DataFrame:
    """Builds the filter for the interactions for a given list of csos.
    We pretend it to be a kingdom as we can easily sanitize it that way.
    df: pd.DataFrame: The interactions dataframe to filter"""
    cols = st.columns([0.8, 0.2])
    with cols[1]:
        require_all = st.checkbox(
            "Require all CSOs",
            value=st.session_state.get("inter_require_all_csos", True),
            key="inter_require_all_csos",
            help="If checked, only interactions that include all CSOs provided here are shown (unless you only input one).",
        )
    with cols[0]:
        logic = "AND" if require_all else "OR"
        kingdom_input = st.text_input(
            f"Enter CSOs you want the interactions to be filtered for with a logical {logic}.",
            value=st.session_state.get("inter_cso_filtering_input", ""),
            help="Enter a kingdom string to filter for interactions. The kingdom string should be formatted as a comma-separated list of CSO names.",
            key="inter_cso_filtering_input",
            placeholder="e.g. Siren, Sailor, Stonemason, Destrier, ...",
        )
    try:
        if kingdom_input != "":
            kingdom = rk.Kingdom.from_dombot_csv_string(
                kingdom_input, add_invalidity_notes=False
            )
        else:
            kingdom = rk.Kingdom(cards=[])
    except ValueError:
        kingdom = rk.Kingdom(
            cards=[], notes="Invalid kingdom input. Please check the format."
        )

    if kingdom.notes != "" and "['']" not in kingdom.notes:
        notes = kingdom.notes.replace("\n", "<br>").removesuffix("<br>")
        red_background_message = f"""
        <div style='background-color: #ffcccc; padding: 10px; border-radius: 5px;'>
            <p style='color: black; font-size: 16px;'>{notes}</p>
        </div>
        """
        st.write(red_background_message, unsafe_allow_html=True)
    if kingdom.is_empty:
        return df
    if require_all and len(kingdom) > 1:
        df = df.loc[kingdom.get_interactions().index]
    else:
        objs = kingdom.full_kingdom_df.index.tolist()
        df = df[df.index.str.contains("|".join(objs))]
    return df


def _get_tab_names(static: bool) -> list[str]:
    """Returns the tab names for the interactions filter."""
    # TODO: Because of the way streamlit works, we currently cannot set the tab names dynamically unfortunately.
    if static:
        return ["CSO Filter", "Expansion Filter", "Other Filter"]
    first_symbol = (
        " 🔍"
        if st.session_state.get("inter_cso_filtering_input", "").strip("") != ""
        else ""
    )
    second_symbol = (
        " 🔍" if st.session_state.get("inter_expansion_filter", []) != [] else ""
    )
    third_symbol = (
        " 🔍"
        if st.session_state.get("inter_exclude_ways", False)
        or st.session_state.get("inter_exclude_first_edition", True)
        else ""
    )
    return [
        f"By CSO list{first_symbol}",
        f"By expansions{second_symbol}",
        f"Other filters{third_symbol}",
    ]


def _reset_all_filters():
    st.session_state["inter_cso_filtering_input"] = ""
    st.session_state["inter_expansion_filter"] = []
    st.session_state["inter_require_all_csos"] = False
    st.session_state["inter_exclude_ways"] = False
    st.session_state["inter_require_all_exps"] = False
    st.session_state["inter_exclude_first_edition"] = True


with st.container(border=True):
    with st.container():
        cols = st.columns([0.8, 0.2])
    with cols[1]:
        if st.button("Reset Filters", use_container_width=True):
            _reset_all_filters()
            st.rerun()
    tabs = st.tabs(_get_tab_names(static=True))
    with tabs[0]:
        INTERACTIONS = build_interactions_filter_for_csos(INTERACTIONS)
    with tabs[1]:
        INTERACTIONS = build_interactions_filter_expansions(INTERACTIONS)
    with tabs[2]:
        INTERACTIONS = build_interactions_filter_other(INTERACTIONS)
    with cols[0]:
        st.write(
            f"#### Filtering for {len(INTERACTIONS)}/{len(get_interactions())} available interactions between Card-Shaped Objects (CSOs)."
        )


def display_interactions_df(df: pd.DataFrame):
    """Displays the interactions DataFrame"""
    col_config = {
        "img_1": st.column_config.ImageColumn("Img 1"),
        "img_2": st.column_config.ImageColumn("Img 2"),
        "exp_img_1": st.column_config.ImageColumn("Exp 1"),
        "exp_img_2": st.column_config.ImageColumn("Exp 2"),
        "Rule": st.column_config.TextColumn("Interaction"),
    }
    st.dataframe(
        df,
        hide_index=True,
        column_config=col_config,
        column_order=[
            "CSO 1",
            "CSO 2",
            "Rule",
            "exp_img_1",
            "exp_img_2",
            "img_1",
            "img_2",
        ],
    )


display_interactions_df(INTERACTIONS)

st.info(
    "Hint: You can also sort by expansion in the expansion column.\\\nNote that the [Kingdom Oracle](/oracle) and the [Randomizer](randomizer) will also display all relevant interactions for any given kingdom."
)

st.write(
    """### Additional Information
         
These interactions are meant to cover finicky rules interactions that might not be immediately obvious. The project was initiated by `nave` on the Dominion Discord.

The following general interactions are omitted here:

- Basic strategy: The typical Village-Smithy-like interactions are omitted.
- Two-CSO combos: Any powerful two-CSO combos like Lurker/Hunting Grounds, Collection/Stampede, Beggar/Guildhall, etc., are omitted here as this tool's intent is to cover shady rules interactions, and not strategies.
- Shadows and Ways: Speaking of shady; while Shadow cards can be played as Ways even from your deck, I decided to omit these interactions.

**Disclaimer**: The interactions have been gathered with the assumption that those using it have a base knowledge of the rules of Dominion. 

**Contribution**: If you have any suggestions for interactions that are not covered here, feel free to visit the `#rules-lookup-project` channel on the [Dominion Discord](https://discord.gg/dominiongame)."""
)
