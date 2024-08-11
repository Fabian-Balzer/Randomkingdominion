import streamlit as st
from ..randomizer_util import load_config
from ...constants import CARD_TYPES_AVAILABLE


@st.fragment
def build_mechanics_options():
    st.write(
        "Select certain card types or mechanics you want to be excluded or included in your kingdoms.\\\nYou can e.g. disable Allies or Prophecies by excluding Liaisons or Omens, and likewise Boons or Hexes by excluding Fate or Doom cards.\\\nNote that Looters are cards that deal with Ruins and not the ones providing Loot.\\\nExcluding Attacks is not the same as disallowing the attack quality as this obviously doesn't remove indirect attacks that don't share the type."
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
    # TODO: Implement mechanic preferences
