import streamlit as st

from ...utils import get_changelog
from ..constants import ST_ICONS


def _get_future_dev_text() -> str:
    future_development_text = """
In the future, the following features might find their way into the randomizer:
- **Cookies**:
    - Save your preferences for future visits, and maybe download the configuration as well as the generated kingdoms.
- **Themes**:
  - Allow for the inclusion of certain themes or mechanics, such as "extra turn enablers" or "cost reducers".
- **Pastable CSO names**:
    - Allow for pasting CSO names to exclude, require, like, or dislike them, or even starting a kingdom with a partial DomBot string.
- **Extra component limitations**:
    - Some cards require extra setup or components, such as tokens or mats. Maybe I'll add a feature to limit them (relevant for IRL play).
- **Kingdom history**:
    - Save the kingdoms you've generated to look at them later.

### Already implemented

I'm proud to say that the following features have already been implemented recently:

- ✅ **Exploring two-card combos**:
    - On the combos page, you can explore pairwise synergies, rushes, counters, and more between CSOs.
- ✅ **Exploring rules interactions**:
    - On the interactions page, you can explore pairwise rules interactions between CSOs that might not be immediately obvious.
- ✅ **Kingdom analysis of recommended sets**:
    - Recommended (and TGG Daily) sets can be loaded into the kingdom oracle for analysis.
"""
    return future_development_text


def _build_changelog():
    st.text(
        "Here you can find a rough changelog of this project, listing notable changes and updates. You may find them to be on the more technical side, but oh well, this is mainly for transparency purposes."
    )
    log = get_changelog()
    close_all = st.checkbox(
        "Close all versions",
        value=False,
        help="If checked, all version changelogs will be collapsed by default.",
    )
    for version, changes in log.items():
        icon = "📦" if version.split()[0].endswith(".0") else "🛠️"
        exp = st.expander(f"Version {version}", expanded=not close_all, icon=icon)
        exp.write("- " + "\n- ".join(changes))


def _get_feedback_text() -> str:
    return """
I hope you enjoy this randomizer and find it useful for your Dominion games.\\
If you have any feedback (especially concerning my quality assessments, they are certainly arguable), suggestions, or bug reports, feel free to contact me via the [GitHub repository](https://github.com/Fabian-Balzer/Randomkingdominion) or on the dominion discord."""


def _get_links_text() -> str:
    return """
Here are some links to relevant Dominion pages:

- [Dominion Strategy Wiki](https://wiki.dominionstrategy.com/)
- [Dominion Online Implementation](https://dominion.games/)
- [Dominion by Temple Gates Games](https://store.steampowered.com/app/1131620/Dominion/)
- [The Dominion Discord](https://discord.gg/dominiongame)
- [The Dominion Subreddit](https://www.reddit.com/r/dominion/)
- [Kieran Millar's Extra Recommended Sets](https://kieranmillar.github.io/extra-recommended-sets/)"""


def st_build_more_info_tabs():
    future_development_text = _get_future_dev_text()
    feedback_text = _get_feedback_text()

    more_tab_names = [
        f"{ST_ICONS['future_development']} Future Development",
        f"{ST_ICONS['changelog']} Changelog",
        f"{ST_ICONS['feedback']} Feedback",
        f"{ST_ICONS['links']} Links",
    ]
    more_tabs = st.tabs(more_tab_names)
    with more_tabs[0]:
        st.write(future_development_text)

    with more_tabs[1]:
        _build_changelog()

    with more_tabs[2]:
        st.write(feedback_text, unsafe_allow_html=True)
    with more_tabs[3]:
        st.write(_get_links_text(), unsafe_allow_html=True)
