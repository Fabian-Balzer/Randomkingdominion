"""Utility functions for adding interactions to the dataframe."""

import pandas as pd

from ...constants import ALL_CSOS
from ...kingdom import get_interaction_identifier, sanitize_cso_name


def add_interaction(
    c1: str,
    c2: str,
    interaction: str,
    df: pd.DataFrame,
    overwrite=False,
    add_together_if_present=False,
    warn_duplicate=True,
) -> None:
    """Add a new interaction to the interactions dataframe, and sort it."""
    c1 = sanitize_cso_name(c1)
    c2 = sanitize_cso_name(c2)
    assert c1 in ALL_CSOS.index, f"{c1} not in the card list."
    assert c2 in ALL_CSOS.index, f"{c2} not in the card list."
    c1, c2 = sorted([c1, c2])
    ident = get_interaction_identifier(c1, c2)
    if ident in df.index:
        if warn_duplicate and not add_together_if_present:
            print(
                f"WARNING: {c1} and {c2} already have a rule ({df.loc[ident]['Rule']})."
            )
        if add_together_if_present:
            df.loc[ident, "Rule"] += "\n" + interaction  # type: ignore
            print(f"NOTE: Adding another interaction for {c1} and {c2}.")
            # print(
            #     f"Adding the new rule to the existing rule, which is now\n\t'{df.loc[ident, 'Rule']}'."
            # )
            return
        elif not overwrite:
            return
        print("Overwriting the existing rule.")
    df.loc[ident] = [c1, c2, interaction]
    df.sort_index(inplace=True)


def add_multiple_interactions(
    csos: str, interaction: str, df: pd.DataFrame, add_together_if_present=False
):
    """Adds interactions for each of the CSOs, assuming that the first and second component
    are separated by the '/' character, and that different csos are separated by the '|'
    character, e.g.
    >>> csos = "Chapel|Village/Moat"
    will construct two interactions (Chapel/Moat), (Village/Moat).
    Refer to the components in the interaction string using '{card_a}' and '{card_b}';
    These will get replaced by the card's names.
    """
    c1s, c2s = csos.split("/")
    for c1 in c1s.split("|"):
        for c2 in c2s.split("|"):
            inter = interaction.replace("{card_a}", c1)
            inter = inter.replace("{card_b}", c2)
            add_interaction(
                c1, c2, inter, df, add_together_if_present=add_together_if_present
            )


def add_multiple_interactions_from_single(
    single_str: str, df: pd.DataFrame, add_together_if_present=False
) -> None:
    """Same as ``add_multiple_interactions``, however the single_str is split by "---"
    assuming the first part are the csos and the second part is the interaction.
    """
    csos, inter = single_str.split("---")
    add_multiple_interactions(
        csos, inter, df, add_together_if_present=add_together_if_present
    )


def get_empty_interaction_df() -> pd.DataFrame:
    """Set up an an empty interactions DataFrame."""
    cols = ["Card1", "Card2", "Rule", "ident"]
    df = pd.DataFrame(columns=cols)
    df.set_index("ident", inplace=True)
    return df
