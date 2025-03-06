import numpy as np
import pandas as pd
import streamlit as st
import streamlit_extras as stx
from streamlit.components.v1 import html
from streamlit_extras.card import card
from streamlit_extras.grid import grid
from streamlit_extras.stylable_container import stylable_container

import random_kingdominion as rk


def _toggle_exp(exp: str):
    sel_expansions = st.session_state.get("selected_expansions", [])
    if exp in sel_expansions:
        sel_expansions.remove(exp)
    else:
        sel_expansions.append(exp)
    st.session_state["selected_expansions"] = sel_expansions


def create_card(exp: str):
    sel_expansions = st.session_state.get("selected_expansions", [])
    icon = rk.get_expansion_icon_path(exp)
    cols = st.columns([0.3, 0.7])
    with cols[0]:
        st.image(icon, width=50)
    with cols[1]:
        color = "green" if exp in sel_expansions else "grey"
        key = rk.sanitize_cso_name(exp).replace(",", "_").replace("&", "_")
        with stylable_container(
            key=f"green_button_{key}",
            css_styles=f"""
                    button {{
                        background-color: {color};
                        color: white;
                        border-radius: 20px;
                    }}
                    """,
        ):
            st.button(
                f"{exp}",
                key=f"color button {exp}",
                use_container_width=True,
                on_click=lambda: _toggle_exp(exp),
            )


# Arrange cards in grid:
def create_exp_grid():
    exps = rk.ALL_EXPANSIONS
    num_cols = 5
    num_rows = len(exps) // num_cols + 1
    my_grid = grid([num_cols] * num_rows, vertical_align="bottom", gap="small")
    for exp in rk.ALL_EXPANSIONS:
        with my_grid.container(border=True):
            key = rk.sanitize_cso_name(exp).replace(",", "_").replace("&", "_")
            with stylable_container(
                key=f"cont_{key}",
                css_styles=f"""
                        height: 100px;
                        """,
            ):
                create_card(exp)


create_exp_grid()
