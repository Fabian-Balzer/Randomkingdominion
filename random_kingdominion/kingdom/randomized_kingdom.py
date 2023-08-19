"""File to contain the KingdomQualities and the Kingdom classes"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from random_kingdominion.constants import ALL_CSOS, QUALITIES_AVAILABLE

from .kingdom import Kingdom
from .kingdom_helper_funcs import _get_total_quality, _sample_card_from_dataframe


def _qual_dict_factory() -> dict[str, int]:
    """Initialize an empty quality dict"""
    return {qual: 0 for qual in QUALITIES_AVAILABLE}


@dataclass
class RandomizedKingdom:
    """A Kingdom that has yet to be completed for randomization"""

    num_landscapes: int
    num_cards: int = 10
    _selected_cards: list[str] = field(default_factory=list)
    _selected_landscapes: list[str] = field(default_factory=list)
    quality_of_selection: dict[str, int] = field(default_factory=_qual_dict_factory)
    use_colonies: bool = False
    use_shelters: bool = False
    obelisk_pile: str = ""
    bane_pile: str = ""
    mouse_card: str = ""
    druid_boons: list[str] = field(default_factory=lambda: [])
    traits: list[list[str, str]] = field(default_factory=lambda: [])
    all_cards_picked = False  # Turned to true once the cards meet the requirement
    all_landscapes_picked = (
        False  # Turned to true once the num landscapes meet the requirement
    )

    @classmethod
    def from_kingdom(cls: RandomizedKingdom, kingdom: Kingdom) -> RandomizedKingdom:
        """Construct an instance of this class from a Kingdom"""
        num_landscapes = len(kingdom.landscapes)
        if kingdom.includes_ally():
            num_landscapes -= 1
        same_attrs = [
            "obelisk_pile",
            "bane_pile",
            "mouse_card",
            "druid_boons",
            "traits",
            "use_colonies",
            "use_shelters",
        ]
        attr_dict = asdict(
            kingdom,
            dict_factory=lambda x: {k: v for k, v in x if k in same_attrs},
        )
        instance = cls(num_landscapes=num_landscapes, **attr_dict)
        for card in kingdom.cards:
            instance.add_card(card)
        for landscape in kingdom.landscapes:
            instance.add_landscape(landscape)
        return instance

    def _get_full_df(self) -> pd.DataFrame:
        combined_list = self._selected_cards + self._selected_landscapes
        if self.mouse_card:
            combined_list += [self.mouse_card]
        return ALL_CSOS.loc[combined_list].copy()

    def _get_card_df(self) -> pd.DataFrame:
        return ALL_CSOS.loc[self._selected_cards].copy()

    def _get_landscape_df(self) -> pd.DataFrame:
        return ALL_CSOS.loc[self._selected_landscapes].copy()

    def _set_quality_values(self):
        """Update the quality values for the selected dataframe by summing them up."""
        df = self._get_full_df()
        for qual in QUALITIES_AVAILABLE:
            val = _get_total_quality(qual, df)
            self.quality_of_selection[qual] = val

    def contains_way(self) -> bool:
        """Checks whether the current selection contains a way."""
        return np.sum(self._get_landscape_df()["Types"].apply(lambda x: "Way" in x)) > 0

    def contains_ally(self) -> bool:
        """Checks whether the current selection contains a way."""
        return (
            np.sum(self._get_landscape_df()["Types"].apply(lambda x: "Ally" in x)) > 0
        )

    def contains_liaison(self) -> bool:
        """Checks whether the current selection contains a way."""
        return np.sum(self._get_card_df()["Types"].apply(lambda x: "Liaison" in x)) > 0

    def contains_card(self, card_name: str) -> bool:
        """Check whether a given card is in the cards"""
        return card_name in self._selected_cards

    def contains_landscape(self, landscape_name: str) -> bool:
        """Check whether a given landscape is in the cards"""
        return landscape_name in self._selected_landscapes

    def does_selection_contain_type(self, card_type: str) -> bool:
        """Returns wether the selection already contains at least one card
        with the given type."""
        return len(self._get_selection_of_certain_type(card_type)) > 0

    def _get_selection_of_certain_type(self, card_type: str) -> pd.DataFrame:
        df = self._get_full_df()
        return df[df["Types"].apply(lambda x: card_type in x)]

    def add_card(self, card_name: str):
        """Safely adds the given card to this kingdom"""
        if card_name == "":
            return
        self._selected_cards.append(card_name)
        self.all_cards_picked = len(self._selected_cards) >= self.num_cards
        self._set_quality_values()

    def remove_card(self, card_name: str) -> bool:
        """Safely removes the given card from the selection
        and returns whether a new bane pile is needed.
        Afterwards you should check whether there is still a Liaison in the kingdom,
        and remove the Ally if necessary.
        """
        if not self.contains_card(card_name):
            return
        self._selected_cards.remove(card_name)
        if card_name == "Young Witch":
            self.set_bane_card("")
        self.all_cards_picked = len(self._selected_cards) >= self.num_cards
        self._set_quality_values()
        return card_name == self.bane_pile

    def remove_landscape(self, landscape_name: str) -> bool:
        """Safely removes the given landscape from the selection, along with
        associated values such as Obelisk, Mouse, and Trait stuff.
        Returns whether a new Ally must be picked.
        """
        if not self.contains_landscape(landscape_name) or landscape_name == "":
            return
        self._selected_landscapes.remove(landscape_name)
        traits = [trait_tuple[0] for trait_tuple in self.traits]
        if landscape_name in traits:
            index = traits.index(landscape_name)
            self.traits.remove(self.traits[index])
        elif landscape_name == "Way of the Mouse":
            self.set_mouse_card("")
        elif landscape_name == "Obelisk":
            self.obelisk_pile = ""
        self._set_quality_values()
        return ALL_CSOS.loc[landscape_name].IsAlly

    def add_landscape(self, landscape_name: str):
        """Safely adds the given landscape to this kingdom"""
        if landscape_name == "":
            return
        self._selected_landscapes.append(landscape_name)
        self._set_quality_values()

    def set_bane_card(self, bane_name: str):
        """Removes any existing old bane card and sets the new one"""
        if self.bane_pile != "":
            if bane_name in self._selected_cards:
                self._selected_cards.remove(bane_name)
        self.bane_pile = bane_name
        self._set_quality_values()
        if bane_name == "":
            return
        if bane_name not in self._selected_cards:
            self.add_card(bane_name)
        self._set_quality_values()

    def set_mouse_card(self, mouse_name: str):
        """Removes any existing old mouse card and sets the new one"""
        self.mouse_card = mouse_name
        self._set_quality_values()

    def pick_traits(self):
        """Since the cards should all be included in the kingdom already, the
        traits may be picked."""
        df = self._get_landscape_df()
        traits = df[df.Types.apply(lambda x: "Trait" in x)]
        # Make sure no card is picked by more than one Trait
        excluded = [trait_tuple[1] for trait_tuple in self.traits]
        for trait, _ in traits.iterrows():
            counterpart = self._pick_action_or_treasure(excluded)
            if counterpart:
                self.traits.append([trait, counterpart])
                excluded.append(counterpart)

    def pick_obelisk(self):
        """Since the cards should all be included in the kingdom already, the
        obelisk may be picked."""
        if "Obelisk" in self._selected_landscapes:
            self.obelisk_pile = self._pick_action()

    def _pick_action_or_treasure(self, excluded: list[str] | None = None) -> str:
        df = self._get_card_df()
        subset = df[df.Types.apply(lambda x: "Action" in x or "Treasure" in x)]
        if excluded:
            subset = subset[~np.isin(list(subset.Name), excluded)]
        return _sample_card_from_dataframe(subset)

    def _pick_action(self) -> str:
        """For the obelisk pile, an Action supply pile must be picked"""
        df = self._get_card_df()
        subset = df[df.Types.apply(lambda x: "Action" in x)]
        return _sample_card_from_dataframe(subset)

    def get_kingdom(self) -> Kingdom:
        """Construct a proper kingdom out of this one"""
        return Kingdom(
            cards=self._selected_cards,
            landscapes=self._selected_landscapes,
            bane_pile=self.bane_pile,
            traits=self.traits,
            obelisk_pile=self.obelisk_pile,
            mouse_card=self.mouse_card,
        )
