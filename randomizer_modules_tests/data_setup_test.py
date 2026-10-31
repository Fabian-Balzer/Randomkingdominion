"""Tests for reading a saved copy of the wiki's List of cards page."""

import pandas as pd
import pytest

from random_kingdominion.utils.data_setup import add_image_paths, read_wiki_card_list

_SAVED_PAGE = """<html><body>
<table class="wikitable sortable">
<tr><th>Name</th><th>Set</th><th>Cost</th><th>Text</th></tr>
<tr><td>Village200px</td><td>Base</td>
<td><span class="coin-icon"><img alt="$3" src="Coin3.png"></span></td>
<td>+1 Card, +2 Actions</td></tr>
<tr><td>City Quarter</td><td>Empires</td>
<td><span class="debt-icon"><img alt="8D" src="Debt8.png"></span></td>
<td>+2 Actions</td></tr>
</table>
</body></html>"""


def test_saved_card_list_is_parsed(tmp_path):
    html_path = tmp_path / "List_of_cards.html"
    html_path.write_text(_SAVED_PAGE, encoding="utf-8")
    df = read_wiki_card_list(html_path)

    assert df["Name"].tolist() == ["Village", "City Quarter"]
    assert df["Expansion"].tolist() == ["Base", "Empires"]
    # Costs are only in the icons' alt texts
    assert df["Cost"].tolist() == ["$3", "8D"]


def test_page_without_card_table_is_rejected(tmp_path):
    html_path = tmp_path / "bot_check.html"
    html_path.write_text("<html><body>Making sure you're not a bot!</body></html>")
    with pytest.raises(ValueError, match="card table"):
        read_wiki_card_list(html_path)


def test_image_paths_follow_expansion_and_name():
    df = pd.DataFrame({"Name": ["Village", "Fake Card"], "Expansion": ["Base, 2E"] * 2})
    assert add_image_paths(df)["ImagePath"].tolist() == [
        "Base_2E/Village.jpg",
        "Base_2E/Fake_Card.jpg",
    ]
