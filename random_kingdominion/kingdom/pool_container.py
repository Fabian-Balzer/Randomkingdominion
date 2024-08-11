"""File to contain the PoolContainer class necessary for randomization"""

import random

import numpy as np
import pandas as pd
from typing import Literal

from random_kingdominion.constants import (
    ALL_CSOS,
    QUALITIES_AVAILABLE,
    CARD_TYPES_AVAILABLE,
)
from random_kingdominion.cso_frame_utils import (
    add_weight_column,
    get_sub_df_for_card,
    get_sub_df_for_true_landscape,
    get_sub_df_listlike_contains_any_or_is_empty,
    get_sub_df_of_categories,
    listlike_contains_any,
    sample_single_cso_from_df,
)
from random_kingdominion.utils.config import (
    CustomConfigParser,
    add_renewed_base_expansions,
)


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

    def get_initial_draw_pool(self, rerolled_csos: list[str]) -> pd.DataFrame:
        """Create the initial draw pool for the kingdom.
        This is the overarching one that is used for all of the draws,
        so here we filter for requested expansions, allowed attack types,
        cards that are in the supply, and remove all cards with forbidden
        qualities.
        """
        # Reduce the complete pool to the requested expansions:
        pool = get_sub_df_of_categories(ALL_CSOS, "Expansion", self.eligible_expansions)

        # Reduce the pool to exclude any attacks that are not wanted
        _allowed_attack_types = self.config.getlist("Specialization", "attack_types")
        pool = get_sub_df_listlike_contains_any_or_is_empty(
            pool, "attack_types", _allowed_attack_types
        )

        # Reduce the pool to exclude any landscapes that are not wanted
        _allowed_landscapes = self.config.getlist("General", "allowed_landscape_types")
        pool = pool[
            ~pool["IsLandscape"]
            | listlike_contains_any(pool["Types"], _allowed_landscapes)
        ]
        _excluded_card_types = self.config.getlist(
            "Specialization", "excluded_card_types"
        )
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
        max_num_expansions = self.config.getint("General", "max_num_expansions")
        if max_num_expansions == 0 or max_num_expansions >= len(user_expansions):
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
    ) -> list[tuple[str, str]]:
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
            Literal["ferryman", "way_of_the_mouse", "young_witch", "riverboat"] | None
        ) = None,
    ) -> str:
        """Pick the next card while also considering the required qualities."""
        pool = get_sub_df_for_card(self.main_pool, special_card_to_pick_for)
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        self.main_pool = self.main_pool.drop(pick)
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
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        self.main_pool = self.main_pool.drop(pick)
        return pick

    def pick_prophecy(self, qualities_so_far: dict[str, int]) -> str:
        """Pick a prophecy while also considering the required qualities."""
        pool = self.main_pool[self.main_pool["IsProphecy"]]
        if len(pool) == 0:
            return ""
        pool = self._narrow_pool_for_quality(pool, qualities_so_far)
        pick = sample_single_cso_from_df(pool)
        self.main_pool = self.main_pool.drop(pick)
        return pick
