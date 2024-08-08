"""File for the KingdomManager class."""

from pathlib import Path
from typing import Any

import yaml

from random_kingdominion.constants import (
    FPATH_KINGDOMS_LAST100,
    FPATH_KINGDOMS_RECOMMENDED,
)

from .kingdom import Kingdom


class KingdomManager:
    """A Manager to keep track of the kingdoms currently loaded."""

    def __init__(self, load_last=False, max_amount: int | None = None):
        self.max_amount = max_amount
        self.kingdoms: list[dict[str, Any]] = []
        self.in_last_kingdom_mode = load_last
        if load_last:
            self.load_last_100_kingdoms()
        # self.load_recommended_kingdoms()

    @classmethod
    def from_yaml(cls, yaml_str: str, max_amount=None) -> "KingdomManager":
        """Create a KingdomManager from a yaml file."""
        kingdom_manager = cls(max_amount=max_amount)
        data = yaml.safe_load(yaml_str)
        if data is not None:
            kingdom_manager.kingdoms = [kingdom_data for kingdom_data in data]
        return kingdom_manager

    def __len__(self):
        return len(self.kingdoms)

    @property
    def yaml_repr(self):
        return yaml.safe_dump(self.kingdoms)

    def get_kindom_by_id(self, kingdom_id: int) -> Kingdom | None:
        """Try to recover the given kingdom by its ID."""
        kingdom_info = next(
            filter(lambda x: x["idx"] == kingdom_id, self.kingdoms), None
        )
        if kingdom_info is None:
            return None
        return Kingdom.from_dict(kingdom_info)

    def add_kingdom(self, kingdom: Kingdom, try_save: bool = True):
        self.kingdoms.append(kingdom.get_dict_repr())
        if try_save:
            self.save_last_100_kingdoms()

    def load_last_100_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_LAST100)

    def load_recommended_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_RECOMMENDED)

    def save_last_100_kingdoms(self):
        if not self.in_last_kingdom_mode:
            print("Skipped saving last 100 kingdoms as not started in lastKingdomMode")
        self.save_kingdoms_to_yaml(FPATH_KINGDOMS_LAST100)

    def load_kingdoms_from_yaml(self, file_path: str | Path):
        with open(file_path, "r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)
            if data is not None:
                self.kingdoms = [kingdom_data for kingdom_data in data]

    def save_kingdoms_to_yaml(self, file_path: str | Path):
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(self.yaml_repr)
