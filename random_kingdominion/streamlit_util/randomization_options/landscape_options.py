import streamlit as st

from ..randomizer_util import load_config

_LANDSCAPE_LIST = ["Event", "Landmark", "Project", "Trait", "Way"]


def _build_landscape_overview():
    landscape_range = st.session_state.get("landscape range", (0, 2))
    landscape_text = "<b>Number Of Landscapes</b><br>"
    if landscape_range[0] == landscape_range[1]:
        landscape_text += f"Exactly {landscape_range[0]}"
    else:
        landscape_text += f"Between {landscape_range[0]} and {landscape_range[1]}"
    landscape_text += " landscapes"
    if landscape_range[0] > 0:
        landscape_text += " [might not work without expansions with landscapes]"
    landscape_text += "."
    included_types = st.session_state.get("allowed_landscape_types", [])
    exclude_text = "<b>Allowed Landscape Types</b><br>"
    if len(included_types) == 0:
        exclude_text += "Landscapes disabled."
    else:
        exclude_text += ", ".join(included_types)
    note_text = "** Allies and Prophecies are not affected here."
    # note_text = f'<div style="font-size: 8px;">{note_text}</div>'
    with st.expander("🖼️Selected Landscape Options**", expanded=True):
        if len(included_types) != 0:
            st.write(landscape_text, unsafe_allow_html=True)
        st.write(exclude_text, unsafe_allow_html=True)
        st.info(note_text)


@st.fragment
def build_landscape_option_selection():
    config = load_config()
    default_min = config.getint("General", "min_num_landscapes", fallback=0)
    default_max = config.getint("General", "max_num_landscapes", fallback=2)
    st.slider(
        "Allowed number of landscapes (other than Allies and Prophecies, 1 Way max)",
        0,
        4,
        (default_min, default_max),
        key="landscape range",
    )
    st.write("Here you may allow/disable certain landscape types.")
    st.info(
        "To disable Allies or Prophecies, put Liaisons/Omens in the excluded Mechanics."
    )

    type_default = config.getlist("Landscapes", "allowed_landscape_types")
    incl = st.segmented_control(
        "Allowed landscape types",
        options=_LANDSCAPE_LIST,
        format_func=lambda x: x + "s",
        selection_mode="multi",
        default=type_default,
        key="allowed_landscape_types",
        # placeholder="Select allowed landscape types",
    )
    excluded = [x for x in _LANDSCAPE_LIST if x not in incl]
    if len(incl) == 0:
        st.warning(
            "No landscape types selected, you might only roll Allies and Prophecies."
        )
    elif len(excluded) > 0:
        st.info(f"Excluded: {'s, '.join(excluded)}s")
    else:
        st.info("All landscape types allowed.")
    st.write(
        "In the future, I plan to add the option to force certain landscapes for each slot, and maybe differentiate the events by expansion."
    )
    with st.sidebar:
        _build_landscape_overview()
