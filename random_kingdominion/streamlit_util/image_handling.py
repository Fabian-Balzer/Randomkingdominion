import base64
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

from ..constants import PATH_CARD_PICS
from .constants import ALL_CACHED_CSOS


# img_to_bytes and img_to_html inspired from https://pmbaumgartner.github.io/streamlitopedia/sizing-and-images.html
def img_to_bytes(img: Image.Image | str | Path) -> str:
    """Convert an image at the given path to bytes for display in Streamlit."""
    if not isinstance(img, Image.Image):
        try:
            img = Image.open(img)
        except FileNotFoundError:
            st.write(f"Couldn't find the image at {img}")
            return ""
    buffer = BytesIO()
    img.save(buffer, format="PNG")  # type: ignore
    img_bytes = buffer.getvalue()
    # img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img: Image.Image | str | Path):
    """Convert an image at the given path to HTML to display it in Streamlit."""
    img_bytes = img_to_bytes(img)
    img_html = f"<img src='data:image/png;base64,{img_bytes}' class='img-fluid' width='auto' height='auto'>"
    return img_html


def display_image_with_tooltip(
    img: Image.Image | str | Path,
    tooltip: str = "",
    link_url: str | None = None,
):
    """Display an image with a tooltip on hover."""
    try:
        img_html = img_to_html(img)
    except FileNotFoundError:
        st.write(f"Couldn't find the image at {img}")
        return
    if link_url is not None:
        img_html = f"""<a href="{link_url}" target="_blank">
            {img_html}
        </a>"""
    cursor_str = "cursor: pointer;" if link_url is not None else ""
    # Define HTML and CSS for the tooltip
    tooltip_html = f'<span class="tooltiptext">{tooltip}</span>' if tooltip else ""
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
    padding: 10px;
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
    {tooltip_html}
    </div>
    """

    # Display HTML in Streamlit
    st.markdown(html_content, unsafe_allow_html=True)
