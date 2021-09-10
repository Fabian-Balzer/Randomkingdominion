import pandas as pd


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



def read_file():
    filename = "card_data.csv"
    df = pd.read_csv(filename, sep=";", header=0)
    return df


def filter_sets(df, sets):
    df = df.loc[df["Set"].apply(lambda x: x in sets)]
    return df


class DataContainer:
    def __init__(self):
        self.params = RandomParameters()
        self.all_cards = read_file()
        self.params.load_sets(set(self.all_cards["Set"]))

    def print_kingdom(self):
        print(self.kingdom_cards[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))
        print(self.csos[["Name", "Cost", "Set"]].sort_values(["Cost", "Name"]))

    def update_card_subset(self):
        self.card_subset = filter_sets(self.all_cards, self.params.sets)  # Subset of the currently overall available cards

    def randomize(self):
        self.update_card_subset()
        self.kingdom = pull_kingdom_cards(self.card_subset, self.params)
        self.csos = pull_csos(self.card_subset, self.params)
        self.supply = create_supply(self.kingdom, self.csos)


def pull_kingdom_cards(cards, params):
    kingdom = cards.iloc[0:0]  # empty kingdom
    for pull in range(params.num_cards):
        subset = CardSubset(cards, kingdom)
        new_card = subset.pick_card(params)
        kingdom = pd.concat([kingdom, new_card])
    return kingdom.sort_values(by=["Cost", "Name"])


def pull_csos(cards, params):
    csos = cards.iloc[0:0]  # empty landmarks
    if len(cards[cards["IsCSO"]]) > 0:
        for pull in range(params.num_landmarks):
            subset = CardSubset(cards, csos)
            new_cso = subset.pick_cso(params)
            csos = pd.concat([csos, new_cso])
    return csos.sort_values(by=["Cost", "Name"])
    

def create_supply(kingdom, csos):
    supply = kingdom.append(csos, sort=False)
    supply = supply.sort_values(by=["IsInSupply", "IsCSO", "IsOtherThing", "Cost", "Name"],
        ascending=[False, True, True, True, True])
    return supply


class CardSubset:
    def __init__(self, df, kingdom):
        self.df = df.drop(kingdom.index)
        self.kingdom = kingdom

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

    def pick_cso(self, randomizerOptions):
        csos = self.df[self.df["IsCSO"]]
        pick = csos.sample(n=1)
        return pick