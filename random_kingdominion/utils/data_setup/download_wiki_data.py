"""Download data from the cards-list page of the wiki"""

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag, NavigableString

_WIKI_URL = "http://wiki.dominionstrategy.com/index.php/List_of_cards"


def _fix_cost_and_vp(doc: Tag) -> None:
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


def _improve_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Improve the dataframe by converting the cost and vp columns to integers."""

    df = df.rename(columns={"Set": "Expansion"})
    df["Name"] = df["Name"].str.replace("200px", "")
    df["Name"] = df["Name"].str.replace("320px", "")
    return df


def download_wiki_data() -> pd.DataFrame:
    """Reads the data from the wiki page and returns a dataframe with the
    necessary data"""
    table_class = "wikitable sortable"
    response = requests.get(_WIKI_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    card_table = soup.find("table", {"class": table_class})
    if not isinstance(card_table, Tag):
        raise ValueError("Could not find the card table on the wiki page.")
    _fix_cost_and_vp(card_table)
    # print(card_table.find('span', {"class": "coin-icon"}))
    # Remove the non-breaking spaces, turning them into regular spaces:
    htmlstring = str(card_table).replace(" ", " ")
    df = pd.read_html(htmlstring, encoding="utf-8")[0]
    df = _improve_dataframe(df)
    return df
