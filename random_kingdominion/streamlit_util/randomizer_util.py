import streamlit as st

from ..constants import QUALITIES_AVAILABLE
from ..kingdom import Kingdom, KingdomRandomizer, sanitize_cso_list
from ..utils import CustomConfigParser
from .constants import ALL_EXPANSIONS, COOKIES, LIKE_BAN_OPTIONS


def load_config():
    """Load the config from the session state."""
    if not COOKIES.get("cookie_consent") and "config" not in st.session_state:
        st.session_state["config"] = CustomConfigParser(load_default=True).to_json()
    elif "config" not in st.session_state:
        if saved_config := COOKIES.get("config"):
            st.session_state["config"] = saved_config
        else:
            st.session_state["config"] = CustomConfigParser(load_default=True).to_json()
    return CustomConfigParser.from_json(st.session_state["config"])


def save_config() -> CustomConfigParser:
    """Read the session state values into the config and save it to the session state."""
    config = load_config()
    config.set(
        "General", "max_num_expansions", str(st.session_state["max_num_expansions"])
    )
    config.set_expansions(
        [exp for exp in ALL_EXPANSIONS if st.session_state[f"{exp} enabled"]]
    )
    config.set(
        "General", "min_num_landscapes", str(st.session_state["landscape range"][0])
    )
    config.set(
        "General", "max_num_landscapes", str(st.session_state["landscape range"][1])
    )
    config.setlist(
        "General",
        "allowed_landscape_types",
        st.session_state["allowed_landscape_types"],
    )

    config.set(
        "General",
        "allow_required_csos_of_other_exps",
        str(st.session_state["allow_required_csos_of_other_exps"]),
    )

    for option in LIKE_BAN_OPTIONS:
        config.setlist(
            "General",
            f"{option.lower()}_csos",
            sanitize_cso_list(st.session_state[f"{option.lower()}_csos"]),
        )
    config.set("General", "like_factor", str(st.session_state["like_factor"]))
    config.set("General", "dislike_factor", str(st.session_state["dislike_factor"]))
    config.setlist(
        "Specialization", "excluded_card_types", st.session_state["excluded_card_types"]
    )

    for quality in QUALITIES_AVAILABLE:
        config.set_requested_quality(quality, st.session_state[f"{quality} count"])
        config.set_forbidden_quality(
            quality, st.session_state[f"disable {quality} selection"]
        )
    if COOKIES.get("cookie_consent"):
        COOKIES.set("config", config.to_json())
    st.session_state["config"] = config.to_json()
    return config


def randomize_kingdom():
    """Randomize a kingdom given the current session state."""
    config = save_config()
    randomizer = KingdomRandomizer(config)
    randomized_kingdom = randomizer.randomize_new_kingdom()
    st.session_state["randomized_kingdom"] = randomized_kingdom.get_dombot_csv_string()


def reroll_selected_csos():
    """Reroll the CSOs currently selected."""
    if "CSOsToReroll" not in st.session_state:
        return
    config = save_config()
    randomizer = KingdomRandomizer(config)
    kingdom = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    for cso_name, do_reroll in st.session_state["CSOsToReroll"].items():
        if do_reroll:
            kingdom = randomizer.reroll_single_cso(kingdom, cso_name)
    st.session_state["randomized_kingdom"] = kingdom.get_dombot_csv_string()


def reroll_cso(cso_name: str):
    """Reroll a single card or landscape in the kingdom."""
    config = save_config()
    randomizer = KingdomRandomizer(config)
    kingdom = Kingdom.from_dombot_csv_string(st.session_state["randomized_kingdom"])
    new_kingdom = randomizer.reroll_single_cso(kingdom, cso_name)
    st.session_state["randomized_kingdom"] = new_kingdom.get_dombot_csv_string()
