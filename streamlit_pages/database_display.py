import re

import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk
from random_kingdominion.streamlit_util.constants import ST_ICONS

rk.build_page_header(
    "Dominion Card and Landscape Database",
    "On this page, you can filter and view the card database of all dominion Card-Shaped Objects (CSOs), and sort and filter them to hunt for whatever you might need, including my hand-curated CSO qualities described in the *about* page.",
    "Learn more about how the card qualities were devised.",
)

SELECTED_EXPANSIONS = []
with st.expander("Filtering options", expanded=False, icon="🔍"):
    filter_header_container = st.container()
    INVERT_MASK = st.checkbox(
        "❗Invert all filters",
        value=False,
        help="Invert all filters applied to the database (except for column filters).",
    )
    TABS = st.tabs(
        ["📃Text", "🗃️Expansions", "🔣Types", "💸Cost", "🔧Other", "💈Columns"]
    )
    with TABS[0]:
        text_search_options = {
            "CSO Name": "Name",
            "CSO Text": "Text",
            "CSO Types": "Types",
            "Quality Types": "Qualities",
            "Components": "Extra Components",
        }
        text_search_columns = st.multiselect(
            "Which columns to search in",
            options=list(text_search_options.keys()),
            default=["CSO Text"],
            placeholder="Select columns to search in",
        )
        if len(text_search_columns) > 0:
            cols = st.columns([0.8, 0.2], gap="small", vertical_alignment="bottom")
            with cols[1]:
                use_regex_search = st.checkbox(
                    "Use regex search",
                    value=False,
                    help="Use regex search for the card text instead of the conventional one (e.g. search for '\\+\\d' for any CSO giving + something).",
                )
            with cols[0]:
                filter_type = "regex" if use_regex_search else "plain text"
                searched_cols = ", ".join(
                    [f"```{col}```" for col in text_search_columns]
                )
                suffix = "s" if len(text_search_columns) > 1 else ""
                input_label = f"Enter a {filter_type} search parameter to filter the {searched_cols} column{suffix}:"
                value = st.session_state.get("card_text_search_param", "")
                placeholder = f"Enter words to {filter_type}-filter for in the {searched_cols.replace("```", "'")} column{suffix}, e.g. 'Next Time'."
                card_text_search_param = st.text_input(
                    input_label,
                    value,
                    key="card_text_search_param",
                    placeholder=placeholder,
                )
        st.info(
            "The search is case-insensitive and will match any part of the texts. Leave the search parameter empty to disable the filter."
        )
        show_examples = st.checkbox(
            "Show search examples",
            value=False,
            help="When checked, examples of search queries are shown. Unfortunately streamlit doesn't let you nest expanders.",
        )
        if show_examples:
            with st.container(border=True):
                st.markdown("#### Search examples")
                st.write(
                    """- You could search for all csos that give +1 something by entering "```+1```", or "```\\+\\d```" for any +X (the latter while having **regex** enabled).
- You could search for all CSOs mentioning "```treasure```", "```attack```" or "```next time```".
- You could search for all CSOs with scaling VP by enabling ```Quality Types``` in the columns to search in, and then enter "```scaling```".
- You could search for all CSOs that require coffers by enabling ```Components``` in the columns to search in, and then enter "```coffers```".

:warning: Let me know if you find any inconsistencies!
"""
                )
    with TABS[1]:
        cols = st.columns(
            spec=[0.7, 0.15, 0.15], gap="small", vertical_alignment="bottom"
        )
        all_expansions = rk.get_cached_expansions()

        with cols[1]:
            disable_exp_filtering = st.checkbox(
                "Disable expansion filtering",
                key="disableExpFilter",
                value=True,
                help="When checked, all expansions are allowed, otherwise we filter for the specified expansions.",
            )
        with cols[0]:
            SELECTED_EXPANSIONS = st.multiselect(
                "Allowed Expansions",
                options=all_expansions,
                default=[exp for exp in all_expansions if "1E" not in exp],
                key="expansionSelectForFilter",
                disabled=disable_exp_filtering,
                help="Select the expansions you want to include in the filtered results.",
            )
        with cols[2]:
            exps_disable_1e = st.checkbox(
                "Remove 1Es",
                value=st.session_state.get("expansions_disable_1e", False),
                help="When checked, we remove all 1E expansions, no matter whether they are specified or not.",
                key="expansions_disable_1e",
            )
    with TABS[2]:
        unique_types = rk.get_cached_unique_types()
        cols = st.columns(
            spec=[0.7, 0.15, 0.15], gap="small", vertical_alignment="bottom"
        )
        with cols[2]:
            disable_cso_filtering = st.checkbox(
                "Disable type filtering", key="disableTypeFilter", value=True
            )
        with cols[1]:
            require_all_selected_cso_types = st.checkbox(
                "Require all selected types",
                value=False,
                disabled=disable_cso_filtering,
            )
        with cols[0]:
            cso_types = st.multiselect(
                "Allowed CSO Types",
                options=unique_types,
                default=["Action", "Attack", "Reaction", "Treasure"],
                key="typeSelectForFilter",
                disabled=disable_cso_filtering,
            )
        type_amounts = st.slider(
            "Allowed Amounts of types",
            1,
            4,
            value=(1, 4),
            help="Filter for the amount of types a CSO has.",
        )

    with TABS[3]:
        cols = st.columns([0.8, 0.2], gap="small", vertical_alignment="bottom")
        with cols[1]:

            disable_cost_filtering = st.checkbox(
                "Disable cost filtering",
                value=True,
            )
        with cols[0]:
            min_cost, max_cost = st.slider(
                "Cost", 0, 14, (0, 14), disabled=disable_cost_filtering
            )
    with TABS[4]:
        cols = st.columns(4, gap="small", vertical_alignment="top")
        landscape_checked = st.session_state.get("landscape_is_checked", False)

        with cols[0]:
            in_supply = st.checkbox(
                "Require CSOs to be in supply", value=landscape_checked
            )
        with cols[1]:
            is_card = st.checkbox("Require CSOs to be cards", value=False)
        with cols[2]:
            is_landscape = st.checkbox(
                "Require CSOs to be extended landscapes",
                value=False,
                help=f"Filter for extended landscapes (i.e., {','.join(rk.EXTENDED_LANDSCAPE_LIST)})",
            )
        with cols[3]:
            has_extra_components = st.checkbox(
                "Require CSOs to have extra components",
                value=False,
                help="Filter for CSOs that require extra components to play with.",
            )
        st.session_state["landscape_is_checked"] = is_landscape
    with TABS[5]:
        st.write(
            "Select the columns you want excluded from being displayed in the table."
        )
        col_config = rk.get_col_config()
        all_labels = [desc["label"] for desc in col_config.values()]
        qual_labels = [label for label in all_labels if "-Q" in label]
        types_labels = [
            label for label in all_labels if "-Types" in label or "Compon" in label
        ]
        extra_labels = [ST_ICONS["combos"], ST_ICONS["interactions"]]
        base_labels = [
            label
            for label in all_labels
            if label not in qual_labels + types_labels + extra_labels
        ]
        cols = st.columns([0.6, 0.2, 0.2, 0.2], gap="small", vertical_alignment="top")
        with cols[0]:
            excluded_columns = st.multiselect(
                "Columns to exclude",
                options=base_labels,
                key="excluded_columns",
            )
        with cols[1]:
            exclude_quality_columns = st.checkbox(
                "Exclude Quality Columns",
                help="Exclude the columns referring to any of the qualities",
                key="exclude_quality_columns",
            )
            if exclude_quality_columns:
                excluded_columns += qual_labels
        with cols[2]:
            exclude_qtypes_columns = st.checkbox(
                "Exclude Quality Type Columns",
                value=True,
                help="Exclude the columns referring to any of the quality types",
                key="exclude_quality_type_columns",
            )
            if exclude_qtypes_columns:
                excluded_columns += types_labels
        with cols[3]:
            exclude_interaction_columns = st.checkbox(
                "Exclude Interaction/Combo Number Columns",
                value=True,
                help="Exclude the columns referring to any of the interaction/combo types",
                key="exclude_interaction_columns",
            )
            if exclude_interaction_columns:
                excluded_columns += extra_labels


def filter_full_df_for_options(df: pd.DataFrame) -> pd.DataFrame:
    filt_str = ""
    df = df.set_index("Name", drop=False)
    filter_mask = np.ones(len(df), dtype=bool)

    global SELECTED_EXPANSIONS
    if SELECTED_EXPANSIONS and not disable_exp_filtering:
        SELECTED_EXPANSIONS += [exp for exp in SELECTED_EXPANSIONS if "1E" in exp]
        SELECTED_EXPANSIONS += [exp for exp in SELECTED_EXPANSIONS if "2E" in exp]
        filter_mask &= df["Expansion"].isin(SELECTED_EXPANSIONS)
    if exps_disable_1e:
        filter_mask &= ~df["Expansion"].str.contains("1E")

    if not disable_cost_filtering:
        if min_cost:
            filter_mask &= df["Sanitized Cost"] >= min_cost
        if max_cost:
            filter_mask &= df["Sanitized Cost"] <= max_cost
        if min_cost or max_cost:
            filt_str += "💸"
    if in_supply:
        filter_mask &= df["IsInSupply"]
    if is_card:
        filter_mask &= df["IsRealSupplyCard"]
    if is_landscape:
        filter_mask &= df["IsExtendedLandscape"]
    if has_extra_components:
        filter_mask &= df["HasExtraComponents"]
    if any((in_supply, is_card, is_landscape, has_extra_components)):
        filt_str += "🔧"
    if cso_types and not disable_cso_filtering:
        filt_str = "🔣" + filt_str
        if require_all_selected_cso_types:
            filter_mask &= df["Types"].apply(lambda x: all([t in x for t in cso_types]))
        else:
            filter_mask &= df["Types"].apply(lambda x: any([t in x for t in cso_types]))
    elif type_amounts[0] > 1 or type_amounts[1] < 4:
        filt_str = "🔣" + filt_str
    filter_mask &= np.isin(
        df["Types"].apply(len), range(type_amounts[0], type_amounts[1] + 1)
    )
    if not disable_exp_filtering or exps_disable_1e:
        filt_str = "🗃️" + filt_str
    # Do regexp search last in hopes of reducing amount that needs to be searched
    if len(text_search_columns) > 0 and card_text_search_param:
        try:
            text_mask = np.zeros(len(df), dtype=bool)
            for key, colname in text_search_options.items():
                if key not in text_search_columns:
                    continue
                if colname == "Qualities":
                    for qual in rk.SPECIAL_QUAL_TYPES_AVAILABLE:
                        col_to_search = df[f"{qual}_types"].apply(
                            lambda x: ", ".join(x)
                        )
                        text_mask |= col_to_search.str.contains(
                            card_text_search_param,
                            case=False,
                            na=False,
                            regex=use_regex_search,
                        )
                    continue
                listlike = ["Types", "Extra Components"]
                col_to_search = (
                    df[colname]
                    if colname not in listlike
                    else df[colname].apply(lambda x: ", ".join(x))
                )
                text_mask |= col_to_search.str.contains(
                    card_text_search_param, case=False, na=False, regex=use_regex_search
                )
            filter_mask &= text_mask
        except re.error as e:
            st.error(
                f"Invalid regex search parameter ('{e.msg}' for '{card_text_search_param}')."
            )
        filt_str = "📃" + filt_str
    if len(excluded_columns) > 0:
        filt_str += "💈"
    if INVERT_MASK:
        filter_mask = ~filter_mask
        filt_str = "❗" + filt_str
    df = df[filter_mask] if not filter_mask.all() else df
    st.session_state["database_filter_str"] = filt_str
    return df


FILTERED_DF = filter_full_df_for_options(rk.ALL_CACHED_CSOS)
filt_str = st.session_state.get("database_filter_str")

st.write(
    f"#### {filt_str}Filtering for {len(FILTERED_DF)}/{len(rk.ALL_CACHED_CSOS)} available Card-Shaped Objects (CSOs)"
)
if FILTERED_DF.shape[0] > 300:
    st.warning(
        "Due to more than 300 entries being selected, the sorting might be slow."
    )

cols = [
    col for col, desc in col_config.items() if desc["label"] not in excluded_columns
]
if "Image" in cols:
    cols.remove("Image")
    cols = ["ImagePath"] + cols
rk.display_stylysed_cso_df(FILTERED_DF[cols + ["Name"]], with_reroll=False)

text = f"*Hint*: You can click on the column names to sort the table."
st.info(text)


def get_clipboard_str(radio_output: str) -> str:
    text = ""
    if radio_output == "Names":
        text += ", ".join(FILTERED_DF["Name"].tolist())
    elif radio_output == "Keys":
        text += ", ".join(
            rk.sanitize_cso_list(FILTERED_DF["Name"].tolist(), sort=False)
        )
    elif radio_output == "Names and Expansions":
        text += ", ".join(FILTERED_DF["Name and Expansion"].tolist())
    return text


@st.fragment
def build_database_clipboard_copy_options():
    from st_copy_to_clipboard import st_copy_to_clipboard

    cols = st.columns([0.8, 0.2])
    radio_options = ["Names", "Keys", "Names and Expansions"]
    with cols[0]:
        radio_output = st.radio(
            "Copy a comma-separated list of all selected CSOs to clipboard.",
            radio_options,
            index=radio_options.index(
                st.session_state.get("radio_db_csv_output_sel", "Names")
            ),
            key="radio_db_csv_output_sel",
            help="Select the type of text that's copied to clipboard.",
            horizontal=True,
        )
    with cols[1]:
        st_copy_to_clipboard(
            get_clipboard_str(radio_output),  # type: ignore
            before_copy_label="📋Copy to clipboard",
            after_copy_label="Copied! Ready to be pasted.",
        )


with st.expander("Copy selection", expanded=False):
    build_database_clipboard_copy_options()

# Add some spacing below as it helps displaying pictures if a user clicks on them
st.write("<br>" * 10, unsafe_allow_html=True)
