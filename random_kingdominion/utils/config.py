"""Functions to load from and save stuff to the config file."""


import json
from configparser import ConfigParser
from pathlib import Path

from ..constants import FPATH_RANDOMIZER_CONFIG, RENEWED_EXPANSIONS


def add_renewed_base_expansions(expansions: list[str]) -> list[str]:
    """For the given list of expansions (e.g. [Seaside 2E, Base 1E, Menagerie]),
    add the underlying common expansions.
    """
    for renewed_exp in RENEWED_EXPANSIONS:
        # If e.g. Seaside, 2E is selected, also put Seaside in.
        if any(renewed_exp in exp for exp in expansions):
            expansions.append(renewed_exp)
    return expansions


class CustomConfigParser(ConfigParser):
    def __init__(self):
        super().__init__()
        self.read(FPATH_RANDOMIZER_CONFIG)

    def getlist(self, section: str, key: str) -> list[str]:
        """Turn the internally as string saved stuff into a list."""
        value = self.get(section, key)
        return json.loads(value)

    def setlist(self, section: str, key: str, listval: list[str]):
        """Save the given list of values as a string in the config options."""
        self.set(section, key, json.dumps(listval))

    def get_expansions(self, add_renewed_bases=True) -> list[str]:
        """Turn the internally as string saved expansions into a list."""
        expansions = self.getlist("General", "Expansions")
        if not add_renewed_bases:
            return expansions
        return add_renewed_base_expansions(expansions)

    def set_expansions(self, expansions: list[str]):
        """Save the given list of expansions as a string in the config options."""
        filtered = [exp for exp in expansions if exp not in RENEWED_EXPANSIONS]
        self.setlist("General", "Expansions", filtered)

    def get_requested_quality(self, qual_name: str) -> int:
        return self.getint("Qualities", "requested_" + qual_name)

    def set_requested_quality(self, qual_name: str, value: int):
        self.set("Qualities", "requested_" + qual_name, str(value))

    def get_forbidden_quality(self, qual_name: str) -> bool:
        return self.getboolean("Qualities", "forbid_" + qual_name)

    def set_forbidden_quality(self, qual_name: str, value: bool):
        self.set("Qualities", "forbid_" + qual_name, str(value))

    def save_to_disk(self, fpath=FPATH_RANDOMIZER_CONFIG):
        """Convenience func to store the config options in the config file."""
        if isinstance(fpath, str):
            fpath = Path(fpath)
        with fpath.open("w", encoding="utf-8") as configfile:
            self.write(configfile)

