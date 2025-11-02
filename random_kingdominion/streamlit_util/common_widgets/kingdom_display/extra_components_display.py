import pandas as pd
import streamlit as st

from ....kingdom import Kingdom
from ...image_util import st_build_expansion_icon_with_tt


def st_build_small_extra_component_display(k: Kingdom, show_exp=False):
    """Display extra components needed for the kingdom."""
    text = k.get_component_string(
        show_exp=show_exp, cutoff_len=None, exclude_trash_mat=False
    ).replace("EXTRAS:", "")
    text = "- " + "\n- ".join(text.split(", "))
    st.write(text)


def st_build_big_extra_component_display(k: Kingdom):
    """Display all components needed for the kingdom, grouped by expansion."""
    tabs = st.tabs(
        ["Cards and Landscapes", "Extra Components"], default="Extra Components"
    )
    exp_groups = k.full_kingdom_df.groupby("Expansion", observed=True)
    for exp, group in exp_groups:
        c = tabs[0].container(border=True)
        cols = c.columns([0.1, 0.9])
        with cols[0]:
            st_build_expansion_icon_with_tt(str(exp), tooltip=str(exp))
        with cols[1]:
            text = ""
            for row in group.itertuples():
                cost = f"({row.Cost})" if pd.notna(row.Cost) else ""
                text += f"- {row.Name} {cost}\n"
            st.write(text)
    tabs[1].write(
        "These extra components might be needed if you set up this kingdom in person:"
    )
    with tabs[1]:
        st_build_small_extra_component_display(k, True)
