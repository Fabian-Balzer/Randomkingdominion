import difflib
from argparse import ArgumentParser, Namespace
from pathlib import Path
from pprint import pformat

import numpy as np

from ..kingdom import KingdomManager
from ..logger import LOGGER


def log_args(
    args: Namespace,
    prog_name: str = "Unknown Program",
    parser: ArgumentParser | None = None,
):
    """Log the arguments in a pretty format."""
    prog_name = Path(prog_name).name
    args_dict = vars(args)

    # If a parser is provided, try to get short options
    if parser is not None:
        short_options = {}
        for action in parser._actions:
            if action.dest == "help" or not action.option_strings:
                continue
            for opt in action.option_strings:
                if len(opt) == 2 and opt.startswith("-"):  # Short option
                    short_options[action.dest] = opt
        args_with_flags = {
            (
                f"{short_options.get(key, '')} ({key})" if key in short_options else key
            ): value
            for key, value in args_dict.items()
        }
    else:
        args_with_flags = args_dict
    LOGGER.info(
        f"Running {prog_name} with the following arguments:\n{pformat(args_with_flags)}"
    )


def get_nearest_kingdom_name(new_name: str, new_date: str, manager: KingdomManager):
    """Use Levenshtein distance to find the closest similarity in strings beween the new kingdom's name and existing kingdoms provided via the kingdom manager."""
    df = manager.dataframe_repr
    names = list(
        np.unique(
            df[df["name"] != new_date]["notes"]
            .fillna("")
            .apply(lambda x: x.get("name", "") if isinstance(x, dict) else "")
        )
    )
    names.remove("")
    return difflib.get_close_matches(new_name, names, n=1, cutoff=0.0)[0]
