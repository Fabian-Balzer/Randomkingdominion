# %%
import json
import random
import time
from dataclasses import dataclass
from urllib import request

import pandas as pd
from card_scraper import read_dataframe_from_file
from matplotlib.pyplot import draw


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
        self.quality_dict = {"DrawQuality": draw_quality,
                             "VillageQuality": village_quality}
        self.draw_requirement_index = random.randint(
            1, num_cards + num_landscapes)
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
                # Otherwise we'd change set size during iteration
                is_in = is_in or (special in current_set)
            if is_in:
                self.sets.add(special)

    def toggle_attack_type(self, type_):
        self.attack_types.discard(
            type_) if type_ in self.sets else self.sets.add(type_)


def filter_sets(df, sets):
    df = df.loc[df["Set"].apply(lambda x: x in sets)]
    return df


class KingdomQualities(dict):
    def __init__(self, default=True, *args, **kwargs):
        defaultkeys = ["Draw", "Village", "Trashing"]
        if default:
            for qual in defaultkeys:
                self[qual] = 0
        else:
            for qual in defaultkeys:
                self[qual] = kwargs["qual_dict"][qual]
        kwargs.clear()
        super(KingdomQualities, self).__init__(*args, **kwargs)

    def reset_values(self):
        for qual in self:
            self[qual] = 0

    def prettify(self):
        return "\n".join(f"{qual:8} quality:\t{val}" for qual, val in self.items())


class EmptyError(Exception):
    pass


class Kingdom:
    card_df = None
    history = []

    def __init__(self, all_cards, kingdom_cards=None, landscapes=None, ally=None):
        self.qualities = KingdomQualities()
        self.card_df = all_cards
        # Each kingdom at first does not contain any cards.
        # They need to be added later.
        self.kingdom_cards = kingdom_cards if kingdom_cards else []
        self.landscapes = landscapes if landscapes else []
        self.ally = ally if ally else []
        self.non_supply = []
        self.id = time.time_ns()
        self.history.append(self)

    def __str__(self):
        s = self.get_kingdom_df().to_string(
            columns=["Name", "Cost", "Set"], index=False)
        s += "\n" + self.qualities.prettify() + "\n"
        s += ", ".join(card for card in self.get_kingdom_df()
                       ["Name"])
        return s

    def set_quality_values(self):
        for qual in self.qualities:
            val = sum(self.get_kingdom_df()[qual + "Quality"])
            self.qualities[qual] = val

    def get_kingdom_df(self):
        df = self.card_df[self.card_df["Name"].isin(
            self.kingdom_cards + self.landscapes + [self.ally])].sort_values(
            by=["IsInSupply", "IsLandscape", "IsOtherThing", "Cost", "Name"], ascending=[False, False, False, True, True])
        return df

    def get_kingdom_card_df(self):
        df = self.get_kingdom_df()
        return df[df["Name"].isin(self.kingdom_cards)]

    def get_landscape_df(self):
        df = self.get_kingdom_df()
        return df[df["Name"].isin(self.landscapes)]

    def randomize(self, request_dict):
        try:
            draw_pool = self.get_draw_pool(request_dict)
        except EmptyError:
            return
        while len(self.kingdom_cards + self.landscapes) < request_dict["num_cards"] + request_dict["num_landscapes"]:
            pick = self.pick_card_or_landscape(draw_pool, request_dict)
            draw_pool = draw_pool[draw_pool["Name"] != pick]
            self.set_quality_values()

    def get_draw_pool(self, request_dict):
        # Discard everything not contained in the requested sets
        pool = self.card_df[self.card_df["Set"].apply(
            lambda set_: set_ in request_dict["expansions"])]
        # Discard all non-supply-cards as we don't need them to draw from
        pool = pool[pool["IsInSupply"] | pool["IsLandscape"]]
        pool = pool[pool["Name"].apply(
            lambda name: name not in self.kingdom_cards + self.landscapes)]
        if len(pool) == 0:
            raise EmptyError
        # Make sure to not include rerolled cards, but reconsider them if no other cards are left:
        rerolled = request_dict["rerolled_cards"]
        if len(pool[pool["Name"].apply(lambda name: name not in rerolled)]) > 0:
            pool = pool[pool["Name"].apply(lambda name: name not in rerolled)]
        return pool

    def pick_card_or_landscape(self, draw_pool, request_dict):
        """Adds a card or landscape fitting the needs to the picked selection"""
        narrowed_pool = self.create_narrowed_pool(draw_pool, request_dict)
        if len(narrowed_pool) > 0:
            pick = narrowed_pool.sample(n=1)
        else:
            print("Could not find any more cards/landscapes to draw from.")
            return ""
        name = pick.iloc[0]["Name"]
        if pick.iloc[0]["IsLandscape"]:
            self.landscapes.append(name)
        else:
            self.kingdom_cards.append(name)
        return name
        # TODO: Append Associated cards

    def create_narrowed_pool(self, draw_pool, request_dict):
        """Creates a pool of cards to pick from. Excludes Kingdom cards and landscapes if the requested quantities have already been picked.
        Discards cards that have been rerolled unless this would imply that none are left."""
        if len(self.landscapes) == request_dict["num_landscapes"]:
            draw_pool = draw_pool[~draw_pool["IsLandscape"]]
        # Discard any secondary ways:
        if self.contains_way():
            draw_pool = draw_pool[draw_pool["Types"].apply(
                lambda x: "Way" not in x)]
        if len(self.kingdom_cards) == request_dict["num_cards"]:
            draw_pool = draw_pool[draw_pool["IsLandscape"]]
        # TODO: Add Rerolled cards in case this leads to nothing
        # Create a dictionary for args that still require fulfilment (i. e. VQ is set to 7-4 if the kingdom already contains a VQ of 4)
        choices = {}
        for qual in self.qualities:
            val = request_dict["qualities"][qual] - self.qualities[qual]
            if val > 0:
                choices[qual] = val
        if len(choices) > 0:  # pick a quality defining this draw
            # weighting the choices by urgency
            qual = random.choice(
                [k for k in choices for x in range(choices[k])])
            min_qual_val = random.randint(1, min(6, choices[qual]))
            defining_quality = qual + "Quality"
            before_narrowing = draw_pool
            draw_pool = draw_pool[draw_pool[defining_quality] >= min_qual_val]
            # If the constraints are too much, do not constrain it.
            if len(draw_pool) == 0:
                draw_pool = before_narrowing
        return draw_pool

    def contains_way(self):
        """Returns wether the kingdom already contains a way."""
        df = self.get_kingdom_df()
        return len(df[df["Types"].apply(lambda x: "Way" in x)]) > 0


class DataContainer:
    def __init__(self):
        self.all_cards = read_dataframe_from_file(
            filename="good_card_data.csv", folder="card_info")
        self.all_sets = list(set(self.all_cards["Set"]))
        self.all_attack_types = self.get_attack_types()
    #     # TODO: Load this from a config file
        self.request_dict = {"expansions": ["Menagerie", "Nocturne"],
                             "num_cards": 10,
                             "num_landscapes": 2,
                             "qualities": KingdomQualities(default=False,
                                                           qual_dict={"Draw": 0, "Village": 5, "Trashing": 2}),
                             "rerolled_cards": []}
        self.parameter_dict = {"RequireReaction": False, "AttackType": None}
        self.kingdom = None

    def read_expansions(self, checkbox_exp_dict):
        """Reads out the currently selected sets and saves them. Also changes the selection."""
        exps = [
            exp for exp, checkbox in checkbox_exp_dict.items() if checkbox.isChecked()]
        for special in ["Base", "Intrigue"]:
            is_in = False
            for current_exp in exps:
                is_in = is_in or (special in current_exp)
            if is_in:
                exps.append(special)
        self.request_dict["expansions"] = exps

    def randomize(self):
        self.request_dict["rerolled_cards"] = []
        self.kingdom = Kingdom(self.all_cards)
        self.kingdom.randomize(self.request_dict)

    def reroll_card(self, old_card):
        """Creates a new card with the old card removed and tries a reroll."""
        kept_cards = [
            card for card in self.kingdom.kingdom_cards if card != old_card]
        kept_landscapes = [
            card for card in self.kingdom.landscapes if card != old_card]
        kept_ally = self.kingdom.ally if old_card != self.kingdom.ally else ""
        # TODO: Watch out for rerolled Liaisons
        self.kingdom = Kingdom(self.all_cards, kingdom_cards=kept_cards,
                               landscapes=kept_landscapes, ally=kept_ally)
        self.request_dict["rerolled_cards"].append(old_card)
        self.kingdom.randomize(self.request_dict)

    def get_attack_types(self):
        all_types = [element.strip("'") for list_ in self.all_cards["AttackType"]
                     for element in list_.strip('][').split(', ')]
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
            self.df = self.df[self.df["Types"].apply(
                lambda types: "Way" not in types)]
        landscapes = self.df[self.df["IsLandscape"]]
        pick = landscapes.sample(n=1)
        return pick


if __name__ == "__main__":
    a = DataContainer()
    a.randomize()
    c = a.all_cards
