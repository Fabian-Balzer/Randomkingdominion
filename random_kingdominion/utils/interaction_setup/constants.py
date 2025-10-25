import numpy as np

from ...constants import ALL_CSOS
from ...cso_frame_utils import listlike_contains

# First, define specific card types
CAN_PLAY_CARD_ON_GAIN = "Innovation, City-State, Rush, Spell Scroll, Gondola".split(
    ", "
)
GAINS_TO_HAND = "Artisan, Cobbler, Sculptor, Falconer, Wish, Transmogrify, Swap, Kind Emperor, Hill Fort, Silver Mine".split(
    ", "
)
WILL_TOPDECK_ON_GAIN = (
    "Armory, Crafter's Guild, Develop, Demand, Graverobber, Invasion".split(", ")
)  # Technically, also Greed
CAN_TOPDECK_ON_GAIN = "Tracker, Royal Seal, Tiara, Insignia, Travelling Fair, Watchtower, Sleigh, Way of the Seal, Bauble, Trapper's Lodge".split(
    ", "
)
MUST_TOPDECK_ON_GAIN = "Progress".split(", ")
GAINS_TO_SET_ASIDE = "Blockade, Quartermaster, Summon, Rapid Expansion, Hasty".split(
    ", "
)

GAINS_SELF_TO_HAND_CARDS = "Villa, Guardian, Ghost Town, Night Watchman, Den of Sin".split(
    ", "
)  # Technically, also Plague. Also, Villa is different from the others due to its wording - when topdecked via the gainer, you can still put it in hand, while the others stay topdecked.

CAN_CAUSE_SHUFFLE_TRIGGER_ON_GAIN = (
    "Hill Fort, Band of Nomads, Footpad, Sheepdog, Trail".split(", ")
)
AFFECTED_BY_END_BUY = (
    "Wine Merchant, Pageant, Merchant Guild, Treasury, Hermit, Exploration".split(", ")
)
BACK_TO_ACTION_CSOS = "Villa, Cavalry, Launch, Continue".split(", ")
GATHERING_CARDS = "Farmers' Market, Temple, Wild Hunt".split(", ")
TRAVELLER_BASE_CARDS = "Peasant, Page".split(", ")

CAN_PLAY_TREASURES_IN_ACTION_PHASE = "Black Market, Storyteller, Courier, Specialist, Fortune Hunter, Herb Gatherer, Farmhands, Spell Scroll, Mining Road, Coronet".split(
    ", "
)
# START OF TURN STUFF
PLAYS_ON_START_OF_TURN = "Mastermind, Piazza, Summon, Ghost, Prepare, Delay".split(", ")
RESERVES_CALLED_ON_START = "Transmogrify, Ratcatcher, Teacher, Guide".split(", ")
CARDS_TRIGGERING_ON_START = "Hireling, Samurai, Prince, Fool, Quartermaster".split(", ")
CARD_IMPOSTORS = "Overlord, Band of Misfits, Captain, Inheritance".split(
    ", "
)  # Technically, also Riverboat and WotMouse somewhat

ACTION_TREASURES = "Crown, Spell Scroll, Coronet".split(", ")
PLAYABLE_REACTION = "Guard Dog, Sheepdog, Pirate, Trail, Weaver, Caravan Guard, Black Cat, Village Green, Falconer, Stowaway, Mapmaker".split(
    ", "
)
_ways = ALL_CSOS[ALL_CSOS["IsWay"]]
stuff_to_provide = (
    _ways["Text"]
    .apply(
        lambda x: [
            stuff for stuff in ["+$", "Action", "Buy"] if stuff in x or "Set aside" in x
        ]
    )
    .to_dict()
)
WAY_DICT: dict[str, list[str]] = {
    _ways.loc[k]["Name"]: v for k, v in stuff_to_provide.items()
}
ALL_TRAITS = ALL_CSOS[ALL_CSOS["IsTrait"]]["Name"].tolist()

ALL_LOOTS = ALL_CSOS[listlike_contains(ALL_CSOS["Types"], "Loot")]["Name"].tolist()
ALL_LOOT_GIVERS = ALL_CSOS[
    listlike_contains(ALL_CSOS["gain_types"], "Loot")
].index.tolist()

KNIGHTS = ALL_CSOS[listlike_contains(ALL_CSOS["Types"], "Knight")]["Name"].tolist()
RUINS = ALL_CSOS[listlike_contains(ALL_CSOS["Types"], "Ruins")]["Name"].tolist()

not_actual_throne = [
    "cemetery",
    "exorcist",
    "peasant",
]  # Things with Village Quality classified as throne room due to other effects
_throne_mask = listlike_contains(ALL_CSOS["village_types"], "Throne") & ~np.isin(
    ALL_CSOS.index, not_actual_throne
)

ALL_THRONES = ALL_CSOS[_throne_mask]["Name"].tolist()

ALL_THRONE_CARDS = ALL_CSOS[
    ALL_CSOS["Types"].apply(
        lambda x: any(stuff in x for stuff in {"Action", "Treasure", "Night"})
    )
    & _throne_mask
]["Name"].tolist()

TOKEN_EVENTS = {
    "Seaway": "+ Buy",
    "Pathfinding": "+ Card",
    "Training": "+ $1",
    "Lost Arts": "+ Action",
    "Ferry": "-$2",
    "Plan": "trashing",
}


TGG_BUG_DISCLAIMER = (
    " [This used to be bugged in the TGG client, let us know if it's resolved!]"
)
