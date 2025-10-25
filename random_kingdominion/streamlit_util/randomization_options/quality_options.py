import streamlit as st

from ...constants import QUALITIES_AVAILABLE, SPECIAL_QUAL_TYPES_AVAILABLE
from ...utils import CustomConfigParser
from ..quality_display import EMOJI_DICT, SHORT_DESCS, get_qual_image_html
from ..randomizer_util import load_config


def _toggle_all_qualities(value: bool, value_to_set_to: int | None = None):
    for quality in QUALITIES_AVAILABLE:
        st.session_state[f"forbid_{quality}"] = value
        if value_to_set_to is not None:
            st.session_state[f"requested_{quality}"] = value_to_set_to


def _build_qual_desc(qual: str):
    st.write(
        get_qual_image_html(qual, 30)
        + SHORT_DESCS[qual].replace(
            "...", " Set the options for cards that allow you to "
        ),
        unsafe_allow_html=True,
    )


def _build_qual_exclusion_checkbox(qual: str, config: CustomConfigParser):
    key = f"forbid_{qual}"
    default: bool = st.session_state.get(
        key, default=config.getboolean("Qualities", key, fallback=0)
    )
    st.checkbox(
        f"No {qual.capitalize()} quality",
        value=default,
        key=key,
        help=f"If enabled, the randomizer will exclude all cards with any {qual} quality.",
    )


def _build_qual_strength_slider(qual: str, config: CustomConfigParser):
    key = f"requested_{qual}"
    default = config.getint("Qualities", key, fallback=0)
    st.slider(
        f"Minimum {qual} quality",
        0,
        3,
        value=default,
        key=key,
        disabled=st.session_state[f"forbid_{qual}"],
        help=f"Select the minimum amount of {qual} quality you desire to have in the kingdom.",
    )


def _build_qual_type_exclusion_select(qual: str, config: CustomConfigParser):
    key = f"forbidden_{qual}_types"
    default = st.session_state.get(
        key, default=config.getlist("Qualities", key, fallback=[])
    )
    avail_types = SPECIAL_QUAL_TYPES_AVAILABLE[qual]
    st.multiselect(
        f"Excluded {qual} types",
        avail_types,
        default=default,
        key=key,
        help=f"Select the {qual} types you want to exclude from the randomization. These are: {', '.join(avail_types)}.",
    )


def _build_qual_row(qual: str):
    config = load_config()
    header = _get_qual_header(qual)
    with st.container(border=True):
        st.write(header)
        _build_qual_desc(qual)
        col_spec = [0.3, 0.2]
        if qual in SPECIAL_QUAL_TYPES_AVAILABLE:
            col_spec = [0.3, 0.4, 0.2]
        cols = st.columns(col_spec)
        with cols[-1]:
            _build_qual_exclusion_checkbox(qual, config)
        with cols[0]:
            _build_qual_strength_slider(qual, config)
        if not qual in SPECIAL_QUAL_TYPES_AVAILABLE:
            return
        with cols[-2]:
            _build_qual_type_exclusion_select(qual, config)


def _get_qual_header(qual: str):
    is_disabled = st.session_state.get(f"forbid_{qual}", False)
    is_requested = not is_disabled and st.session_state.get(f"requested_{qual}", 0) > 0
    has_excluded_types = (
        not is_disabled and len(st.session_state.get(f"forbidden_{qual}_types", [])) > 0
    )
    extra_str = ""
    if is_disabled:
        extra_str += " ❌"
    if is_requested:
        extra_str += " ✔️"
    if has_excluded_types:
        extra_str += "✖️"
    return f"{EMOJI_DICT[qual]} {qual.capitalize()}{extra_str}"


def _build_group_select_buttons():
    """The buttons in which all qualities can be reset at the same time"""
    with st.container(border=True):
        st.write(
            "Toggle things for all qualities. Individually selected excluded types are not affected."
        )
        cols = st.columns(3)
    with cols[0]:
        st.button(
            "Reset",
            on_click=lambda: _toggle_all_qualities(False, 0),
            use_container_width=True,
            help="Reset everything such that the randomization is not influenced.",
        )
    with cols[1]:
        st.button(
            "Enable all",
            on_click=lambda: _toggle_all_qualities(False, 2),
            use_container_width=True,
            help="Enable all qualities to be required for the randomized kingdom. This usually results in a kingdom suitable for engines.",
        )
    with cols[2]:
        st.button(
            "Exclude all",
            on_click=lambda: _toggle_all_qualities(True),
            use_container_width=True,
            help="Have the randomizer consider only CSOs that do not have any qualities.",
        )


@st.fragment
def build_quality_selection():
    st.write(
        "Select the minimum amount of a quality you desire to have in the kingdom, or exclude some completely.\\\nAlso lets you exclude certain types of qualities, allowing you to e.g. create kingdoms without + Buy but with other gain options, or kingdoms with Moat-likes as the only draw, etc.\\\nNote: The quality options are not mutually exclusive, but if you're too restrictive, you might end up with no kingdom at all."
    )
    with st.expander("Individual selection", expanded=False):
        _build_group_select_buttons()
        for qual in QUALITIES_AVAILABLE:
            _build_qual_row(qual)

    cols = st.columns(len(QUALITIES_AVAILABLE))
    for i, qual in enumerate(QUALITIES_AVAILABLE):
        with cols[i]:
            st.write(_get_qual_header(qual))
