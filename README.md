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

## Web card scraper

`wiki_card_scraper.py` is a (probably at this point outdated, hasn't been tested in a while) separate helper that retrieves card and Ally information from the Dominion Strategy Wiki and prints formatted table entries. Review its output and update the local data manually as needed; it does not automatically update the app's data or images.

## Affiliations

Dominion is a game by Donald X. Vaccarino and published by Rio Grande Games. This project is fan-made and is not affiliated with either party. Card images are from the Dominion Strategy Wiki and are available under the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported license](https://creativecommons.org/licenses/by-nc-sa/3.0/).
