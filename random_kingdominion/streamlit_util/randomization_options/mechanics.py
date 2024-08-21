import streamlit as st

from ...constants import CARD_TYPES_AVAILABLE
from ..randomizer_util import load_config


def _build_colony_select():
    with st.expander("Colony and Platinum", expanded=False):
        st.write(
            """As per the rules, the probability of including Colony/Platinum should be proportional to how many Prosperity cards are used. If you don't want this, you can set the probability yourself here (even applies if Prosperity isn't among the enabled expansions)."""
        )
        cols = st.columns(2)
    with cols[0]:
        st.checkbox(
            "Use Prosperity for probability",
            value=load_config().getboolean(
                "Specialization", "use_prosperity_for_colony", fallback=False
            ),
            key="use_prosperity_for_colony",
            help="If enabled, the probability of including Colony/Platinum will be proportional to the number of Prosperity cards used.",
        )
    with cols[1]:
        st.slider(
            "Custom Colony/Platinum probability",
            0.0,
            1.0,
            value=load_config().getfloat(
                "Specialization", "colony_probability", fallback=0.0
            ),
            key="colony_probability",
            help="Set the probability of including Colony/Platinum in the kingdom.",
            disabled=st.session_state.get("use_prosperity_for_colony", False),
        )


def _build_shelter_select():
    with st.expander("Shelters", expanded=False):
        st.write(
            """As per the rules, the probability of including Shelters should be proportional to how many Dark Ages cards are used. If you don't want this, you can set the probability yourself here (even applies if Dark Ages isn't among the enabled expansions)."""
        )
        cols = st.columns(2)
    with cols[0]:
        st.checkbox(
            "Use Dark Ages for probability",
            value=load_config().getboolean(
                "Specialization", "use_dark_ages_for_shelters", fallback=False
            ),
            key="use_dark_ages_for_shelters",
            help="If enabled, the probability of including Shelters will be proportional to the number of Dark Ages cards used.",
        )
    with cols[1]:
        st.slider(
            "Custom Shelter probability",
            0.0,
            1.0,
            value=load_config().getfloat(
                "Specialization", "shelter_probability", fallback=0.0
            ),
            key="shelter_probability",
            help="Set the probability of including Shelters in the kingdom.",
            disabled=st.session_state.get("use_dark_ages_for_shelters", False),
        )


@st.fragment
def build_mechanics_options():
    st.write(
        "Select certain card types <s>or mechanics</s> you want to be excluded from <s>or included in</s> your kingdoms.\\\nYou can e.g. disable Allies or Prophecies by excluding Liaisons or Omens, and likewise Boons or Hexes by excluding Fate or Doom cards.\\\nNote that Looters are cards that deal with Ruins and not the ones providing Loot.\\\nExcluding Attacks is not the same as disallowing the attack quality as this obviously doesn't remove indirect attacks that don't share the type.",
        unsafe_allow_html=True,
    )
    excluded_types = load_config().getlist("Specialization", "excluded_card_types")
    st.multiselect(
        "Excluded card types",
        CARD_TYPES_AVAILABLE,
        default=excluded_types,
        key="excluded_card_types",
        placeholder="Choose card types to exclude",
        help="Select the types of cards you want to exclude from the randomization.",
    )
    _build_colony_select()
    _build_shelter_select()

    st.info(
        """**Force Mechanics into the kingdom**\n
*Forcing certain non-obvious mechanics (e.g. CSOs with cost reduction or extra-turn enablers) is not yet implemented, but on my to-do list. Stay tuned for updates!*"""
    )
    # TODO: Implement mechanic preferences
