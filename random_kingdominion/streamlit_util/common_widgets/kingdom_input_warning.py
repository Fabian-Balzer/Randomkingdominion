import streamlit as st
from ...kingdom import Kingdom


def _get_invalidity_issues_text(k: Kingdom) -> str:
    warn_text = k.notes
    if not k.is_valid:
        warn_text += "\nThis kingdom is invalid for the following reasons:\n- "
        warn_text += "\n- ".join(
            [f"{r.name}: {r.get_description()}" for r in k.invalidity_reasons]
        )
    return warn_text


def st_build_kingdom_input_warning(k: Kingdom, ref_to_randomizer=False):
    """Build a warning if the kingdom input is invalid."""

    if (
        k.notes != "" and not k.notes.startswith("{") or not k.is_valid
    ) and ref_to_randomizer:
        amount_wrong = k.notes.count(", ") + 1 if k.notes != "" else 0
        if not k.is_valid:
            amount_wrong += len(k.invalidity_reasons)
        # TODO: As soon as streamlit provides a separate key for the expander,
        # we should try to use it.
        # Currently, whenever the number in the label changes, the expander is reset to its
        # default state, which is pretty annoying.
        pl_suffix = "s" if amount_wrong > 1 else ""
        expander_label = f"Incomplete kingdom input ({amount_wrong} issue{pl_suffix})"
        with st.expander(expander_label, expanded=True):
            st.warning(_get_invalidity_issues_text(k))
            if len(k) > 0:
                st.info(
                    "Feel free to follow the button to the randomizer to complete the kingdom."
                )
    elif k.notes != "" and not k.notes.startswith("{"):
        notes = k.notes.replace("\n", "<br>").removesuffix("<br>")
        red_background_message = f"""
        <div style='background-color: #ffcccc; padding: 2px; border-radius: 3px;'>
            <p style='color: black; font-size: 16px;'>{notes}</p>
        </div>
        """
        st.write(red_background_message, unsafe_allow_html=True)
