import streamlit as st

from ..constants import ST_ICONS


def _get_randomizer_desc_text() -> str:
    randomizer_desc_text = f"""This Dominion Kingdom Randomizer is a tool to quickly generate a random kingdom for your Dominion games with a few clicks. It allows for a lot of customization, including the ability to exclude or require specific cards, landscapes, or card types. In detail, these are the options you can set:

- {ST_ICONS["expansions"]} **Expansions**:\\
You can select which expansions you want to include in the randomization, and also limit the randomization to a maximum amount of expansions you want to occur.
- {ST_ICONS["mechanics"]} **Mechanics**:\\
You can currently exclude certain card Types, such as Attack, Duration, or Reserve cards. In the future, you might be able to force the inclusion of certain mechanics or themes (depending on whether I get my hands on the #two-themes tournament data, or alternatively find the time to categorize them myself :D). This section also contains customization options for the inclusion of Colony/Platinum and Shelters.
- {ST_ICONS["landscapes"]} **Landscape options**:\\
You can choose the amount of allowed landscapes and specify the allowed landscape types.
- {ST_ICONS["cso_qualities"]} **Engine Qualities**:\\
This part is based on the idea of CSO qualities (see the description above).\\
The randomizer then allows to exclude or require specific qualities, which can be useful if you want to play a kingdom with a certain focus.\\
For this task, upon each step of randomization, the randomizer will pick a random quality that in total is not fulfilled by the partially randomized kingdom, and limit the subset of remaining CSOs to those that fulfill this quality. This means that if you're requesting a kingdom with all qualities at the highest level, it can occur that they aren't perfectly fulfilled.
- {ST_ICONS["bans"]} **Banning, Forcing, Liking or Disliking CSOs**:\\
You can specify CSOs that you want to exclude, require, like, or dislike. The randomizer will then try to include or exclude these CSOs to its best abilities, where the liked and disliked CSOs are assigned weights relative to the other CSOs. In the future, I aim to implement pasting CSO names here - sorry that you currently have to do this manually!"""
    return randomizer_desc_text


def _get_oracle_desc_text() -> str:
    oracle_desc_text = f"""The Kingdom Oracle allows you to easily input a kingdom to visualize its engine qualities derived from the included CSOs, and to take a more detailed look on its cards. The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form, and can also provide information on special combos or rules interactions that are present in the kingdom.

### How to use

Just insert the names of the 10 kingdom cards (and optionally any landscapes) into the text box, separated by commas, and hit Enter. The resulting plots and information will then be displayed below.

### Displaying existing kingdoms

In addition to letting you input your own kingdoms, the Oracle can also display existing kingdoms from various sources:

- The officially recommended kingdoms
- The Daily Dominion kingdoms from the TGG client
- The Reddit Kingdom of the Week kingdoms
- And some recommendations by myself.

You can select these kingdoms from a simple dropdown menu, and even filter them via several fun criteria."""
    return oracle_desc_text


def _get_cso_database_desc_text() -> str:
    cso_db_desc_text = f"""The CSO Database page provides an overview of all CSOs available in the game of Dominion, and the qualities I have associated with them. You can filter and sort the CSOs by their properties, qualities, and other fun stuff."""
    return cso_db_desc_text


def _get_cso_interactions_desc_text() -> str:
    cso_inter_desc_text = f"""The CSO Interactions page allows you to explore interactions between CSOs that might catch you off-guard rules-wise. The project was initiated on discord by `nave`; while there are lot of different combinations, these do not cover the straight-forward interactions like your typical Village/Smithy. The interactions have been gathered with the assumption that those reading them have a base knowledge of the rules of Dominion and are looking for edge-cases and things that might not be 100 % intuitive.

### Contribution

Please contact me via [discord](https://discord.gg/dominiongame) (e.g. in the #rules-lookup-project channel) or GitHub if you have any suggestions for interactions that are not covered here but you think would fit in."""
    return cso_inter_desc_text


def _get_cso_combos_desc_text() -> str:
    cso_combos_desc_text = f"""The CSO Combo page allows you to explore pairwise CSO synergies, rushes, counters, and more.

### Contribution

Please contact me via [discord](https://discord.gg/dominiongame) (e.g. in the #rules-lookup-project channel) or GitHub if you have any suggestions for interactions that are not covered here but you think would fit in."""
    return cso_combos_desc_text


def st_build_site_desc_tabs():
    randomizer_desc_text = _get_randomizer_desc_text()
    oracle_text = _get_oracle_desc_text()
    cso_db_text = _get_cso_database_desc_text()
    cso_interactions_text = _get_cso_interactions_desc_text()
    cso_combos_text = _get_cso_combos_desc_text()
    tab_names = [
        f"{ST_ICONS['randomizer']} Randomizer",
        f"{ST_ICONS['oracle']} Kingdom Oracle",
        f"{ST_ICONS['cso_overview']} CSO Database",
        f"{ST_ICONS['interactions']} CSO Interactions",
        f"{ST_ICONS['combos']} CSO Combos",
    ]
    tabs = st.tabs(tab_names)

    with tabs[0]:
        st.write(randomizer_desc_text)

    with tabs[1]:
        st.write(oracle_text)

    with tabs[2]:
        st.write(cso_db_text)

    with tabs[3]:
        st.write(cso_interactions_text)

    with tabs[4]:
        st.write(cso_combos_text)
