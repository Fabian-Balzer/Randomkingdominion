from .image_handling import img_to_html
import streamlit as st
import re

from ..constants import ALL_CSOS


def extract_and_convert(value):
    """Extract the first number from a string and convert it to an integer."""
    # Use regular expression to find all digits in the string
    numbers = re.findall(r"\d+", str(value))
    if numbers:
        # Convert the first found number to integer
        return int(numbers[0])
    else:
        # Return some default value or raise an error if no number is found
        return 0  # or use `raise ValueError(f"No numbers found in '{value}'")` for stricter handling


@st.cache_data
def load_main_df():
    """Cache the CSOs for streamlit (Not sure this is the correct way)"""
    ALL_CSOS["Sanitized Cost"] = ALL_CSOS["Cost"].apply(extract_and_convert)
    return ALL_CSOS


MAIN_DF = load_main_df()


@st.cache_data
def get_cached_unique_types():
    unique_types = set()
    MAIN_DF["Types"].apply(lambda x: unique_types.update(x))
    return sorted(unique_types)


def _get_card_cost_fpaths(card_cost: str) -> list[str]:
    repl_dict = {"*": "star", "+": "plus", "P": " 74px-Potion", "$": "120px-Coin"}
    for key, value in repl_dict.items():
        card_cost = card_cost.replace(key, value)
    substrings = card_cost.split()
    if "D" in substrings[-1]:
        substrings[-1] = "Debt" + substrings[-1].replace("D", "")
    return [f"{sub}.png" for sub in substrings]


def get_cost_html(cost_str: str) -> str:
    """Convert a card cost string to an HTML string with images of the cost components."""
    costs = _get_card_cost_fpaths(cost_str)
    cost_img_str = ""
    for cost_str in costs:
        cost_img_str += img_to_html(f"./static/icons/{cost_str}")
    return cost_img_str
