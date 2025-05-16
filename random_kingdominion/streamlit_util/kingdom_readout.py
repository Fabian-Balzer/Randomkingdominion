import streamlit as st

from ..kingdom import Kingdom
from .randomizer_util import load_config


def _clear_text(key):
    st.session_state[key] = ""


def build_kingdom_text_input(
    key="kingdom_input", description_text: str | None = None
) -> Kingdom:
    """Build the input text to enter a kingdom."""
    full_kingdom_expected = key == "kingdom_input"
    config = load_config()
    if description_text is None:
        description_text = "Enter a (partial) kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN'. You may specify the bane card with 'Young Witch: card' or 'Young Witch(Card)'."
    cols = st.columns([0.9, 0.1])
    with cols[1]:
        st.text("\n")
        if st.button(
            "",
            "clearinput",
            help="Clear input",
            icon="❌",
            disabled=st.session_state.get(key, "") == "",
        ):
            _clear_text(key)
    with cols[0]:
        kingdom_input = st.text_input(
            description_text,
            value=config.get("General", key, fallback=""),
            key=key,
            placeholder="e.g. Chapel, Village, Young Witch (Moat), Pious (Poet), Swindler, Growth, ...",
        )
    try:
        if kingdom_input != "":
            kingdom = Kingdom.from_dombot_csv_string(
                kingdom_input, check_validity=full_kingdom_expected
            )
            if not kingdom.is_valid:
                st.session_state["kingdom_name"] = kingdom.name
                st.session_state["kingdom_notes"] = kingdom.notes
        else:
            kingdom = Kingdom([])
            st.session_state["kingdom_name"] = ""
            st.session_state["kingdom_notes"] = "No kingdom input."
    except ValueError:
        kingdom = Kingdom([], notes="Invalid kingdom input. Please check the format.")
    if full_kingdom_expected and kingdom.is_valid:
        kingdom.name = st.session_state.get("kingdom_name", "")
        kingdom.notes = st.session_state.get("kingdom_notes", "")
    return kingdom


def build_kingdom_input_warning(k: Kingdom, ref_to_randomizer=False):
    """Build a warning if the kingdom input is invalid."""

    if (k.notes != "" and not k.notes.startswith("{") or not k.is_valid) and ref_to_randomizer:
        amount_wrong = k.notes.count(", ") + 1 if k.notes != "" else 0
        if not k.is_valid:
            amount_wrong += len(k.invalidity_reasons)
        # TODO: As soon as streamlit provides a separate key for the expander,
        # we should try to use it.
        # Currently, whenever the number in the label changes, the expander is reset to its
        # default state, which is pretty annoying.
        expander_label = f"Incomplete kingdom input ({amount_wrong} issues)"
        with st.expander(expander_label, expanded=True):
            warn_text = k.notes
            if not k.is_valid:
                warn_text += "\nThis kingdom is invalid for the following reasons:\n- "
                warn_text += "\n- ".join([f"{r.name}: {r.get_description()}" for r in k.invalidity_reasons])
            st.warning(warn_text)
            
            st.info("Feel free to follow the link to the randomizer to complete the kingdom.")
    elif k.notes != "" and not k.notes.startswith("{"):
        notes = k.notes.replace("\n", "<br>").removesuffix("<br>")
        red_background_message = f"""
        <div style='background-color: #ffcccc; padding: 2px; border-radius: 3px;'>
            <p style='color: black; font-size: 16px;'>{notes}</p>
        </div>
        """
        st.write(red_background_message, unsafe_allow_html=True)
