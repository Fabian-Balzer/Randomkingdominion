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
        self.num_cards = num_cards
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

    def change_quality_arg(self, arg_name, value):
        self.quality_dict[arg_name] = value

    def does_kingdom_fulfill_requirements(self, supply):
        """Checks wether a given kingdom fulfils the requirements passed."""
        for quality in ["DrawQuality", "VillageQuality"]:
                if sum(supply[quality]) < self.quality_dict[quality]:
                    return False
        return True


def filter_sets(df, sets):
    df = df.loc[df["Set"].apply(lambda x: x in sets)]
    return df


class DataContainer:
    def __init__(self):
        self.params = RandomParameters()
        self.all_cards = read_dataframe_from_file(filename="good_card_data.csv", folder="card_info")
        self.params.load_sets(set(self.all_cards["Set"]))
        self.params.load_attack_types(set())

    def print_kingdom(self):
        print(self.kingdom_cards[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))
        print(self.landscapes[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))

    def update_card_subset(self):
        self.card_subset = filter_sets(self.all_cards, self.params.sets)  # Subset of the currently overall available cards

    def randomize(self):
        self.update_card_subset()
        try_, max_tries = 1, 200
        no_good_kingdom = True
        while no_good_kingdom:
            self.kingdom = pull_kingdom_cards(self.card_subset, self.params)
            self.landscapes = pull_landscapes(self.card_subset, self.params)
            self.supply = create_supply(self.kingdom, self.landscapes)
            no_good_kingdom = not self.params.does_kingdom_fulfill_requirements(self.supply)
            if try_ > max_tries:
                print("Did not find a kingdom with the necessary requirements")
                break
            try_ += 1
        print(self.supply[["Name", "DrawQuality", "VillageQuality"]])
        print(f"Took me {try_-1} tries to get this kingdom.")

    def get_attack_types(self):
        all_types = [element.strip("'") for list_ in self.all_cards["AttackType"] for element in list_.strip('][').split(', ')]
        set_ = set(all_types)
        set_.discard("")
        return set_




def pull_kingdom_cards(cards, params):
    kingdom = cards.iloc[0:0]  # empty kingdom
    for pull in range(params.num_cards):
        subset = CardSubset(cards, kingdom)
        if len(subset) == 0:
            break
        new_card = subset.pick_card(params)
        kingdom = pd.concat([kingdom, new_card])
    return kingdom.sort_values(by=["Cost", "Name"])


def pull_landscapes(cards, params):
    landscapes = cards.iloc[0:0]  # empty landscapes
    if len(cards[cards["IsLandscape"]]) > 0:
        for pull in range(params.num_landscapes):
            subset = CardSubset(cards, landscapes)
            if len(subset) == 0:
                break
            new_landscape = subset.pick_landscape(params)
            landscapes = pd.concat([landscapes, new_landscape])
    return landscapes.sort_values(by=["Cost", "Name"])
    

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

    def pick_card(self, randomizerOptions):
        self.filter_in_supply()
        if randomizerOptions.distribute_cost:
            pass
        pick = self.df.sample(n=1)
        return pick

    def pick_landscape(self, randomizerOptions):
        if self.already_picked["Types"].apply(lambda types: "Way" in types).any():
            self.df = self.df[self.df["Types"].apply(lambda types: "Way" not in types)]
        landscapes = self.df[self.df["IsLandscape"]]
        pick = landscapes.sample(n=1)
        return pick