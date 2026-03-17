from pathlib import Path
import re
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


def _discard_line(line: str) -> bool:
    """Determine if a line from the VTT file should be discarded."""
    return (
        line.startswith("WEBVTT")
        or line.strip() == ""
        or "-->" in line
        or line.startswith("Kind:")
        or line.startswith("Language:")
    )


def extract_text_from_vtt(fpath: Path) -> str:
    lines = []
    with open(fpath, encoding="utf-8") as f:
        # lines = f.readlines()
        # print(len(lines), "lines read from VTT file.")
        for line in f.readlines():
            # Skip header, timestamps, and empty lines
            if _discard_line(line):
                continue
            # Remove any inline tags (e.g., <c>...</c>)
            clean = re.sub(r"<.*?>", "", line).strip()
            if clean:
                lines.append(clean)
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:  # Only add if different from last
            deduped.append(line)

    # Join lines, removing any remaining empty ones
    return " ".join(l for l in deduped if l)
