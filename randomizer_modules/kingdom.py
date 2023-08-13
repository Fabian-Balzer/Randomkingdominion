"""File to contain the KingdomQualities and the Kingdom classes"""
import random
import time
from math import ceil
from typing import Optional

import numpy as np
import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from .base_widgets import KingdomCardImageWidget
from .config import CustomConfigParser
from .constants import PATH_MAIN, QUALITIES_AVAILABLE, EmptyError
from .utils import filter_column, get_mask_for_listlike_col_to_contain_any


def _calculate_total_quality(values: list[int]) -> int:
    # Initialize array with zeros representing 0, 1, 2, 3, 4
    counts = np.zeros(5)

    # If there are 5-i values of the same thing, increment the value count of the next one
    # e.g. a list of [1, 1, 1, 1, 2] should be counted as two 2s. because there are four
    # ones, three 2s will be counted as a single 3, and two 3s will yield a 4.
    for i in range(4):
        counts[i] += values.count(i)
        if i == 0:
            continue
        counts[i + 1] += counts[i] // (5 - i)

    # Look where the first nonzero value sits.
    total_quality_value = np.nonzero(counts)[0][-1]

    return total_quality_value


def _get_total_quality(qual_name: str, kingdom_df: pd.DataFrame) -> int:
    value_list = kingdom_df[qual_name + "_quality"].to_list()
    return _calculate_total_quality(value_list)


class Kingdom:
    card_df = None
    history = []

    def __init__(
        self,
        all_cards: pd.DataFrame,
        config: CustomConfigParser,
        kingdom_cards: Optional[list[str]] = None,
        landscapes: Optional[list[str]] = None,
        ally: str = None,
    ):
        self.total_qualities: dict[str, int] = {qual: 0 for qual in QUALITIES_AVAILABLE}
        self.config = config
        self.card_df = all_cards
        # Each kingdom at first does not contain any cards.
        # They need to be added later.
        self.kingdom_cards: list[str] = kingdom_cards if kingdom_cards else []
        self.landscapes: list[str] = landscapes if landscapes else []
        self.ally = ally if ally else ""
        self.non_supply: list[str] = []
        self.id = time.time_ns()
        self.history.append(self)

        self.special_targets = {
            "Bane": None,
            "Obelisk": None,
            "Mouse": None,
            "Druid Boons": None,
        }

    def __str__(self):
        s = self.get_kingdom_df().to_string(
            columns=["Name", "Cost", "Expansion"], index=False
        )
        quality_summary = "\n".join(
            f"Total {qual.capitalize() + ' quality:':20}\t{val}"
            for qual, val in self.total_qualities.items()
        )
        s += "\n" + quality_summary + "\n"
        s += "CSV representation:\n\n" + self.get_csv_representation()
        return s

    def get_csv_representation(self):
        """TODO: proper Bane/Trait/Mouse/Druid Boons representation"""
        return ", ".join(card for card in self.get_kingdom_df()["Name"])

    def set_quality_values(self):
        """Update the quality values for this kingdom by summing them up."""
        for qual in QUALITIES_AVAILABLE:
            val = _get_total_quality(qual, self.get_kingdom_df())
            self.total_qualities[qual] = val

    def get_kingdom_df(self) -> pd.DataFrame:
        """Get a dataframe representing only the kingdom cards/landscapes."""
        df = self.card_df[
            self.card_df["Name"].isin(
                self.kingdom_cards + self.landscapes + [self.ally]
            )
        ].sort_values(
            by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"],
            ascending=[False, False, False, True, True],
        )
        return df

    def get_kingdom_card_df(self) -> pd.DataFrame:
        """Return the subset of the kingdom containing only the cards."""
        df = self.get_kingdom_df()
        return df[df["Name"].isin(self.kingdom_cards)]

    def get_landscape_df(self) -> pd.DataFrame:
        """Return the subset of the kingdom containing only the landscapes"""
        df = self.get_kingdom_df()
        return df[df["Name"].isin(self.landscapes)]

    def get_all_ally_df(self) -> pd.DataFrame:
        """Retrieve all possible allies"""
        return self.card_df[self.card_df["Types"].apply(lambda x: "Ally" in x)]

    def get_ally_df(self) -> pd.DataFrame:
        """Get the Ally that was chosen for this kingdom"""
        df = self.get_kingdom_df()
        return df[df["Types"].apply(lambda x: "Ally" in x)]

    def randomize(self, rerolled_cards: list[str]):
        """Perform randomization with an attempt to discard all formerly rerolled
        cards."""
        try:
            draw_pool = self.get_draw_pool(rerolled_cards)
        except EmptyError:
            return
        num_objs_to_draw = self.config.getint(
            "General", "num_cards"
        ) + self.config.getint("General", "num_landscapes")
        for _ in range(num_objs_to_draw):
            new_pick_name = self.pick_card_or_landscape(draw_pool)
            draw_pool = draw_pool[draw_pool["Name"] != new_pick_name]
            self.set_quality_values()
        # Pick a bane card in case the young witch is amongst the picks:
        if "Young Witch" in self.kingdom_cards:
            new_pick_name = self.pick_bane_card(draw_pool)
            draw_pool = draw_pool[draw_pool["Name"] != new_pick_name]
            self.set_quality_values()
        # In case just the ally has been rerolled:
        if (
            self.ally == ""
            and len(
                self.get_kingdom_card_df()[
                    self.get_kingdom_card_df()["Types"].apply(lambda x: "Liaison" in x)
                ]
            )
            > 0
        ):
            self.ally = self.get_all_ally_df().sample(n=1).iloc[0]["Name"]

    def get_draw_pool(self, rerolled_cards: list[str]):
        # Discard everything not contained in the requested sets
        pool = filter_column(self.card_df, "Expansion", self.config.get_expansions())
        allowed_types = self.config.get_special_list("attack_types")
        mask = get_mask_for_listlike_col_to_contain_any(
            pool.attack_types, allowed_types, empty_too=True
        )
        pool = pool[mask]
        # Discard all non-supply-cards as we don't need them to draw from
        pool = pool[pool["IsInSupply"] | pool["IsLandscape"]]
        pool = pool[~np.isin(pool.Name, self.kingdom_cards + self.landscapes)]
        if len(pool) == 0:
            raise EmptyError
        # Make sure to not include rerolled cards, but reconsider them if no other cards are left:
        not_rerolled_mask = ~np.isin(pool.Name, rerolled_cards)
        if np.sum(not_rerolled_mask) > 0:
            pool = pool[not_rerolled_mask]
        return pool

    def pick_card_or_landscape(self, draw_pool: pd.DataFrame) -> str:
        """Adds a card or landscape fitting the needs to the picked selection"""
        narrowed_pool = self.create_narrowed_pool(draw_pool)
        if len(narrowed_pool) > 0:
            pick = narrowed_pool.sample(n=1)
        else:
            # print("Could not find any more cards/landscapes to draw from.")
            return ""
        name = pick.iloc[0]["Name"]
        if pick.iloc[0]["IsLandscape"]:
            self.landscapes.append(name)
        else:
            self.kingdom_cards.append(name)
        if self.ally == "" and "Liaison" in pick.iloc[0]["Types"]:
            self.ally = self.get_all_ally_df().sample(n=1).iloc[0]["Name"]
        return name
        # TODO: Append Associated cards

    def pick_bane_card(self, draw_pool: pd.DataFrame) -> str:
        pool = self.create_narrowed_pool(
            draw_pool, exclude_picked_quantities=False, cost_limits=["$2", "$3"]
        )
        if len(pool) > 0:
            pick = pool.sample(n=1)
        else:
            # print("Could not find any more cards/landscapes to draw from.")
            return ""
        name = pick.iloc[0]["Name"]
        self.kingdom_cards.append(name)
        self.special_targets["Bane"] = name
        return name

    def _limit_pool_to_remaining_requirements(
        self, draw_pool: pd.DataFrame
    ) -> pd.DataFrame:
        """Exclude Kingdom cards and landscapes if the requested quantities have already been picked."""
        if len(self.landscapes) == self.config.getint("General", "num_landscapes"):
            draw_pool = draw_pool[~draw_pool["IsLandscape"]]
        # Discard any secondary ways:
        if self.contains_way():
            draw_pool = draw_pool[draw_pool["Types"].apply(lambda x: "Way" not in x)]
        if len(self.kingdom_cards) == self.config.getint("General", "num_cards"):
            draw_pool = draw_pool[draw_pool["IsLandscape"]]
        return draw_pool

    def create_narrowed_pool(
        self,
        draw_pool: pd.DataFrame,
        exclude_picked_quantities=True,
        cost_limits: list[str] | None = None,
    ):
        """Creates a pool of cards to pick from.
        Discards cards that have been rerolled unless this would imply that none are left.
        """
        if exclude_picked_quantities:
            draw_pool = self._limit_pool_to_remaining_requirements(draw_pool)
        else:
            draw_pool = draw_pool[~draw_pool["IsLandscape"]]
        if cost_limits:
            draw_pool = draw_pool[draw_pool.Cost.isin(cost_limits)]
        # TODO: Add Rerolled cards in case this leads to nothing
        # Create a dictionary for args that still require fulfilment (i. e. VQ is set to 7-4 if the kingdom already contains a VQ of 4)
        choices = {}
        for qual in self.total_qualities:
            val = self.config.get_quality("min_" + qual) - self.total_qualities[qual]
            if val > 0:
                choices[qual] = val
        if len(choices) > 0:  # pick a quality defining this draw
            # weighting the choices by urgency
            qual = random.choice([k for k in choices for x in range(choices[k])])
            min_qual_val = random.randint(1, min(6, choices[qual]))
            defining_quality = qual + "_quality"
            before_narrowing = draw_pool
            draw_pool = draw_pool[draw_pool[defining_quality] >= min_qual_val]
            # If the constraints are too much, do not constrain it.
            if len(draw_pool) == 0:
                draw_pool = before_narrowing
        return draw_pool

    def contains_way(self) -> bool:
        """Returns wether the kingdom already contains a way."""
        df = self.get_kingdom_df()
        return len(df[df["Types"].apply(lambda x: "Way" in x)]) > 0


class KingdomDisplayWidget(QW.QWidget):
    """Display all the kingdom cards (but not the landscapes) in
    an array similar to how DomBot provides it.
    Also hosts the buttons for rerolling which need to be
    reconnected externally."""

    def __init__(self):
        super().__init__()
        lay = QW.QGridLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(0)
        lay.setAlignment(QC.Qt.AlignTop | QC.Qt.AlignLeft)
        self.grid_layout = lay
        self.setAutoFillBackground(True)
        # palette = self.palette()
        # palette.setColor(self.backgroundRole(), QC.Qt.black)
        # self.setPalette(palette)

        # Dictionary to contain buttons to be connected for the rerolling
        self.reroll_button_dict = {}

    def replace_images(
        self,
        kingdom: Kingdom,
    ):
        """Resets the widget by clearing the grid layout and displaying
        the kingdom"""
        while self.grid_layout.count():
            item = self.grid_layout.itemAt(0)
            self.grid_layout.removeItem(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.reroll_button_dict = {}

        # Recreate the image grid
        self.display_kingdom_cards(kingdom)
        self.display_kingdom_landscapes(kingdom)

    def display_kingdom_cards(self, kingdom: Kingdom):
        kingdom_df = kingdom.get_kingdom_card_df()
        inverted_specialities = {v: k for k, v in kingdom.special_targets.items()}
        num_rows = 2
        num_cols = ceil(len(kingdom_df) / num_rows)
        for row in range(num_rows):
            for col in range(num_cols):
                index = row * num_cols + col
                if index >= len(kingdom_df):
                    continue
                card = kingdom_df.iloc[index]
                special_text = (
                    inverted_specialities[card.Name]
                    if card.Name in inverted_specialities
                    else None
                )
                wid = KingdomCardImageWidget(card, special_text=special_text)
                self.reroll_button_dict[card.Name] = wid.reroll_button
                self.grid_layout.addWidget(wid, row, col)

    def display_kingdom_landscapes(self, kingdom: Kingdom):
        kingdom_df = kingdom.get_landscape_df()

        num_cols = len(kingdom_df)
        for col in range(num_cols):
            landscape = kingdom_df.iloc[col]
            wid = KingdomCardImageWidget(landscape)
            self.reroll_button_dict[landscape.Name] = wid.reroll_button
            self.grid_layout.addWidget(wid, 2, col * 2, 1, 2)
