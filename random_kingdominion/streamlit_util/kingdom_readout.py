import streamlit as st

from ..kingdom import Kingdom


def build_kingdom_text_input(
    key="kingdom_input", description_text: str | None = None
) -> Kingdom:
    """Build the input text to enter a kingdom."""
    if description_text is None:
        description_text = "Enter a (partial) kingdom in the DomBot-typical-csv Format 'card1, card2, ..., cardN'. You may specify the bane card with 'Young Witch: card' or 'Young Witch(Card)'."
    kingdom_input = st.text_input(
        description_text,
        value=st.session_state.get(key, ""),
        key=key,
        placeholder="e.g. Chapel, Village, Young Witch (Moat), Pious (Poet), Swindler, Growth, ...",
    )
    try:
        if kingdom_input != "":
            kingdom = Kingdom.from_dombot_csv_string(kingdom_input)
        else:
            kingdom = Kingdom([])
    except ValueError:
        kingdom = Kingdom([], notes="Invalid kingdom input. Please check the format.")
    kingdom.name = st.session_state.get("kingdom_name", "")
    return kingdom
