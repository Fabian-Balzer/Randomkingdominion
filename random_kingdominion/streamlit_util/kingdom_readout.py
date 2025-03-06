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
        st.button(
            "",
            "clearinput",
            help="Clear input",
            on_click=(lambda: _clear_text(key)),
            icon="❌",
            disabled=st.session_state.get(key, "") == "",
        )
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
                kingdom_input, add_invalidity_notes=full_kingdom_expected
            )
        else:
            kingdom = Kingdom([])
    except ValueError:
        kingdom = Kingdom([], notes="Invalid kingdom input. Please check the format.")
    # if full_kingdom_expected:
    #     kingdom.name = st.session_state.get("kingdom_name", "")
    #     kingdom.notes = st.session_state.get("kingdom_notes", "")
    return kingdom


def build_kingdom_input_warning(k: Kingdom, ref_to_randomizer=False):
    """Build a warning if the kingdom input is invalid."""

    if k.notes != "" and "['']" not in k.notes and not k.notes.startswith("{"):
        notes = k.notes.replace("\n", "<br>").removesuffix("<br>")
        red_background_message = f"""
        <div style='background-color: #ffcccc; padding: 8px; border-radius: 5px;'>
            <p style='color: black; font-size: 16px;'>{notes}</p>
        </div>
        """
        if ref_to_randomizer:
            extra = "Feel free to follow the link to the randomizer to complete the kingdom."
            extra = f"""
        <div style='background-color: #ffffcc; padding: 8px; border-radius: 5px;'>
            <p style='color: black; font-size: 16px;'>{extra}</p>
        </div>"""
            red_background_message += extra
        st.write(red_background_message, unsafe_allow_html=True)
