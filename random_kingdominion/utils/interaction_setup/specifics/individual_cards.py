"""Interactions that occur with individual card"""

import pandas as pd

from ..constants import (
    ACTION_TREASURES,
    ALL_THRONES,
    CAN_PLAY_TREASURES_IN_ACTION_PHASE,
    CARD_IMPOSTORS,
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
        "If you play an Experiment that was bought from the Black Market deck, you get +2 Cards and +1 Action, but it does not return to a pile. This is because Experiment does not have a pile to return to.",
        df,
    )
    add_interaction(
        "black_market",
        "way_of_the_horse",
        "If you play a card from the Black Market deck using Way of the Horse, you get +2 Cards and +1 Action, but it does not return to a pile. This is because cards from the Black Market deck do not have a pile to return to.",
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


def _add_garrison_interaction(other: str, df: pd.DataFrame):
    token_target = other if other != "Inheritance" else "Estate"
    rule = f"If you play a Garrison using {other}, you can't put tokens on Garrison because it's not in play, and you don't put tokens on {token_target} either. This means it won't draw any cards next turn and will be discarded this turn."
    add_interaction("Garrison", other, rule, df)


def _add_all_garrison_interactions(df: pd.DataFrame):
    for impostor in CARD_IMPOSTORS:
        if impostor == "Captain":
            continue
        _add_garrison_interaction(impostor, df)


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
        "Even if an Action-Liaison (that normally doesn't give +$) you play after a Harbor Village yields +$1 through League of Shopkeepers, you don't get +$1 from Harbor village.",
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
        "When you play Leprechaun as your seventh card in play, you might get a nasty surprise if you react any Sheepdogs for the Gold gain. On the other hand, reacting Sheepdogs might help you reach the seventh card in play necessary for the wish gain.",
        df,
    )
    add_interaction(
        "Mining Road",
        "Leprechaun",
        "When you play Leprechaun after having played Mining Road, you can choose to play the gained Gold before the seven-card condition is checked. This can be used to your advantage, or come as a nasty surprise.",
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


def _add_all_necromancer_interactions(df: pd.DataFrame):
    necro_turn = "Necromancer/Lurker|Lich|Graverobber|Rogue---If you use a Necromancer to play a card from the trash (turning it face down), then gain it with {card_b}, then trash it again, you may play it again with a subsequent Necromancer as it will be turned face up again."
    add_multiple_interactions_from_single(necro_turn, df)


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
        "If you reveal the cards in your discard pile since you don't have any Coppers, you will get +1 Coffers for each Patron in there as long as it's during an Action phase.",
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


def _add_all_procession_interactions(df: pd.DataFrame):
    # PROCESSION [see also Experiment]
    add_interaction(
        "Horse",
        "Procession",
        "When you play a Horse with Procession, you return it to its pile after its first play, so it doesn't get trashed. Nevertheless, you gain a card costing $1 more than it.",
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


def _add_urchin_throne_inter(throne: str, df: pd.DataFrame):
    rule = f"If you play an Urchin multiple times using {throne}, you may not trash this Urchin, since you need to play *another* attack card to be able to trash it."
    add_interaction(throne, "Urchin", rule, df)


def _add_all_urchin_interactions(df: pd.DataFrame):
    for other in ALL_THRONES:
        _add_urchin_throne_inter(other, df)


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
    _add_all_encampment_interactions(df)
    _add_all_enchantress_interactions(df)
    _add_all_experiment_interactions(df)
    _add_all_garrison_interactions(df)
    _add_all_harbor_village_interactions(df)
    _add_all_highwayman_interactions(df)
    _add_all_leprechaun_interactions(df)
    _add_all_mandarin_interactions(df)
    _add_all_market_square_interactions(df)
    _add_all_necromancer_interactions(df)
    _add_all_patron_interactions(df)
    _add_all_prince_interactions(df)
    _add_all_procession_interactions(df)
    _add_all_soothsayer_interactions(df)
    if verbose:
        print(f"Added {len(df) - num_before} individual card interactions.")
