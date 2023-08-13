# TODOS

Things and ideas I am having to improve 

## General

### Backend and implementation stuff

- Refactor Data_Container with get and set methods
- Refactor widget infrastructure (halfway done, see expansion widget)
- Refactor how the randomizer picks cards depending on the attributes given
- Implement 'Revert to recommended settings'
- Implement permanent kingdom history of the last 100 kindoms and allow to save kingdoms even more permanently
- Implemnt loading kingdoms from csv
- Show kingdom strength from general availability of engine components
- Write Tests

### Randomizer options

- Add options to prioritize an expansion or to choose a subset of expansions
- Add options to distribute the cost
- Add options to take other card metadata into account
- Add options to disable attacks or require reaction
- Implement picking Trait, Obelisk, Mouse and Bane Cards

### UI

- Add sorting options for kingdom (and fix sorting of debt/potion cost cards)
- Implement showing the whole kingdom to set up (e.g. Wishes, Boons, Loot)
- Implement Shortened Kingdom View (i.e. only name, picture and cost) with toggle between short and long
- Implement showing the number of cards in a setup pile
- Save the UI state in config (for collapsible views)

### Card metadata

- Fix debt cost
- Fix Harem/Farm picture
- Add TrashType (All, Treasure, NoTreasure, Action)?
- Add Associated Cards (Horses, Knights, Castles, Potion etc.)
- Add DecisionQuality (high for many decisions, low for i.e. Necro or Gardens)

### Misc

- Fix DomBot print command (split piles don't work)

## Finished :party:!

DONE Finish Refactoring Widgets
DONE Klick on single cards to exchange them
DONE Implement 'select all' button for expansions
DONE Add TrashingQuality
DONE Add VillageQuality (Normal Village has 5, up to 10)
DONE Add AltVPQuality
DONE Card Draw Quality for cards with plain draw
DONE GainQuality
DONE GainType (Buys, AllWithCost, Treasure, Action, Trash)
DONE CardAmount (i. e. 12 for ports, 46 for coppers etc.)
DONE Implement permanently stored data
