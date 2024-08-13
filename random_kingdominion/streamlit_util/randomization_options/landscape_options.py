import streamlit as st
from ..randomizer_util import load_config


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
    st.write(
        "Here you may allow/disable certain landscape types. To disable Allies or Prophecies, put Liaisons/Omens in the excluded Mechanics."
    )
    landscape_list = ["Event", "Landmark", "Project", "Trait", "Way"]
    type_default = config.getlist("Landscapes", "allowed_landscape_types")
    st.multiselect(
        "Allowed landscape types",
        landscape_list,
        default=type_default,
        key="allowed_landscape_types",
        placeholder="Select allowed landscape types",
    )
    st.write(
        "In the future, I plan to add the option to force certain landscapes for each slot, and maybe differentiate the events by expansion."
    )
