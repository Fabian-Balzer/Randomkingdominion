from datetime import datetime, timedelta

import streamlit as st

from .constants import COOKIES

# def allow_cookies():
#     """Function to allow cookies"""
#     COOKIES.set(
#         "cookie_consent",
#         True,
#         expires=datetime.now() + timedelta(days=365),
#         max_age=31536000,
#         same_site="lax",
#         secure=True,
#     )
#     st.rerun()


# def disallow_cookies():
#     """Function to disallow cookies"""
#     dict_keys = COOKIES.getAll().copy()
#     for key in dict_keys:
#         COOKIES.remove(key)
#     st.rerun()


def build_cookie_options():
    """Build the cookie options"""
    return
    if not COOKIES.get("cookie_consent"):
        st.sidebar.write(
            "This app can use cookies to save your randomizer configuration."
        )
        if st.sidebar.button("Allow Cookies?", use_container_width=True):
            allow_cookies()
    else:
        st.sidebar.write(
            "You have allowed this app to use cookies to save your randomizer configuration.\nDisallowing cookies might reset your configuration."
        )
        if st.sidebar.button("Disallow Cookies", use_container_width=True):
            disallow_cookies()
