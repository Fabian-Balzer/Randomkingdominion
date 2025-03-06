from PIL import Image

from ...constants import ALL_CSOS, PATH_CARD_PICS


def load_cso_img_by_key(cso_key: str) -> Image.Image:
    """Load the image of the card specified by the cso_key"""

    cso = ALL_CSOS.loc[cso_key]
    fpath = PATH_CARD_PICS.joinpath(cso["ImagePath"])  # type: ignore
    if not fpath.exists():
        raise FileNotFoundError(f"Couldn't find the image at {fpath}")
    img = Image.open(fpath)
    if img.width > img.height:
        img = img.resize((367, 224))
    else:
        img = img.resize((224, 367))
    return img


def crop_img_by_percentage(img: Image.Image, crop_rect: list[float]) -> Image.Image:
    """Crop the image according to the crop_rect, where the crop_rect is a list
    of four floats between 0 and 1, specifying the left, upper, right, and lower
    bounds of the crop rectangle, respectively."""
    assert len(crop_rect) == 4
    w, h = img.size
    vals = [crop_rect[0] * w, crop_rect[1] * h, crop_rect[2] * w, crop_rect[3] * h]
    return img.crop(vals)  # type: ignore


def crop_img_symmetrically(
    img: Image.Image, width_crop: float, height_crop: float
) -> Image.Image:
    """Crop the image symmetrically, where width- and height crops
    are percentages (i.e. floats between 0 and 1)"""
    return crop_img_by_percentage(
        img, [width_crop, height_crop, (1 - width_crop), (1 - height_crop)]
    )


def compose_images_vertically(img_1: Image.Image, img_2: Image.Image) -> Image.Image:
    """Combine two images vertically, i.e. one on top of the other, assuming
    that both images have the same width."""
    assert img_1.width == img_2.width
    # Create a new blank image with the combined height of both images
    total_height = img_1.height + img_2.height
    combined_image = Image.new("RGBA", (img_1.width, total_height))

    # Paste the images onto the new blank image
    combined_image.paste(img_1, (0, 0))
    combined_image.paste(img_2, (0, img_1.height))

    return combined_image


def get_card_img_without_text(cso_key: str):
    """Get the image of a card without the text box."""
    img = load_cso_img_by_key(cso_key)
    upper_crop_rect = [0, 0, 1, 16 / 30]
    lower_crop_rect = [0, 62 / 70, 1, 1]
    crop_1 = crop_img_by_percentage(img, upper_crop_rect)
    crop_2 = crop_img_by_percentage(img, lower_crop_rect)
    return compose_images_vertically(crop_1, crop_2)


def overlay_cutout(
    base_img: Image.Image,
    overlay_img: Image.Image,
    cutout_size: float,
    position: tuple[float, float],
):
    """Overlay a cutout from the overlay image onto the base image at the"""
    # Open the base image and the overlay image
    base_img = base_img.convert("RGBA")
    overlay_img = overlay_img.convert("RGBA")

    resize = int(overlay_img.width * cutout_size), int(overlay_img.height * cutout_size)
    cutout = overlay_img.resize(resize)

    # Paste the cutout onto the base image at the desired position
    pixel_pos = int(base_img.width * position[0]), int(base_img.height * position[1])
    base_img.paste(cutout, pixel_pos, cutout)

    return base_img
