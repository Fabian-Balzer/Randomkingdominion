import streamlit as st

from ...kingdom import Kingdom, KingdomRandomizer
from ...utils import get_cso_name
from .randomizer_util import save_config


def reroll_selected_csos():
    """Reroll the CSOs currently selected."""
    if "CSOsToReroll" not in st.session_state:
        return
    config = save_config()
    randomizer = KingdomRandomizer(config)
    kingdom = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    cso_to_reroll = [
        k for k, do_reroll in st.session_state["CSOsToReroll"].items() if do_reroll
    ]
    for cso_name in cso_to_reroll:
        name = get_cso_name(cso_name)
        st.toast(f"🔁Rerolling {name}...", duration=7)
        kingdom = randomizer.reroll_single_cso(kingdom, cso_name)
    st.session_state["randomized_kingdom"] = kingdom.get_dombot_csv_string()


def reroll_cso(cso_name: str):
    """Reroll a single card or landscape in the kingdom."""
    config = save_config()
    name = get_cso_name(cso_name)
    st.toast(f"🔁Rerolling {name}...", duration=7)
    randomizer = KingdomRandomizer(config)

    kingdom = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    new_kingdom = randomizer.reroll_single_cso(kingdom, cso_name)
    st.session_state["randomized_kingdom"] = new_kingdom.get_dombot_csv_string()
