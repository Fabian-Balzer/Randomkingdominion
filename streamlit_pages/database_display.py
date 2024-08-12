import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk

st.title("Card Overview")
st.write(
    """On this page, you can filter and view the card database of all dominion Card-Shaped Objects, and sort and filter them to hunt for whatever you might need.

This also includes my hand-curated card qualities.
"""
)

SELECTED_EXPANSIONS = []
with st.container(border=True):
    st.write("### Filters\n\nUse these options to filter the CSO database.")
    TABS = st.tabs(["Expansions", "Types", "Cost", "Other"])
    with TABS[0]:
        cols = st.columns(
            spec=[0.7, 0.15, 0.15], gap="small", vertical_alignment="bottom"
        )
        all_expansions = rk.get_cached_expansions()

        with cols[2]:
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
        with cols[1]:
            exps_disable_1e = st.checkbox(
                "Remove 1Es",
                value=True,
                disabled=disable_exp_filtering,
                help="When checked, we remove all 1E expansions, no matter whether they are specified or not.",
            )
    with TABS[1]:
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

    with TABS[2]:
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
    with TABS[3]:
        cols = st.columns(3, gap="small", vertical_alignment="bottom")
        landscape_checked = st.session_state.get("landscape_is_checked", False)

        with cols[0]:
            in_supply = st.checkbox(
                "Require CSOs to be in supply", value=landscape_checked
            )
        with cols[1]:
            is_card = st.checkbox("Require CSOs to be cards", value=False)
        with cols[2]:
            is_landscape = st.checkbox(
                "Require CSOs to be exteneded landscapes",
                value=False,
                help=f"Filter for extended landscapes (i.e. {','.join(rk.EXTENDED_LANDSCAPE_LIST)})",
            )
        st.session_state["landscape_is_checked"] = is_landscape
    INVERT_MASK = st.checkbox(
        "Invert filters", value=False, help="Invert all applied filters."
    )


def filter_full_df_for_options(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index("Name")
    filter_mask = np.ones(len(df), dtype=bool)
    global SELECTED_EXPANSIONS
    if SELECTED_EXPANSIONS and not disable_exp_filtering:
        if exps_disable_1e:
            SELECTED_EXPANSIONS = [
                exp for exp in SELECTED_EXPANSIONS if "1E" not in exp
            ]
        SELECTED_EXPANSIONS += [exp for exp in SELECTED_EXPANSIONS if "1E" in exp]
        SELECTED_EXPANSIONS += [exp for exp in SELECTED_EXPANSIONS if "2E" in exp]
        filter_mask &= df["Expansion"].isin(SELECTED_EXPANSIONS)
    if not disable_cost_filtering:
        if min_cost:
            filter_mask &= df["Sanitized Cost"] >= min_cost
        if max_cost:
            filter_mask &= df["Sanitized Cost"] <= max_cost
    if in_supply:
        filter_mask &= df["IsInSupply"]
    if is_card:
        filter_mask &= df["IsRealSupplyCard"]
    if is_landscape:
        filter_mask &= df["IsExtendedLandscape"]
    if cso_types and not disable_cso_filtering:
        if require_all_selected_cso_types:
            filter_mask &= df["Types"].apply(lambda x: all([t in x for t in cso_types]))
        else:
            filter_mask &= df["Types"].apply(lambda x: any([t in x for t in cso_types]))
    if INVERT_MASK:
        filter_mask = ~filter_mask
    df = df[filter_mask] if not filter_mask.all() else df
    return df


filtered_df = filter_full_df_for_options(rk.MAIN_DF)
text = f"Found {filtered_df.shape[0]}/{len(rk.MAIN_DF)} CSOs with the given filter options."
if filtered_df.shape[0] > 200:
    text += " Due to more than 200 entries being selected, the sorting might be slow."
st.write(text)

rk.display_stylysed_cso_df(filtered_df)
