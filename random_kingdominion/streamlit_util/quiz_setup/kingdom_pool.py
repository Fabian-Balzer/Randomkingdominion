"""The pools quiz kingdoms are drawn from: random kingdoms from the selected
expansions, or curated kingdoms using only those expansions. Kept free of Streamlit
so that it can be used (and tested) without a running app."""

import random
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache

from ...constants import (
    ALL_CSOS,
    EXPANSION_LIST,
    QUALITIES_AVAILABLE,
    SPECIAL_QUAL_TYPES_AVAILABLE,
)
from ...kingdom import Kingdom, KingdomManager, KingdomRandomizer
from ...utils.config import CustomConfigParser, add_renewed_base_expansions
from ...utils.kingdom_helper_funcs import sanitize_cso_list, sanitize_cso_name

# The expansions in the order they are offered: second editions first, 1E at the end
QUIZ_EXPANSION_OPTIONS = tuple(
    [exp for exp in EXPANSION_LIST if "1E" not in exp]
    + [exp for exp in EXPANSION_LIST if "1E" in exp]
)
QUIZ_DEFAULT_EXPANSIONS = tuple(
    exp for exp in QUIZ_EXPANSION_OPTIONS if "1E" not in exp and exp != "Promo"
)

# Mirrors the randomizer's default config, but without its default bans, so that the
# quiz doesn't change whenever those defaults do.
_QUIZ_RANDOMIZER_CONFIG = {
    "General": {
        "num_cards": "10",
        "allow_required_csos_of_other_exps": "False",
        "required_csos": "[]",
        "banned_csos": "[]",
        "disliked_csos": "[]",
        "dislike_factor": "0.5",
        "liked_csos": "[]",
        "like_factor": "2.0",
        "partial_kingdom_input": "",
    },
    "Expansions": {
        "expansions": "[]",
        "max_num_expansions": "5",
        "enable_max": "False",
    },
    "Landscapes": {
        "min_num_landscapes": "0",
        "max_num_landscapes": "2",
        "allowed_landscape_types": '["Event", "Landmark", "Project", "Trait", "Way"]',
    },
    "Qualities": {
        **{f"requested_{q}": "0" for q in QUALITIES_AVAILABLE},
        **{f"forbid_{q}": "False" for q in QUALITIES_AVAILABLE},
        **{f"forbidden_{q}_types": "[]" for q in SPECIAL_QUAL_TYPES_AVAILABLE},
    },
    "Specialization": {
        "excluded_card_levels": "[]",
        "excluded_card_types": "[]",
        "use_dark_ages_for_shelters": "True",
        "shelter_probability": "0.0",
        "use_prosperity_for_colony": "True",
        "colony_probability": "0.0",
    },
}

# How often a random kingdom is redrawn if it was already part of the run
_MAX_RANDOM_RETRIES = 3


class QuizPoolSource(StrEnum):
    RANDOM = "random"
    RECOMMENDED = "recommended"
    TGG_DAILIES = "tgg_dailies"

    @property
    def label(self) -> str:
        return {
            QuizPoolSource.RANDOM: "🎲 Random",
            QuizPoolSource.RECOMMENDED: "⭐ Recommended",
            QuizPoolSource.TGG_DAILIES: "📅 TGG Dailies",
        }[self]

    @property
    def is_curated(self) -> bool:
        return self is not QuizPoolSource.RANDOM

    def get_description(self, include_name: bool = True) -> str:
        d = {
            QuizPoolSource.RANDOM: "Freshly randomized kingdoms from your expansions.",
            QuizPoolSource.RECOMMENDED: "The recommended kingdoms from the rulebooks (at most two expansions each).",
            QuizPoolSource.TGG_DAILIES: "The daily kingdoms of the Temple Gates Games client, except those with twists, stamps or setup effects (as in the TGG Campaigns), which the qualities don't cover.",
        }[self]
        if not include_name:
            return d
        return f"**{self.label}**: {d}"

    def get_kingdom_name_label(self, name: str) -> str:
        """How the name of a curated kingdom is shown once it's solved."""
        if self is QuizPoolSource.TGG_DAILIES:
            return f"📅 TGG Daily of {name}"
        return f"⭐ Recommended kingdom *{name}*"


def sort_expansions(expansions: Collection[str]) -> tuple[str, ...]:
    """The known expansions out of `expansions`, in the order they are offered."""
    return tuple(exp for exp in QUIZ_EXPANSION_OPTIONS if exp in expansions)


@dataclass(frozen=True)
class QuizKingdomPool:
    source: QuizPoolSource = QuizPoolSource.RANDOM
    expansions: tuple[str, ...] = field(default=QUIZ_DEFAULT_EXPANSIONS)

    def __post_init__(self) -> None:
        unknown = set(self.expansions) - set(QUIZ_EXPANSION_OPTIONS)
        if unknown:
            raise ValueError(f"Unknown expansions: {sorted(unknown)}")
        # A canonical order, so that equal selections give equal pools
        object.__setattr__(self, "expansions", sort_expansions(self.expansions))

    @property
    def uses_all_expansions(self) -> bool:
        return len(self.expansions) == len(QUIZ_EXPANSION_OPTIONS)

    @property
    def expansion_summary(self) -> str:
        if self.uses_all_expansions:
            return "all expansions"
        num = len(self.expansions)
        return f"{num} expansion{'s' if num != 1 else ''}"

    @property
    def label(self) -> str:
        return f"{self.source.label} · {self.expansion_summary}"


# The supply (kingdom cards and landscapes) plus whether Colonies and Shelters are
# used: enough to tell kingdoms apart, and cheap to get from the stored kingdoms.
_KingdomIdentity = tuple[frozenset[str], bool, bool]

# Non-supply piles, which Kingdom removes from its cards
_NON_SUPPLY_FIELDS = ("ferryman_pile", "riverboat_card", "mouse_card")
_EXTRA_PILE_FIELDS = ("bane_pile", "obelisk_pile", "army_pile") + _NON_SUPPLY_FIELDS


@dataclass(frozen=True)
class _CuratedKingdom:
    name: str
    identity: _KingdomIdentity
    csos_expansions: frozenset[str]
    """The expansions of all its CSOs, with "Base" etc. for those in both editions."""
    info: dict = field(compare=False, hash=False, repr=False)
    """The kingdom as stored by the KingdomManager."""


def _is_set(info: dict, key: str) -> bool:
    # Missing values come as NaN from the stored kingdoms
    return info.get(key) is True


def _has_campaign_effects(info: dict) -> bool:
    effects = info.get("campaign_effects")
    return isinstance(effects, list) and len(effects) > 0


def _get_identity_of_info(info: dict) -> _KingdomIdentity:
    non_supply = {sanitize_cso_name(info.get(f, "")) for f in _NON_SUPPLY_FIELDS}
    supply = set(sanitize_cso_list(info.get("cards", []))) - non_supply
    supply |= set(sanitize_cso_list(info.get("landscapes", [])))
    return (
        frozenset(supply),
        _is_set(info, "use_colonies"),
        _is_set(info, "use_shelters"),
    )


@lru_cache(maxsize=256)
def _get_identity_of_string(kingdom_str: str) -> _KingdomIdentity:
    k = Kingdom.from_dombot_csv_string(kingdom_str)
    return frozenset(k.cards + k.landscapes), k.use_colonies, k.use_shelters


def _get_csos_expansions(info: dict) -> frozenset[str]:
    """The expansions of the CSOs a Kingdom built from `info` would contain. Building
    each Kingdom instead would take ~30 ms per kingdom, i.e. ~40 s for the Dailies."""
    csos = sanitize_cso_list(info.get("cards", []))
    csos += sanitize_cso_list(info.get("landscapes", []))
    csos += sanitize_cso_list(info.get("druid_boons", []))
    csos += [sanitize_cso_name(info.get(f, "")) for f in _EXTRA_PILE_FIELDS]
    if _is_set(info, "use_colonies"):
        csos += ["colony", "platinum"]
    if _is_set(info, "use_shelters"):
        csos += ["necropolis", "hovel", "overgrown_estate"]
    cso_expansions = _get_cso_expansion_dict()
    # Unknown CSOs get an expansion no selection contains, so that broken kingdoms
    # are never drawn
    return frozenset(cso_expansions.get(cso, "Unknown") for cso in csos if cso)


@lru_cache(maxsize=1)
def _get_cso_expansion_dict() -> dict[str, str]:
    return ALL_CSOS["Expansion"].to_dict()


@lru_cache(maxsize=None)
def _load_curated_kingdoms(source: QuizPoolSource) -> tuple[_CuratedKingdom, ...]:
    manager = KingdomManager()
    if source is QuizPoolSource.RECOMMENDED:
        manager.load_recommended_kingdoms()
    elif source is QuizPoolSource.TGG_DAILIES:
        manager.load_tgg_dailies()
    else:
        raise ValueError(f"{source} is not a curated pool.")
    kingdoms: dict[_KingdomIdentity, _CuratedKingdom] = {}
    for info in manager.kingdoms:
        # Twists, stamps and setup effects change a kingdom in ways the qualities
        # don't cover (the same reason the TGG Campaigns aren't offered)
        if _has_campaign_effects(info):
            continue
        identity = _get_identity_of_info(info)
        # Duplicates count once, so that a run can't contain the same kingdom twice
        kingdoms.setdefault(
            identity,
            _CuratedKingdom(
                str(info.get("name", "")), identity, _get_csos_expansions(info), info
            ),
        )
    return tuple(kingdoms.values())


@lru_cache(maxsize=64)
def _get_available_curated_kingdoms(
    pool: QuizKingdomPool,
) -> tuple[_CuratedKingdom, ...]:
    """The curated kingdoms of the pool that only use its expansions."""
    return tuple(
        k
        for k in _load_curated_kingdoms(pool.source)
        if uses_only_expansions(k.csos_expansions, pool.expansions)
    )


def uses_only_expansions(
    csos_expansions: Collection[str], expansions: Collection[str]
) -> bool:
    """Whether CSOs of the given expansions (as in ALL_CSOS, e.g. "Base" for cards in
    both editions) are all available with the selected expansions."""
    # Cards that are in both editions are fine with either of them
    allowed = set(add_renewed_base_expansions(list(expansions)))
    return set(csos_expansions) <= allowed


def count_available_kingdoms(pool: QuizKingdomPool) -> int | None:
    """The number of different kingdoms in the pool, or None if it's (practically)
    unlimited, as for random kingdoms."""
    if not pool.expansions:
        return 0
    if not pool.source.is_curated:
        return None
    return len(_get_available_curated_kingdoms(pool))


@lru_cache(maxsize=None)
def _get_curated_names(source: QuizPoolSource) -> dict[_KingdomIdentity, str]:
    return {k.identity: k.name for k in _load_curated_kingdoms(source) if k.name}


def get_curated_kingdom_name(pool: QuizKingdomPool, kingdom_str: str) -> str | None:
    if not pool.source.is_curated:
        return None
    return _get_curated_names(pool.source).get(_get_identity_of_string(kingdom_str))


def get_quiz_randomizer_config(expansions: Sequence[str]) -> CustomConfigParser:
    config = CustomConfigParser.from_dict(_QUIZ_RANDOMIZER_CONFIG)
    config.set_expansions(list(expansions))
    return config


def draw_quiz_kingdom(pool: QuizKingdomPool, exclude: Collection[str] = ()) -> str:
    """Draw a kingdom (as DomBot csv string) from the pool that isn't in `exclude`."""
    if not pool.expansions:
        raise ValueError("The pool has no expansions.")
    if pool.source.is_curated:
        used = {_get_identity_of_string(kingdom_str) for kingdom_str in exclude}
        candidates = [
            k for k in _get_available_curated_kingdoms(pool) if k.identity not in used
        ]
        if not candidates:
            raise ValueError("The pool has no kingdoms left.")
        return Kingdom.from_dict(random.choice(candidates).info).get_dombot_csv_string()

    randomizer = KingdomRandomizer(get_quiz_randomizer_config(pool.expansions))
    for _ in range(_MAX_RANDOM_RETRIES):
        kingdom_str = randomizer.randomize_new_kingdom().get_dombot_csv_string()
        if kingdom_str not in exclude:
            break
    return kingdom_str
