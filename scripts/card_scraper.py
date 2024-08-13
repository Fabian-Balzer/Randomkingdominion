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

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.append("..")

import random_kingdominion as rk
from random_kingdominion.constants import read_dataframe_from_file
from random_kingdominion.utils.data_setup.add_info_columns import (
    add_quality_info_columns,
    add_split_piles,
)
from random_kingdominion.utils.data_setup.write_image_database import (
    write_image_database,
)
from random_kingdominion.utils.utils import ask_yes_now, write_dataframe_to_file


def fix_cost_and_vp(doc):
    """As cost and victory points are hidden in images, the parser has a hard time
    reading it. Thus, we modify it a little to only have the alt value."""
    pics = doc.find_all("span", {"class": "coin-icon"})
    for pic in pics:
        if pic.find("img") is not None:
            alt_price = pic.find("img")["alt"]
            pic.string = alt_price
    debts = doc.find_all("span", {"class": "debt-icon"})
    for debt in debts:
        if debt.find("img") is not None:
            alt_price = debt.find("img")["alt"]
            debt.string = " " + alt_price


def retrieve_data():
    """Reads the data from the wiki page and returns a dataframe with the
    necessary data"""
    wiki_url = "http://wiki.dominionstrategy.com/index.php/List_of_cards"
    table_class = "wikitable sortable"
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")
    card_table = soup.find("table", {"class": table_class})
    fix_cost_and_vp(card_table)
    # print(card_table.find('span', {"class": "coin-icon"}))
    # Remove the non-breaking spaces, turning them into regular spaces:
    htmlstring = str(card_table).replace(" ", " ")
    df = pd.read_html(htmlstring, encoding="utf-8")[0]
    return df


def main():
    if ask_yes_now("Do you want to try to download the card data from the wiki?"):
        df = retrieve_data()
        df = df.rename(columns={"Set": "Expansion"})
        df["Name"] = df["Name"].str.replace("200px", "")
        df["Name"] = df["Name"].str.replace("320px", "")
        df = write_image_database(df)
        write_dataframe_to_file(df, rk.FPATH_RAW_DATA)
    df = read_dataframe_from_file(rk.FPATH_RAW_DATA)
    df = add_split_piles(df)
    df = add_quality_info_columns(df)
    write_dataframe_to_file(df, rk.FPATH_CARD_DATA)
    return df


if __name__ == "__main__":
    df = main()  # For me to inspect it in variable manager
