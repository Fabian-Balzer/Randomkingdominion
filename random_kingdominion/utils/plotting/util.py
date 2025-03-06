from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from scipy.ndimage import zoom as zoom_image

if TYPE_CHECKING:
    from ...kingdom import Kingdom


def plot_gradient_image(
    ax: Axes, extent: tuple, direction: str = "horizontal", cmap: str = "viridis"
) -> None:
    """Set a gradient background for the given axes."""
    gradient = np.linspace(80, 200, 500)
    gradient = np.vstack((gradient, gradient))
    if direction == "vertical":
        gradient = gradient.T
    ax.imshow(
        gradient, aspect="auto", extent=extent, cmap=cmap, vmin=0, vmax=255, zorder=-1
    )


def get_video_title(k: "Kingdom") -> str:
    """Generate a canonical title for the video."""
    title = k.name
    if "name" in k.unpacked_notes:
        title = f"{k.unpacked_notes['name']} [{title}]"
    return title


def annotate_single_expansion_icon(
    img_name: str, ax: Axes, x0: float, y0: float, final_zoom=0.4
):
    from ..utils import get_expansion_icon_path

    icon_path = get_expansion_icon_path(img_name)
    return annotate_icon(icon_path, ax, x0, y0, final_zoom, size=100)


def annotate_icon(
    fpath: str | Path, ax: Axes, x0: float, y0: float, final_zoom=0.4, size=100
):
    img = plt.imread(fpath)
    height, width = img.shape[:2]
    new_height, new_width = size, size
    zoom_factors = (new_height / height, new_width / width, 1)
    # Resize the image
    img_resized = zoom_image(img, zoom_factors)
    # Convert back to array for matplotlib
    image_rgb = np.clip(img_resized, 0, 1)
    img = OffsetImage(image_rgb, zoom=final_zoom)
    ab = AnnotationBbox(
        img, (x0, y0), frameon=False, xycoords="data", box_alignment=(0, 1)
    )
    ax.add_artist(ab)
    return ab
