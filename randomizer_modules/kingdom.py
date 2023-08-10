"""File to contain the KingdomQualities and the Kingdom classes"""
import random
import time
from typing import Optional

import numpy as np
import pandas as pd
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW

from .base_widgets import KingdomCardImageWidget
from .config import CustomConfigParser
from .constants import PATH_MAIN, QUALITIES_AVAILABLE, EmptyError
from .utils import filter_column, is_in_requested_types


class KingdomQualities(dict):
    def __init__(self, default=True, *args, **kwargs):
        defaultkeys = [qual.lower() for qual in QUALITIES_AVAILABLE]
        if default:
            for qual in defaultkeys:
                self["min_" + qual] = 0
        else:
            for qual in defaultkeys:
                self["min_" + qual] = kwargs["qual_dict"][qual]
        kwargs.clear()
        super(KingdomQualities, self).__init__(*args, **kwargs)

    def reset_values(self):
        for qual in self:
            self[qual] = 0

    def prettify(self):
        return "\n".join(
            f"{qual.capitalize() + ' quality:':20}\t{val}" for qual, val in self.items()
        )


class Kingdom:
    card_df = None
    history = []

    def __init__(
        self,
        all_cards,
        config: CustomConfigParser,
        kingdom_cards: Optional[list[str]] = None,
        landscapes: Optional[list[str]] = None,
        ally: str = None,
    ):
        self.qualities = KingdomQualities()
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

    def __str__(self):
        s = self.get_kingdom_df().to_string(
            columns=["Name", "Cost", "Expansion"], index=False
        )
        s += "\n" + self.qualities.prettify() + "\n"
        s += ", ".join(card for card in self.get_kingdom_df()["Name"])
        return s

    def set_quality_values(self):
        for qual in QUALITIES_AVAILABLE:
            val = sum(self.get_kingdom_df()[qual + "_quality"])
            self.qualities["min_" + qual] = val

    def get_kingdom_df(self):
        df = self.card_df[
            self.card_df["Name"].isin(
                self.kingdom_cards + self.landscapes + [self.ally]
            )
        ].sort_values(
            by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"],
            ascending=[False, False, False, True, True],
        )
        return df

    def get_kingdom_card_df(self):
        df = self.get_kingdom_df()
        return df[df["Name"].isin(self.kingdom_cards)]

    def get_landscape_df(self):
        df = self.get_kingdom_df()
        return df[df["Name"].isin(self.landscapes)]

    def get_all_ally_df(self):
        return self.card_df[self.card_df["Types"].apply(lambda x: "Ally" in x)]

    def get_ally_df(self):
        df = self.get_kingdom_df()
        return df[df["Types"].apply(lambda x: "Ally" in x)]

    def randomize(self, rerolled_cards: list[str]):
        try:
            draw_pool = self.get_draw_pool(rerolled_cards)
        except EmptyError:
            return
        num_objs_to_draw = self.config.getint(
            "General", "num_cards"
        ) + self.config.getint("General", "num_landscapes")
        for _ in range(num_objs_to_draw):
            pick = self.pick_card_or_landscape(draw_pool)
            draw_pool = draw_pool[draw_pool["Name"] != pick]
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
        pool = pool.loc[
            pool["attack_types"].apply(
                lambda x: is_in_requested_types(
                    x, self.config.get_special_list("attack_types")
                )
            )
        ]
        # pool = filter_column(pool, "AttackType", request_dict["attack_types"])
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

    def pick_card_or_landscape(self, draw_pool: pd.DataFrame):
        """Adds a card or landscape fitting the needs to the picked selection"""
        narrowed_pool = self.create_narrowed_pool(draw_pool)
        if len(narrowed_pool) > 0:
            pick = narrowed_pool.sample(n=1)
        else:
            print("Could not find any more cards/landscapes to draw from.")
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

    def create_narrowed_pool(self, draw_pool: pd.DataFrame):
        """Creates a pool of cards to pick from. Excludes Kingdom cards and landscapes if the requested quantities have already been picked.
        Discards cards that have been rerolled unless this would imply that none are left.
        """
        if len(self.landscapes) == self.config.getint("General", "num_landscapes"):
            draw_pool = draw_pool[~draw_pool["IsLandscape"]]
        # Discard any secondary ways:
        if self.contains_way():
            draw_pool = draw_pool[draw_pool["Types"].apply(lambda x: "Way" not in x)]
        if len(self.kingdom_cards) == self.config.getint("General", "num_cards"):
            draw_pool = draw_pool[draw_pool["IsLandscape"]]
        # TODO: Add Rerolled cards in case this leads to nothing
        # Create a dictionary for args that still require fulfilment (i. e. VQ is set to 7-4 if the kingdom already contains a VQ of 4)
        choices = {}
        for qual in self.qualities:
            val = self.config.get_quality(qual) - self.qualities[qual]
            if val > 0:
                choices[qual] = val
        if len(choices) > 0:  # pick a quality defining this draw
            # weighting the choices by urgency
            qual = random.choice([k for k in choices for x in range(choices[k])])
            min_qual_val = random.randint(1, min(6, choices[qual]))
            defining_quality = qual.split("min_")[1] + "_quality"
            before_narrowing = draw_pool
            draw_pool = draw_pool[draw_pool[defining_quality] >= min_qual_val]
            # If the constraints are too much, do not constrain it.
            if len(draw_pool) == 0:
                draw_pool = before_narrowing
        return draw_pool

    def contains_way(self):
        """Returns wether the kingdom already contains a way."""
        df = self.get_kingdom_df()
        return len(df[df["Types"].apply(lambda x: "Way" in x)]) > 0


class ShortKingdomCardDisplay(QW.QWidget):
    """Display all the kingdom cards (but not the landscapes) in
    an array similar to how DomBot provides it."""

    def __init__(self, kingdom: Kingdom):
        super().__init__()
        lay = QW.QGridLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(0)
        num_cols = int(len(kingdom.kingdom_cards) / 2)
        for i in range(num_cols):
            for j in range(2):
                impath = PATH_MAIN.joinpath(
                    kingdom.kingdom_cards.iloc[i + j * num_cols]["ImagePath"]
                )
                wid = KingdomCardImageWidget(str(impath))
                lay.addWidget(wid, j, i)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QC.Qt.black)
        self.setPalette(palette)
