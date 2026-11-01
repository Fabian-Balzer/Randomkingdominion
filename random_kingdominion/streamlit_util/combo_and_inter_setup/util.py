import difflib
from typing import Literal

import pandas as pd
import streamlit as st

from ...utils import filter_combo_or_inter_df_for_csos, sanitize_cso_list
from ..constants import (
    ALL_CACHED_CSOS,
    ST_ICONS,
    VALID_COMBO_TYPES,
    get_cached_combo_df,
    get_cached_inter_df,
)
from .constants import PAIR_TYPE


def _get_close_match(input_str: str, valid_options: set[str]) -> str | None:
    """Returns the closest match to the input string from the valid options, or None if no close match is found."""
    matches = difflib.get_close_matches(input_str, valid_options, n=1, cutoff=0.6)
    return matches[0] if matches else None


def st_parse_csv_input(csv_input: str) -> set[str]:
    """Parses a comma-separated string into a list of sanitized CSO names."""
    input_strs = csv_input.split(",")
    requested_csos: dict[str, str] = dict(
        zip(sanitize_cso_list(input_strs, sort=False), input_strs)
    )
    valid_csos = set(ALL_CACHED_CSOS.index.to_list())
    invalid = list(set(requested_csos) - valid_csos)
    suggestions: dict[str, str] = {}
    for inval in invalid:
        close_match = _get_close_match(inval, valid_csos)
        if close_match:
            suggestions[inval] = close_match
    if len(invalid) > 0:
        is_plural = len(invalid) > 1
        if is_plural:
            invalids = "**', '**".join(invalid[:-1])
            invalids += f"**' and '**{invalid[-1]}"
        else:
            invalids = invalid[0]
        warn_str = f"The CSO{ 's' if is_plural else ''} '**{invalids}**' {'are' if is_plural else 'is'} not recognized. Did you spell everything correctly, and did you use commas as separators?"
        if len(suggestions) > 0:
            suggestion_msgs = []
            for inval, sugg in suggestions.items():
                input_str = requested_csos.get(inval, inval).strip()
                try:
                    name = ALL_CACHED_CSOS.at[sugg, "Name"]
                except KeyError:
                    name = sugg
                suggestion_msgs.append(
                    f"Did you mean '**{name}**' instead of '**{input_str}**'?"
                )
            warn_str += "\n\n- " + "\n- ".join(suggestion_msgs)
        st.warning(warn_str)
    return set(requested_csos) - set(invalid)


def get_name(pair_type: PAIR_TYPE) -> str:
    """Returns the name corresponding to the pair type."""
    return "interaction" if pair_type == "inter" else "combo"


def get_combo_icon(combo_type: str) -> str:
    return ST_ICONS.get("combo_type_" + combo_type.lower().replace(" ", "_"), "")


def st_build_combo_type_filter(
    label: str,
    key: str,
    default: Literal["all_but_weak", "none", "all"],
) -> list[str]:

    val_dict = {t + " " + get_combo_icon(t): t for t in VALID_COMBO_TYPES}

    if default == "none":
        default_vals = []
    elif default == "all_but_weak":
        default_vals = [t for t in val_dict if "Weak" not in t]
    else:  # default == "all"
        default_vals = list(val_dict.keys())
    selected = st.segmented_control(
        label,
        val_dict.keys(),
        default=default_vals,
        selection_mode="multi",
        help="Which Combo Types to filter for.",
        width="stretch",
        key=key,
    )
    return [val_dict[s] for s in selected]


def _get_pairs_by_first_cso(df: pd.DataFrame) -> dict[str, list[tuple[int, str]]]:
    """For each CSO, the row positions of the pairs it's the first CSO of, together
    with the second CSO."""
    pairs_by_first_cso: dict[str, list[tuple[int, str]]] = {}
    for pos, (cso1, cso2) in enumerate(zip(df["CSO1"], df["CSO2"])):
        pairs_by_first_cso.setdefault(cso1, []).append((pos, cso2))
    return pairs_by_first_cso


def _get_pair_positions_within(
    pairs_by_first_cso: dict[str, list[tuple[int, str]]], csos: set[str]
) -> list[int]:
    """The row positions of the pairs with both CSOs among the given ones, in table
    order, as `filter_combo_or_inter_df_for_csos` with `require_all=True` returns them.
    """
    return sorted(
        pos
        for cso in csos
        for pos, other in pairs_by_first_cso.get(cso, [])
        if other in csos
    )


def add_combo_inter_info_for_kingdoms(df: pd.DataFrame) -> pd.DataFrame:
    """Add combo and interaction information to the given DataFrame of kingdoms."""
    all_inters = get_cached_inter_df()
    all_combos = get_cached_combo_df()
    # Looked up per kingdom instead of filtering both tables for each one, which took
    # ~1.3 s of the ~1.9 s for the 1370 TGG Dailies (M28)
    inters_by_cso = _get_pairs_by_first_cso(all_inters)
    combos_by_cso = _get_pairs_by_first_cso(all_combos)
    inter_keys = all_inters.index.tolist()
    combo_keys = all_combos.index.tolist()
    combo_type_list = all_combos["Type"].tolist()
    combo_infos = []
    combo_types = []
    inter_infos = []
    for cards, landsc in zip(df["cards"], df["landscapes"]):
        kingdom_csos = set(cards + landsc)
        csos = sanitize_cso_list(kingdom_csos, replace_parent_pile=True)
        if len(csos) <= 1:
            # The filter then takes pairs with any of the CSOs
            inters = filter_combo_or_inter_df_for_csos(all_inters, kingdom_csos, True)
            combos = filter_combo_or_inter_df_for_csos(all_combos, kingdom_csos, True)
            inter_infos.append(inters.index.tolist())
            combo_infos.append(combos.index.tolist())
            combo_types.append(combos["Type"].tolist())
            continue
        inter_pos = _get_pair_positions_within(inters_by_cso, set(csos))
        combo_pos = _get_pair_positions_within(combos_by_cso, set(csos))
        inter_infos.append([inter_keys[pos] for pos in inter_pos])
        combo_infos.append([combo_keys[pos] for pos in combo_pos])
        combo_types.append([combo_type_list[pos] for pos in combo_pos])
    df["interactions"] = inter_infos
    df["num_interactions"] = df["interactions"].apply(len)
    df["combos"] = combo_infos
    df["combo_types"] = combo_types
    df["num_combos"] = df["combo_types"].apply(
        lambda x: x.count("Combo") + x.count("Synergy") + x.count("Rush")
    )
    return df
