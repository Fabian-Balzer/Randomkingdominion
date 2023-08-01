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

import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

from modules.add_info_columns import add_info_columns, add_split_piles
from modules.write_image_database import write_image_database

# Determines wether the program tries to scrape the wiki pages for
# card and image data or just meddle with existing data
DOWNLOAD_DATA = not os.path.isfile("card_info/raw_card_data.csv")


def fix_cost_and_vp(doc):
    """As cost and victory points are hidden in images, the parser has a hard time
    reading it. Thus, we modify it a little to only have the alt value."""
    pics = doc.find_all('span', {"class": "coin-icon"})
    for pic in pics:
        alt_price = pic.find("img")["alt"]
        pic.string = alt_price
    return pics


def retrieve_data():
    """Reads the data from the wiki page and returns a dataframe with the
    necessary data"""
    wiki_url = "http://wiki.dominionstrategy.com/index.php/List_of_cards"
    table_class = "wikitable sortable"
    response = requests.get(wiki_url)
    soup = BeautifulSoup(response.text, "html.parser")
    card_table = soup.find('table', {'class': table_class})
    fix_cost_and_vp(card_table)
    # print(card_table.find('span', {"class": "coin-icon"}))
    htmlstring = str(card_table)
    df = pd.read_html(htmlstring, encoding='utf-8')[0]
    return df


def write_dataframe_to_file(df, filename, folder):
    """Writes the given dataframe to a file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    fpath = folder + "/" + filename
    if os.path.isfile(fpath):
        answer = input(
            f"The file '{fpath}' already exists.\nDo you want to overwrite (y) or cancel (n)?\n>>> ")
        while True:
            if answer == "n":
                print("Did not rewrite the file due to your concerns.")
                return
            if answer == "y":
                break
            answer = input(
                "Please type y for overwriting or n for cancelling.\n>>> ")
    df.to_csv(fpath, sep=";", index=False)
    print(
        f"Successfully wrote the dominion cards to the file '{fpath}' in the current path.")


def read_dataframe_from_file(filename, folder, eval_lists=False):
    fpath = folder + "/" + filename
    if os.path.isfile(fpath):
        df = pd.read_csv(fpath, sep=";", header=0)
        if eval_lists:
            for colname in "Types", "AttackType":
                # Make sure we properly handle lists
                df[colname] = df[colname].apply(eval)
    else:
        raise FileNotFoundError(
            2, "Couldn't find the raw card data file, please download it first.")
    return df


def main():
    if DOWNLOAD_DATA:
        df = retrieve_data()
        df["Cost"] = df["Cost"].str.replace("star", "*")
        df["Cost"] = df["Cost"].str.replace("plus", "+")
        df = df.rename(columns={"Set": "Expansion"})
        df = write_image_database(df)
        write_dataframe_to_file(
            df, filename="raw_card_data.csv", folder="card_info")
    df = read_dataframe_from_file(
        filename="raw_card_data.csv", folder="card_info")
    df = add_split_piles(df)
    df = add_info_columns(df)
    write_dataframe_to_file(
        df, filename="good_card_data.csv", folder="card_info")
    return df


if __name__ == "__main__":
    df = main()  # For me to inspect it in variable manager
    print(df[df["Name"] == "Elder"]["AttackType"])
