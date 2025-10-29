import pandas as pd

from ...utils import get_cso_name
from ..interaction_util import add_interaction

_EXTRA_TURN_GIVERS = [
    "Outpost",
    "Voyage",
    "Journey",
    "Mission",
    "Island Folk",
    "Seize the Day",
]


def _add_lich_interactions(df: pd.DataFrame):
    for extra_turn_giver, acquire_str, condition in [
        ("outpost", "play", ", but you only draw 3 cards for your next turn"),
        ("voyage", "play", ", and your next turn proceeds as normal"),
        (
            "journey",
            "buy",
            ", but your cards remain in play until your opponent's Clean-up phase",
        ),
        ("mission", "buy", ", and your next turn proceeds as normal"),
        ("island_folk", "activate", ", and your next turn proceeds as normal"),
        ("seize_the_day", "buy", ", and your next turn proceeds as normal"),
    ]:
        name = get_cso_name(extra_turn_giver)
        rule = f"If you play Lich and then {acquire_str} {name}, the {name} turn is skipped{condition}."
        if extra_turn_giver != "seize_the_day":
            rule += f" If, however, you play Lich during an extra turn, even if you {acquire_str} {name} then, your next normal turn will still be skipped."
        add_interaction("Wizards", extra_turn_giver, rule, df)


def _add_fleet_interactions(df: pd.DataFrame):
    for extra_turn_giver, acquire_str in [
        ("outpost", "play"),
        ("voyage", "play"),
        ("journey", "buy"),
        ("mission", "buy"),
        ("possession", "play"),
        ("island_folk", "activate"),
        ("seize_the_day", "buy"),
    ]:
        name = get_cso_name(extra_turn_giver)
        rule = f"If you {acquire_str} {name} on your Fleet turn, you will only get an extra turn from it if any other turns (from an opponent) would follow."
        add_interaction("Fleet", extra_turn_giver, rule, df)


def _add_on_extra_turn_interactions(df: pd.DataFrame):
    for extra_turn_giver in _EXTRA_TURN_GIVERS:
        rule = f"Playing Outpost on an extra {extra_turn_giver} turn will not give you an extra turn, but you will still only draw 3 cards for your next turn."
        add_interaction(
            "Outpost", extra_turn_giver, rule, df, add_together_if_present=True
        )
        rule = f"Buying Journey on an extra {extra_turn_giver} turn will not give you an extra turn, but your cards will remain in play until your opponent's Clean-up phase."
        add_interaction(
            "Journey", extra_turn_giver, rule, df, add_together_if_present=True
        )
        if extra_turn_giver != "Seize the Day":
            rule = f"Buying Seize the Day on an extra {extra_turn_giver} turn will still give you a normal extra turn."
            add_interaction(
                "Seize the Day",
                extra_turn_giver,
                rule,
                df,
                add_together_if_present=True,
            )

    rule = "If you play Outpost and Voyage, then in Clean-up you don't discard either of them and only draw 3 cards. In between turns, you choose to take the Voyage turn next. (Outpost hasn't failed yet because another player might somehow be able to take an extra turn first.) In Clean-up of the Voyage turn, you discard Voyage but not Outpost and draw 5 cards. In between turns again, Outpost now fails - it is up next but would be your 3rd turn in a row. The next player takes their turn and during their Clean-up, you discard Outpost."
    add_interaction("Outpost", "Voyage", rule, df, add_together_if_present=True)


def add_all_extra_turn_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all extra turn interactions to the DataFrame."""
    num_before = len(df)
    _add_lich_interactions(df)
    _add_fleet_interactions(df)
    _add_on_extra_turn_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} extra turn interactions.")
