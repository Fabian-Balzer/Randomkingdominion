# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 10:09:11 2021

@author: Fabian Balzer

***
LICENSE:
    Copyright 2021 Fabian Balzer

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
***

Code to read the table data and save it as CSV
"""
# %%

import sys

sys.path.append("..")

import argparse

import random_kingdominion as rk
from random_kingdominion.utils.data_setup import (
    add_additional_entries,
    add_additional_info_columns,
    download_wiki_data,
    write_image_database,
)
from random_kingdominion.utils.interaction_setup import write_interaction_database


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--download",
        "-d",
        action="store_true",
        default=False,
        help="If set, the script will try to download the data freshly from the Cards List page of the wiki, and try to download all unavailable pictures from the Wiki and write the image database.",
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        default=False,
        help="If set, the script will overwrite the existing data files (e.g. the processed one, and, if you've downloaded it, the raw data one). Otherwise, you'll be prompted to confirm overwriting.",
    )
    parser.add_argument(
        "--interactions",
        "-i",
        action="store_true",
        default=False,
        help="If set, rewrite the interactions file.",
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
    """Main function to download the card data from the wiki and write it to a file.
    Asks the user if they want to download the data from the wiki, and whether they want to write the image database.
    """
    args = parse_args()
    overwrite, verbose = args.overwrite, args.verbose
    if args.download:
        df = download_wiki_data()
        df = write_image_database(df)
        rk.write_dataframe_to_file(
            df, rk.FPATH_RAW_DATA, overwrite=overwrite, verbose=verbose
        )
    df = rk.read_dataframe_from_file(rk.FPATH_RAW_DATA)
    df = add_additional_entries(df)
    df = add_additional_info_columns(df)
    rk.write_dataframe_to_file(
        df, rk.FPATH_CARD_DATA, overwrite=overwrite, verbose=verbose
    )
    if args.interactions:
        write_interaction_database(overwrite=overwrite, verbose=verbose)
    return df


if __name__ == "__main__":
    df = main()  # For me to inspect it in variable manager
