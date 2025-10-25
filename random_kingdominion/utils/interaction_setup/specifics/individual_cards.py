"""Interactions that occur with individual card"""

import pandas as pd

from random_kingdominion.constants import ALL_CSOS, ROTATOR_DICT, SPLITPILE_DICT

from ..constants import (
    ACTION_TREASURES,
    ALL_THRONE_CARDS,
    ALL_THRONES,
    CAN_PLAY_TREASURES_IN_ACTION_PHASE,
    GATHERING_CARDS,
    TRAVELLER_BASE_CARDS,
)
from ..interaction_util import add_interaction, add_multiple_interactions_from_single


### Certain Black Market interactions that have to do with pile absence
def _add_gathering_black_market_interaction(other: str, df: pd.DataFrame):
    rule = f"When you get {other} from the Black Market deck, since there is no pile to gather VP tokens on, the gathering will have no effect."
    add_interaction("Black Market", other, rule, df)


def _add_traveller_black_market_interaction(other: str, df: pd.DataFrame):
    rule = f"When you get {other} from the Black Market deck, you cannot exchange it for other Travellers."
    add_interaction("Black Market", other, rule, df)


def _add_all_black_market_interactions(df: pd.DataFrame):
    for gathering_cso in GATHERING_CARDS:
        _add_gathering_black_market_interaction(gathering_cso, df)

    for traveller_base_cso in TRAVELLER_BASE_CARDS:
        _add_traveller_black_market_interaction(traveller_base_cso, df)
    # Specific Black Market interactions
    add_interaction(
        "black_market",
        "encampment",
        "When you play an Encampment that came from the Black Market deck, if you don't reveal a Gold or Plunder, then you set aside the Encampment but since it has no pile to return to, it stays set aside for the rest of the game (it still counts as one of your cards for scoring).",
        df,
    )
    add_interaction(
        "black_market",
        "experiment",
        "If you play an Experiment that was bought from the Black Market deck, you get +2 Cards and +1 Action, but it does not return to a pile and stays in play/in your deck instead. This is because Experiment does not have a pile to return to.",
        df,
    )
    add_interaction(
        "black_market",
        "way_of_the_horse",
        "If you play a card from the Black Market deck using Way of the Horse, you get +2 Cards and +1 Action, but it does not return to a pile. This is because cards from the Black Market deck do not have a pile to return to.",
        df,
    )
    add_interaction(
        "black_market",
        "mission",
        "You cannot buy cards from the Black Market during Mission turns.",
        df,
    )
    add_interaction(
        "black_market",
        "enlightenment",
        "When Enlightenment is active, playing Treasures using it will provide +1 Card, +1 Action instead of the normal effect (but not use up an Action to play them).",
        df,
    )
    add_interaction(
        "black_market",
        "Capitalism",
        "If you have bought Capitalism, you can play a Black Market while playing Treasures for another Black Market. You resolve them recursively, i.e. the three cards of the first Black Market stay out until you have decided to buy (or decline) one of the cards of the second Black Market, and only after that you can buy cards from the first Black Market.",
        df,
    )


##########################################################################################################
### Crown interactions
def _add_crown_interaction(other: str, df: pd.DataFrame, multiple=False):
    if multiple:
        rule = f"If {other}'s ability lets you play Treasures in your Action phase, and one of those Treasures is Crown, then because it is your Action phase, Crown lets you play an Action card (and not a Treasure) from your hand twice."
    else:
        rule = f"If {other}'s ability lets you play a Treasure in your Action phase, and this Treasure is a Crown, then because it is your Action phase, Crown lets you play an Action card (and not a Treasure) from your hand twice."
    add_interaction("Crown", other, rule, df)


def _add_all_crown_interactions(df: pd.DataFrame):
    for on_play_cso in CAN_PLAY_TREASURES_IN_ACTION_PHASE:
        multiple = on_play_cso in ["Black Market", "Storyteller"]
        _add_crown_interaction(on_play_cso, df, multiple=multiple)


def _add_all_changeling_interactions(df: pd.DataFrame):
    # CHANGELING
    add_interaction(
        "Sculptor",
        "Changeling",
        "If you play Sculptor to gain a Treasure and exchange it for a Changeling, will still get the Villager (but the Changeling will be gained to your discard pile).",
        df,
    )
    add_interaction(
        "Silk Merchant",
        "Changeling",
        "If you gain Silk Merchant and exchange it for a Changeling, will still get the Coffers and Villager (but the Changeling will be gained to your discard pile).",
        df,
    )
    add_interaction(
        "Changeling",
        "Infirmary",
        "If you overpay for an Infirmary and exchange it for a Changeling, you cannot play it and vice versa.",
        df,
    )


def _add_all_clerk_interactions(df: pd.DataFrame):
    # CLERK
    # See also Desert Guides, Cave Dwellers
    add_interaction(
        "Guide",
        "Clerk",
        "You may arbitrarily order reacting Clerks and calling Guides at the start of your turn; you could e.g. react a Clerk, call Guide, react another two Clerks that you've just drawn, and call another Guide.",
        df,
    )


def _add_all_charlatan_interactions(df: pd.DataFrame):
    add_interaction(
        "Charlatan",
        "Bandit",
        "If a Bandit reveals a Curse with Charlatan in the kingdom, the Curse (or another non-Copper Treasure) is trashed.",
        df,
    )


def _add_all_elder_interactions(df: pd.DataFrame):
    # Omitting Elder/Steward|Minion|Nobles|Native Village|Spice Merchant|Squire|Treasurer|Innkeeper|Town|Specialist|Hill Fort|Stronghold.
    # Also omitting any of the Choice-treasures as they are only relevant with Enlightenment.
    add_interaction(
        "Elder",
        "Catacombs",
        "If you play a Catacombs using Elder, you put the looked-at cards into your hand, but then have to immediately discard them (from your hand), and then draw three different cards.",
        df,
    )
    add_interaction(
        "Elder",
        "Lurker",
        "If you play a Lurker using Elder, you first trash an Action card and then gain one from the trash.",
        df,
    )
    add_interaction(
        "Elder",
        "Courtier",
        "If you play a Courtier using Elder, you get to pick up to one more option than you usually would have because of the types of the revealed card (but no single option twice).",
        df,
    )
    add_interaction(
        "Elder",
        "Pawn",
        "If you play a Pawn using Elder, you get to pick up to three of the options (but no single option twice).",
        df,
    )
    add_interaction(
        "Elder",
        "Pirate Ship",
        "If you play a Pirate Ship using Elder, you first get +$, and then possibly trash other players' treasures.",
        df,
    )
    add_interaction(
        "Elder",
        "Courser",
        "If you play a Courser using Elder, you get to pick three of the options.",
        df,
    )
    add_interaction(
        "Elder",
        "Trusty Steed",
        "If you play a Trusty Steed using Elder, you get to pick three of the options.",
        df,
    )
    add_interaction(
        "Elder",
        "Count",
        "If you play a Count using Elder, for each of the choices you get to pick up to two (but can decide e.g. for only one of the Topdeck/Discard/Gain Copper, and two of the +$3/Trash Hand/Gain Duchy choices).",
        df,
    )
    add_interaction(
        "Elder",
        "Graverobber",
        "If you play a Graverobber using Elder, you first try to gain a card costing $3-$6 from the trash (failing if there is no such card), and then trash an Action from your hand.",
        df,
    )
    add_interaction(
        "Elder",
        "Amulet",
        "If you play an Amulet using Elder, you get to pick two of the options this turn, but only one option on the next turn.",
        df,
    )
    add_interaction(
        "Elder",
        "Miser",
        "If you play a Miser using Elder, you can first put a Copper on your Tavern Mat, and then immediately profit off of it.",
        df,
    )
    add_interaction(
        "Elder",
        "Wild Hunt",
        "If you play a Wild Hunt using Elder, you can first draw and put a token on the pile, and then immediately gain an Estate to take the VP from the pile.",
        df,
    )
    add_interaction(
        "Elder",
        "Necromancer",
        "You don't get to choose more than one card from the trash when playing Necromancer using Elder. Neither do you get an additional option when playing a Choice card from the trash with a Necromancer played in such a way.",
        df,
    )
    add_interaction(
        "Elder",
        "Scrap",
        "If you play a Scrap using Elder, you get to pick up to one additional option (but not a single option twice).",
        df,
    )
    add_interaction(
        "Elder",
        "Broker",
        "If you play a Broker using Elder, you only trash one card and then get to pick up two options (but not a single option twice) corresponding to the $ of the trashed card.",
        df,
    )
    add_interaction(
        "Elder",
        "Blacksmith",
        "If you play a Blacksmith using Elder, the options you choose are resolved in the order they are on the card; if you e.g. choose to draw to 6 cards in hand and get +1 Card, +1 Action, you'll do the latter after the former, ending up with 7 cards in hand.",
        df,
    )
    add_interaction(
        "Elder",
        "Town Crier",
        "If you play a Town Crier using Elder, the options you choose are resolved in the order they are on the card; if you e.g. choose to gain a Silver and get +1 Card, +1 Action, you'll be able to draw the Silver you just gained.",
        df,
    )
    add_interaction(
        "Elder",
        "Modify",
        "If you play a Modify using Elder, you first have to decide whether you want to pick both choices (i.e. after having drawn a card, you cannot reconsider whether you want to gain a card costing up to $2 more than the trashed one).",
        df,
    )
    add_interaction(
        "Elder",
        "Cabin Boy",
        "If you play a Cabin Boy using Elder, due to the 'this turn' wording, it does not have an effect on the next turn, so you don't get to both receive +$2 and trash the Cabin Boy for a Duration card.",
        df,
    )
    add_interaction(
        "Elder",
        "Quartermaster",
        "If you play a Quartermaster using Elder, due to the 'this turn' wording, it does not have an effect on the next turns, so you only get to either tuck away a card, or take one from Quartermaster.",
        df,
    )
    add_interaction(
        "Elder",
        "Kitsune",
        "If you play a Kitsune using Elder, you get to pick up to three of the options (but no single option twice).",
        df,
    )


def _add_all_encampment_interactions(df: pd.DataFrame):
    # ENCAMPMENT [see also Prince, Black Market]
    add_interaction(
        "Royal Galley",
        "Encampment",
        "If you play an Encampment with Royal Galley (RG) and you fail to reveal a Gold or Plunder, you set it aside and return it to its pile at the end of the turn; the RG gets discarded during Clean-up as it doesn't have anything left to do.",
        df,
    )


def _add_all_enchantress_interactions(df: pd.DataFrame):
    act_treas_str = (
        "|".join(ACTION_TREASURES)
        + "/Enchantress---If Enchantress affects {card_a} played in a Buy phase, its player gets +1 Card +1 Action, but has no way to use the +1 Action, since it is their Buy phase (but it might matter e.g. if the player buys Villa)."
    )
    add_multiple_interactions_from_single(act_treas_str, df)


def _add_all_experiment_interactions(df: pd.DataFrame):
    # EXPERIMENT [see also Prince, Black Market]
    add_interaction(
        "Experiment",
        "Procession",
        "When you play an Experiment with Procession, you return it to its pile after its first play, so it doesn't get trashed. Nevertheless, you gain a card costing $1 more than it.",
        df,
    )


def _add_all_grand_market_interactions(df: pd.DataFrame):
    add_interaction(
        "Grand Market",
        "Mint",
        "Coppers that were in play earlier in the turn but are removed are not a restriction for buying Grand Market; if you have 11 Coppers in play and 2 Buys, you could buy a Mint, trash all of your played Treasures, and then buy a Grand Market.",
        df,
    )
    add_interaction(
        "Grand Market",
        "Counterfeit",
        "Coppers that you play and trash using Counterfeit are not a restriction for buying Grand Market.",
        df,
    )
    add_interaction(
        "Grand Market",
        "Bonfire",
        "Coppers that were in play earlier in the turn but are removed are not a restriction for buying Grand Market; if you have $9 with two Coppers in play and 2 Buys, you could buy Bonfire, trash the two Coppers, and then buy a Grand Market.",
        df,
    )


def _add_all_harbor_village_interactions(df: pd.DataFrame):
    # HARBOR VILLAGE [See also the Ways section]
    add_interaction(
        "Harbor Village",
        "Approaching Army",
        "Even if Approaching Army is active, Harbor Village does not give you +$1 when you play an Attack (that doesn't give +$) after it, since it's Approaching Army providing the +$1, not the Attack card itself.",
        df,
    )
    add_interaction(
        "Harbor Village",
        "League of Shopkeepers",
        "Even if an Action-Liaison (that normally doesn't give +$) you play after a Harbor Village yields +$1 through League of Shopkeepers, you don't get +$1 from Harbor Village.",
        df,
    )
    add_interaction(
        "Harbor Village",
        "Merchant",
        "If you play a Merchant after Harbor Village, you do not retroactively get +$1 from Harbor Village if you later play a Silver for the first time (barring some edge cases that involve immediately letting Merchant give +$ like e.g. Inspiring Merchant playing Black Market playing Silver).",
        df,
    )

    hv_coin_tokens = "Harbor Village/Training|Teacher---If you have put the +Coin token on a card (that normally doesn't give +$) and play it after a Harbor Village, you don't get +$1 from Harbor Village."
    hv_minus_coin = "Harbor Village/Bridge Troll|Ball---If you play a card giving only +$1 and use that to remove the -Coin token after playing Harbor Village, you don't get +$1 from Harbor Village as the card didn't produce any $."
    add_multiple_interactions_from_single(hv_coin_tokens, df)
    add_multiple_interactions_from_single(hv_minus_coin, df)


def _add_all_highwayman_interactions(df: pd.DataFrame):
    # More Highwayman interactions in the on-clean-up section with Reckless and in the traits section with Inspiring
    add_interaction(
        "Coin of the Realm",
        "Highwayman",
        "Calling Coin of the Realm from your Tavern mat will work and provide +2 Actions even if you are affected by the Highwayman attack because you don't *play* it there.",
        df,
    )


def _add_all_leprechaun_interactions(df: pd.DataFrame):
    add_interaction(
        "Sheepdog",
        "Leprechaun",
        "When you play Leprechaun as your seventh card in play, if you react any Sheepdogs for the Gold gain, you will receive a Hex as the seven-card condition is checked afterwards. On the other hand, reacting Sheepdogs to the Gold gain might help you reach the seventh card in play necessary for the Wish gain.",
        df,
    )
    add_interaction(
        "Mining Road",
        "Leprechaun",
        "When you play Leprechaun after having played Mining Road, you can choose to play the gained Gold before the seven-card condition is checked. This can be used to your advantage to be the necessary card to fulfil the condition, or become the eighth card, in which case you receive a Hex instead.",
        df,
    )


def _add_all_mandarin_interactions(df: pd.DataFrame):
    TREASURE_DURATION = "Astrolabe, Contract, Cage, Abundance, Gondola, Rope, Buried Treasure, Amphora, Endless Chalice, Figurehead, Jewels".split(
        ", "
    )
    td = "|".join(TREASURE_DURATION)
    manda_str = (
        td
        + "/Mandarin---If you gain a Mandarin and have played {card_a} before that, you put it on top of your deck, but the duration effect still persists."
    )
    add_multiple_interactions_from_single(manda_str, df)


def _add_all_market_square_interactions(df: pd.DataFrame):
    add_interaction(
        "Market Square",
        "Gladiator",
        "If a Gladiator is trashed from the supply, since it is none of your cards, you cannot react Market Square to gain a Gold.",
        df,
    )
    add_interaction(
        "Market Square",
        "Lurker",
        "If Lurker trashes a card from the supply, since it is none of your cards, you cannot react Market Square to gain a Gold.",
        df,
    )
    draws_on_trash_str = "Rats|Trail|Cultist|Overgrown Estate/Market Square---When trashing a {card_a} with Market Square in hand, you get to decide which effect to resolve first, and can even react a Market Square you have just drawn from the on-trash draw ability of {card_a}."
    add_multiple_interactions_from_single(draws_on_trash_str, df)


def _add_all_monkey_interactions(df: pd.DataFrame):
    pass  # Moved to on-gain skirmisher stuff


def _add_all_necromancer_interactions(df: pd.DataFrame):
    necro_turn = "Necromancer/Lurker|Lich|Graverobber|Rogue---If you use a Necromancer to play a card from the trash (turning it face down), then gain it with {card_b}, then trash it again, you may play it again with a subsequent Necromancer as it will be turned face up again."
    add_multiple_interactions_from_single(necro_turn, df)
    add_interaction(
        "Hermit",
        "Necromancer",
        "If you play a Hermit from the trash using Necromancer, you cannot exchange the Hermit for a Madman, it will stay in the trash even if you don't gain any cards during your Buy phase.",
        df,
    )


def _add_all_outpost_interactions(df: pd.DataFrame):
    for throne in ALL_THRONE_CARDS:
        if throne == "Procession":
            continue
        rule = f"If you play an Outpost using {throne}, you will still only take one extra turn, but the {throne} will stay out with it anyways."
        add_interaction("Outpost", throne, rule, df)
    rule = "if you play Outpost and Voyage, then in Clean-up you don't discard either of them and only draw 3 cards. In between turns, you choose to take the Voyage turn next. (Outpost hasn't failed yet because another player might somehow be able to take an extra turn first.) In Clean-up of the Voyage turn, you discard Voyage but not Outpost and draw 5 cards. In between turns again, Outpost now fails - it is up next but would be your 3rd turn in a row. The next player takes their turn and during their Clean-up, you discard Outpost."
    add_interaction("Outpost", "Voyage", rule, df)


def _add_all_prince_interactions(df: pd.DataFrame):
    # PRINCE [see also WotHorse, WotButterfly]
    add_interaction(
        "Prince",
        "Raze",
        "If you Prince a Raze and choose the option to trash itself, you fail to do so and don't get to look at any other cards, and the Raze stays set aside.",
        df,
    )
    add_interaction(
        "Prince",
        "Mining Village",
        "If you Prince a Mining Village and choose the option to trash itself, you fail to do so and don't get +$2, and the Mining Village stays set aside.",
        df,
    )
    add_interaction(
        "Prince",
        "Encampment",
        "If you set aside an Encampment with Prince, it will fail to set itself aside when you play it and don't reveal Gold or Plunder, so Prince replays it at the start of each turn successfully.",
        df,
    )
    add_interaction(
        "Prince",
        "Throne Room",
        "If you set aside a Throne Room with Prince, if you play another Duration card (such as Prince) with it at the start of on of your turns, the Duration card will be played twice, and you'll still get to play a card twice from the original Throne Room at the start of each of your future turns.",
        df,
    )


def _add_patron_buy_phase_interaction(other: str, when: str, df: pd.DataFrame):
    rule = f"If you {when} {other} during your Buy phase and reveal a Patron this way, you will not get +1 Coffers since it's not an Action phase."
    add_interaction("Patron", other, rule, df)


def _add_all_patron_interactions(df: pd.DataFrame):
    buy_phase_revealers = {
        "Loan": "play",
        "Investment": "play",
        "Venture": "play",
        "Gamble": "buy",
        "Pursue": "buy",
        "Foray": "buy",
    }
    for other, when in buy_phase_revealers.items():
        _add_patron_buy_phase_interaction(other, when, df)

    add_interaction(
        "Patron",
        "Inn",
        "If you gain an Inn during your Buy phase and reveal a Patron from your discard, you will not get +1 Coffers since it's not an Action phase.",
        df,
    )
    add_interaction(
        "Patron",
        "Grand Castle",
        "If you gain a Grand Castle during your Buy phase and reveal a Patron from your hand, you will not get +1 Coffers since it's not an Action phase.",
        df,
    )
    add_interaction(
        "Patron",
        "Raider",
        "If you reveal your hand due to an opponent's Raider being played, and you reveal a Patron, you will not get +1 Coffers since that happens during a Night (and not Action) phase.",
        df,
    )
    add_interaction(
        "Patron",
        "Ghost",
        "If you reveal a Patron by playing Ghost, you will not get +1 Coffers since that happens during a Night (and not Action) phase.",
        df,
    )
    add_interaction(
        "Patron",
        "Bad Omens",
        "If you reveal the cards in your discard pile when you don't have any Coppers, you will get +1 Coffers for each Patron in there as long as it's during an Action phase.",
        df,
    )
    add_interaction(
        "Patron",
        "Famine",
        "If you reveal a Patron among the three cards, you will get +1 Coffers as long as it's during an Action phase.",
        df,
    )
    add_interaction(
        "Patron",
        "War",
        "If you reveal a Patron due to War, you will get +1 Coffers as long as it's during an Action phase.",
        df,
    )
    add_interaction(
        "Patron",
        "Fated",
        "If Patron is Fated, you will get +1 Coffers from each Patron as long as you shuffle during an Action phase, and put them onto the top or bottom of your deck.",
        df,
    )


def _add_all_peasant_interactions(df: pd.DataFrame):
    rule = f"You can never put any token on the Castles pile (even with Small or Opulent Castle on top) using Teacher because they are only a Victory Supply pile, not an Action supply pile."
    add_interaction("Castles", "Peasant", rule, df)
    splitpiles = (
        list(SPLITPILE_DICT.keys()) + list(ROTATOR_DICT.keys()) + ["Ruins", "Knights"]
    )
    for pile in splitpiles:
        rule = f"You may put any token on the {pile} pile using Teacher. This will affect all of its cards."
        add_interaction(pile, "Peasant", rule, df)
    rule = f"Once Divine Wind is triggered, any token is removed from its pile upon the pile's removal."
    add_interaction("Peasant", "Divine Wind", rule, df)
    rule = f"Even after buying Inheritance, you may not put any token on the Estate pile using Teacher as it's not natively an Action supply pile."
    add_interaction("Inheritance", "Peasant", rule, df)
    rule = f"Even if Enlightenment is active, you may not put any token on any Treasure pile using Teacher as it's not natively an Action supply pile."
    add_interaction("Enlightenment", "Peasant", rule, df)


def _add_all_procession_interactions(df: pd.DataFrame):
    # PROCESSION [see also Experiment]
    add_interaction(
        "Horse",
        "Procession",
        "When you play a Horse with Procession, you return it to its pile after its first play, so it doesn't get trashed. Nevertheless, you gain a card costing $1 more than it.",
        df,
    )


def _add_all_possession_interactions(df: pd.DataFrame):
    add_interaction(
        "Possession",
        "Credit",
        "When you buy Credit while Possessing an opponent, since they never gain a card from it, the 'it' in 'equal to its cost' is undefined, and they wouldn't be scheduled to gain debt. Therefore, you also don't gain any debt from it.",
        df,
    )
    add_interaction(
        "Possession",
        "Change",
        "When you play Change while Possessing an opponent, trash one of their cards, and gain a card costing more $ than it, since they never gain it, they would never gain debt from that play. Therefore, you also don't gain any debt from it.",
        df,
    )


def _add_all_soothsayer_interactions(df: pd.DataFrame):
    add_interaction(
        "moat",
        "soothsayer",
        "If an opponent plays Soothsayer and you gain a Curse and draw a Moat, it is too late for you to use that Moat to defend against the Soothsayer.",
        df,
    )
    add_interaction(
        "sheepdog",
        "soothsayer",
        "If an opponent plays Soothsayer and you gain a Curse, you may react with Sheepdogs. Once you're done reacting, you draw a card due to Soothsayer, and if that card is a Sheepdog, it is too late for you to react with that one.",
        df,
    )
    add_interaction(
        "caravan guard",
        "soothsayer",
        "If an opponent plays Soothsayer, you may react with Caravan Guard immediately, and then gain a Curse. Once you're done reacting, you draw a card due to Soothsayer, and if that card is a Caravan Guard, it is too late for you to react with that one.",
        df,
    )
    add_interaction(
        "diplomat",
        "soothsayer",
        "If an opponent plays Soothsayer, you may react with Diplomat immediately, and then gain a Curse. Once you're done reacting, you draw a card due to Soothsayer, and if that card is a Diplomat, it is too late for you to react with that one.",
        df,
    )
    add_interaction(
        "soothsayer",
        "watchtower",
        "If an opponent plays Soothsayer and you gain a Curse and draw a Watchtower, it is too late for you to react with that Watchtower to trash the Curse (or put the Curse onto your deck).",
        df,
    )


def _add_single_urchin_throne_inter(throne: str, df: pd.DataFrame):
    rule = f"If you play an Urchin multiple times using {throne}, you may not trash this Urchin, since you need to play *another* attack card to be able to trash it."
    add_interaction(throne, "Urchin", rule, df)


def _add_all_urchin_interactions(df: pd.DataFrame):
    for other in ALL_THRONES:
        _add_single_urchin_throne_inter(other, df)


def _add_all_voyage_interactions(df: pd.DataFrame):
    add_interaction(
        "Voyage",
        "Black Market",
        "Playing Treasures for Black Market during Voyage turn is limited by Voyage's restriction.",
        df,
    )
    add_interaction(
        "Voyage",
        "Trail",
        "Playing Trail via its on-gain/on-trash/on-discard effect does not count as playing it from hand as far as Voyage turns are concerned.",
        df,
    )
    other_discard_play = "Voyage/Weaver|Village Green---Playing {card_b} via its on-discard effect does not count as playing it from hand as far as Voyage turns are concerned."
    add_multiple_interactions_from_single(other_discard_play, df)
    play_from_discard = "Voyage/Courier|Herb Gatherer|Orb---Playing a card from your discard pile using {card_b} does not count as playing it from hand as far as Voyage turns are concerned."
    add_multiple_interactions_from_single(play_from_discard, df)


def _add_all_warlord_interactions(df: pd.DataFrame):
    add_interaction(
        "Warlord",
        "Black Market",
        "Playing Action-Treasures for Black Market is limited by Warlord's attack restriction.",
        df,
    )
    add_interaction(
        "Warlord",
        "Crown",
        "Playing Crown is limited by Warlord's attack restriction, no matter whether you try to play it during your Action or your Buy phase.",
        df,
    )
    add_interaction(
        "Warlord",
        "Trail",
        "Playing Trail via its on-gain/on-trash/on-discard effect does not count as playing it from hand as far as Warlord's attack is concerned.",
        df,
    )
    other_discard_play = "Warlord/Weaver|Village Green---Playing {card_b} via its on-discard effect does not count as playing it from hand as far as Warlord's attack is concerned."
    add_multiple_interactions_from_single(other_discard_play, df)
    play_from_discard = "Warlord/Courier|Herb Gatherer|Orb---Playing an Action card using {card_b} from your discard pile does not count as playing it from hand as far as Warlord's attack is concerned."
    add_multiple_interactions_from_single(play_from_discard, df)


def _add_all_farmland_interactions(df: pd.DataFrame):
    rule = "If you gain a Farmland and exchange it for a Changeling, you will still have to trash a card from your hand and gain one costing exactly $2 more than the trashed card."
    add_interaction("Farmland", "Changeling", rule, df)
    rule = "If you buy a Farmland while under the Haunted Woods attack, you get to choose which effect (topdecking or remodeling) to resolve first."
    add_interaction("Haunted Woods", "Farmland", rule, df)


##########################################################################################################
# Final function
def add_all_individual_card_interactions(df: pd.DataFrame, verbose=False) -> None:
    """Adds all individual card interactions to the DataFrame."""
    num_before = len(df)
    _add_all_black_market_interactions(df)
    _add_all_crown_interactions(df)
    _add_all_changeling_interactions(df)
    _add_all_charlatan_interactions(df)
    _add_all_clerk_interactions(df)
    _add_all_elder_interactions(df)
    _add_all_encampment_interactions(df)
    _add_all_enchantress_interactions(df)
    _add_all_experiment_interactions(df)
    _add_all_farmland_interactions(df)
    _add_all_grand_market_interactions(df)
    _add_all_harbor_village_interactions(df)
    _add_all_highwayman_interactions(df)
    _add_all_leprechaun_interactions(df)
    _add_all_mandarin_interactions(df)
    _add_all_market_square_interactions(df)
    _add_all_monkey_interactions(df)
    _add_all_necromancer_interactions(df)
    _add_all_outpost_interactions(df)
    _add_all_patron_interactions(df)
    _add_all_peasant_interactions(df)
    _add_all_prince_interactions(df)
    _add_all_procession_interactions(df)
    _add_all_possession_interactions(df)
    _add_all_soothsayer_interactions(df)
    _add_all_urchin_interactions(df)
    _add_all_voyage_interactions(df)
    _add_all_warlord_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} individual card interactions.")
