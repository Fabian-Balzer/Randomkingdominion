# -*- coding: utf-8 -*-
"""
@author: Fabian Balzer

***
LICENSE:
    Copyright 2021 Fabian Balzer

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
***

Code to open a GUI Dominion randomizer
"""

import streamlit as st

st.set_page_config(layout="wide")
import random_kingdominion as rk

rk.LOGGER.setLevel("ERROR")

quality_pages = [
    rk.get_quality_page_navigation(qual) for qual in rk.QUALITIES_AVAILABLE
]

pg = st.navigation(
    {
        "": [
            # st.Page(
            #     "streamlit_pages/st_test.py", title="Test", url_path="test", icon="🏠"
            # ),
            st.Page(
                "streamlit_pages/randomizer.py",
                title="Dominion Kingdom Randomizer",
                url_path="randomizer",
                icon=rk.ST_ICONS["randomizer"],
            ),
            st.Page(
                "streamlit_pages/kingdom_oracle.py",
                title="Kingdom Oracle",
                url_path="oracle",
                icon=rk.ST_ICONS["oracle"],
            ),
            st.Page(
                "streamlit_pages/database_display.py",
                title="CSO Database",
                url_path="cso_overview",
                icon=rk.ST_ICONS["cso_overview"],
            ),
            st.Page(
                "streamlit_pages/interactions.py",
                title="CSO Interactions",
                url_path="interactions",
                icon=rk.ST_ICONS["interactions"],
            ),
            st.Page(
                "streamlit_pages/combos.py",
                title="CSO Combos",
                url_path="combos",
                icon=rk.ST_ICONS["combos"],
            ),
            st.Page(
                "streamlit_pages/about.py",
                title="About this page",
                url_path="about",
                icon=rk.ST_ICONS["about"],
            ),
        ],
        f"{rk.ST_ICONS['cso_qualities']}CSO Quality Descriptions": quality_pages,
    },
    expanded=False,
)
pg.run()
