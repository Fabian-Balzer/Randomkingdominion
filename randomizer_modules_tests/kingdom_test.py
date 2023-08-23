from random_kingdominion.kingdom import Kingdom


def test_kingdom_readout_and_printout_compatability():
    """Test whether kingdoms are properly read and written via some example kingdoms."""
    example_1 = "Archive, Druid (The Earth's Gift, The Field's Gift, The Sun's Gift), Inherited (Sanctuary), Investment, Lighthouse, Mining Village, No Colonies, No Shelters, Obelisk (Cargo Ship), Sanctuary, Sentry, Taxman, Villa, Cargo Ship"
    example_2 = "Banish, Cage, Coin of the Realm, Figurine, Governor, Merchant Camp, No Colonies, No Shelters, Prosper, Quartermaster, Secluded Shrine, Sheepdog, Torturer, Young Witch (Improve)"
    example_3 = "Beggar, Border Village, Colonies, Harbinger, Hireling, Knights, Masterpiece, Mountain Pass, No Shelters, Nobles, Stowaway, Tools, Way of the Owl, Wine Merchant"
    example_4 = "Architects' Guild, Camel Train, Cartographer, Druid (The Field's Gift, The Flame's Gift, The Wind's Gift), Emissary, Encampment, Fortress, Gladiator, Hostelry, Mirror, No Colonies, Shelters, Tournament, Villain"
    example_5 = "Black Cat, Conquest, Crucible, Enchantress, Gladiator, Gondola, Longship, Moneylender, No Colonies, No Shelters, Pooka, Treasure Map, Vassal, Way of the Mouse (Menagerie)"
    example_6 = "black_cat, enchantress, gladiator, vassal, crucible, gondola, moneylender, treasure_map, longship, pooka, way_of_the_mouse:menagerie, conquest -m NoColonies, NoShelters"

    for example in [example_1, example_2, example_3, example_4, example_5, example_6]:
        kingdom = Kingdom.from_dombot_csv_string(example)
        redone = Kingdom.from_dombot_csv_string(kingdom.get_dombot_csv_string())
        assert kingdom == redone
