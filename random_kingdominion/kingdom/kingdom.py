"""File to contain the KingdomQualities and the Kingdom classes"""
from dataclasses import asdict, dataclass, field
from functools import reduce
from uuid import uuid4

import numpy as np
import pandas as pd

from random_kingdominion.constants import (
    ALL_CSOS,
    QUALITIES_AVAILABLE,
    RENEWED_EXPANSIONS,
)

from .kingdom_helper_funcs import _dict_factory_func, _get_total_quality, _sort_kingdom


@dataclass
class Kingdom:
    """Kingdom model similar to Kieranmillar's sets.
    It has the following attributes:
        idx : UUID
            An identifier (random python uuid4)
        name : str, by default ""
            The kingdom name, if any
        cards : list[str]
            A list of card names
        use_colonies : bool, by default False
            A boolean to include Colony and Platinum (optional)
        use_shelters : bool, by default False
            A boolean to include Shelters (optional)
        extras : list[str], by default []
            An array of extra component names (optional)
        landscapes : list[str], by default []
            An array of landscape names (optional)
        obelisk_pile : str, by default ""
            The obelisk target, should already be listed in the cards list (optional)
        bane_pile : str, by default ""
            Which card is the bane, should already be listed in the cards list (optional)
        mouse_card : str, by default ""
            Which card is the Way of the Mouse target,
            should not be contained in the cards list (optional)
        druid_boons : list[str], by default []
            An array of boons, 3 max (optional)
        traits : list[tuple[str, str]], by default []
            An array containing a comma separated list with pairs of cards,
            a trait first then the card it applies to next,
            both should already be in the cards and landscapes lists (optional)
        notes : str
            Any extra notes (optional)
        expansions : list[str]
            The expansions needed to recreate this kingdom
    """

    cards: list[str]
    name: str = ""
    landscapes: list[str] = field(default_factory=lambda: [])
    expansions: list[str] = field(default_factory=lambda: [])
    use_colonies: bool = False
    use_shelters: bool = False
    extras: list[str] = field(default_factory=lambda: [])
    obelisk_pile: str = ""
    bane_pile: str = ""
    mouse_card: str = ""
    druid_boons: list[str] = field(default_factory=lambda: [])
    traits: list[list[str, str]] = field(default_factory=lambda: [])
    notes: str = ""
    idx: int = field(default_factory=lambda: int(uuid4()))

    full_kingdom_df: pd.DataFrame = None
    kingdom_card_df: pd.DataFrame = None
    kingdom_landscape_df: pd.DataFrame = None
    total_qualities: dict[str, int] = field(default_factory=lambda: {})

    __yaml_ignore__ = {
        "full_kingdom_df",
        "kingdom_card_df",
        "kingdom_landscape_df",
        "expansions",
        "extras",
        "total_qualities",
    }

    def __post_init__(self):
        key_list = self.cards + self.landscapes
        if self.mouse_card != "":
            key_list += [self.mouse_card]
        full_kingdom_df = ALL_CSOS.loc[key_list]
        self.full_kingdom_df = _sort_kingdom(full_kingdom_df)

        self.kingdom_card_df = self.full_kingdom_df.loc[self.cards]
        self.kingdom_landscape_df = self.full_kingdom_df.loc[self.landscapes]
        self._set_quality_values()

        # TODO: Calculate extra piles necessary for the kingdom.
        # Also don't forgot to add a df for it?
        unique_expansions = np.unique(full_kingdom_df["Expansion"])
        self.expansions = [
            exp for exp in unique_expansions if exp not in RENEWED_EXPANSIONS
        ]

    def contains_ally(self) -> bool:
        """Checks whether this kingdom contains an ally"""
        return np.sum(self.kingdom_landscape_df["IsAlly"]) > 0

    def pretty_print(self) -> str:
        """Return a string describing the most important things about this kingdom"""
        text = self.full_kingdom_df.to_string(
            columns=["Name", "Cost", "Expansion"], index=False
        )
        quality_summary = "\n".join(
            f"Total {qual.capitalize() + ' quality:':20}\t{val}"
            for qual, val in self.total_qualities.items()
        )
        text += "\n" + quality_summary + "\n"
        text += "CSV representation:\n\n" + self.get_csv_repr()
        return text

    def get_dict_repr(self) -> dict[str, any]:
        """Return the dictionary representation of the kingdom,
        using only the properties that should be exposed.
        """
        return asdict(
            self, dict_factory=lambda x: _dict_factory_func(x, self.__yaml_ignore__)
        )

    def get_csv_repr(self) -> str:
        """TODO: proper Bane/Trait/Mouse/Druid Boons representation"""
        return ", ".join(card for card in self.full_kingdom_df["Name"])

    def _set_quality_values(self):
        """Update the quality values for this kingdom by summing them up."""
        for qual in QUALITIES_AVAILABLE:
            val = _get_total_quality(qual, self.full_kingdom_df)
            self.total_qualities[qual] = val

    def get_card_string_for_quality(self, qual_name: str) -> str:
        """Get a string to describe which cards contribute to the given
        quality, and how much they do that.

        Parameters
        ----------
        qual_name : str
            The name of the quality.

        Returns
        -------
        str
            The description containing the cards.
        """
        qual_name += "_quality"
        df = self.full_kingdom_df
        sub_df = df[df[qual_name] > 0].sort_values(qual_name)
        return ", ".join(
            [f"{card.Name} ({card[qual_name]})" for _, card in sub_df.iterrows()]
        )

    def get_unique_types(self, type_name: str) -> str:
        """For the given quality name, return all of the unique types
        that are part of the kingdom (e.g. all gain types, which might be a list
        of [Buys, Workshop] etc.)
        """
        type_name += "_types"
        if not type_name in self.full_kingdom_df.columns:
            return ""
        df = self.full_kingdom_df
        avail_types = reduce(lambda x, y: x + y, df[type_name])
        if len(avail_types) == 0:
            return ""
        unique_types = np.unique(avail_types)
        return str(sorted(unique_types))

    def get_special_card_text(self, card_name: str):
        """Generate additional attributes for this card."""
        text_list = []
        if card_name == self.bane_pile:
            text_list.append("Bane")
        if card_name == self.obelisk_pile:
            text_list.append("Obelisk")
        for tup in self.traits:
            if card_name == tup[1]:
                text_list.append(tup[0])
        return ",\n".join(text_list)
