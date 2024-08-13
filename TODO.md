# TODOS

Things and ideas I am having to improve

## General

### Backend and implementation stuff

- Refactor widget infrastructure (reorder everything for a nicer structure -> Only Buttons left)
- Write Tests

### Randomizer options

- Add options to distribute the cost
- Add options to take card mechanics
- Add options to disable attacks or require reaction or other quirky things

### UI

- Add capability to manipulate name, notes etc. for a given kingdom in the UI
- Add sorting options for kingdom (Cost as default, but also Card Name and Expansion?)
- Improve the kingdom overview
- Implement showing the whole kingdom to set up (e.g. Wishes, Boons, Loot, Ruins)
- Add possibility of clicking on a single card/landscape to get full screen view
- Save the UI state in config (for collapsible views)

### Card metadata

- Fix debt cost
- Add Associated Cards (Horses, Knights, Castles, Potion etc.)
- Add DecisionQuality (high for many decisions, low for i.e. Necro or Gardens)

### Misc


## Finished :party:!

DONE Fix DomBot print command (split piles don't work, banes don't work etc)
DONE Cards lists:
  DONE Introduce Ban lists
  DONE Introduce Required Cards lists
  DONE Introduce disliked/liked cards?
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
DONE Add ThinningType (All, Treasure, NoTreasure, Action)?
DONE Implement showing the number of cards in a setup pile
DONE options to disable a quality to exclude it from randomization
DONE options to prioritize an expansion or to choose a subset of expansions  --> Choose max number of expansions possible
DONE ~~Refactored~~ Removed Data_Container ~~with get and set methods~~ and built randomizer class
DONE Fix Harem/Farm picture: Removed Harem completely
DONE Implement 'Revert to recommended settings' --> The select all/deselect all buttons should be enough.
DONE Implement permanent kingdom history of the last 100 kindoms and allow to save kingdoms even more permanently
DONE Implement loading kingdoms from and saving to ~~csv~~ yaml
DONE Show kingdom strength from general availability of engine components (is possible with the bars)
DONE Add options to have random numbers of landscapes
DONE Implement picking Trait, Obelisk, Mouse and Bane Cards
DONE Show expansions used for a kingdom separately
DONE fix sorting of debt/potion cost cards
DONE Refactor how the randomizer picks cards depending on the attributes given
DONE Make rerolling single csos possible again
DONE Implement Shortened Kingdom View (i.e. only name, picture and cost)
