import numpy as np
import pytest

import random_kingdominion as rk


def _test_dombot_readin_readout(kingdom_string):
    kingdom = rk.Kingdom.from_dombot_csv_string(kingdom_string)
    redone = rk.Kingdom.from_dombot_csv_string(kingdom.get_dombot_csv_string())
    assert kingdom == redone


def test_kingdom_readout_and_printout_compatability():
    """Test whether kingdoms are properly read and written via some example kingdoms."""
    example_1 = "Archive, Druid (The Earth's Gift, The Field's Gift, The Sun's Gift), Inherited (Sanctuary), Investment, Lighthouse, Mining Village, No Colonies, No Shelters, Obelisk (Cargo Ship), Sanctuary, Sentry, Taxman, Villa, Cargo Ship"
    example_2 = "Banish, Cage, Coin of the Realm, Figurine, Governor, Merchant Camp, No Colonies, No Shelters, Prosper, Quartermaster, Secluded Shrine, Sheepdog, Torturer, Young Witch (Improve)"
    example_3 = "Beggar, Border Village, Colonies, Harbinger, Hireling, Knights, Masterpiece, Mountain Pass, No Shelters, Nobles, Stowaway, Tools, Way of the Owl, Wine Merchant"
    example_4 = "Architects' Guild, Camel Train, Cartographer, Druid (The Field's Gift, The Flame's Gift, The Wind's Gift), Emissary, Encampment, Fortress, Gladiator, Hostelry, Mirror, No Colonies, Shelters, Tournament, Villain"
    example_5 = "Black Cat, Conquest, Crucible, Enchantress, Gladiator, Gondola, Longship, Moneylender, No Colonies, No Shelters, Pooka, Treasure Map, Vassal, Way of the Mouse (Menagerie)"
    example_6 = "black_cat, enchantress, gladiator, vassal, crucible, gondola, moneylender, treasure_map, longship, pooka, way_of_the_mouse:menagerie, conquest -m NoColonies, NoShelters"
    # Extra complicated kingdom to test Ferryman, Necromancer, Hunter, Way of the Mouse and Young Witch
    example_7 = "Baths, Caravan, Charm, City Quarter, Ferryman (Dungeon), Fishing Village, Innkeeper, Lost City, Inherited(Necromancer), No Colonies, No Shelters, Pixie, Riverboat (Hunter), Way of the Mouse (Sleigh), Young Witch (Fishing Village), Approaching Army (Swindler)"

    for example in [
        example_1,
        example_2,
        example_3,
        example_4,
        example_5,
        example_6,
        example_7,
    ]:
        _test_dombot_readin_readout(example)


def test_random_kingdom():
    """Test the generation and dombot string generation of a random kingdom."""
    kingdom = rk.KingdomRandomizer().randomize_new_kingdom()
    redone = rk.Kingdom.from_dombot_csv_string(kingdom.get_dombot_csv_string())
    assert kingdom == redone


def test_mouse():
    """Test whether a mouse card is forced in after specifying way of the mouse"""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["way_of_the_mouse"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert (
        "way_of_the_mouse" in kingdom.landscapes
    ), "WotMouse has not been chosen correctly"
    assert kingdom.mouse_card != "", "No Mouse card has been chosen"
    # Reroll mouse card:
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.mouse_card)
    assert new_kingdom.mouse_card != kingdom.mouse_card
    assert new_kingdom.mouse_card != ""
    # Test rerolling way of the mouse itself
    new_kingdom = randomizer.reroll_single_cso(kingdom, "way_of_the_mouse")
    assert new_kingdom.mouse_card == ""
    assert "way_of_the_mouse" not in new_kingdom.landscapes


def test_ferryman():
    """Test whether a ferryman card is forced in after specifying ferryman"""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["ferryman"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "ferryman" in kingdom.cards, "Ferryman has not been chosen correctly"
    assert kingdom.ferryman_pile != "", "No Ferryman card has been chosen"
    assert (
        kingdom.ferryman_pile not in kingdom.cards
    ), "Ferryman pile somehow is also kingdom card"
    # Test rerolling the ferryman card:
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.ferryman_pile)
    assert new_kingdom.ferryman_pile != kingdom.ferryman_pile
    assert new_kingdom.ferryman_pile != ""
    new_kingdom = randomizer.reroll_single_cso(kingdom, "ferryman")
    assert new_kingdom.ferryman_pile == ""
    assert "ferryman" not in new_kingdom.cards


def test_riverboat():
    """Test whether a riverboat card has correctly been chosen."""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["riverboat"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "riverboat" in kingdom.cards, "Riverboat has not been chosen correctly"
    assert kingdom.riverboat_card != "", "No Riverboat card has been chosen"
    assert (
        kingdom.riverboat_card not in kingdom.cards
    ), "Riverboat card somehow ended up in kingdom"
    obj = rk.ALL_CSOS.loc[kingdom.riverboat_card]
    assert "Duration" not in obj["Types"], "Riverboat target shouldn't be duration"
    assert all(
        [obj["Name"] not in list(rk.ROTATOR_DICT.keys()) + ["Knights", "Castles"]]
    )
    if len((intersect := set(obj["Types"]).intersection(rk.SPLIT_CARD_TYPES))) > 0:
        intersecting_str = list(intersect)[0]
        name = (
            intersecting_str + "s"
            if intersecting_str not in ["Townsfolk", "Clashes"]
            else intersecting_str if intersecting_str == "Townsfolk" else "Clashes"
        )
        root_rotator_pile = rk.ALL_CSOS.loc[rk.sanitize_cso_name(name)]
        assert (
            root_rotator_pile.index not in kingdom.cards
        ), "Riverboat card is unexpectedly also part of kingdom"
    assert all([obj["Name"] not in rk.ROTATOR_DICT])
    # Now that we've checked that Riverboat has been correctly added, we can first reroll its card
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.riverboat_card)
    assert new_kingdom.riverboat_card != ""
    assert new_kingdom.riverboat_card != kingdom.riverboat_card
    # Now we reroll riverboat and check whether its pick has correctly been removed.
    new_kingdom = randomizer.reroll_single_cso(kingdom, "riverboat")
    assert "riverboat" not in new_kingdom.cards
    assert new_kingdom.riverboat_card == ""


def _drain_pool(pool_con, special_card_to_pick_for=None) -> list[str]:
    """All picks until the pool is empty."""
    qualities = {qual: 0 for qual in rk.QUALITIES_AVAILABLE}
    picks = []
    while (pick := pool_con.pick_next_card(qualities, special_card_to_pick_for)) != "":
        picks.append(pick)
    return picks


def test_riverboat_picks_single_knights_not_the_pile():
    """The Knights pile counted as a single card costing $5*, so Riverboat got it in
    ~1 of 100 kingdoms. A single Knight is fine, but only one, and only while the
    Knights aren't in the kingdom."""
    from random_kingdominion.kingdom.pool_container import PoolContainer
    from random_kingdominion.utils.kingdom_helper_funcs import get_parent_piles

    config = rk.CustomConfigParser(load_default=True)
    config.set_expansions(["Dark Ages"])
    pool_con = PoolContainer(config)
    picks = _drain_pool(pool_con, "riverboat")
    assert "knights" not in picks
    assert len([p for p in picks if get_parent_piles().get(p) == "knights"]) == 1
    assert "knights" not in pool_con.main_pool.index
    pool_con = PoolContainer(config)
    pool_con.drop_csos(["knights"])
    picks = _drain_pool(pool_con, "riverboat")
    assert "bandit_camp" in picks
    assert not [p for p in picks if get_parent_piles().get(p) == "knights"]


def test_riverboat_never_gets_small_castle():
    """It would gain a Castle, but the Castles aren't in the kingdom."""
    from random_kingdominion.kingdom.pool_container import PoolContainer

    config = rk.CustomConfigParser(load_default=True)
    config.set_expansions(["Empires"])
    picks = _drain_pool(PoolContainer(config), "riverboat")
    assert "small_castle" not in picks
    assert "legionary" in picks


def test_split_piles_are_picked_as_kingdom_cards():
    """Normal picks drew from the single cards, without the split pile headers, so
    e.g. the Augurs were never picked (since 2024-08)."""
    from random_kingdominion.kingdom.pool_container import PoolContainer
    from random_kingdominion.utils.kingdom_helper_funcs import get_parent_piles

    config = rk.CustomConfigParser(load_default=True)
    config.set_expansions(["Allies", "Dark Ages", "Empires"])
    picks = set(_drain_pool(PoolContainer(config)))
    assert {"augurs", "castles", "knights", "patrician/emporium"} <= picks
    single_cards = {key for key, pile in get_parent_piles().items() if key != pile}
    assert not picks & single_cards


def test_liaison_as_riverboat_card_gets_an_ally(monkeypatch):
    """The randomizer looked for Liaisons before setting Riverboat's card, so only
    later picks added the Ally: none when the card was rerolled or picked last."""
    from random_kingdominion.kingdom.invalidity_stuff import InvalidityReason
    from random_kingdominion.kingdom.pool_container import PoolContainer

    config = rk.CustomConfigParser(load_default=True)
    config.set_expansions(["Rising Sun"])  # No Liaisons of its own
    config.setlist("General", "required_csos", ["riverboat"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert not kingdom.contains_ally()

    pick_next_card = PoolContainer.pick_next_card

    def pick_guildmaster(self, qualities, special_card_to_pick_for=None):
        if special_card_to_pick_for != "riverboat":
            return pick_next_card(self, qualities, special_card_to_pick_for)
        self.main_pool = self.main_pool.drop("guildmaster", errors="ignore")
        return "guildmaster"

    monkeypatch.setattr(PoolContainer, "pick_next_card", pick_guildmaster)
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.riverboat_card)
    assert new_kingdom.riverboat_card == "guildmaster"
    assert new_kingdom.contains_ally()
    assert InvalidityReason.check_kingdom_validity(new_kingdom) == []


def test_young_witch():
    """Test whether a bane card is forced in after specifying young witch"""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["young_witch"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "young_witch" in kingdom.cards, "young_witch has not been chosen correctly"
    assert kingdom.bane_pile != "", "No Bane card has been chosen"
    assert kingdom.bane_pile in kingdom.cards, "Bane pile not part of kingdom"
    old_bane = kingdom.bane_pile
    # First, reroll the bane pile:
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.bane_pile)
    assert new_kingdom.bane_pile != ""
    assert new_kingdom.bane_pile in new_kingdom.cards
    assert old_bane not in new_kingdom.cards
    # Now, we can reroll young witch and see if everything has been removed correctly
    new_kingdom = randomizer.reroll_single_cso(kingdom, "young_witch")
    assert new_kingdom.bane_pile == ""
    assert old_bane not in new_kingdom.cards
    assert "young_witch" not in new_kingdom.cards


def test_young_witch_as_ferryman_pile_gets_a_bane(monkeypatch):
    """Young Witch as Ferryman's pile still needs a Bane, which is then the only
    reason for an extra Supply pile."""
    from random_kingdominion.kingdom.invalidity_stuff import InvalidityReason
    from random_kingdominion.kingdom.pool_container import PoolContainer

    pick_next_card = PoolContainer.pick_next_card

    def pick_young_witch_for_ferryman(self, qualities, special_card_to_pick_for=None):
        if special_card_to_pick_for != "ferryman":
            return pick_next_card(self, qualities, special_card_to_pick_for)
        self.main_pool = self.main_pool.drop("young_witch", errors="ignore")
        return "young_witch"

    monkeypatch.setattr(PoolContainer, "pick_next_card", pick_young_witch_for_ferryman)
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["ferryman"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert kingdom.ferryman_pile == "young_witch"
    assert "young_witch" not in kingdom.cards
    assert kingdom.bane_pile in kingdom.cards
    assert InvalidityReason.check_kingdom_validity(kingdom) == []
    # Rerolling the Ferryman pile removes the Bane
    monkeypatch.undo()
    new_kingdom = randomizer.reroll_single_cso(kingdom, "young_witch")
    assert new_kingdom.ferryman_pile not in ["", "young_witch"]
    assert new_kingdom.bane_pile == ""
    assert kingdom.bane_pile not in new_kingdom.cards


# Daily 2024-03-20, with the Bane nested into Ferryman's pile
_FERRYMAN_ON_YOUNG_WITCH = (
    "barge, bounty_hunter, camel_train, cavalry, ferryman(young_witch(black_cat)), "
    "hamlet, horn_of_plenty, remake, sleigh, stockpile"
)


def test_young_witch_as_ferryman_pile_in_dombot_strings():
    kingdom = rk.Kingdom.from_dombot_csv_string(_FERRYMAN_ON_YOUNG_WITCH)
    assert kingdom.notes == ""
    assert kingdom.ferryman_pile == "young_witch"
    assert kingdom.bane_pile == "black_cat"
    assert "black_cat" in kingdom.cards and "young_witch" not in kingdom.cards
    assert kingdom.is_valid, kingdom.invalidity_reasons
    # Young Witch isn't printed on its own, so its Bane goes with it (M19, step 7)
    assert "Ferryman (Young Witch (Black Cat))" in kingdom.get_dombot_csv_string()
    assert "ferryman (young_witch (black_cat))" in kingdom.get_sanitized_tgg_string()
    _test_dombot_readin_readout(_FERRYMAN_ON_YOUNG_WITCH)

    without_bane = _FERRYMAN_ON_YOUNG_WITCH.replace("(black_cat)", "")
    kingdom = rk.Kingdom.from_dombot_csv_string(without_bane)
    assert _reason_keys(kingdom) == {"young_witch_but_no_bane"}


def test_bane_syntax_is_invalid():
    """DomBot doesn't understand bane(…) (M19, step 8): the Bane is still read, and
    the kingdom is marked invalid until it's written as Young Witch's target."""
    bane_syntax = _FERRYMAN_ON_YOUNG_WITCH.replace(
        "ferryman(young_witch(black_cat))", "ferryman(young_witch), bane(black_cat)"
    )
    kingdom = rk.Kingdom.from_dombot_csv_string(bane_syntax)
    assert kingdom == rk.Kingdom.from_dombot_csv_string(_FERRYMAN_ON_YOUNG_WITCH)
    assert _reason_keys(kingdom) == {"bane_syntax_not_supported"}
    assert "'young_witch(black_cat)'" in kingdom.invalidity_reasons[0].get_description()
    # Printed as DomBot syntax, which is valid again
    reparsed = rk.Kingdom.from_dombot_csv_string(kingdom.get_dombot_csv_string())
    assert reparsed.is_valid, reparsed.invalidity_reasons
    assert "uses_bane_syntax" not in kingdom.get_dict_repr()


def test_druid_boons():
    """Test whether druid boons are forced in after specifying druid"""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["druid"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "druid" in kingdom.cards, "druid has not been chosen correctly"
    assert len(kingdom.druid_boons) == 3, "Wrong boons chosen."
    # Test rerolling druid
    new_kingdom = randomizer.reroll_single_cso(kingdom, "druid")
    assert len(new_kingdom.druid_boons) == 0
    assert "druid" not in new_kingdom.cards


@pytest.mark.parametrize(
    "boons, expected_reasons",
    [
        (["the_earths_gift", "the_flames_gift", "the_swamps_gift"], []),
        ([], ["druid_but_no_boons"]),
    ],
)
def test_druid_as_mouse_card_needs_its_boons(boons: list[str], expected_reasons):
    """The randomizer picks Boons for Druid as Mouse's card, which were flagged as
    Boons without a Druid (in ~1 of 30 kingdoms with Way of the Mouse)."""
    from random_kingdominion.kingdom.invalidity_stuff import InvalidityReason

    kingdom = rk.Kingdom(
        ["village", "smithy", "militia", "market", "mine", "witch", "festival"]
        + ["library", "laboratory", "moat"],
        landscapes=["way_of_the_mouse"],
        mouse_card="druid",
        druid_boons=boons,
    )
    reasons = InvalidityReason.check_kingdom_validity(kingdom)
    assert [r.key for r in reasons] == expected_reasons


def test_traits():
    """Test randomization and targeting of traits."""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["inherited"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "inherited" in kingdom.landscapes, "inherited has not been chosen correctly"
    assert "inherited" in kingdom.trait_targets
    target = kingdom.trait_targets["inherited"][0]
    assert target in kingdom.cards
    # Test rerolling target
    new_kingdom = randomizer.reroll_single_cso(kingdom, target)
    assert new_kingdom.trait_targets["inherited"][0] != target
    assert target not in new_kingdom.cards
    # Test rerolling the trait itself
    new_kingdom = randomizer.reroll_single_cso(kingdom, "inherited")
    assert "inherited" not in new_kingdom.landscapes
    assert "inherited" not in new_kingdom.trait_targets


def test_required_csos_are_not_drawn_again():
    """Required CSOs stayed in the draw pool, so a random pick could add a required
    landscape a second time (which crashed `add_landscape`, in ~1 of 400 kingdoms
    with Inherited required) or leave the kingdom a card short."""
    from random_kingdominion.kingdom.pool_container import PoolContainer
    from random_kingdominion.kingdom.randomized_kingdom import RandomizedKingdom

    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["inherited", "village"])
    randomizer = rk.KingdomRandomizer(config)
    randomizer.pool_con = PoolContainer(config)
    required = {"inherited", "village"}
    assert required <= set(randomizer.pool_con.main_pool.index)
    kingdom = randomizer.add_required_csos(RandomizedKingdom(num_desired_landscapes=2))
    assert required <= set(kingdom.contained_csos)
    assert not required & set(randomizer.pool_con.main_pool.index)


def test_obelisk():
    """Test setting the obelisk pile."""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["obelisk"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "obelisk" in kingdom.landscapes, "obelisk has not been chosen correctly"
    assert kingdom.obelisk_pile != "", "No Obelisk pile chosen."
    assert kingdom.obelisk_pile in kingdom.cards
    # Test rerolling obelisk pile, checking whether new obelisk target has been chosen correctly
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.obelisk_pile)
    assert new_kingdom.obelisk_pile != ""
    assert new_kingdom.obelisk_pile != kingdom.obelisk_pile
    assert kingdom.obelisk_pile not in new_kingdom.cards
    assert new_kingdom.obelisk_pile in new_kingdom.cards
    # Test rerolling the obelisk itself
    new_kingdom = randomizer.reroll_single_cso(kingdom, "obelisk")
    assert "obelisk" not in new_kingdom.landscapes
    assert new_kingdom.obelisk_pile == ""
    assert (
        kingdom.obelisk_pile in new_kingdom.cards
    ), "Old obelisk target has accidentally been removed"


def test_approaching_army():
    """Test whether an army card is forced in after specifying approaching army."""
    config = rk.CustomConfigParser(load_default=True)
    config.setlist("General", "required_csos", ["approaching_army"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert (
        "approaching_army" in kingdom.landscapes
    ), "approaching_army has not been chosen correctly"
    assert kingdom.army_pile != "", "No army card has been chosen"
    assert kingdom.army_pile in kingdom.cards, "Army pile not part of kingdom"
    # First, reroll the army pile:
    new_kingdom = randomizer.reroll_single_cso(kingdom, kingdom.army_pile)
    assert new_kingdom.army_pile != ""
    assert new_kingdom.army_pile in new_kingdom.cards
    assert kingdom.army_pile not in new_kingdom.cards
    # Now, we can reroll army and see if everything has been removed correctly
    new_kingdom = randomizer.reroll_single_cso(kingdom, "approaching_army")
    assert new_kingdom.army_pile == ""
    assert kingdom.army_pile not in new_kingdom.cards
    assert "approaching_army" not in new_kingdom.landscapes


def test_ally_addition_and_removal():
    """Test whether an ally is properly added and removed given the existence of liaisons."""
    config = rk.CustomConfigParser(load_default=True)
    config.set("General", "allow_required_csos_of_other_exps", "True")
    config.set_expansions(["Base, 2E"])
    config.setlist("General", "required_csos", ["underling"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "underling" in kingdom.cards, "Underling has not been chosen correctly"
    assert kingdom.contains_ally(), "No Ally chosen"
    # First, reroll the ally:
    ally = kingdom.landscapes[0]  # Should be the only landscape
    new_kingdom = randomizer.reroll_single_cso(kingdom, ally)
    assert new_kingdom.contains_ally()
    assert ally not in new_kingdom.landscapes
    # Now, reroll the underling
    new_kingdom = randomizer.reroll_single_cso(kingdom, "underling")
    assert "underling" not in new_kingdom.cards
    assert not new_kingdom.contains_ally()

    # Randomize another kingdom with two liaisons, reroll one of them and check if the ally is still there
    config = rk.CustomConfigParser(load_default=True)
    config.set("General", "allow_required_csos_of_other_exps", "True")
    config.set_expansions(["Base, 2E"])
    config.setlist("General", "required_csos", ["underling", "sycophant"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    new_kingdom = randomizer.reroll_single_cso(kingdom, "underling")
    assert new_kingdom.contains_ally()


def test_liaison_addition_and_removal():
    """Test whether a liaison is properly added and removed given the existence of an ally."""
    config = rk.CustomConfigParser(load_default=True)
    config.set("General", "allow_required_csos_of_other_exps", "True")
    config.set_expansions(["Base, 2E"])
    config.setlist("General", "required_csos", ["league_of_bankers"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert (
        "league_of_bankers" in kingdom.landscapes
    ), f"Ally has not been chosen correctly, landscapes are {kingdom.landscapes}"
    assert np.sum(kingdom.kingdom_card_df["IsLiaison"]) > 0, "No liaison chosen"
    # First, reroll the ally:
    new_kingdom = randomizer.reroll_single_cso(kingdom, "league_of_bankers")
    assert new_kingdom.contains_ally()
    assert "league_of_bankers" not in new_kingdom.landscapes
    # Now, reroll the liaison
    df = kingdom.kingdom_card_df
    liaison = df[df["IsLiaison"]].index[0]
    new_kingdom = randomizer.reroll_single_cso(kingdom, liaison)
    assert liaison not in new_kingdom.cards
    assert not new_kingdom.contains_ally()


def test_prophecy_addition_and_removal():
    """Test whether a prophecy is properly added and removed given the existence of omen."""
    config = rk.CustomConfigParser(load_default=True)
    config.set("General", "allow_required_csos_of_other_exps", "True")
    config.set_expansions(["Base, 2E"])
    config.setlist("General", "required_csos", ["tea_house"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert "tea_house" in kingdom.cards, "tea_house has not been chosen correctly"
    assert kingdom.contains_prophecy(), "No Prophecy chosen"
    # First, reroll the ally:
    prophecy = kingdom.landscapes[0]  # Should be the only landscape
    new_kingdom = randomizer.reroll_single_cso(kingdom, prophecy)
    assert new_kingdom.contains_prophecy()
    assert prophecy not in new_kingdom.landscapes
    # Now, reroll the tea_house
    new_kingdom = randomizer.reroll_single_cso(kingdom, "tea_house")
    assert "tea_house" not in new_kingdom.cards
    assert not new_kingdom.contains_prophecy()


def test_omen_addition_and_removal():
    """Test whether a omen is properly added and removed given the existence of a prophecy."""
    config = rk.CustomConfigParser(load_default=True)
    config.set("General", "allow_required_csos_of_other_exps", "True")
    config.set_expansions(["Base, 2E"])
    config.setlist("General", "required_csos", ["approaching_army"])
    randomizer = rk.KingdomRandomizer(config)
    kingdom = randomizer.randomize_new_kingdom()
    assert (
        "approaching_army" in kingdom.landscapes
    ), "Prophecy has not been chosen correctly"
    assert np.sum(kingdom.kingdom_card_df["IsOmen"]) > 0, "No omen chosen"
    # First, reroll the ally:
    new_kingdom = randomizer.reroll_single_cso(kingdom, "approaching_army")
    assert new_kingdom.contains_prophecy()
    assert "approaching_army" not in new_kingdom.landscapes
    # Now, reroll the omen
    df = kingdom.kingdom_card_df
    omen = df[df["IsOmen"]].index[0]
    new_kingdom = randomizer.reroll_single_cso(kingdom, omen)
    assert omen not in new_kingdom.cards
    assert not new_kingdom.contains_prophecy()


def test_total_quality_docstring_examples():
    import doctest
    import importlib

    helper_funcs = importlib.import_module(
        "random_kingdominion.utils.kingdom_helper_funcs"
    )
    assert doctest.testmod(helper_funcs).failed == 0


def test_cso_names_match_the_card_data():
    """get_cso_name builds its name dict only once (M9); it must still agree with ALL_CSOS."""
    from random_kingdominion.utils import utils

    for key, name in rk.ALL_CSOS["Name"].items():
        assert rk.get_cso_name(key) == name
    assert rk.get_cso_name("not_a_cso") == "NOT FOUND"
    assert rk.get_cso_name("not_a_cso", default_val="") == ""
    assert utils._get_cso_name_dict() is utils._get_cso_name_dict()


def test_split_piles_agree_with_the_card_data(caplog):
    """`sanitize_cso_name(…, True)` uses a dict built once instead of a lookup in
    ALL_CSOS per name (~150 µs); it must give the same split piles."""
    csos = rk.ALL_CSOS
    for key, cso in csos.iterrows():
        expected = (
            rk.sanitize_cso_name(cso["ParentPile"]) if cso["HasParentPile"] else key
        )
        assert rk.sanitize_cso_name(str(key), replace_parent_pile=True) == expected
    assert rk.sanitize_cso_name("Elder", replace_parent_pile=True) == "townsfolk"
    assert rk.sanitize_cso_name("not_a_cso", replace_parent_pile=True) == "not_a_cso"
    assert "Could not find cso: not_a_cso" in caplog.text


def test_cso_sort_ranks_order_like_sort_kingdom():
    """Kingdoms sort their tables by a rank computed once per CSO (M19, step 2),
    which only gives `sort_kingdom`'s order as long as no two CSOs tie."""
    from random_kingdominion.utils.kingdom_helper_funcs import sort_kingdom

    columns_before = rk.ALL_CSOS.columns.to_list()
    ranks = rk.get_cso_sort_ranks()
    assert rk.ALL_CSOS.columns.to_list() == columns_before  # Not changed in place
    assert sorted(ranks) == sorted(rk.ALL_CSOS.index)
    rng = np.random.default_rng(19)
    for _ in range(100):
        keys = list(rng.choice(rk.ALL_CSOS.index, size=15, replace=False))
        expected = sort_kingdom(rk.ALL_CSOS.loc[keys]).index.to_list()
        assert sorted(keys, key=ranks.__getitem__) == expected


def test_kingdom_tables_are_sorted():
    from random_kingdominion.utils.kingdom_helper_funcs import sort_kingdom

    # Potion and Debt costs, landscapes, campaign effects and extra piles
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "familiar, city_quarter, village, smithy, ferryman(cellar), "
        "druid(the_earths_gift, the_fields_gift, the_suns_gift), market, militia, "
        "witch, festival, alms, nearby(village), obelisk(smithy), colonies "
        "-x stamp_pay_later(market), start_replace_copper(silver)"
    )
    assert kingdom.notes == ""
    for df in [
        kingdom.full_kingdom_df,
        kingdom.kingdom_card_df,
        kingdom.kingdom_landscape_df,
        kingdom.kingdom_campaign_effects_df,
    ]:
        assert df.index.to_list() == sort_kingdom(df).index.to_list()
    assert kingdom.kingdom_card_df.index[0] == "city_quarter"  # Debt costs first
    assert kingdom.kingdom_campaign_effects_df.index.to_list() == [
        "pay_later",
        "replace_copper",
    ]


def test_kingdom_tables_are_built_on_first_use():
    """Building them took ~1.2 of ~1.5 ms per Kingdom, which most uses don't need;
    the qualities and expansions come without them."""
    kingdom = rk.Kingdom(["village", "smithy"], landscapes=["alms"])
    assert "full_kingdom_df" not in vars(kingdom)
    assert kingdom.total_qualities["village"] == 2  # Village is a 2
    assert kingdom.expansions == ["Adventures", "Base, 2E"]
    assert kingdom.kingdom_card_df.index.to_list() == ["village", "smithy"]
    assert "full_kingdom_df" in vars(kingdom)
    assert "full_kingdom_df" not in kingdom.get_dict_repr()  # Not stored


def test_unknown_csos_raise_when_building_a_kingdom():
    # Callers rely on it, e.g. the quiz's pools to skip broken stored kingdoms
    with pytest.raises(KeyError, match="not_a_card"):
        rk.Kingdom(["village", "not_a_card"])


def test_dombot_string_uses_display_names_of_cards_and_extra_piles():
    kingdom = rk.Kingdom(
        cards=[
            "kings_court",
            "young_witch",
            "village",
            "smithy",
            "wine_merchant",
            "ferryman",
            "gladiator",
            "sir_martin",
            "vassal",
            "merchant_camp",
        ],
        landscapes=["way_of_the_mouse"],
        bane_pile="moat",
        ferryman_pile="cellar",
        mouse_card="harbinger",
        use_colonies=True,
    )

    assert kingdom.get_dombot_csv_string() == (
        "Colonies, Ferryman (Cellar), Gladiator, King's Court, Merchant Camp, "
        "No Shelters, Sir Martin, Smithy, Vassal, Village, "
        "Way of the Mouse (Harbinger), Wine Merchant, Young Witch (Moat)"
    )


def test_colony_spellings_in_dombot_strings():
    """All Colony/Platinum spellings switch Colonies on and aren't reported as
    unrecognized (M19: "colony/platinum" used to turn into "colonies/colonies")."""
    for colony_str in ["colonies", "colony", "platinum", "colony/platinum"]:
        kingdom = rk.Kingdom.from_dombot_csv_string(f"village, smithy, {colony_str}")
        assert kingdom.use_colonies, colony_str
        assert kingdom.cards == ["smithy", "village"]
        assert kingdom.notes == ""
    assert not rk.Kingdom.from_dombot_csv_string("village, no colonies").use_colonies


def test_expansions_without_edition_map_to_the_second_edition():
    # Village is in both Base editions, Young Witch in both Cornucopia editions
    kingdom = rk.Kingdom(["village", "young_witch"])
    assert kingdom.expansions == ["Base, 2E", "Cornucopia & Guilds, 2E"]
    # Fortune Teller is only in the first edition, which then covers Young Witch too
    kingdom = rk.Kingdom(["village", "young_witch", "fortune_teller"])
    assert kingdom.expansions == ["Base, 2E", "Cornucopia, 1E"]


# DomBot strings as they appear in scripts/data/new_kingdoms/, with the special
# targets the parser has to recognize (M5, safety net for splitting the parser, M19)
_DOMBOT_CASES = {
    "bane": (
        "hamlet, farmhands, gardens, young_witch(village), ferryman(shop), "
        "horn_of_plenty, jester, library, mine, artisan, stamp_offers_insight(ferryman)",
        {
            "bane_pile": "village",
            "ferryman_pile": "shop",
            "stamps_and_effects": [["offers_insight", "ferryman"]],
        },
    ),
    "ferryman": (
        "hamlet, vassal, workshop, farmhands, gardens, carnival, ferryman(remake), "
        "horn_of_plenty, jester, joust",
        {"ferryman_pile": "remake"},
    ),
    "riverboat": (
        "riverboat(imperial_envoy), village, smithy, chapel, market, militia, witch, "
        "festival, library, laboratory",
        {"riverboat_card": "imperial_envoy"},
    ),
    "mouse": (
        "secret_cave, shop, bridge, sailor, ferryman(marauder), governor, hunter, mine, "
        "quartermaster, sanctuary, practice, way_of_the_mouse(squire)",
        {"mouse_card": "squire", "ferryman_pile": "marauder"},
    ),
    "obelisk_and_stamp": (
        "city_quarter, patrician, moneylender, remodel, villa, charm, council_room, "
        "crown, forum, witch, obelisk(patrician), basilica, stamp_pay_later(crown)",
        {
            "obelisk_pile": "patrician/emporium",
            "stamps_and_effects": [["pay_later", "crown"]],
        },
    ),
    "approaching_army": (
        "fishmonger, sentinel, shop, wizards, alley, ninja, river_shrine, emissary, "
        "ferryman(clashes), tea_house, approaching_army(jester), woodworkers_guild",
        {"army_pile": "jester", "ferryman_pile": "clashes"},
    ),
    "druid_boons": (
        "druid(the_moons_gift, the_suns_gift, the_mountains_gift), faithful_hound, "
        "tracker, fool, secret_cave, bard, militia, shepherd, cursed_village, "
        "sacred_grove",
        {"druid_boons": ["the_moons_gift", "the_mountains_gift", "the_suns_gift"]},
    ),
    "trait": (
        "engineer, daimyo, artist, overlord, search, abundance, rustic_village, "
        "capital, imperial_envoy, kitsune, rush, nearby(imperial_envoy), sickness",
        {"traits": [["nearby", "imperial_envoy"]]},
    ),
    "two_stamps_on_one_card": (
        "cage, siren, stowaway, gondola, rope, council_room, frigate, mining_road, "
        "sentry, trickster, nearby(rope), stamp_treasurified(mining_road), "
        "stamp_durationified(mining_road)",
        {
            "traits": [["nearby", "rope"]],
            "stamps_and_effects": [
                ["durationified", "mining_road"],
                ["treasurified", "mining_road"],
            ],
        },
    ),
}


@pytest.mark.parametrize(
    "dombot_str, expected", _DOMBOT_CASES.values(), ids=_DOMBOT_CASES.keys()
)
def test_dombot_string_special_targets(dombot_str: str, expected: dict):
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.notes == ""
    for attr, value in expected.items():
        assert getattr(kingdom, attr) == value, attr
    _test_dombot_readin_readout(dombot_str)


_NEARBY_ON_TWO_CARDS = (
    "engineer, daimyo, artist, overlord, search, abundance, rustic_village, "
    "capital, imperial_envoy, kitsune, rush, nearby(imperial_envoy), "
    "nearby(engineer), sickness"
)
# Campaign "Plunder 3": Shy on Gold, which isn't a supply pile
_SHY_ON_GOLD = (
    "cellar, shaman, gardens, gondola, harbor_village, landing_party, mapmaker, "
    "smithy, bandit, first_mate, patient(first_mate), shy(gold)"
)
# A Trait on a Night card, as in some of TGG's campaigns (campaign_dump.yml, M30)
_PIOUS_ON_MONASTERY = (
    "cellar, shaman, gardens, gondola, harbor_village, landing_party, mapmaker, "
    "smithy, bandit, monastery, pious(monastery)"
)


def _reason_keys(kingdom: rk.Kingdom) -> set[str]:
    return {reason.key for reason in kingdom.invalidity_reasons}


def test_same_trait_on_two_cards():
    """Only allowed in campaigns (M24), but parsed either way."""
    kingdom = rk.Kingdom.from_dombot_csv_string(_NEARBY_ON_TWO_CARDS)
    assert kingdom.traits == [["nearby", "engineer"], ["nearby", "imperial_envoy"]]
    assert kingdom.trait_targets == {"nearby": ["engineer", "imperial_envoy"]}
    assert kingdom.get_traits_on("engineer") == ["nearby"]
    _test_dombot_readin_readout(_NEARBY_ON_TWO_CARDS)


def test_trait_with_two_targets_in_one_entry():
    """TGG's campaigns write "friendly(scavenger, trickster)", which used to be
    unrecognized (32 kingdoms of campaign_dump.yml, M30)."""
    one_entry = _NEARBY_ON_TWO_CARDS.replace(
        "nearby(imperial_envoy), nearby(engineer)", "nearby(imperial_envoy, engineer)"
    )
    kingdom = rk.Kingdom.from_dombot_csv_string(one_entry)
    assert kingdom.notes == ""
    assert kingdom == rk.Kingdom.from_dombot_csv_string(_NEARBY_ON_TWO_CARDS)


def test_trait_on_a_non_supply_pile():
    kingdom = rk.Kingdom.from_dombot_csv_string(_SHY_ON_GOLD)
    assert kingdom.notes == ""
    assert ["shy", "gold"] in kingdom.traits
    assert "gold" not in kingdom.cards  # Gold isn't a kingdom pile
    _test_dombot_readin_readout(_SHY_ON_GOLD)


@pytest.mark.parametrize(
    "dombot_str, reason",
    [
        (_NEARBY_ON_TWO_CARDS, "trait_on_several_piles_outside_campaign"),
        (_SHY_ON_GOLD, "trait_on_non_supply_pile_outside_campaign"),
        (_PIOUS_ON_MONASTERY, "trait_targets_invalid"),
    ],
)
def test_campaign_only_traits_are_invalid_outside_of_campaigns(
    dombot_str: str, reason: str
):
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert not kingdom.is_campaign
    assert _reason_keys(kingdom) == {reason}

    campaign = rk.Kingdom.from_dombot_csv_string(dombot_str + ", campaign")
    assert campaign.is_campaign
    assert campaign.is_valid, campaign.invalidity_reasons
    # The flag survives printing ("Campaign") and parsing again
    _test_dombot_readin_readout(dombot_str + ", campaign")


def test_campaign_kingdoms_are_loaded_as_campaigns():
    manager = rk.KingdomManager()
    manager.load_campaigns()
    plunder_3 = manager.get_kingdom_by_name("Plunder 3")
    assert plunder_3 is not None and plunder_3.is_campaign
    assert ["shy", "gold"] in plunder_3.traits


def test_start_effect_with_several_targets():
    """One pair per target, duplicates included: they replace several Coppers."""
    dombot_str = (
        "fishing_village, lookout, sea_chart, village, warehouse, sailor, bandit, "
        "corsair, festival, laboratory, start_replace_copper(silver), "
        "start_replace_copper(silver), start_replace_copper(estate)"
    )
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.notes == ""  # Repeated campaign effects aren't duplicates
    assert kingdom.stamps_and_effects == [
        ["replace_copper", "estate"],
        ["replace_copper", "silver"],
        ["replace_copper", "silver"],
    ]
    deck = kingdom.get_starting_deck
    assert (deck.count("copper"), deck.count("silver"), deck.count("estate")) == (
        4,
        2,
        4,
    )
    _test_dombot_readin_readout(dombot_str)


def test_merged_effect_targets_of_older_files_are_split():
    """Older kingdom files stored several targets as one "silver,_estate"."""
    kingdom = rk.Kingdom(
        ["village"], stamps_and_effects=[["replace_copper", "silver,_silver,_estate"]]
    )
    assert kingdom.effect_targets == {"replace_copper": ["estate", "silver", "silver"]}


def test_replace_estate_from_pile_is_its_own_effect():
    """It used to be merged into replace_estate, as its name contains it."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "village, smithy, chapel, market, militia, witch, festival, library, "
        "laboratory, moat, start_replace_estate(silver), "
        "start_replace_estate_from_pile(moat)"
    )
    assert kingdom.effect_targets == {
        "replace_estate": ["silver"],
        "replace_estate_from_pile": ["moat"],
    }
    assert kingdom.has_modified_starting_deck
    deck = kingdom.get_starting_deck
    assert deck.count("estate") == 1
    assert deck.count("silver") == 1 and deck.count("moat") == 1


@pytest.mark.parametrize(
    "dombot_str, expected_counts",
    [
        # Daily 2025-03-02: one replacement takes the Hovel
        (
            "Colonies, Continue, Farrier, Forager, Fortress, Forum, King's Court, "
            "Lurker, Rogue, Shelters, Souk, Tomb, Transmogrify, Warehouse -x "
            "twist_head_start, start_replace_estate(lurker)",
            {"lurker": 1, "hovel": 0, "overgrown_estate": 1, "necropolis": 1},
        ),
        # Campaign Dark Ages 9: the Overgrown Estates put in aren't replaced again
        (
            "Altar, Armory, Chapel, Counterfeit, Death Cart, Ironmonger, Market "
            "Square, Merchant, No Colonies, Scavenger, Shelters, Village -x "
            "start_replace_estate(overgrown_estate), "
            "start_replace_estate(overgrown_estate), "
            "start_replace_estate(overgrown_estate), stamp_with_spoils(ironmonger)",
            {"overgrown_estate": 3, "hovel": 0, "necropolis": 0, "copper": 7},
        ),
        # Both effects together, the Necropolis goes last
        (
            "village, smithy, chapel, market, militia, witch, festival, library, "
            "laboratory, moat, shelters, start_replace_estate(silver), "
            "start_replace_estate_from_pile(moat)",
            {
                "silver": 1,
                "moat": 1,
                "hovel": 0,
                "overgrown_estate": 0,
                "necropolis": 1,
            },
        ),
    ],
)
def test_replace_estate_with_shelters(dombot_str: str, expected_counts: dict):
    """With Shelters, there's no Estate to replace (M19 step 13)."""
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.use_shelters
    deck = kingdom.get_starting_deck
    assert len(deck) == 10
    assert {card: deck.count(card) for card in expected_counts} == expected_counts


@pytest.mark.parametrize(
    "dombot_str, expected_counts",
    [
        # Campaign Nocturne 7
        (
            "Cobbler, Cursed Village, Monastery, Necromancer, No Colonies, No "
            "Shelters, Raider, Secret Cave, Sentry, Smithy, Witch, Workshop -x "
            "start_double_heirloom(secret_cave)",
            {"copper": 5, "magic_lamp": 2, "estate": 3},
        ),
        # Campaign Nocturne 10: Cemetery's Heirloom isn't doubled
        (
            "Bard, Cemetery, Changeling, Cursed Village, Devil's Workshop, Exorcist, "
            "Faithful Hound, No Colonies, No Shelters, Pooka, Skulk, Tormentor -x "
            "twist_delayed_joy, start_double_heirloom(pooka)",
            {"copper": 4, "cursed_gold": 2, "haunted_mirror": 1, "estate": 3},
        ),
        # Two of them (campaign_dump.yml)
        (
            "fool, pixie, village, smithy, militia, market, mine, witch, festival, "
            "library, start_double_heirloom(fool), start_double_heirloom(pixie)",
            {"copper": 3, "lucky_coin": 2, "goat": 2, "estate": 3},
        ),
    ],
)
def test_double_heirloom_doubles_the_targets_heirloom(
    dombot_str: str, expected_counts: dict
):
    """It looked up an Heirloom for every card (KeyError on the first without one)."""
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.has_modified_starting_deck
    deck = kingdom.get_starting_deck
    assert len(deck) == 10
    assert {card: deck.count(card) for card in expected_counts} == expected_counts


@pytest.mark.parametrize(
    "cards, target",
    [(["village", "smithy"], "smithy"), (["pixie", "village"], "secret_cave")],
    ids=["no_heirloom", "not_in_kingdom"],
)
def test_double_heirloom_on_a_wrong_target_raises(cards: list[str], target: str):
    kingdom = rk.Kingdom(cards, stamps_and_effects=[["double_heirloom", target]])
    with pytest.raises(ValueError, match="Double Heirloom"):
        kingdom.get_starting_deck


def test_copper_replacements_beyond_the_coppers_are_skipped(caplog):
    """Campaign Nocturne 4: four Heirlooms and four Copper replacements; TGG's client
    skips the last replacement."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "druid(the_moons_gift, the_suns_gift, the_mountains_gift), faithful_hound, "
        "tracker, fool, secret_cave, bard, militia, shepherd, cursed_village, "
        "sacred_grove, start_replace_copper(silver), start_replace_copper(silver), "
        "start_replace_copper(estate), start_replace_copper(estate)"
    )
    with caplog.at_level("WARNING", logger=rk.LOGGER.name):
        deck = kingdom.get_starting_deck
    assert len(deck) == 10 and "copper" not in deck
    assert {"lucky_coin", "magic_lamp", "pasture", "pouch"} <= set(deck)
    assert deck.count("estate") + deck.count("silver") == 6
    assert "4 Copper replacements, but only 3 Coppers" in caplog.text


def test_estate_replacements_beyond_the_estates_are_skipped(caplog):
    """Like the Coppers (11 kingdoms of campaign_dump.yml, M30)."""
    kingdom = rk.Kingdom(
        ["village"], stamps_and_effects=[["replace_estate", "silver"]] * 4
    )
    with caplog.at_level("WARNING", logger=rk.LOGGER.name):
        deck = kingdom.get_starting_deck
    assert deck.count("silver") == 3 and "estate" not in deck
    assert "4 Estate replacements, but only 3 Estates or Shelters" in caplog.text


def test_campaign_effect_aliases():
    """TGG calls the Free Stamp 'cost_zero' (Daily 2025-08-17) and writes
    'chameleonize' in its campaigns (M30)."""
    assert rk.sanitize_cso_name("stamp_cost_zero") == "free"
    assert rk.sanitize_cso_name("harem") == "farm"
    assert rk.sanitize_cso_name("stamp_chameleonize") == "chameleonized"
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "monastery, sleigh, watchtower, sailor, wandering_minstrel, crypt, ronin, "
        "farmland, nobles, wayfarer, seize_the_day, stamp_cost_zero(seize_the_day)"
    )
    assert kingdom.notes == ""
    assert kingdom.effect_targets == {"free": ["seize_the_day"]}


def test_divine_wind_survives_printing_and_parsing():
    """The Divine Wind CSOs are stored as sorted keys, however they were entered."""
    dombot_str = (
        "mountain_shrine, daimyo, dungeon, infirmary, poet, transmogrify, baker, "
        "footpad, lost_city, samurai, training, amass, divine_wind(Distant Lands, "
        "page, miser, stonemason, snake_witch, journeyman, magpie, wine_merchant, "
        "guide, aristocrat)"
    )
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.divine_wind_cso_str.startswith("aristocrat, distant_lands, guide")
    _test_dombot_readin_readout(dombot_str)


_DIVINE_WIND_WITH_BANE = (
    "mountain_shrine, daimyo, dungeon, infirmary, poet, transmogrify, baker, "
    "footpad, lost_city, samurai, training, amass, divine_wind(Distant Lands, "
    "page, miser, stonemason, Young Witch (Vassal), journeyman, magpie, "
    "wine_merchant, guide, aristocrat, vassal)"
)


def test_specials_inside_divine_wind():
    """The Divine Wind piles are a kingdom of their own, with its own specials, which
    don't apply to the kingdom itself (M19, step 9)."""
    dombot_str = _DIVINE_WIND_WITH_BANE
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.notes == ""
    assert kingdom.is_valid, kingdom.invalidity_reasons
    assert kingdom.bane_pile == "" and "vassal" not in kingdom.cards
    assert kingdom.divine_wind_cso_str.endswith("wine_merchant, young_witch(vassal)")
    subkingdom = kingdom.divine_wind_subkingdom
    assert subkingdom is not None and subkingdom.bane_pile == "vassal"
    assert "Young Witch (Vassal))" in kingdom.get_dombot_csv_string()
    _test_dombot_readin_readout(dombot_str)


def test_bane_inside_divine_wind_is_stored_as_a_pile():
    """Printing lists the Bane on its own, so the stored string changed after one
    roundtrip when it was only entered as the target (2 kingdoms of
    campaign_dump.yml, M30). Unknown piles stay, for their note."""
    without_vassal = _DIVINE_WIND_WITH_BANE.replace(", vassal)", ")")
    kingdom = rk.Kingdom.from_dombot_csv_string(without_vassal)
    with_vassal = rk.Kingdom.from_dombot_csv_string(_DIVINE_WIND_WITH_BANE)
    assert kingdom.divine_wind_cso_str == with_vassal.divine_wind_cso_str
    printed = rk.Kingdom.from_dombot_csv_string(kingdom.get_dombot_csv_string())
    assert printed.divine_wind_cso_str == kingdom.divine_wind_cso_str
    unknown = rk.Kingdom.from_dombot_csv_string(without_vassal.replace("page", "foo"))
    assert "foo" in unknown.divine_wind_cso_str.split(", ")
    assert "divine_wind_incorrect" in _reason_keys(unknown)


# Bauble is a Liaison, Band of Nomads its Ally
_DIVINE_WIND_WITH_ALLY = _DIVINE_WIND_WITH_BANE.replace(
    "samurai", "bauble, band_of_nomads"
)


@pytest.mark.parametrize(
    "dombot_str, is_valid",
    [
        # The kingdom's Ally stays when the Divine Wind piles replace the cards, so
        # a Liaison among them (Sycophant) needs no Ally of its own...
        (_DIVINE_WIND_WITH_ALLY.replace("aristocrat", "sycophant"), True),
        # ... and can't bring a second one
        (
            _DIVINE_WIND_WITH_ALLY.replace("aristocrat", "sycophant, cave_dwellers"),
            False,
        ),
        # Without a Liaison (and so an Ally) before, the piles' Liaison brings one
        (_DIVINE_WIND_WITH_BANE.replace("aristocrat", "sycophant"), False),
        (
            _DIVINE_WIND_WITH_BANE.replace("aristocrat", "sycophant, cave_dwellers"),
            True,
        ),
        # Divine Wind is the Prophecy, so the piles can't bring another one, even
        # with an Omen (Poet) among them
        (_DIVINE_WIND_WITH_BANE.replace("aristocrat", "poet, biding_time"), False),
    ],
    ids=[
        "liaison_with_the_kingdoms_ally",
        "second_ally",
        "liaison_without_ally",
        "liaison_with_its_own_ally",
        "second_prophecy",
    ],
)
def test_allies_and_prophecies_among_divine_wind_piles(dombot_str: str, is_valid):
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.notes == ""
    if is_valid:
        assert kingdom.is_valid, kingdom.invalidity_reasons[0].get_description()
    else:
        assert _reason_keys(kingdom) == {"divine_wind_incorrect"}
    _test_dombot_readin_readout(dombot_str)


def test_ally_among_divine_wind_piles():
    """It joins with the piles: not one of the kingdom's landscapes, but needed to
    set up the game."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        _DIVINE_WIND_WITH_BANE.replace("aristocrat", "sycophant, cave_dwellers")
    )
    assert "cave_dwellers" not in kingdom.landscapes
    subkingdom = kingdom.divine_wind_subkingdom
    assert subkingdom is not None and subkingdom.landscapes == ["cave_dwellers"]
    assert "Allies" in kingdom.expansions
    assert "Cave Dwellers" in kingdom.get_dombot_csv_string()


def test_divine_wind_piles_count_for_the_expansions():
    """They're needed to set up the game (M19, step 11): Vassal (Base) is only
    among the Divine Wind piles."""
    kingdom = rk.Kingdom.from_dombot_csv_string(_DIVINE_WIND_WITH_BANE)
    without_piles = _DIVINE_WIND_WITH_BANE.split(", divine_wind")[0]
    assert "Base, 2E" not in rk.Kingdom.from_dombot_csv_string(without_piles).expansions
    assert "Base, 2E" in kingdom.expansions


def test_divine_wind_subkingdom_is_shared_and_left_unchanged():
    """It's parsed once per string and shared (M19, step 10), so the validity check
    mustn't filter the sub-kingdom's reasons in place, as it did before."""
    from random_kingdominion.kingdom.invalidity_stuff import InvalidityReason

    # Poet is an Omen, and Divine Wind, the Prophecy, is gone once its piles join
    dombot_str = _DIVINE_WIND_WITH_BANE.replace("aristocrat", "poet")
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    subkingdom = kingdom.divine_wind_subkingdom
    other = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert subkingdom is not None and subkingdom is other.divine_wind_subkingdom
    assert kingdom.is_valid, kingdom.invalidity_reasons
    assert InvalidityReason.check_kingdom_validity(kingdom) == []
    assert _reason_keys(subkingdom) == {"omen_but_no_prophecy"}


def test_colony_as_a_campaign_effect_target():
    """The Colony/Platinum spellings are only normalized in standalone entries."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "grotto, catapult, clashes, stockpile, blockade, clerk, patrol, rice_broker, "
        "sculptor, forge, way_of_the_butterfly, ritual, colonies, "
        "start_double_pile(province), start_double_pile(colony)"
    )
    assert kingdom.use_colonies
    assert kingdom.notes == ""
    assert kingdom.effect_targets == {"double_pile": ["colony", "province"]}


def test_dombot_parsing_docstring_examples():
    import doctest

    from random_kingdominion.kingdom import dombot_parsing

    assert doctest.testmod(dombot_parsing).failed == 0


def _entry_tree(entries) -> list:
    """Tokenized entries as names, or (name, arguments) if they have any."""
    return [(e.name, _entry_tree(e.args)) if e.args else e.name for e in entries]


_UNCLOSED = ["Closed 1 '(' at the end of the entry."]
_UNOPENED = ["Ignored 1 ')' without a '('."]


@pytest.mark.parametrize(
    "dombot_str, tree, notes",
    [
        ("village, smithy", ["village", "smithy"], []),
        (" village ,, smithy , ", ["village", "smithy"], []),
        (
            "druid(the_earths_gift, the_flames_gift, the_swamps_gift), moat",
            [
                ("druid", ["the_earths_gift", "the_flames_gift", "the_swamps_gift"]),
                "moat",
            ],
            [],
        ),
        (
            "nearby(druid(the_earths_gift, the_flames_gift)), druid",
            [("nearby", [("druid", ["the_earths_gift", "the_flames_gift"])]), "druid"],
            [],
        ),
        ("a(b(c(d)), e)", [("a", [("b", [("c", ["d"])]), "e"])], []),
        ("young_witch(), moat", ["young_witch", "moat"], []),
        # Broken input: an unclosed "(" ends with its entry, a stray ")" is dropped
        ("village, smithy(, market", ["village", "smithy", "market"], _UNCLOSED),
        ("young_witch(moat, smithy", [("young_witch", ["moat"]), "smithy"], _UNCLOSED),
        ("a(b(c), d, e", [("a", [("b", ["c"])]), "d", "e"], _UNCLOSED),
        (
            "smithy(, market(moat",
            ["smithy", ("market", ["moat"])],
            ["Closed 2 '(' at the end of the entry."],
        ),
        ("village, smithy), market", ["village", "smithy", "market"], _UNOPENED),
        ("smithy(moat)), market", [("smithy", ["moat"]), "market"], _UNOPENED),
        (
            "young_witch(moat) extra, market",
            [("young_witch", ["moat"]), "market"],
            ["Ignored 'extra' after 'young_witch(moat)'."],
        ),
    ],
)
def test_tokenize_dombot_string(dombot_str: str, tree: list, notes: list[str]):
    from random_kingdominion.kingdom.dombot_parsing import tokenize_dombot_string

    entries, actual_notes = tokenize_dombot_string(dombot_str)
    assert _entry_tree(entries) == tree
    assert actual_notes == notes


def test_normalized_colon_syntax_and_separators():
    from random_kingdominion.kingdom.dombot_parsing import (
        normalize_dombot_string,
        tokenize_dombot_string,
    )

    normalized = normalize_dombot_string(
        "Black Cat, Way_of_the_Mouse:Menagerie, Conquest -m NoColonies; NoShelters"
    )
    assert _entry_tree(tokenize_dombot_string(normalized)[0]) == [
        "black cat",
        ("way_of_the_mouse", ["menagerie"]),
        "conquest",
        "nocolonies",
        "noshelters",
    ]


def test_nested_special_targets():
    """A target resolves its own targets without becoming a pile itself (M19); for
    a nested Bane, see `test_young_witch_as_ferryman_pile_in_dombot_strings`."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "nearby(druid(the_earths_gift, the_flames_gift, the_swamps_gift)), village, "
        "smithy, militia, market, mine, witch, festival, library, moat"
    )
    assert kingdom.notes == ""
    assert kingdom.traits == [["nearby", "druid"]]
    assert kingdom.druid_boons == [
        "the_earths_gift",
        "the_flames_gift",
        "the_swamps_gift",
    ]
    assert "druid" in kingdom.cards  # As a Trait's target
    assert kingdom.is_valid, kingdom.invalidity_reasons


def test_nested_targets_carry_their_specials_once():
    """Young Witch isn't printed on its own, so its Bane goes with Ferryman's pile,
    but not a second time with an effect on it (M19, step 7)."""
    dombot_str = _FERRYMAN_ON_YOUNG_WITCH + " -x start_in_play(young_witch)"
    printed = rk.Kingdom.from_dombot_csv_string(dombot_str).get_dombot_csv_string()
    assert "Ferryman (Young Witch (Black Cat))" in printed
    assert printed.endswith(" -x start_in_play(young_witch)")
    _test_dombot_readin_readout(dombot_str)


def test_specials_inside_typhoon_are_ignored():
    """Typhoon's piles join later, like Divine Wind's, so their specials don't apply
    to the kingdom (campaign Rising Sun 5; M19, step 9)."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "mountain_shrine, snake_witch, aristocrat, council_room, gold_mine, kitsune, "
        "mine, ronin, artisan, samurai, good_harvest, credit, twist_typhoon(harbinger, "
        "alley, riverboat(imperial_envoy), village)"
    )
    assert kingdom.notes == (
        "Specials inside Typhoon aren't supported yet, ignored the targets of: "
        "riverboat(imperial_envoy).\n"
    )
    assert kingdom.riverboat_card == ""
    assert kingdom.effect_targets["typhoon"] == [
        "alley",
        "harbinger",
        "riverboat",
        "village",
    ]
    assert kingdom.is_valid, kingdom.invalidity_reasons


def test_ignored_and_unknown_targets_get_notes():
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "village(smithy), young_witch(moat, cellar), young_witch(harbinger), "
        "ferryman(not_a_card), obelisk(village)"
    )
    assert kingdom.bane_pile == "moat"  # The first one counts
    assert kingdom.ferryman_pile == ""
    assert kingdom.obelisk_pile == "village"
    assert kingdom.notes == (
        "The following inputs could not be associated with any known CSOs: "
        "'not_a_card'\n"
        "The following targets were ignored, as their CSO takes none or only one: "
        "'village(smithy)', 'young_witch(cellar)', 'young_witch(harbinger)'\n"
    )
    # Repeating the same target is a duplicate, not an ignored target
    kingdom = rk.Kingdom.from_dombot_csv_string("young_witch(moat), young_witch(moat)")
    assert kingdom.notes == "Duplicates: {'young_witch(moat)': 2}\n"


def test_unrecognized_inputs_are_noted_in_input_order():
    kingdom = rk.Kingdom.from_dombot_csv_string("village, zzz, smithy, foo, aaa, foo")
    assert kingdom.notes.startswith(
        "The following inputs could not be associated with any known CSOs: "
        "'zzz', 'foo', 'aaa'\n"
    )


@pytest.mark.parametrize("effect", ["add_card", "in_play", "tavern"])
def test_effects_on_specific_cards_keep_the_card(effect: str):
    """Like the replacements of starting cards, these target a specific card (Lich),
    not its split pile (Wizards), which doesn't become a pile either (M19)."""
    kingdom = rk.Kingdom.from_dombot_csv_string(
        f"village, smithy, militia, moat, market, mine, witch, festival, library, "
        f"laboratory -x start_{effect}(lich)"
    )
    assert kingdom.notes == ""
    assert kingdom.effect_targets == {effect: ["lich"]}
    assert "wizards" not in kingdom.cards and "lich" not in kingdom.cards
    _test_dombot_readin_readout(f"village, smithy -x start_{effect}(lich)")
