from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...constants import ALL_CSOS
from ...utils.utils import get_cso_name
from .invalidity_reason import InvalidityReason

if TYPE_CHECKING:
    from ..kingdom import Kingdom

@dataclass
class BaneButNoYoungWitch(InvalidityReason):
    def get_description(self) -> str:
        return "There is a Bane pile but no Young Witch in the kingdom."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.bane_pile != "" and "young_witch" not in k.cards

@dataclass
class YoungWitchButNoBane(InvalidityReason):
    def get_description(self) -> str:
        return "There is a Young Witch in the kingdom but no Bane pile."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.bane_pile == "" and "young_witch" in k.cards

@dataclass
class BaneNotInCards(InvalidityReason):
    def get_description(self) -> str:
        return "The bane pile is not in the kingdom cards."

    def check_if_invalid(self, k: Kingdom) -> bool:
        if k.bane_pile == "" or k.bane_pile in k.cards:
            return False
        self.params["bane_pile"] = k.bane_pile
        return True

@dataclass
class IncorrectBaneCost(InvalidityReason):
    def get_description(self) -> str:
        c = self.params.get("cost", "$5").replace("$", "\\$")
        return f"The Bane card has an incorrect cost of {c} (instead of \\$2 or \\$3)."

    def check_if_invalid(self, k: Kingdom) -> bool:
        if k.bane_pile == "":
            return False
        cso = ALL_CSOS.loc[k.bane_pile]
        self.params["cost"] = cso["Cost"]
        return cso["Sanitized Cost"] not in [2, 3]

@dataclass
class WrongCardNumber(InvalidityReason):
    def get_description(self) -> str:
        should = self.params.get("expected", 10)
        avail = self.params.get("actual", 0)
        pre = "is only" if avail == 1 else "are only" if avail < should else "are"
        return f"The number of cards in the kingdom is incorrect, there should be {should} but there {pre} {avail}."

    def check_if_invalid(self, k: Kingdom) -> bool:
        expected_card_num = 10
        if "ruins" in k.cards:
            expected_card_num += 1
        if k.bane_pile != "":
            expected_card_num += 1
        if k.army_pile != "":
            expected_card_num += 1
        if "room_for_more" in k.campaign_effects:
            expected_card_num += 1
        if len(k.cards) == expected_card_num:
            return False
        self.params["expected"] = expected_card_num
        self.params["actual"] = len(k.cards)
        return True

@dataclass
class TooManyLandscapes(InvalidityReason):
    def get_description(self) -> str:
        return "There are more than 4 landscapes in the kingdom."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return len(k.landscapes) > 4

@dataclass
class LiaisonButNoAlly(InvalidityReason):
    def get_description(self) -> str:
        return "There is at least one Liaison card but no Ally in the kingdom."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.check_cards_for_type("IsLiaison") and not k.contains_ally()

@dataclass
class OmenButNoProphecy(InvalidityReason):
    def get_description(self) -> str:
        return "There is at least one Omen card but no Prophecy in the kingdom."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.check_cards_for_type("IsOmen") and not k.contains_prophecy()

@dataclass
class ProphecyButNoOmen(InvalidityReason):
    def get_description(self) -> str:
        return "A Prophecy has been specified, but there's no Omen in the kingdom."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.contains_prophecy() and not k.check_cards_for_type("IsOmen")

@dataclass
class AllyButNoLiaison(InvalidityReason):
    def get_description(self) -> str:
        return "An Ally has been specified, but there's no Liaison in the kingdom."
    
    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.contains_ally() and not k.check_cards_for_type("IsLiaison")

@dataclass
class ArmyPileButNoApproachingArmy(InvalidityReason):
    def get_description(self) -> str:
        return "There is an Army pile but no Approaching Army in the kingdom."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.army_pile != "" and "approaching_army" not in k.landscapes

@dataclass
class ApproachingArmyButNoArmyPile(InvalidityReason):
    def get_description(self) -> str:
        return "Approaching Army is in the kingdom, but there's no army pile."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.army_pile == "" and "approaching_army" in k.landscapes

@dataclass
class ArmyPileNotInCards(InvalidityReason):
    def get_description(self) -> str:
        return "The Approaching Army pile is not in the kingdom cards."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return k.army_pile != "" and k.army_pile not in k.cards

@dataclass
class TraitsWithoutTargets(InvalidityReason):   

    def check_if_invalid(self, k: Kingdom) -> bool:
        """Check if there are traits in the kingdom with no targets specified, and add them to the internal params.
        """
        trait_dict = k.trait_dict
        ls = k.kingdom_landscape_df
        traits = ls[ls["IsTrait"]].index.tolist()
        for trait in traits:
            if trait not in trait_dict:
                prev = self.params.get("traits", [])
                self.params["traits"] = prev + [trait]
        return self.params.get("traits", []) != []
    
    def get_description(self) -> str:
        traits = ", ".join(self.params.get("traits", []))
        return f"There are one or more Traits in the kingdom with no targets specified: {traits}."

@dataclass
class TraitTargetNotInCards(InvalidityReason):
    
    def check_if_invalid(self, k: Kingdom) -> bool:
        """Check if there are Trait targets in the kingdom that are not in the cards, and add them to the internal params.
        """
        trait_dict = k.trait_dict
        ls = k.kingdom_landscape_df
        traits = ls[ls["IsTrait"]].index.tolist()
        for trait in traits:
            target = trait_dict.get(trait, "")
            if target not in k.cards:
                prev = self.params.get("targets", [])
                self.params["targets"] = prev + [target]
        return self.params.get("targets", []) != []
    
    def get_description(self) -> str:
        targets = ", ".join(self.params.get("targets", []))
        return f"There are Trait targets in the kingdom that are not in the cards: {targets}."

@dataclass
class TraitNotInLandscapes(InvalidityReason):
    
    def check_if_invalid(self, k: Kingdom) -> bool:
        """Check if there are Traits in the kingdom that are not in the landscapes, and add them to the internal params.
        """
        for trait in k.trait_dict:
            if trait not in k.landscapes:
                prev = self.params.get("traits", [])
                self.params["traits"] = prev + [trait]
        return self.params.get("traits", []) != []
    
    def get_description(self) -> str:
        traits = ", ".join(self.params.get("traits", []))
        return f"There are Traits specified that are not in the landscapes: {traits}."

@dataclass
class FerrymanButNoTarget(InvalidityReason):

    def get_description(self) -> str:
        return "Ferryman is in the kingdom, but there's no target for it."
    
    def check_if_invalid(self, k: Kingdom) -> bool:
        return "ferryman" in k.cards and k.ferryman_pile == ""

@dataclass
class FerrymanTargetButNoFerryman(InvalidityReason):

    def get_description(self) -> str:
        return "There is a target for Ferryman in the kingdom, but Ferryman itself hasn't been added."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return "ferryman" not in k.cards and k.ferryman_pile != ""

@dataclass
class FerrymanTargetInCards(InvalidityReason):
    def get_description(self) -> str:
        p = get_cso_name(self.params.get("pile", ""))
        
        return f"The Ferryman target ({p}) is part of the kingdom cards."

    def check_if_invalid(self, k: Kingdom) -> bool:
        if k.ferryman_pile not in k.cards:
            return False
        self.params["pile"] = k.ferryman_pile
        return True

@dataclass
class IncorrectFerrymanPileCost(InvalidityReason):
    def get_description(self) -> str:
        c = self.params.get("cost", "$5").replace("$", "\\$")
        return f"The pile specified for Ferryman has an incorrect cost of {c} (instead of \\$3 or \\$4)."

    def check_if_invalid(self, k: Kingdom) -> bool:
        if k.ferryman_pile == "":
            return False
        cso = ALL_CSOS.loc[k.ferryman_pile]
        self.params["cost"] = cso["Cost"]
        return cso["Sanitized Cost"] not in [3, 4]

@dataclass
class RiverboatButNoTarget(InvalidityReason):

    def get_description(self) -> str:
        return "Riverboat is in the kingdom, but there's no target for it."
    
    def check_if_invalid(self, k: Kingdom) -> bool:
        return "riverboat" in k.cards and k.riverboat_card == ""

@dataclass
class RiverboatTargetButNoRiverboat(InvalidityReason):

    def get_description(self) -> str:
        return "There is a target for Riverboat in the kingdom, but Riverboat itself hasn't been added."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return "riverboat" not in k.cards and k.riverboat_card != ""

@dataclass
class WayOfTheMouseButNoTarget(InvalidityReason):

    def get_description(self) -> str:
        return "Way of the Mouse is in the kingdom, but there's no target for it."
    
    def check_if_invalid(self, k: Kingdom) -> bool:
        return "way_of_the_mouse" in k.landscapes and k.mouse_card == ""

@dataclass
class MouseTargetButNoWayOfTheMouse(InvalidityReason):
    def get_description(self) -> str:
        return "There is a target for Way of the Mouse in the kingdom, but Way of the Mouse itself hasn't been added."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return "way_of_the_mouse" not in k.landscapes and k.mouse_card != ""
    
@dataclass
class ObeliskButNoPile(InvalidityReason):

    def get_description(self) -> str:
        return "Obelisk is in the kingdom, but there's no Obelisk pile."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return "obelisk" in k.landscapes and k.obelisk_pile == ""
    
@dataclass
class ObeliskPileButNoObelisk(InvalidityReason):

    def get_description(self) -> str:
        return "There is an Obelisk pile in the kingdom, but Obelisk itself hasn't been added."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return "obelisk" not in k.landscapes and k.obelisk_pile != ""

@dataclass
class DruidButNoBoons(InvalidityReason):

    def get_description(self) -> str:
        return f"Druid is in the kingdom, but instead of the 3 required ones, {self.params.get("boon_num", 0)} Boons have been specified."

    def check_if_invalid(self, k: Kingdom) -> bool:
        self.params["boon_num"] = len(k.druid_boons)
        return "druid" in k.cards and not len(k.druid_boons) == 3

@dataclass
class DruidBoonsSpecifiedButNoDruid(InvalidityReason):

    def get_description(self) -> str:
        return f"Druid Boons have been specified, but Druid itself hasn't been added."

    def check_if_invalid(self, k: Kingdom) -> bool:
        return "druid" not in k.cards and len(k.druid_boons) > 0
        return "druid" not in k.cards and len(k.druid_boons) > 0
