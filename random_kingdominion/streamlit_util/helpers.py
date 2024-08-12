import base64
import re
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from ..constants import ALL_CSOS, EXPANSION_LIST, RENEWED_EXPANSIONS


# img_to_bytes and img_to_html inspired from https://pmbaumgartner.github.io/streamlitopedia/sizing-and-images.html
def img_to_bytes(
    img_path: str | Path, crop_rect: tuple[float, float, float, float] | None = None
):
    """Convert an image at the given path to bytes for display in Streamlit."""

    img = Image.open(img_path)

    if crop_rect is not None and len(crop_rect) == 4:
        width, height = img.size
        vals = [
            crop_rect[0] * width,
            crop_rect[1] * height,
            crop_rect[2] * width,
            crop_rect[3] * height,
        ]
        img = img.crop(vals)  # type: ignore

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    # img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(
    img_path: str | Path,
    size: int | None = None,
    height: int | None = None,
    width: int | None = None,
    crop_rect: tuple[int, int, int, int] | None = None,
):
    """Convert an image at the given path to HTML to display it in Streamlit."""
    img_bytes = img_to_bytes(img_path, crop_rect)
    height_ = height if height else size if size else "auto"
    width_ = width if width else size if size else "auto"
    img_html = f"<img src='data:image/png;base64,{img_bytes}' class='img-fluid' width='{width_}' height='{height_}'>"
    return img_html


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


@st.cache_data
def get_cached_expansions():
    return [exp for exp in EXPANSION_LIST if exp not in RENEWED_EXPANSIONS]


def display_image_with_tooltip(
    img_path: str,
    tooltip: str = "",
    link_url: str | None = None,
    crop_rect=None,
    **kwargs,
):
    """Display an image with a tooltip on hover."""
    try:
        img_html = img_to_html(img_path, crop_rect=crop_rect, **kwargs)
    except FileNotFoundError:
        st.write(f"Couldn't find the image at {img_path}")
        return
    if link_url is not None:
        img_html = f"""<a href="{link_url}" target="_blank">
            {img_html}
        </a>"""
    cursor_str = "cursor: pointer;" if link_url is not None else ""
    # Define HTML and CSS for the tooltip
    html_content = f"""
    <style>
    .tooltip {{
    position: relative;
    display: inline-block;
    {cursor_str}
    }}

    .tooltip .tooltiptext {{
    visibility: hidden;
    width: 200px;
    background-color: black;
    color: white;
    text-align: center;
    border-radius: 6px;
    padding: 5px 5x;
    position: absolute;
    z-index: 1;
    bottom: 80%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
    }}

    .tooltip:hover .tooltiptext {{
    visibility: visible;
    opacity: 1;
    }}
    </style>

    <div class="tooltip">
        {img_html}
    <span class="tooltiptext">{tooltip}</span>
    </div>
    """

    # Display HTML in Streamlit
    st.markdown(html_content, unsafe_allow_html=True)


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
        cost_img_str += img_to_html(f"./static/icons/{cost_str}", size=20)
    return cost_img_str
