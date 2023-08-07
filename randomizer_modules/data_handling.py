# %%

from .constants import FPATH_CARD_DATA, RENEWED_EXPANSIONS
from .kingdom import Kingdom, KingdomQualities
from .utils import read_dataframe_from_file


class DataContainer:
    def __init__(self):
        self.all_cards = read_dataframe_from_file(FPATH_CARD_DATA, eval_lists=True)
        self.all_sets = list(set(self.all_cards["Expansion"]))
        self.all_attack_types = self.get_attack_types()
        #     # TODO: Load this from a config file
        self.request_dict = {
            "expansions": ["Plunder"],
            "attack_types": ["Handsize", "Scoring", "Junking"],
            "num_cards": 10,
            "num_landscapes": 2,
            "qualities": KingdomQualities(
                default=False,
                qual_dict={
                    "Draw": 1,
                    "Village": 1,
                    "Thinning": 1,
                    "Attack": 0,
                    "Interactivity": 2,
                    "AltVP": 2,
                },
            ),
            "rerolled_cards": [],
        }
        self.parameter_dict = {"RequireReaction": False, "AttackType": None}
        self.kingdom = None

    def read_expansions(self, checkbox_exp_dict, button):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        exps = [
            exp for exp, checkbox in checkbox_exp_dict.items() if checkbox.isChecked()
        ]
        for special in RENEWED_EXPANSIONS:
            is_in = False
            for current_exp in exps:
                is_in = is_in or (special in current_exp)
            if is_in:
                exps.append(special)
        self.request_dict["expansions"] = exps
        if all([checkbox.isChecked() for checkbox in checkbox_exp_dict.values()]):
            button.setText("Deselect all Expansions")
        else:
            button.setText("Select all Expansions")

    def toggle_all_expansions(self, checkbox_exp_dict, button):
        if all([checkbox.isChecked() for checkbox in checkbox_exp_dict.values()]):
            for checkbox in checkbox_exp_dict.values():
                checkbox.toggle()
        else:
            for checkbox in checkbox_exp_dict.values():
                checkbox.setChecked(True)
        self.read_expansions(checkbox_exp_dict, button)

    def read_attack_types(self, checkbox_att_dict, button):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        atts = [
            att for att, checkbox in checkbox_att_dict.items() if checkbox.isChecked()
        ]
        self.request_dict["attack_types"] = atts
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
        self.request_dict["rerolled_cards"] = []
        self.kingdom = Kingdom(self.all_cards)
        self.kingdom.randomize(self.request_dict)

    def reroll_card(self, old_card):
        """Creates a new card with the old card removed and tries a reroll."""
        kept_cards = [card for card in self.kingdom.kingdom_cards if card != old_card]
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
            kingdom_cards=kept_cards,
            landscapes=kept_landscapes,
            ally=kept_ally,
        )
        self.request_dict["rerolled_cards"].append(old_card)
        self.kingdom.randomize(self.request_dict)

    def get_attack_types(self):
        all_types = [
            element for list_ in self.all_cards["AttackType"] for element in list_
        ]
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
        self.request_dict["qualities"][qual] = val

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


class CardSubset:
    def __init__(self, df, already_picked):
        self.df = df.drop(already_picked.index)
        self.already_picked = already_picked

    def __len__(self):
        return len(self.df)

    def filter_requirement(self, req):
        df = self.df
        self.df = df.loc(df[req] > 0)

    def filter_cost(self, cost):
        raise Exception  # unfinished
        self.df = self.df.loc(df["Cost"] == cost)

    def filter_types(self, types):
        df = self.df
        # set().intersect finds the intersection of the two, bool returns False if empty
        self.df = df.loc(df["Types"].apply(lambda x: types in x))

    def filter_in_supply(self):
        self.df = self.df[self.df["IsInSupply"]]

    def pick_card(self):
        self.filter_in_supply()
        pick = self.df.sample(n=1)
        return pick

    def pick_landscape(self):
        if self.already_picked["Types"].apply(lambda types: "Way" in types).any():
            self.df = self.df[self.df["Types"].apply(lambda types: "Way" not in types)]
        landscapes = self.df[self.df["IsLandscape"]]
        pick = landscapes.sample(n=1)
        return pick


def give_card(df, name):
    return df[df["Name"] == name]


if __name__ == "__main__":
    a = DataContainer()
    a.randomize()
    print(a.kingdom)
    c = a.all_cards
