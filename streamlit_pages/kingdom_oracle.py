from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st

import random_kingdominion as rk
from random_kingdominion.streamlit_util.constants import ST_ICONS  # type: ignore

rk.build_page_header(
    "Dominion Kingdom Oracle",
    (
        "This page allows you to easily input a kingdom to visualize its engine qualities "
        "and take a more detailed look on its Card-Shaped Objects (CSOs). "
        "The resulting plot also shows any extra components you'd need to set up the kingdom in its physical form."
    ),
    "Learn more about the CSO and kingdom qualities on the 'About' page.",
)

rk.st_build_existing_kingdom_select()

k = rk.st_build_oracle_kingdom_input_display()

rk.st_build_oracle_kingdom_display(k)
