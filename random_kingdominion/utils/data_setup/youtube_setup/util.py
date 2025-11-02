from pathlib import Path
from ....constants import PATH_ASSETS
import yaml


def _get_fpath(key: str) -> Path:
    return PATH_ASSETS / f"other/yt_stats/{key}.yaml"


def yml_load_entries(key: str) -> list[dict]:
    fpath = _get_fpath(key)
    if not fpath.exists():
        fpath.touch()
    with open(fpath, "r") as f:
        return yaml.safe_load(f) or []


def yml_save_entries(entries: list[dict], key: str) -> None:
    fpath = _get_fpath(key)
    with open(fpath, "w") as f:
        yaml.dump(entries, f)
