import pandas as pd
from card_scraper import read_dataframe_from_file


class RandomParameters:
    """A class containing all options as attributes"""
    def __init__(self, num_cards=10,
                 num_landmarks=2,
                 drawers=None,
                 trashers=None,
                 attacks=None,
                 distribute_cost=False):
        self.num_cards = num_cards
        self.num_landmarks = num_landmarks
        self.drawers = drawers
        self.trashers = trashers
        self.distribute_cost = distribute_cost

    def load_sets(self, sets):
        self.sets = sets

    def toggle_set(self, set):
        self.sets.discard(set) if set in self.sets else self.sets.add(set)


def filter_sets(df, sets):
    df = df.loc[df["Set"].apply(lambda x: x in sets)]
    return df


class DataContainer:
    def __init__(self):
        self.params = RandomParameters()
        self.all_cards = read_dataframe_from_file(filename="good_card_data.csv", folder="card_info")
        self.params.load_sets(set(self.all_cards["Set"]))

    def print_kingdom(self):
        print(self.kingdom_cards[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))
        print(self.landscapes[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))

    def update_card_subset(self):
        self.card_subset = filter_sets(self.all_cards, self.params.sets)  # Subset of the currently overall available cards

    def randomize(self):
        self.update_card_subset()
        self.kingdom = pull_kingdom_cards(self.card_subset, self.params)
        self.landscapes = pull_landscapes(self.card_subset, self.params)
        self.supply = create_supply(self.kingdom, self.landscapes)


def pull_kingdom_cards(cards, params):
    kingdom = cards.iloc[0:0]  # empty kingdom
    for pull in range(params.num_cards):
        subset = CardSubset(cards, kingdom)
        new_card = subset.pick_card(params)
        kingdom = pd.concat([kingdom, new_card])
    return kingdom.sort_values(by=["Cost", "Name"])


def pull_landscapes(cards, params):
    landscapes = cards.iloc[0:0]  # empty landmarks
    if len(cards[cards["IsLandscape"]]) > 0:
        for pull in range(params.num_landmarks):
            subset = CardSubset(cards, landscapes)
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
            print("Excluding ways," + str(self.already_picked))
            self.df = self.df[self.df["Types"].apply(lambda types: "Way" not in types)]
        landscapes = self.df[self.df["IsLandscape"]]
        pick = landscapes.sample(n=1)
        return pick