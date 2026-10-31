# -*- coding: utf-8 -*-
"""
@author: Fabian Balzer

***
LICENSE:
    Copyright (C) 2021-2026 Fabian Balzer
    SPDX-License-Identifier: AGPL-3.0-or-later

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program (LICENSE.txt). If not, see <https://www.gnu.org/licenses/>.

    Additional terms under section 7(b) of the GNU AGPL: modified versions must
    retain the notice "Based on Random KingDominion by Fabian Balzer
    (https://github.com/Fabian-Balzer/Randomkingdominion)" in the user interface,
    e.g. on an About page.

***

Code to open a GUI Dominion randomizer
"""

import streamlit as st

import random_kingdominion as rk

st.set_page_config(
    layout="wide",
    menu_items={
        "About": "This is a hobby project. Check out my [YouTube channel](https://www.youtube.com/@fabyy5713) for Dominion videos. Also, (unrelated to Dominion), I've been involved in an App for the game of werewolf, which you can check out [here](https://werewolf-app.com).",
    },
)
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
                "streamlit_pages/quiz.py",
                title="Quiz",
                url_path="quiz",
                icon=rk.ST_ICONS["quiz"],
            ),
            st.Page(
                "streamlit_pages/about.py",
                title="About and more",
                url_path="about",
                icon=rk.ST_ICONS["about"],
            ),
        ],
        f"{rk.ST_ICONS['cso_qualities']}CSO Quality Descriptions": quality_pages,
    },
    expanded=False,
)
pg.run()
