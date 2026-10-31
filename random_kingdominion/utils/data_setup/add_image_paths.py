import pandas as pd

from ...constants import PATH_CARD_PICS
from ...logger import LOGGER


def add_image_paths(df: pd.DataFrame) -> pd.DataFrame:
    """Add the ``ImagePath`` column (``<Expansion>/<Name>.jpg``, relative to
    ``static/card_pictures``) and warn about images that don't exist yet, since
    they have to be added by hand."""
    df["ImagePath"] = [
        f"{exp.replace(', ', '_')}/{name.replace(' ', '_')}.jpg"
        for name, exp in zip(df["Name"], df["Expansion"])
    ]
    missing = [p for p in df["ImagePath"] if not PATH_CARD_PICS.joinpath(p).exists()]
    if missing:
        LOGGER.warning(
            f"{len(missing)} card images are missing in {PATH_CARD_PICS}: {missing}"
        )
    return df
