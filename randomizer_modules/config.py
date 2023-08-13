"""Functions to load from and save stuff to the config file."""


import json
from configparser import ConfigParser
from pathlib import Path

import numpy as np

from .constants import FPATH_RANDOMIZER_CONFIG, RENEWED_EXPANSIONS


class CustomConfigParser(ConfigParser):
    def get_expansions(self, add_renewed_bases=True) -> list[str]:
        """Turn the internally as string saved expansions into a list."""
        value = self.get("General", "Expansions")
        expansions = json.loads(value)
        if not add_renewed_bases:
            return expansions
        for renewed_exp in RENEWED_EXPANSIONS:
            # If e.g. Seaside, 2E is selected, also put Seaside in.
            if any(renewed_exp in exp for exp in expansions):
                expansions.append(renewed_exp)
        return expansions

    def set_expansions(self, expansions: list[str]):
        """Save the given list of expansions as a string in the config options."""
        filtered = [exp for exp in expansions if exp not in RENEWED_EXPANSIONS]
        self.set("General", "Expansions", json.dumps(filtered))

    def get_special_list(self, option_key: str) -> list[str]:
        """Turn the internally as string saved stuff into a list."""
        value = self.get("Specialization", option_key)
        return json.loads(value)

    def set_special_list(self, option_key: str, values: list[str]):
        """Save the given list of values as a string in the config options."""
        self.set("Specialization", option_key, json.dumps(values))

    def get_quality(self, qual_name) -> int:
        return self.getint("Qualities", "requested_" + qual_name)

    def set_quality(self, qual_name: str, value: int):
        self.set("Qualities", "requested_" + qual_name, str(value))

    def save_to_disk(self, fpath=FPATH_RANDOMIZER_CONFIG):
        """Convenience func to store the config options in the config file."""
        if isinstance(fpath, str):
            fpath = Path(fpath)
        with fpath.open("w", encoding="utf-8") as configfile:
            self.write(configfile)


def get_randomizer_config_options() -> CustomConfigParser:
    config = CustomConfigParser()
    config.read(FPATH_RANDOMIZER_CONFIG)
    return config
