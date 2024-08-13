import numpy as np

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
    assert "inherited" in kingdom.trait_dict
    target = kingdom.trait_dict["inherited"]
    assert target in kingdom.cards
    # Test rerolling target
    new_kingdom = randomizer.reroll_single_cso(kingdom, target)
    assert new_kingdom.trait_dict["inherited"] != target
    assert target not in new_kingdom.cards
    # Test rerolling the trait itself
    new_kingdom = randomizer.reroll_single_cso(kingdom, "inherited")
    assert "inherited" not in new_kingdom.landscapes
    assert "inherited" not in new_kingdom.trait_dict


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
    ), "Ally has not been chosen correctly"
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
