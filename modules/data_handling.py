import pandas as pd
from card_scraper import read_dataframe_from_file
import random
import json


class RandomParameters:
    """A class containing all options as attributes"""
    def __init__(self, num_cards=10,
                 num_landscapes=2,
                 draw_quality=5,
                 village_quality=5,
                 trashers=None,
                 attacks=None,
                 distribute_cost=False):
        self.num_kingdomcards = num_cards
        self.num_landscapes = num_landscapes
        self.quality_dict = {"DrawQuality": draw_quality, "VillageQuality": village_quality}
        self.draw_requirement_index = random.randint(1, num_cards + num_landscapes)
        self.distribute_cost = distribute_cost


    def load_sets(self, sets):
        self.sets = sets

    def load_attack_types(self, types):
        self.attack_types = types

    def toggle_set(self, set_):
        self.sets.discard(set_) if set_ in self.sets else self.sets.add(set_)
        for special in ["Base", "Intrigue"]:
            is_in = False
            self.sets.discard(special)
            for current_set in self.sets:
                is_in = is_in or (special in current_set)  # Otherwise we'd change set size during iteration
            if is_in:
                self.sets.add(special)

    def toggle_attack_type(self, type_):
        self.attack_types.discard(type_) if type_ in self.sets else self.sets.add(type_)




def filter_sets(df, sets):
    df = df.loc[df["Set"].apply(lambda x: x in sets)]
    return df


class DataContainer:
    def __init__(self):
        self.all_cards = read_dataframe_from_file(filename="good_card_data.csv", folder="card_info")
        self.all_sets = list(set(self.all_cards["Set"]))
        self.selected_sets = []
        self.selected_cards = self.all_cards
        self.picked_selection = self.all_cards.iloc[0:0]
        self.num_kingdomcards = 10
        self.num_landscapes = 2
        self.quality_dict = {"DrawQuality": 0, "VillageQuality": 0}  # Dict containing the quality parameters for the kingdom
        self.kingdom_dict = {"DrawQuality": 0, "VillageQuality": 0}  # Dict containing information about the kingdom

        # self.params.load_sets(set(self.all_cards["Set"]))
        # self.params.load_attack_types(set())

    def print_kingdom(self):
        print(self.kingdom_cards[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))
        print(self.landscapes[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))

    def get_sets(self, checkbox_set_dict):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        self.selected_sets = [setname for setname, checkbox in checkbox_set_dict.items() if checkbox.isChecked()]
        for special in ["Base", "Intrigue"]:
            is_in = False
            for current_set in self.selected_sets:
                is_in = is_in or (special in current_set)
            if is_in:
                self.selected_sets.append(special)

    def set_sets(self, set_dict):
        # TODO: Load this from a config file.
        for set_ in ["Menagerie", "Nocturne"]:
            set_dict[set_].setChecked(True)

    def get_quality_arg(self, arg_name, value):
        self.quality_dict[arg_name] = value

    def set_quality_args(self, spin_dict):
        # TODO: Load this from a config file
        for arg_name in self.quality_dict.keys():
            spin_dict[arg_name].setValue(self.quality_dict[arg_name])

    def reset_kingdom_dict(self):
        for key in self.kingdom_dict.keys():
            self.kingdom_dict[key] = 0

    def randomize(self):
        self.reset_kingdom_dict()
        self.selected_cards = self.all_cards[self.all_cards["Set"].apply(lambda set_: set_ in self.selected_sets)]
        print(self.selected_cards)
        self.selected_cards = self.selected_cards[self.selected_cards["IsInSupply"] | self.selected_cards["IsLandscape"]]
        self.picked_selection = self.all_cards.iloc[0:0]
        for i in range(self.num_kingdomcards + self.num_landscapes):
            self.pick_card_or_landscape()
        self.sort_selection()
        self.kingdom = self.picked_selection[~self.picked_selection["IsLandscape"]]
        self.landscapes = self.picked_selection[self.picked_selection["IsLandscape"]]
        print(self.picked_selection[["Name", "DrawQuality", "VillageQuality"]])
        qualities = {qual: sum(self.picked_selection[qual + "Quality"]) for qual in ["Draw", "Village"]}
        print("\n".join([f"Total {qual} Quality:\t{val}" for qual, val in qualities.items()]))

    def pick_card_or_landscape(self):
        draw_pool = self.create_draw_pool()
        if len(draw_pool) > 0:
            pick = draw_pool.sample(n=1)
            self.picked_selection = pd.concat([self.picked_selection, pick])
        # TODO: Append Associated cards
        for arg_name in self.quality_dict.keys():
            self.kingdom_dict[arg_name] = sum(self.picked_selection[arg_name])

    def create_draw_pool(self):
        draw_pool = self.selected_cards.drop(self.picked_selection.index)
        if len(self.picked_selection[self.picked_selection["IsLandscape"]]) == self.num_landscapes:
            draw_pool = draw_pool[~draw_pool["IsLandscape"]]
        if len(self.picked_selection[~self.picked_selection["IsLandscape"]]) == self.num_kingdomcards:
            draw_pool = draw_pool[draw_pool["IsLandscape"]]
        # Create a dictionary for args that still require fulfilment (i. e. VQ is set to 7-4 if the kingdom already contains a DQ of 4)
        choices = {arg_name: (val - self.kingdom_dict[arg_name]) \
            for arg_name, val  in self.quality_dict.items() if val - self.kingdom_dict[arg_name] > 0}
        if len(choices) > 0:  # pick a quality defining this draw
            defining_quality = random.choice([k for k in choices for x in range(choices[k])])  # weighting the choices by urgency
            min_quality = random.randint(1, min(6, choices[defining_quality]))
            before_narrowing = draw_pool
            draw_pool = draw_pool[draw_pool[defining_quality] >= min_quality]
            if len(draw_pool) == 0:  # If the constraints are too much, do not constrain it.
                draw_pool = before_narrowing
        return draw_pool

    def randomize_brute_force(self):
        try_, max_tries = 1, 200
        no_good_kingdom = True
        while no_good_kingdom:
            self.kingdom = self.pull_kingdom_cards()
            self.landscapes = self.pull_landscapes()
            self.picked_cards = create_supply(self.kingdom, self.landscapes)
            no_good_kingdom = not self.does_kingdom_fulfill_requirements()
            if try_ > max_tries:
                print("Did not find a kingdom with the necessary requirements")
                break
            try_ += 1
        print(self.picked_cards[["Name", "DrawQuality", "VillageQuality"]])
        print(f"Took me {try_-1} tries to get this kingdom.")

    def get_attack_types(self):
        all_types = [element.strip("'") for list_ in self.all_cards["AttackType"] for element in list_.strip('][').split(', ')]
        set_ = set(all_types)
        set_.discard("")
        return set_

    def pull_kingdom_cards(self):
        kingdom = self.selected_cards.iloc[0:0]  # empty kingdom
        for pull in range(self.num_kingdomcards):
            subset = CardSubset(self.selected_cards, kingdom)
            if len(subset) == 0:
                break
            new_card = subset.pick_card()
            kingdom = pd.concat([kingdom, new_card])
        return kingdom.sort_values(by=["Cost", "Name"])

    def pull_landscapes(self):
        landscapes = self.selected_cards.iloc[0:0]  # empty landscapes
        if len(self.selected_cards[self.selected_cards["IsLandscape"]]) > 0:
            for pull in range(self.num_landscapes):
                subset = CardSubset(self.selected_cards, landscapes)
                if len(subset) == 0:
                    break
                new_landscape = subset.pick_landscape()
                landscapes = pd.concat([landscapes, new_landscape])
        return landscapes.sort_values(by=["Cost", "Name"])

    def does_kingdom_fulfill_requirements(self):
        """Checks wether a given kingdom fulfils the requirements passed."""
        for quality in ["DrawQuality", "VillageQuality"]:
                if sum(self.picked_cards[quality]) < self.quality_dict[quality]:
                    return False
        return True

    def sort_selection(self):
        self.picked_selection = self.picked_selection.sort_values(by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"])
    

def create_supply(kingdom, landscapes):
    supply = kingdom.append(landscapes, sort=False)
    supply = supply.sort_values(by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"],
        ascending=[False, True, True, True, True])
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