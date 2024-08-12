import pandas as pd

from .constants import ALL_CARDS, ALL_CSOS, ALL_LANDSCAPES


def is_extended_landscape(cso: pd.Series | str) -> bool:
    """Check whether the given cso is a landscape or an ally."""
    if not isinstance(cso, str):
        cso = cso["Name"]
    return cso in ALL_LANDSCAPES


def is_card(cso: pd.Series | str) -> bool:
    """Check whether the given cso is a (supply) kingdom card."""
    if not isinstance(cso, str):
        cso = cso["Name"]
    return cso in ALL_CARDS


def is_cso_in_expansions(cso: pd.Series | str, expansions: list[str]) -> bool:
    """Check whether the given cso is included in the given expansions."""
    if isinstance(cso, str):
        cso = ALL_CSOS.loc[cso]  # type: ignore
    return cso["Expansion"] in expansions  # type: ignore
