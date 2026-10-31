# Random KingDominion - yet another Dominion randomizer

Generate and explore Dominion kingdoms, inspect engine qualities, browse card data, and look up card interactions and combos.

## Features

- **Kingdom randomizer:** Choose expansions and mechanics, ban or force Card-Shaped Objects (CSOs), set like/dislike weights, and specify desired or excluded kingdom qualities to randomize kingdoms to your liking.
- **Kingdom oracle:** Enter a kingdom to view its engine qualities and the extra components needed to set it up, or browse the recommended kingdoms, the TGG Dailies, and more.
- **CSO database:** Browse and filter Dominion cards and landscapes by text, expansion, type, cost, quality, and other properties.
- **Interactions and combos:** Explore pairwise rules interactions and synergies, filtered by expansion or by entering a comma-separated list of CSO names.

The app includes local CSO data under `card_info/` and card images under `static/card_pictures/`.

## Run locally

The project requires Python 3.11 or newer. From the repository root, create and activate a virtual environment, install the app dependencies, and launch the Streamlit app:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run RandomKingdominion.py
```

On macOS or Linux, activate the environment with:

```sh
source .venv/bin/activate
```

The Streamlit entry point is `RandomKingdominion.py`; run it with Streamlit rather than `python RandomKingdominion.py`. The root `requirements.txt` lists the app's Python dependencies.

## Development

Dependencies are declared twice on purpose: `requirements.txt` pins the exact versions the deployed app installs and the tests pass with, while `pyproject.toml` describes the package with loose lower bounds. A test keeps both lists in sync. Optional extras: `pip install -e .[scripts]` for the data maintenance scripts, `.[test]` for pytest. The test suite needs both (`pip install -e .[scripts,test]`).

Running the tests:

```sh
python -m pytest randomizer_modules_tests                 # everything (~1.5 min)
python -m pytest randomizer_modules_tests -m "not slow"   # without the Streamlit page tests (~25 s)
```

Pitfalls for writing page tests with Streamlit's `AppTest` are listed in the docstring of `randomizer_modules_tests/conftest.py`.

Upgrading Streamlit (or another pinned package): bump the pin in `requirements.txt` (and the floor in `pyproject.toml` if new APIs are used), run the full test suite, then click through the pages once in a browser.

## Updating the card data

The files in `card_info/` are built by `scripts/set_up_database.py`; never edit the `good_*.csv` files by hand. The test suite fails if one of them is out of date.

New cards come from the wiki's [List of cards](https://wiki.dominionstrategy.com/index.php/List_of_cards), which has to be saved by hand (the wiki is protected by a bot check):

1. Open the page in a browser and save it ("Save page as", HTML only).
2. `python scripts/set_up_database.py --wiki_html <saved page>.html -o` parses its card table into `card_info/raw_card_data.csv` and lists the card images that are missing in `static/card_pictures/`; add those by hand.
3. Add the new cards' qualities and types in `card_info/specifics/*.json`, then rebuild the card table with `python scripts/set_up_database.py -m -o`.

Interactions (`-i`, from `random_kingdominion/utils/interaction_setup/specifics/`) and combos (`-c`, from `card_info/raw_combo_data.csv`) are rebuilt the same way.

## License

The code is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE.txt) (AGPL-3.0-or-later). In short: you may use, modify and share it, but modified versions, including ones only run as a hosted web app, have to be published under the same license, with their source code available to their users. Versions up to 1.5.2 were released under the Apache License 2.0.

Additional terms under section 7(b) of the GNU AGPL apply to all code in this repository: modified versions must retain the notice "Based on Random KingDominion by Fabian Balzer (https://github.com/Fabian-Balzer/Randomkingdominion)" in the user interface, e.g. on an About page.

## Affiliations and data sources

Dominion is a game by Donald X. Vaccarino and published by Rio Grande Games. This project is fan-made and is not affiliated with either party. Card names, card text and card art are © Rio Grande Games / Donald X. Vaccarino.

Card images are from the [Dominion Strategy Wiki](https://wiki.dominionstrategy.com) and are available under the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported license](https://creativecommons.org/licenses/by-nc-sa/3.0/) (CC BY-NC-SA 3.0).

Card data (names, expansions, types, costs and card text) is based on the [List of cards](https://wiki.dominionstrategy.com/index.php/List_of_cards) of the Dominion Strategy Wiki by its contributors, used under CC BY-NC-SA 3.0. It was reformatted and extended with this project's own qualities and types; the resulting card table (`card_info/good_card_data.csv`) is shared under the same license.
