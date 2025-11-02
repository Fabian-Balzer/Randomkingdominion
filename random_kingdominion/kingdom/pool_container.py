"""File to contain the PoolContainer class necessary for randomization"""

import random
from typing import Literal

import numpy as np
import pandas as pd

from ..constants import ALL_CSOS, QUALITIES_AVAILABLE, SPECIAL_QUAL_TYPES_AVAILABLE
from ..cso_frame_utils import (
    add_weight_column,
    get_sub_df_for_special_card,
    get_sub_df_for_true_landscape,
    get_sub_df_of_categories,
    listlike_contains_any,
    sample_single_cso_from_df,
)
from ..utils.config import CustomConfigParser, add_renewed_base_expansions


class PoolContainer:
    """A class to set up a draw pool from which one can pick new cards.
    The pool needs to be set up freshly for each new randomization.
    On a basic level, it containts an initial pool which is a pandas
    DataFrame"""

    def __init__(
        self, config: CustomConfigParser, rerolled_csos: list[str] | None = None
    ):
        rerolled_csos = rerolled_csos if rerolled_csos else []
        self.config = config
        self.eligible_expansions = self._determine_eligible_expansions()

        self.main_pool: pd.DataFrame = self.get_initial_draw_pool(rerolled_csos)

    def drop_rerolled_csos(self, rerolled_csos: list[str]):
        """Drop the given rerolled CSOs from the main pool."""
        self.main_pool = self.main_pool.drop(rerolled_csos, errors="ignore")

    def get_initial_draw_pool(
        self, rerolled_csos: list[str], ignore_expansions: bool = False
    ) -> pd.DataFrame:
        """Create the initial draw pool for the kingdom.
        This is the overarching one that is used for all of the draws,
        so here we filter for requested expansions, allowed attack types,
        cards that are in the supply, and remove all cards with forbidden
        qualities.
        """
        # Reduce the complete pool to the requested expansions:
        pool = (
            get_sub_df_of_categories(ALL_CSOS, "Expansion", self.eligible_expansions)
            if not ignore_expansions
            else ALL_CSOS.copy()
        )
        if len(pool) == 0:
            return pool

        # Reduce the pool to exclude any sorts of quality types that are not wanted
        for qual in SPECIAL_QUAL_TYPES_AVAILABLE:
            excluded_types = self.config.getlist("Qualities", f"forbidden_{qual}_types")
            pool = pool[~listlike_contains_any(pool[qual + "_types"], excluded_types)]

        # Reduce the pool to exclude any landscapes that are not wanted
        _allowed_landscapes = self.config.getlist(
            "Landscapes", "allowed_landscape_types"
        )
        pool = pool[
            ~pool["IsLandscape"]
            | listlike_contains_any(pool["Types"], _allowed_landscapes)
        ]
        _excluded_card_types = self.config.getlist(
            "Specialization", "excluded_card_types"
        ) + ["Ruins"]
        pool = pool[
            pool["IsLandscape"]
            | ~listlike_contains_any(pool["Types"], _excluded_card_types)
        ]

        pool = self._exclude_forbidden_qualities(pool)

        # Discard all non-supply-non-landscape-non-ally cards as we don't need them to draw from
        pool = pool[pool["IsInSupply"] | pool["IsExtendedLandscape"]]

        # Drop bans and rerolls
        banned_csos = self.config.getlist("General", "banned_csos")
        pool = pool.drop(rerolled_csos + banned_csos, errors="ignore")

        # Set the weights to account for liked and disliked cards
        disliked = self.config.getlist("General", "disliked_csos")
        liked = self.config.getlist("General", "liked_csos")
        dislike_weight = self.config.getfloat("General", "dislike_factor")
        like_weight = self.config.getfloat("General", "like_factor")
        pool = add_weight_column(pool, disliked, liked, dislike_weight, like_weight)
        return pool

    def _exclude_forbidden_qualities(self, pool: pd.DataFrame) -> pd.DataFrame:
        """Filter the pool to exclude any quality that is not wanted."""
        for qual in QUALITIES_AVAILABLE:
            if self.config.get_forbidden_quality(qual):
                pool = pool[pool[qual + "_quality"] == 0]
        return pool

    def _determine_eligible_expansions(self) -> list[str]:
        """From all of the expansions the user has selected, sub-select a number
        that corresponds to the one the user has chosen."""
        user_expansions = self.config.get_expansions(add_renewed_bases=False)
        exp_limit_enabled = self.config.getboolean("Expansions", "enable_max")
        max_num_expansions = self.config.getint("Expansions", "max_num_expansions")
        if (
            not exp_limit_enabled
            or max_num_expansions == 0
            or max_num_expansions >= len(user_expansions)
        ):
            return add_renewed_base_expansions(user_expansions)
        sampled_expansions = random.sample(user_expansions, k=max_num_expansions)
        return add_renewed_base_expansions(sampled_expansions)

    def _narrow_pool_for_quality(
        self, pool: pd.DataFrame, qualities_so_far: dict[str, int]
    ):
        """Pick out the most urgent of the qualities and lower the pool size, as long as cards
        remain afterwards.
        Otherwise try to reduce for the next most urgent quality, and so on.
        """
        unfulfilled_qualities = self._get_unfulfilled_qualities(qualities_so_far)
        for qual, diff in unfulfilled_qualities:
            # If the difference is big, try to sometimes also pick only cards with higher
            # values in that category
            minimum_requirement = random.randint(1, min(diff, 3))
            mask = pool[qual + "_quality"] >= minimum_requirement
            if np.sum(mask) > 0:
                return pool[mask]
        return pool

    def _get_unfulfilled_qualities(
        self, qualities_so_far: dict[str, int]
    ) -> list[tuple[str, int]]:
        """Determine which qualities are needed the most, and return a dictionary
        that maps the quality names to the amount they are needed.

        Parameters
        ----------
        qualities_so_far : dict[str, int]
            The qualities that are making up the currently randomized kingdom

        Returns
        -------
        list[str]
            A list of the qualities that still need to fulfil their requirements,
            sorted by their urgency
        """
        # Calculate the difference to the required kingdom quality
        diffs = {
            qual: self.config.get_requested_quality(qual) - val
            for qual, val in qualities_so_far.items()
        }
        # Exclude all values where the difference is <= 0,
        # because in these cases we do not want to pick for them.
        # Also, exclude the forbidden ones as it wouldn't make sense to narrow the pool down to them
        diffs = {
            qual: val
            for qual, val in diffs.items()
            if val > 0 and not self.config.get_forbidden_quality(qual)
        }
        sorted_quals = sorted(diffs, key=lambda x: diffs[x], reverse=True)
        return [(qual, diffs[qual]) for qual in sorted_quals]

    def pick_next_card(
        self,
        qualities_so_far: dict[str, int],
        special_card_to_pick_for: (
            Literal[
                "ferryman",
                "way_of_the_mouse",
                "young_witch",
                "riverboat",
                "approaching_army",
            ]
            | None
        ) = None,
    ) -> str:
        """Pick the next card while also considering the required qualities."""
        try:
            pool = get_sub_df_for_special_card(self.main_pool, special_card_to_pick_for)
        except KeyError:
            return ""
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        self.main_pool = self.main_pool.drop(pick)
        if special_card_to_pick_for in ["way_of_the_mouse", "riverboat"]:
            if (ancestor := ALL_CSOS.loc[pick]["ParentPile"]) != "":  # type: ignore
                try:
                    self.main_pool.drop(ancestor)  # type: ignore
                except KeyError:
                    pass
        return pick

    def pick_next_landscape(
        self, qualities_so_far: dict[str, int], exclude_ways: bool
    ) -> str:
        """Pick the next landscape while also considering the required qualities."""
        pool = get_sub_df_for_true_landscape(self.main_pool, exclude_ways)
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        self.main_pool = self.main_pool.drop(pick)
        return pick

    def pick_ally(self, qualities_so_far: dict[str, int]) -> str:
        """Pick an ally while also considering the required qualities."""
        pool = self.main_pool[self.main_pool["IsAlly"]]
        # Pick an ally from the complete pool if otherwise not possible
        if len(pool) == 0:
            pool = self.get_initial_draw_pool(rerolled_csos=[], ignore_expansions=True)
            pool = pool[pool["IsAlly"]]
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        try:
            self.main_pool = self.main_pool.drop(pick)
        except KeyError:
            pass
        return pick

    def pick_liaison(self, qualities_so_far: dict[str, int]) -> str:
        """Pick a liaison while also considering the required qualities."""
        pool = self.main_pool[self.main_pool["IsLiaison"]]
        if len(pool) == 0:
            pool = self.get_initial_draw_pool(rerolled_csos=[], ignore_expansions=True)
            pool = pool[pool["IsLiaison"]]
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        try:
            self.main_pool = self.main_pool.drop(pick)
        except KeyError:
            pass
        return pick

    def pick_prophecy(self, qualities_so_far: dict[str, int]) -> str:
        """Pick a prophecy while also considering the required qualities."""
        pool = self.main_pool[self.main_pool["IsProphecy"]]
        if len(pool) == 0:
            pool = self.get_initial_draw_pool(rerolled_csos=[], ignore_expansions=True)
            pool = pool[pool["IsProphecy"]]
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        try:
            self.main_pool = self.main_pool.drop(pick)
        except KeyError:
            pass
        return pick

    def pick_omen(self, qualities_so_far: dict[str, int]) -> str:
        """Pick an omen while also considering the required qualities."""
        pool = self.main_pool[self.main_pool["IsOmen"]]
        if len(pool) == 0:
            pool = self.get_initial_draw_pool(rerolled_csos=[], ignore_expansions=True)
            pool = pool[pool["IsOmen"]]
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        try:
            self.main_pool = self.main_pool.drop(pick)
        except KeyError:
            pass
        return pick
