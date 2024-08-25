"""File for the KingdomManager class."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from ..constants import (
    FPATH_KINGDOMS_CUSTOM,
    FPATH_KINGDOMS_LAST100,
    FPATH_KINGDOMS_RECOMMENDED,
    FPATH_KINGDOMS_TGG_DAILIES,
    PATH_ASSETS,
)
from .kingdom import Kingdom


def _load_tgg_winrate_data() -> dict[str, float]:
    win_data = pd.read_csv(
        PATH_ASSETS.joinpath("other/daily_hard_win_approx_percent.csv"),
        names=["date", "win_percent"],
        index_col=0,
    )
    return win_data["win_percent"].apply(lambda x: float(x.strip("%")) / 100).to_dict()


def _add_winrate(name: str, win_data: dict[str, float]) -> float:
    date = "-".join([f"{num:0>2}" for num in name.split("-")])
    return win_data.get(date, np.nan)


def custom_fillna(column: pd.Series) -> pd.Series:
    """Fill NaN values based on the type of the column."""
    if column.dtype == "object":
        if column.apply(lambda x: isinstance(x, list)).any():
            filled_column = column.apply(lambda x: x if isinstance(x, list) else [])
        elif column.apply(lambda x: isinstance(x, bool)).any():
            filled_column = column.fillna(False)
        else:
            filled_column = column.fillna("")
    elif column.dtype == "bool":
        filled_column = column.fillna(False)
    else:
        filled_column = column.fillna("")
    # Call infer_objects to handle the FutureWarning
    return filled_column.infer_objects(copy=False)  # type: ignore


class KingdomManager:
    """A Manager to keep track of the kingdoms currently loaded."""

    def __init__(self, load_last=False, max_amount: int | None = None):
        self.max_amount = max_amount
        self.kingdoms: list[dict[str, Any]] = []
        self.in_last_kingdom_mode = load_last
        if load_last:
            self.load_last_100_kingdoms()
        # self.load_recommended_kingdoms()

    def __len__(self):
        return len(self.kingdoms)

    def load_expansions(self):
        for kingdom in self.kingdoms:
            try:
                kingdom["expansions"] = Kingdom.from_dict(kingdom).expansions
            except TypeError:
                pass

    @classmethod
    def from_yaml(cls, yaml_str: str, max_amount=None) -> "KingdomManager":
        """Create a KingdomManager from a yaml file."""
        kingdom_manager = cls(max_amount=max_amount)
        data = yaml.safe_load(yaml_str)
        if data is not None:
            kingdom_manager.kingdoms = [kingdom_data for kingdom_data in data]
        return kingdom_manager

    @property
    def yaml_repr(self):
        return yaml.safe_dump(self.kingdoms)

    @property
    def dataframe_repr(self) -> pd.DataFrame:
        """Return the kingdoms as a DataFrame."""
        return pd.DataFrame(self.kingdoms).set_index("idx").apply(custom_fillna)

    def get_kingdom_by_name(self, kingdom_name: str) -> Kingdom | None:
        """Try to recover the given kingdom by its name."""
        if kingdom_name == "":
            return None
        kingdom_info = next(
            filter(lambda x: x.get("name", "") == kingdom_name, self.kingdoms), None
        )
        if kingdom_info is None:
            return None
        return Kingdom.from_dict(kingdom_info)

    def get_kingdom_by_id(self, kingdom_id: int) -> Kingdom | None:
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

    def load_tgg_dailies(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_TGG_DAILIES)
        win_data = _load_tgg_winrate_data()
        for k in self.kingdoms:
            k["winrate"] = _add_winrate(k["name"], win_data)

    def load_custom_kingdoms(self):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_CUSTOM)

    def save_last_100_kingdoms(self):
        if not self.in_last_kingdom_mode:
            print("Skipped saving last 100 kingdoms as not started in lastKingdomMode")
            return
        self.save_kingdoms_to_yaml(FPATH_KINGDOMS_LAST100)

    def load_kingdoms_from_yaml(self, file_path: str | Path):
        with open(file_path, "r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)
            if data is not None:
                self.kingdoms = [
                    kingdom_data for kingdom_data in data if "cards" in kingdom_data
                ]

    def save_kingdoms_to_yaml(self, file_path: str | Path):
        if isinstance(file_path, str):
            if "/" in file_path:
                file_path = Path(file_path)
            else:
                file_path = FPATH_KINGDOMS_RECOMMENDED.parent.joinpath(file_path)
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(self.yaml_repr)
