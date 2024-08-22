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

quality_pages = [
    rk.get_quality_page_navigation(qual) for qual in rk.QUALITIES_AVAILABLE
]

pg = st.navigation(
    {
        "": [
            st.Page(
                "streamlit_pages/randomizer.py",
                title="Kingdom Randomizer",
                url_path="randomizer",
                icon="🔀",
            ),
            st.Page(
                "streamlit_pages/kingdom_oracle.py",
                title="Kingdom Oracle",
                url_path="oracle",
                icon="💥",
            ),
            st.Page(
                "streamlit_pages/database_display.py",
                title="CSO Database",
                url_path="cso_overview",
                icon="📂",
            ),
            st.Page(
                "streamlit_pages/about.py",
                title="About this page",
                url_path="about",
                icon="❓",
            ),
        ],
        "CSO and Kingdom Qualities": quality_pages,
    }
)
pg.run()

rk.build_cookie_options()

# %%

# import sys

# import PyQt5.QtWidgets as QW

# from random_kingdominion.widgets.main_ui import UIMainWindow

# def start_program():
#     """A function to include everything needed to start the application"""
#     # Check whether there is already a running QApplication (e.g. if running
#     # from an IDE). This setup prevents crashes for the next run:
#     qapp = QW.QApplication.instance()
#     if not qapp:
#         qapp = QW.QApplication(sys.argv)
#     app = UIMainWindow()  # creating the instance
#     app.show()
#     qapp.exec_()  # Start the Qt event loop


# if __name__ == "__main__":
#     start_program()
