# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 10:09:11 2021

@author: Fabian Balzer

***
LICENSE:
    Copyright (C) 2021-2026 Fabian Balzer
    SPDX-License-Identifier: AGPL-3.0-or-later

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program (LICENSE.txt). If not, see <https://www.gnu.org/licenses/>.

    Additional terms under section 7(b) of the GNU AGPL: modified versions must
    retain the notice "Based on Random KingDominion by Fabian Balzer
    (https://github.com/Fabian-Balzer/Randomkingdominion)" in the user interface,
    e.g. on an About page.

***

Code to read the table data and save it as CSV
"""

# %%

import sys

sys.path.append("..")

import argparse

import random_kingdominion as rk
from random_kingdominion.utils.data_setup import (
    add_image_paths,
    build_card_df,
    perform_full_yt_processing,
    read_wiki_card_list,
)
from random_kingdominion.utils.interaction_setup import (
    write_combo_database,
    write_interaction_database,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--wiki_html",
        "-w",
        type=str,
        default=None,
        help="Path to a copy of the wiki's List of cards page saved in a browser (https://wiki.dominionstrategy.com/index.php/List_of_cards, 'Save page as', HTML only). Its card table is parsed and written to the raw data file; missing card images are listed, they have to be added by hand.",
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        default=False,
        help="If set, the script will overwrite the existing data files (e.g. the processed one, and, with --wiki_html, the raw data one). Otherwise, you'll be prompted to confirm overwriting.",
    )
    parser.add_argument(
        "--main_db",
        "-m",
        action="store_true",
        default=False,
        help="If set, rewrite the main database file.",
    )
    parser.add_argument(
        "--interactions",
        "-i",
        action="store_true",
        default=False,
        help="If set, rewrite the interactions file.",
    )
    parser.add_argument(
        "--combos",
        "-c",
        action="store_true",
        default=False,
        help="If set, rewrite the combos file.",
    )
    parser.add_argument(
        "--youtube",
        "-y",
        action="store_true",
        default=False,
        help="If set, rewrite the youtube link file.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="If set, print out more information during the process.",
    )
    return parser.parse_args()


def main():
    """Main function to (re)build the data files in card_info from their sources.
    Without --overwrite, asks before replacing an existing file.
    """
    args = parse_args()
    if not (
        args.wiki_html
        or args.main_db
        or args.interactions
        or args.combos
        or args.youtube
    ):
        rk.LOGGER.warning(
            "No action specified. Use --wiki_html, --main_db, --youtube, --interactions, or --combos, or -w, -m, -y, -i, -c flags to run any mode."
        )
        return
    overwrite, verbose = args.overwrite, args.verbose
    if args.wiki_html:
        df = add_image_paths(read_wiki_card_list(args.wiki_html))
        rk.write_dataframe_to_file(
            df, rk.FPATH_RAW_DATA, overwrite=overwrite, verbose=verbose
        )
    if args.main_db:
        rk.write_dataframe_to_file(
            build_card_df(), rk.FPATH_CARD_DATA, overwrite=overwrite, verbose=verbose
        )
    if args.interactions:
        write_interaction_database(overwrite=overwrite, verbose=verbose)
    if args.combos:
        write_combo_database(overwrite=overwrite, verbose=verbose)
    if args.youtube:
        perform_full_yt_processing(overwrite=overwrite, verbose=verbose, download=True)
    # return df


if __name__ == "__main__":
    main()
