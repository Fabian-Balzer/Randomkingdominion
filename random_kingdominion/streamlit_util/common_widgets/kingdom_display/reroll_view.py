from typing import Callable

import pandas as pd
import streamlit as st

from .. import display_stylysed_cso_df


def _build_reroll_selection_button(
    key: str, reroll_selection_callback: Callable[[], None]
):
    if st.button(
        "Reroll selected CSOs",
        help="Reroll the CSOs you selected to generate a new kingdom.",
        on_click=reroll_selection_callback,
        use_container_width=True,
        key=key,
        type="primary",
    ):
        st.rerun()


def st_build_reroll_kingdom_display(
    kingdom_df: pd.DataFrame, reroll_selection_callback: Callable[[], None]
):
    display_stylysed_cso_df(
        kingdom_df[["ImagePath", "Expansion", "Cost"]],
        with_reroll=True,
        width="stretch",
    )
    _build_reroll_selection_button("Reroll selection", reroll_selection_callback)
