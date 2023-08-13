# %%

from functools import reduce
from typing import Optional

from .config import CustomConfigParser, get_randomizer_config_options
from .constants import FPATH_CARD_DATA, RENEWED_EXPANSIONS
from .kingdom import Kingdom
from .utils import read_dataframe_from_file


class DataContainer:
    def __init__(self, config: Optional[CustomConfigParser] = None):
        self.config = config if config is not None else get_randomizer_config_options()
        self.all_cards = read_dataframe_from_file(FPATH_CARD_DATA, eval_lists=True)
        self.all_expansions = list(set(self.all_cards["Expansion"]))
        self.all_attack_types = self.get_attack_types()
        self.rerolled_cards = []
        self.parameter_dict = {"RequireReaction": False, "attack_types": None}
        self.kingdom = None

    def read_attack_types(self, checkbox_att_dict, button):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        atts = [
            att for att, checkbox in checkbox_att_dict.items() if checkbox.isChecked()
        ]
        self.config.set_special_list("attack_types", atts)
        if all([checkbox.isChecked() for checkbox in checkbox_att_dict.values()]):
            button.setText("Deselect all attack types")
        else:
            button.setText("Select all attack types")

    def toggle_all_attack_types(self, checkbox_att_dict, button):
        if all([checkbox.isChecked() for checkbox in checkbox_att_dict.values()]):
            for checkbox in checkbox_att_dict.values():
                checkbox.toggle()
        else:
            for checkbox in checkbox_att_dict.values():
                checkbox.setChecked(True)
        self.read_attack_types(checkbox_att_dict, button)

    def randomize(self):
        self.rerolled_cards = []
        self.kingdom = Kingdom(self.all_cards, config=self.config)
        self.kingdom.randomize(self.rerolled_cards)

    def reroll_card(self, old_card):
        """Creates a new card with the old card removed and tries a reroll."""
        kept_cards = [card for card in self.kingdom.kingdom_cards if card != old_card]
        if old_card == "Young Witch":
            kept_cards = [
                card
                for card in kept_cards
                if card != self.kingdom.special_targets["Bane"]
            ]
        kept_landscapes = [card for card in self.kingdom.landscapes if card != old_card]
        kept_ally = self.kingdom.ally if old_card != self.kingdom.ally else ""
        if (
            len(
                self.kingdom.get_kingdom_df()[
                    self.kingdom.get_kingdom_df()["Types"].apply(
                        lambda x: "Liaison" in x
                    )
                ]
            )
            == 0
        ):
            kept_ally = ""
        self.kingdom = Kingdom(
            self.all_cards,
            config=self.config,
            kingdom_cards=kept_cards,
            landscapes=kept_landscapes,
            ally=kept_ally,
        )
        self.rerolled_cards.append(old_card)
        self.kingdom.randomize(self.rerolled_cards)

    def get_attack_types(self):
        all_types = reduce(lambda x, y: x + y, self.all_cards["attack_types"])
        set_ = set(all_types)
        set_.discard("")
        return sorted(list(set_))

    def select_or_deselect(self, checkbox_dict, button):
        pass
        # if len(self.selected_sets) == 0:
        #     for checkbox in

    def select_previous(self):
        index = self.kingdom.history.index(self.kingdom)
        if index > 0:
            self.kingdom = self.kingdom.history[index - 1]

    def select_next(self):
        index = self.kingdom.history.index(self.kingdom)
        if index < len(self.kingdom.history) - 1:
            self.kingdom = self.kingdom.history[index + 1]

    def read_quality(self, qual, val):
        self.config.set_quality(qual, val)

    # def set_quality_args(self, spin_dict):
    #     for arg_name in self.quality_dict.keys():
    #         spin_dict[arg_name].setValue(self.quality_dict[arg_name])

    # def randomize_brute_force(self):
    #     try_, max_tries = 1, 200
    #     no_good_kingdom = True
    #     while no_good_kingdom:
    #         self.kingdom = self.pull_kingdom_cards()
    #         self.landscapes = self.pull_landscapes()
    #         self.picked_cards = create_supply(self.kingdom, self.landscapes)
    #         no_good_kingdom = not self.does_kingdom_fulfill_requirements()
    #         if try_ > max_tries:
    #             print("Did not find a kingdom with the necessary requirements")
    #             break
    #         try_ += 1
    #     print(self.picked_cards[["Name", "DrawQuality", "VillageQuality"]])
    #     print(f"Took me {try_-1} tries to get this kingdom.")

    # def pull_kingdom_cards(self):
    #     kingdom = self.selected_cards.iloc[0:0]  # empty kingdom
    #     for pull in range(self.num_kingdomcards):
    #         subset = CardSubset(self.selected_cards, kingdom)
    #         if len(subset) == 0:
    #             break
    #         new_card = subset.pick_card()
    #         kingdom = pd.concat([kingdom, new_card])
    #     return kingdom.sort_values(by=["Cost", "Name"])

    # def pull_landscapes(self):
    #     landscapes = self.selected_cards.iloc[0:0]  # empty landscapes
    #     if len(self.selected_cards[self.selected_cards["IsLandscape"]]) > 0:
    #         for pull in range(self.num_landscapes):
    #             subset = CardSubset(self.selected_cards, landscapes)
    #             if len(subset) == 0:
    #                 break
    #             new_landscape = subset.pick_landscape()
    #             landscapes = pd.concat([landscapes, new_landscape])
    #     return landscapes.sort_values(by=["Cost", "Name"])

    # def does_kingdom_fulfill_requirements(self):
    #     """Checks wether a given kingdom fulfils the requirements passed."""
    #     for quality in ["DrawQuality", "VillageQuality"]:
    #         if sum(self.picked_cards[quality]) < self.quality_dict[quality]:
    #             return False
    #     return True


def create_supply(kingdom, landscapes):
    supply = kingdom.append(landscapes, sort=False)
    supply = supply.sort_values(
        by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"],
        ascending=[False, True, True, True, True],
    )
    return supply


def give_card(df, name):
    return df[df["Name"] == name]


if __name__ == "__main__":
    a = DataContainer()
    a.randomize()
    print(a.kingdom)
    c = a.all_cards
