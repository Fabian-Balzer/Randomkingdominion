from PIL import Image

from ...utils import get_expansion_icon_path
from .image_handling import display_image_with_tooltip


def st_build_expansion_icon_with_tt(exp: str, icon_size: int = 30, tooltip: str = ""):

    fpath = "./static/" + get_expansion_icon_path(exp, relative_only=True)
    im = Image.open(fpath).convert("RGBA").resize((icon_size, icon_size))
    # bg = Image.new("RGBA", im.size, bg_color)
    # # Paste the original image onto the background
    # im = Image.alpha_composite(bg, im)

    display_image_with_tooltip(im, tooltip)
