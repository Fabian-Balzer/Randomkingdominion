"""File for the KingdomManager class."""

import yaml
from random_kingdominion.constants import (
    FPATH_KINGDOMS_LAST100,
    FPATH_KINGDOMS_RECOMMENDED,
)

from .kingdom import Kingdom


class KingdomManager:
    """A Manager to keep track of the kingdoms currently loaded."""

    def __init__(self):
        self.kingdoms: list[Kingdom] = []
        self.load_last_100_kingdoms()
        # self.load_recommended_kingdoms()

    def get_kindom_by_id(self, kingdom_id: int) -> Kingdom | None:
        """Try to recover the given kingdom by its ID."""
        return next(filter(lambda x: x.idx == kingdom_id, self.kingdoms), None)

    def add_kingdom(self, kingdom: Kingdom):
        self.kingdoms.append(kingdom)
        self.save_last_100_kingdoms()

    def load_last_100_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_LAST100)

    def load_recommended_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_RECOMMENDED)

    def save_last_100_kingdoms(self):
        self.save_kingdoms_to_yaml(FPATH_KINGDOMS_LAST100)

    def load_kingdoms_from_yaml(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)
            if data is not None:
                self.kingdoms = [Kingdom(**kingdom_data) for kingdom_data in data]

    def save_kingdoms_to_yaml(self, file_path: str):
        data = [kingdom.get_dict_repr() for kingdom in self.kingdoms]
        yaml_stream = yaml.safe_dump(data)
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(yaml_stream)
