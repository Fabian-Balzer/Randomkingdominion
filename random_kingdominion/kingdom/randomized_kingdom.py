"""File to contain the KingdomQualities and the Kingdom classes"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from random_kingdominion.constants import ALL_CSOS, QUALITIES_AVAILABLE
from random_kingdominion.cso_frame_utils import sample_single_cso_from_df

from .kingdom import Kingdom
from .kingdom_helper_funcs import _get_total_quality


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
    army_pile: str = ""
    ferryman_pile: str = ""
    riverboat_card: str = ""
    mouse_card: str = ""
    druid_boons: list[str] = field(default_factory=lambda: [])
    traits: list[list[str]] = field(default_factory=lambda: [])

    @classmethod
    def from_kingdom(cls, kingdom: Kingdom) -> RandomizedKingdom:
        """Construct an instance of this class from a Kingdom"""
        num_landscapes = len(kingdom.landscapes)
        if kingdom.contains_ally():
            num_landscapes -= 1
        if kingdom.contains_prophecy():
            num_landscapes -= 1
        same_attrs = [
            "obelisk_pile",
            "bane_pile",
            "ferryman_pile",
            "army_pile",
            "riverboat_card",
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
        instance = RandomizedKingdom(num_landscapes=num_landscapes, **attr_dict)
        for card in kingdom.cards:
            instance.add_card(card)
        for landscape in kingdom.landscapes:
            instance.add_landscape(landscape, pick_targets=False)
        return instance

    def _get_full_df(self) -> pd.DataFrame:
        combined_list = self._selected_cards + self._selected_landscapes
        if self.mouse_card:
            combined_list += [self.mouse_card]
        if self.ferryman_pile:
            combined_list += [self.ferryman_pile]
        if self.riverboat_card:
            combined_list += [self.riverboat_card]
        if self.druid_boons:
            combined_list += self.druid_boons
        return ALL_CSOS.loc[combined_list].copy()

    def _get_card_df(self, include_extras: bool = False) -> pd.DataFrame:
        cards = self._selected_cards
        if include_extras:
            for obj in self.riverboat_card, self.ferryman_pile, self.mouse_card:
                if obj != "":
                    cards = cards + [obj]
        return ALL_CSOS.loc[cards].copy()

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
        return np.sum(self._get_landscape_df()["IsWay"]) > 0

    def contains_ally(self) -> bool:
        """Checks whether the current selection contains an ally."""
        return np.sum(self._get_landscape_df()["IsAlly"]) > 0

    def contains_liaison(self) -> bool:
        """Checks whether the current selection contains a liaison."""
        return np.sum(self._get_card_df(include_extras=True)["IsLiaison"]) > 0

    def contains_prophecy(self) -> bool:
        """Checks whether the current selection contains a Prophecy."""
        return np.sum(self._get_landscape_df()["IsProphecy"]) > 0

    def contains_omen(self) -> bool:
        """Checks whether the current selection contains an Omen."""
        return np.sum(self._get_card_df(include_extras=True)["IsOmen"]) > 0

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
        if card_name == "" or card_name in self._selected_cards:
            return
        self._selected_cards.append(card_name)
        self._set_quality_values()

    def remove_card_and_test_bane_army(
        self, card_name: str
    ) -> dict[Literal["bane", "army"], bool]:
        """Safely removes the given card from the selection
        and returns whether a new bane or army pile is needed.
        Afterwards you should check whether there is still a Liaison in the kingdom,
        and remove the Ally if necessary.
        """
        if self.contains_card(card_name):
            self._selected_cards.remove(card_name)
        if card_name == "young_witch":
            self.set_bane_pile("")
        if card_name == "ferryman":
            self.set_ferryman_pile("")
        if card_name == "riverboat":
            self.set_riverboat_card("")
        if card_name == "druid":
            self.set_druid_boons([])
        # Remove Ally if card was the only Liaison:
        if not self.contains_liaison() and self.contains_ally():
            ally_name = self._get_landscape_df()[
                self._get_landscape_df()["IsAlly"]
            ].index.values[0]
            self._selected_landscapes.remove(ally_name)
        # Remove Prophecy if card was the only Omen:
        if not self.contains_omen() and self.contains_prophecy():
            prophecy_name = self._get_landscape_df()[
                self._get_landscape_df()["IsProphecy"]
            ].index.values[0]
            self._selected_landscapes.remove(prophecy_name)
        self._set_quality_values()
        # Pick new trait if the card was a trait target:
        trait_targets = [trait_tuple[1] for trait_tuple in self.traits]
        if card_name in trait_targets:
            index = trait_targets.index(card_name)
            trait_tup = self.traits[index]
            self.traits.remove(trait_tup)
            self._pick_trait_target(trait_tup[0])
        # Pick new obelisk if the card was the obelisk target:
        if self.obelisk_pile == card_name:
            self._pick_obelisk()
        return {
            "bane": card_name == self.bane_pile,
            "army": card_name == self.army_pile,
        }

    def remove_landscape_and_return_types(self, landscape_name: str) -> list[str]:
        """Safely removes the given landscape from the selection, along with
        associated values such as Obelisk, Mouse, and Trait stuff.
        Returns whether a new Ally must be picked.
        """
        if not self.contains_landscape(landscape_name) or landscape_name == "":
            return []
        self._selected_landscapes.remove(landscape_name)
        traits = [trait_tuple[0] for trait_tuple in self.traits]
        if landscape_name in traits:
            index = traits.index(landscape_name)
            self.traits.remove(self.traits[index])
        elif landscape_name == "way_of_the_mouse":
            self.set_mouse_card("")
        elif landscape_name == "obelisk":
            self.obelisk_pile = ""
        elif landscape_name == "approaching_army":
            self.set_army_pile("")
        self._set_quality_values()
        return ALL_CSOS.loc[landscape_name]["Types"]  # type: ignore

    def add_landscape(self, landscape_name: str, pick_targets=True):
        """Safely adds the given landscape to this kingdom"""
        if landscape_name == "":
            return
        self._selected_landscapes.append(landscape_name)
        self._set_quality_values()
        if not pick_targets:
            return
        if landscape_name == "Obelisk":
            self._pick_obelisk()
        if self._get_landscape_df().loc[landscape_name]["IsTrait"]:
            self._pick_trait_target(landscape_name)

    def set_bane_pile(self, bane_name: str):
        """Removes any existing old bane card and sets the new one"""
        if self.bane_pile != "":
            if self.bane_pile in self._selected_cards:
                self.remove_card_and_test_bane_army(self.bane_pile)
        self.bane_pile = bane_name
        self._set_quality_values()
        if bane_name == "":
            return
        if bane_name not in self._selected_cards:
            self.add_card(bane_name)
        self._set_quality_values()

    def set_army_pile(self, army_name: str):
        """Removes any existing old approaching army pile and sets the new one"""
        if self.army_pile != "":
            if self.army_pile in self._selected_cards:
                self.remove_card_and_test_bane_army(self.army_pile)
        self.army_pile = army_name
        self._set_quality_values()
        if army_name == "":
            return
        if army_name not in self._selected_cards:
            self.add_card(army_name)
        self._set_quality_values()

    def set_ferryman_pile(self, card_name: str):
        """Removes any existing ferryman card and sets the new one"""
        self.ferryman_pile = card_name
        self._set_quality_values()

    def set_riverboat_card(self, card_name: str):
        """Removes any existing riverboat card and sets the new one"""
        self.riverboat_card = card_name
        self._set_quality_values()

    def set_druid_boons(self, boons: list[str]):
        """Removes existing boons and sets the new ones."""
        self.druid_boons = boons
        self._set_quality_values()

    def set_mouse_card(self, mouse_name: str):
        """Removes any existing old mouse card and sets the new one"""
        self.mouse_card = mouse_name
        self._set_quality_values()

    def _pick_trait_target(self, trait_name: str):
        """Pick the target for the given trait."""
        # Make sure no card is picked by more than one Trait
        excluded = [trait_tuple[1] for trait_tuple in self.traits]
        counterpart = self._pick_action_or_treasure(excluded)
        if counterpart:
            self.traits.append([trait_name, counterpart])

    def _pick_obelisk(self):
        """Since the cards should all be included in the kingdom already, the
        obelisk may be picked."""
        if "obelisk" in self._selected_landscapes:
            self.obelisk_pile = self._pick_action()

    def _pick_action_or_treasure(self, excluded: list[str] | None = None) -> str:
        """For Traits, only Actions or Treasures can be picked."""
        df = self._get_card_df()
        subset = df[df["IsAction"] | df["IsTreasure"]]
        if excluded:
            subset = subset[~np.isin(subset.index.to_list(), excluded)]
        return sample_single_cso_from_df(subset)

    def _pick_action(self) -> str:
        """For the obelisk pile, an Action supply pile must be picked"""
        df = self._get_card_df()
        subset = df[df["IsAction"]]
        if len(subset) == 0:
            print("No action available for obelisk")
            return ""
        return sample_single_cso_from_df(subset)

    def finish_randomization(self):
        """Take care of picking Trait/Obelisk targets in case that hasn't been done."""
        if self.contains_landscape("obelisk") and not self.obelisk_pile:
            self._pick_obelisk()
        landscapes = self._get_landscape_df()
        for trait in landscapes[landscapes["IsTrait"]]["Name"].tolist():
            if trait not in [t[0] for t in self.traits]:
                self._pick_trait_target(trait)

    def get_kingdom(self) -> Kingdom:
        """Construct a proper kingdom out of this one"""
        return Kingdom(
            cards=self._selected_cards,
            landscapes=self._selected_landscapes,
            bane_pile=self.bane_pile,
            army_pile=self.army_pile,
            traits=self.traits,
            obelisk_pile=self.obelisk_pile,
            ferryman_pile=self.ferryman_pile,
            riverboat_card=self.riverboat_card,
            mouse_card=self.mouse_card,
            druid_boons=self.druid_boons,
            use_colonies=self.use_colonies,
            use_shelters=self.use_shelters,
        )
