"""The Streamlit layer of the app: widgets, page setup and cached data loaders.

Pages import it as ``import random_kingdominion.streamlit_util as rks``; ``__all__``
holds the names used that way. Importing it needs Streamlit, while the core
(``random_kingdominion``) doesn't.
"""

from .log_filter import remove_streamlit_logs

# Before the imports below, whose module-level `st.cache_data` calls log warnings
# outside of `streamlit run`
remove_streamlit_logs()

from .about_page_setup import (
    st_build_cso_description_tabs,
    st_build_introduction_video_showcase,
    st_build_more_info_tabs,
    st_build_site_desc_tabs,
)
from .combo_and_inter_setup import (
    st_build_combo_page_content,
    st_build_inter_page_content,
)
from .common_widgets import display_stylysed_cso_df, get_col_config
from .constants import (
    ALL_CACHED_CSOS,
    ST_ICONS,
    count_cso_occurrences,
    get_cached_expansions,
)
from .helpers import build_page_header, get_cached_unique_types
from .kingdom_oracle_setup import (
    st_build_existing_kingdom_select,
    st_build_oracle_kingdom_display,
    st_build_oracle_kingdom_input_display,
)
from .quality_display import build_quality_page, get_quality_page_navigation
from .quiz_setup import st_build_full_quiz_display
from .randomizer_setup import (
    randomize_new_kingdom,
    st_build_current_randomized_kingdom_display,
    st_build_full_randomization_options,
)

__all__ = [
    # Data
    "ALL_CACHED_CSOS",
    "ST_ICONS",
    "count_cso_occurrences",
    "get_cached_expansions",
    "get_cached_unique_types",
    # Page setup
    "build_page_header",
    "build_quality_page",
    "get_quality_page_navigation",
    # About
    "st_build_cso_description_tabs",
    "st_build_introduction_video_showcase",
    "st_build_more_info_tabs",
    "st_build_site_desc_tabs",
    # Combos and interactions
    "st_build_combo_page_content",
    "st_build_inter_page_content",
    # Card database
    "display_stylysed_cso_df",
    "get_col_config",
    # Kingdom oracle
    "st_build_existing_kingdom_select",
    "st_build_oracle_kingdom_display",
    "st_build_oracle_kingdom_input_display",
    # Quiz
    "st_build_full_quiz_display",
    # Randomizer
    "randomize_new_kingdom",
    "st_build_current_randomized_kingdom_display",
    "st_build_full_randomization_options",
]
