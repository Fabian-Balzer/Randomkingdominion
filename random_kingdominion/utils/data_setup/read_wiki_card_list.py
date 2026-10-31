"""Read the card table from a saved copy of the wiki's List of cards page.

The wiki sits behind a bot check, so the page is saved by hand in a browser
(https://wiki.dominionstrategy.com/index.php/List_of_cards, "Save page as", HTML only).
"""

from io import StringIO
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup, Tag


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


def read_wiki_card_list(html_path: str | Path) -> pd.DataFrame:
    """Read the card table from a saved List of cards page and return it as a
    dataframe with the raw card data columns (without ``ImagePath``)."""
    table_class = "wikitable sortable"
    html = Path(html_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    card_table = soup.find("table", {"class": table_class})
    if not isinstance(card_table, Tag):
        raise ValueError(
            f"Could not find the card table in '{html_path}'. Is it a saved copy "
            "of the List of cards page (and not e.g. the wiki's bot check page)?"
        )
    _fix_cost_and_vp(card_table)
    # print(card_table.find('span', {"class": "coin-icon"}))
    # Remove the non-breaking spaces, turning them into regular spaces:
    htmlstring = str(card_table).replace(" ", " ")
    # convert to stringIO object:
    df = pd.read_html(StringIO(htmlstring), encoding="utf-8")[0]
    df = _improve_dataframe(df)
    return df
