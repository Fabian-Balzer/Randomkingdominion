# -*- coding: utf-8 -*-

"""Script to cut off the black borders of the DomBot images."""

# %%

from datetime import datetime
from pathlib import Path

from PIL import Image

import random_kingdominion as rk


def get_file_creation_time(fpath: Path) -> datetime:
    # Get the file creation time
    creation_time = Path(fpath).stat().st_ctime

    # Convert the creation time to a readable format
    return datetime.fromtimestamp(creation_time)


# Calculate the new size maintaining the aspect ratio
def resize_to_aspect_ratio(im: Image.Image, aspect_ratio):
    """Resize the image to the given aspect ratio, keeping its height."""
    width, height = im.size
    target_width, target_height = aspect_ratio
    new_height = int((target_height / target_width) * width)
    return im.resize((width, new_height))


def crop_landscape(cso_key: str):
    return rk.crop_img_symmetrically(rk.load_cso_img_by_key(cso_key), 0.038, 0.06)


def crop_card(cso_key: str):
    return rk.crop_img_symmetrically(rk.load_cso_img_by_key(cso_key), 0.06, 0.038)


def crop_recent_images(last_date: datetime):
    for cso_key, cso in rk.ALL_CSOS.iterrows():
        fpath = rk.PATH_CARD_PICS.joinpath(cso["ImagePath"])
        # The path where the old image will be moved to
        replace_path = fpath.with_suffix(".old.jpg")
        if get_file_creation_time(fpath) > last_date and not replace_path.exists():
            if cso["IsExtendedLandscape"]:
                cropped_img = crop_landscape(str(cso_key))
            else:
                cropped_img = crop_card(str(cso_key))
            # Move old image:
            fpath.rename(replace_path)
            cropped_img.save(fpath)


if __name__ == "__main__":
    # crop_recent_images(datetime(2024, 8, 11))

    pass
# %%
