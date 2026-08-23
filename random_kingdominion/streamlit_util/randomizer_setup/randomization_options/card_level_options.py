import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.grid import grid

from ....utils import get_expansion_icon_path
from ...constants import ALL_EXPANSIONS, NUM_EXPS
from ...image_util import st_build_expansion_icon_with_tt
from ...image_util.image_handling import img_to_bytes
from ..randomizer_util import get_or_initialize_key, load_config


@st.fragment
def build_card_level_selection():
    config = load_config()
    default = config.getlist("Specialization", "excluded_card_levels")
    default = [int(x) for x in default] if default else []
    inverted = [i for i in range(11) if i not in default]
    st.text(
        "Select card levels to allow in the randomization, as provided by dominion.games. Thanks to tracer for providing the data!\nA card level of 0 includes all CSOs that haven't been assigned a level, which includes 1st Edition cards. Thus, if you only select 0, be aware that you'll need to select 1E expansions. If you only select 1, the Base game must be active."
    )
    st.segmented_control(
        "Allowed card levels",
        options=list(range(11)),
        default=inverted,
        selection_mode="multi",
        key="allowed_card_levels",
        help="Select card levels to allow in the randomization. Card levels are used to indicate the complexity of cards, curated by DXV and available on the dominion.games client.",
        width="stretch",
    )
    c1, c2 = st.columns(2)
    c1.button(
        "Deselect All",
        on_click=lambda: st.session_state.update({"allowed_card_levels": []}),
    )
    c2.button(
        "Select All",
        on_click=lambda: st.session_state.update(
            {"allowed_card_levels": list(range(11))}
        ),
    )
