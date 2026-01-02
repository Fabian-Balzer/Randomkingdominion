"""File for the KingdomManager class."""

import json
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
import yaml

from ..constants import (
    FPATH_KINGDOMS_CAMPAIGNS,
    FPATH_KINGDOMS_FABI_RECSETS,
    FPATH_KINGDOMS_LAST100,
    FPATH_KINGDOMS_RECOMMENDED,
    FPATH_KINGDOMS_TGG_DAILIES,
    PATH_ASSETS,
    PATH_MAIN,
)
from ..logger import LOGGER
from .kingdom import Kingdom

try:
    pd.set_option("future.no_silent_downcasting", True)
except pd.errors.OptionError:
    pass


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

    def __init__(
        self, load_last=False, max_amount: int | None = None, add_yt_note_basics=False
    ):
        """Initialize the KingdomManager."""
        self.max_amount = max_amount
        self.kingdoms: list[dict[str, Any]] = []
        self.in_last_kingdom_mode = load_last
        self.add_yt_note_basics = add_yt_note_basics
        if load_last:
            self.load_last_100_kingdoms()
        # self.load_recommended_kingdoms()

    def __len__(self):
        return len(self.kingdoms)

    def _add_kingdoms_from_txt(
        self,
        ftype: Literal["tgg_dailies", "fabi_recsets", "campaigns"],
        do_assertion=True,
    ):
        for k in self.kingdoms:
            if "/" in k["name"]:
                year = k["name"][-2:]
                k["name"] = f"20{year}-" + k["name"].replace("/", "-")[:-3]
        with open(
            PATH_MAIN.joinpath(f"scripts/data/new_kingdoms/{ftype}.txt"), "r"
        ) as f:
            dombot_descs = f.read().split("\n")[::-1]
        has_added_kingdoms = False
        for line in dombot_descs:
            if line.strip() == "":
                continue
            name, kingdom_str = line.split("---")[:2]
            if name in [k["name"] for k in self.kingdoms] or kingdom_str.strip() == "":
                continue
            has_added_kingdoms = True
            k = Kingdom.from_dombot_csv_string(kingdom_str)
            k.name = name
            if len(parts := (line.split("---"))) > 2:
                if ftype == "fabi_recsets":
                    k.notes = '{"Comment": "' + parts[2] + '"'
                    if len(parts) > 3:
                        k.notes += ', "Previous Results": "' + parts[3] + '"'
                else:
                    notes = parts[2]
                    k.notes += notes
            elif self.add_yt_note_basics:
                k.notes = {  # type: ignore
                    "crucial_cards": [],
                    "name": "",
                    "subtitle": "",
                    "openings": [
                        {
                            "type": "4/3|3/4",
                            "t1": "",
                            "t1_csos": [],
                            "t2": "",
                            "t2_csos": [],
                            "grade": "",
                        },
                        {
                            "type": "5/2|2/5",
                            "t1": "",
                            "t1_csos": [],
                            "t2": "",
                            "t2_csos": [],
                            "grade": "",
                        },
                    ],
                    "ending": [],
                    "points": [],
                    "turns": [],
                    "link": "",
                }
            try:
                assert (
                    k.is_valid
                ), f"{k.invalidity_reasons}, {k.name}, {k.cards}, {k.notes}"
            except AssertionError as e:
                if do_assertion:
                    raise (e)
                LOGGER.info(f"Unrecognized: {k.name}, {k.cards}, {k.notes}")
            self.kingdoms.insert(0, k.get_dict_repr())
            LOGGER.info(f"Added {k.name}")
        if not has_added_kingdoms:
            return
        savepath = {
            "tgg_dailies": FPATH_KINGDOMS_TGG_DAILIES,
            "fabi_recsets": FPATH_KINGDOMS_FABI_RECSETS,
            "campaigns": FPATH_KINGDOMS_CAMPAIGNS,
        }[ftype]
        self.save_kingdoms_to_yaml(savepath)

    def load_expansions(self):
        for kingdom in self.kingdoms:
            try:
                kingdom["expansions"] = Kingdom.from_dict(kingdom).expansions
            except TypeError:
                pass

    def load_qualities(self):
        for kingdom in self.kingdoms:
            if "qualities" in kingdom:
                continue
            try:
                kingdom["qualities"] = Kingdom.from_dict(kingdom).total_qualities
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
        """Return the kingdoms as a DataFrame.

        Use 'load_qualities' on the manager first to add the 'qualities' columns."""
        return pd.DataFrame(self.kingdoms).set_index("idx").apply(custom_fillna)

    def get_dataframe_repr_with_unpacked_notes(self):
        """Unpack the notes for and include them as columns in dataframe. Add 'notes_' prefix if col would otherwise exist."""
        df = self.dataframe_repr
        all_notes_keys = set([k for keys in df["notes"] for k in keys])
        notes_col = df["notes"]
        for k in all_notes_keys:
            colname = k if k not in df.columns else f"notes_{k}"
            df[colname] = notes_col.apply(
                lambda x: x.get(k, None) if isinstance(x, dict) else None
            )
        return df

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

    def get_kingdom_by_index(self, kingdom_index: int) -> Kingdom:
        """Try to recover the given kingdom by its index."""
        return Kingdom.from_dict(self.kingdoms[kingdom_index])

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

    def load_tgg_dailies(self, reload=False, sort=True):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_TGG_DAILIES, sort=sort)
        if reload:
            self._add_kingdoms_from_txt("tgg_dailies")
        win_data = _load_tgg_winrate_data()
        for k in self.kingdoms:
            k["winrate"] = _add_winrate(k["name"], win_data)

    def load_fabi_recsets_kingdoms(self, reload=False):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_FABI_RECSETS)
        if reload:
            self._add_kingdoms_from_txt("fabi_recsets")

    def load_campaigns(self, reload=False, do_assertion=True, curated_only=False):
        self.load_kingdoms_from_yaml(FPATH_KINGDOMS_CAMPAIGNS)
        if curated_only:
            self.kingdoms = [
                kingdom
                for kingdom in self.kingdoms
                if not kingdom.get("is_grand_campaign", False)
            ]
        if reload:
            self._add_kingdoms_from_txt("campaigns", do_assertion=do_assertion)

    def save_last_100_kingdoms(self):
        if not self.in_last_kingdom_mode:
            print("Skipped saving last 100 kingdoms as not started in lastKingdomMode")
            return
        self.save_kingdoms_to_yaml(FPATH_KINGDOMS_LAST100)

    def load_kingdoms_from_yaml(self, file_path: str | Path, sort: bool = False):
        # In the future, I might want to use pickling or a database for faster loading
        with open(file_path, "r", encoding="utf-8") as yaml_file:
            data = yaml.safe_load(yaml_file)
            if data is not None:
                self.kingdoms = [
                    kingdom_data for kingdom_data in data if "cards" in kingdom_data
                ]
            if sort:
                self.kingdoms.sort(key=lambda k: k.get("name", ""), reverse=True)

    def save_kingdoms_to_yaml(self, file_path: str | Path):
        if isinstance(file_path, str):
            if "/" in file_path:
                file_path = Path(file_path)
            else:
                file_path = FPATH_KINGDOMS_RECOMMENDED.parent.joinpath(file_path)
        with open(file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(self.yaml_repr)
