from typing import Literal

import streamlit as st

from ...kingdom import Kingdom


def _clear_text(key: str):
    st.session_state[key] = ""


def _build_clear_text_button(key: str):
    if st.button(
        "Clear\n",
        "clearinput",
        help="Clear input",
        type="primary",
        icon="❌",
        width="content",
    ):
        _clear_text(key)


def validate_kingdom_input(kingdom_input: str, check_validity=True) -> Kingdom:
    """Set the kingdom input in the session state."""
    try:
        if kingdom_input != "":
            kingdom = Kingdom.from_dombot_csv_string(
                kingdom_input, check_validity=check_validity
            )
            select = st.session_state.get("existing_selected_kingdom_str", "")
            if not kingdom.is_valid or kingdom_input != select:
                st.session_state["kingdom_name"] = kingdom.name
                st.session_state["kingdom_notes"] = kingdom.notes
                st.session_state["existing_selected_kingdom_str"] = ""
            elif select == kingdom_input:
                # In this case, we want to keep the name and notes from the
                # existing kingdom selection.
                kingdom.name = st.session_state.get("kingdom_name", "")
                kingdom.notes = st.session_state.get("kingdom_notes", "")
        else:
            kingdom = Kingdom([])
            st.session_state["kingdom_name"] = ""
            st.session_state["kingdom_notes"] = "No kingdom input."
    except ValueError:
        kingdom = Kingdom([], notes="Invalid kingdom input. Please check the format.")
    return kingdom


def st_build_kingdom_text_input(
    key: Literal["oracle_kingdom_input", "partial_kingdom_input"],
    initial_value: str = "",
    description_text: str | None = None,
):
    """Build the input text to enter a kingdom."""
    full_kingdom_expected = key == "oracle_kingdom_input"
    if description_text is None:
        description_text = "Enter a (partial) kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN'. You may specify the bane card with 'Young Witch: card' or 'Young Witch(Card)'."
    flex = st.container(
        horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"
    )
    with flex:
        input_container = st.container()
        _build_clear_text_button(key)
    with input_container:
        kingdom_input = st.text_input(
            description_text,
            value=initial_value,
            key=key,
            placeholder="e.g. Chapel, Village, Young Witch (Moat), Pious (Poet), Swindler, Growth, ...",
        )
    return validate_kingdom_input(kingdom_input, check_validity=full_kingdom_expected)
