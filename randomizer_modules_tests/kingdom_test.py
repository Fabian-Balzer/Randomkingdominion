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


# Daily 2024-03-20
_FERRYMAN_ON_YOUNG_WITCH = (
    "barge, bounty_hunter, camel_train, cavalry, ferryman(young_witch), hamlet, "
    "horn_of_plenty, remake, sleigh, stockpile, bane(black_cat)"
)


def test_young_witch_as_ferryman_pile_in_dombot_strings():
    kingdom = rk.Kingdom.from_dombot_csv_string(_FERRYMAN_ON_YOUNG_WITCH)
    assert kingdom.ferryman_pile == "young_witch"
    assert kingdom.bane_pile == "black_cat"
    assert "black_cat" in kingdom.cards and "young_witch" not in kingdom.cards
    assert kingdom.is_valid, kingdom.invalidity_reasons
    # The Bane can't be printed with Young Witch, which isn't in the cards
    assert "Bane (Black Cat)" in kingdom.get_dombot_csv_string()
    _test_dombot_readin_readout(_FERRYMAN_ON_YOUNG_WITCH)

    without_bane = _FERRYMAN_ON_YOUNG_WITCH.replace(", bane(black_cat)", "")
    kingdom = rk.Kingdom.from_dombot_csv_string(without_bane)
    assert _reason_keys(kingdom) == {"young_witch_but_no_bane"}


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


def _reason_keys(kingdom: rk.Kingdom) -> set[str]:
    return {reason.key for reason in kingdom.invalidity_reasons}


def test_same_trait_on_two_cards():
    """Only allowed in campaigns (M24), but parsed either way."""
    kingdom = rk.Kingdom.from_dombot_csv_string(_NEARBY_ON_TWO_CARDS)
    assert kingdom.traits == [["nearby", "engineer"], ["nearby", "imperial_envoy"]]
    assert kingdom.trait_targets == {"nearby": ["engineer", "imperial_envoy"]}
    assert kingdom.get_traits_on("engineer") == ["nearby"]
    _test_dombot_readin_readout(_NEARBY_ON_TWO_CARDS)


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
    assert (deck.count("copper"), deck.count("silver"), deck.count("estate")) == (4, 2, 4)
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


def test_campaign_effect_aliases():
    """TGG calls the Free Stamp 'cost_zero' (Daily 2025-08-17)."""
    assert rk.sanitize_cso_name("stamp_cost_zero") == "free"
    assert rk.sanitize_cso_name("harem") == "farm"
    kingdom = rk.Kingdom.from_dombot_csv_string(
        "monastery, sleigh, watchtower, sailor, wandering_minstrel, crypt, ronin, "
        "farmland, nobles, wayfarer, seize_the_day, stamp_cost_zero(seize_the_day)"
    )
    assert kingdom.notes == ""
    assert kingdom.effect_targets == {"free": ["seize_the_day"]}


def test_divine_wind_survives_printing_and_parsing():
    """The Divine Wind CSOs are stored as sorted keys, however they were entered
    (specials inside them aren't supported yet, M19)."""
    dombot_str = (
        "mountain_shrine, daimyo, dungeon, infirmary, poet, transmogrify, baker, "
        "footpad, lost_city, samurai, training, amass, divine_wind(Distant Lands, "
        "page, miser, stonemason, snake_witch, journeyman, magpie, wine_merchant, "
        "guide, aristocrat)"
    )
    kingdom = rk.Kingdom.from_dombot_csv_string(dombot_str)
    assert kingdom.divine_wind_cso_str.startswith("aristocrat, distant_lands, guide")
    _test_dombot_readin_readout(dombot_str)


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
