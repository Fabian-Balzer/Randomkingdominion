from typing import Literal

OracleSelectionType = Literal[
    "TGG Dailies",
    "TGG Campaigns",
    "Recommended",
    "Reddit's KOTW",
    "Fabi's Recommendations",
]

ALL_SELECTION_TYPES = [
    "Recommended",
    "TGG Dailies",
    "TGG Campaigns",
    "Reddit's KOTW",
    "Fabi's Recommendations",
]


def get_selection_description(selected_stuff: OracleSelectionType) -> str:
    if selected_stuff == "Recommended":
        return "The kingdoms recommended by DXV himself, found in the rulebooks of the Dominion expansions, and mixing two expansions at max. Shoutout to Kieran Millar's [Extra Recommended Kingdoms page](https://kieranmillar.github.io/extra-recommended-sets/) where these these kingdoms are conveniently provided."
    elif selected_stuff == "TGG Dailies":
        return "The TGG Dailies are kingdoms provided each day in the Temple Gates Games (TGG) (Steam/mobile) client, where you compete against the Hard AI.\\\nShoutout to the amazing people on the TGG discord who helped me collect these initially (most notably ``probably-lost``, ``igorbone`` and ``Diesel Pioneer``).\\\nThese will only contain the kingdoms up to the point when I've last updated this website."
    elif selected_stuff == "TGG Campaigns":
        return "The kingdoms from the curated campaigns of the Dominion expansions available on the Temple Gates Games (Steam/mobile) client. These each consist of a series of 10 kingdoms that can have surprising effects that aren't available elsewhere - have fun exploring them!"
    elif selected_stuff == "Fabi's Recommendations":
        return "My personal recommendations of kingdoms I randomly stumbled upon, played in the TGG client against the Hard AI, and deemed to be interesting.\\\nHave fun with those!\\\nThey usually contain a large amount of expansions, so they might be more suitable for online play than in-person setup, but go for whatever you prefer!"
    elif selected_stuff == "Reddit's KOTW":
        return "The Kingdom of the Week (KOTW) is a weekly event on the Dominion subreddit, where a curated kingdom is covered. These usually offer especially interesting interactions.\\\nCheck out the [Dominion subreddit](https://www.reddit.com/r/dominion/) for more information; the selection available here might not be fully up to date."
    else:
        raise ValueError(f"Unknown selection type: {selected_stuff}")
