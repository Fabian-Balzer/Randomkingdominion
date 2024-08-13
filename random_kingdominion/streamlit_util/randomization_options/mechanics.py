import streamlit as st

from ...constants import CARD_TYPES_AVAILABLE
from ..randomizer_util import load_config


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
    st.write(
        """**Force Mechanics into the kingdom**\\\n
             Forcing certain mechanics is not yet implemented, but on my to-do list. Stay tuned for updates!"""
    )
    # TODO: Implement mechanic preferences
