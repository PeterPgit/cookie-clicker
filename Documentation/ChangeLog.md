# Change Log

## December 8 (Sprint 4)

### Added

- Made it so all upgrade buttons dynamically show up according to their price **(Andrew)**
- Fixed event lock for gambling event **(Andrew)**
- Fixed display bug of upgrades prices **(Andrew)**
- Support for multiple save slots **(Jack)**
- Finished Prestige Menu **(Peter)**

### Modified

- Added control instructions to options menu **(Ian)**
- changed menu settings to toggle music and sfx independetly, got rid of Quit button **(Jack)**

## December 5 (Sprint 4)

### Added

- Prestige Menu and class methods **(Peter)**

### Modified

- Fixed bugs related to popup menus **(Peter)**

## December 1 (Sprint 4)

### Added

- Documentation for Sprint 4 **(Peter)**
- Background for the middle column so viewing upgrades text is easier **(Peter)**
- Starter code for the prestige mechanism **(Peter)**

## November 26 (Sprint 4)

### Added

- Cursor click animation **(Jack)**

### Modified

- changes to cursor.py to add animation **(Jack)**

## November 24 (Sprint 3)

### Added

- Balancing changes for Click Multiplier and Increase Click **(Andrew)**
- Dynamic buttons for Click Multiplier and Increase Click **(Andrew)**
- Added dates to the offline notification screen **(Peter)**
- Cookie Analytics **(Peter)**
- Item cost to shop display **(Peter)**
- Sprint 4 documentation **(Peter)**
- Cookie click animation **(Jack)**

## November 24 (Sprint 3)

### Added

- Balancing changes for Click Multiplier and Increase Click **(Andrew)**
- Dynamic buttons for Click Multiplier and Increase Click **(Andrew)**
- Added dates to the offline notification screen **(Peter)**
- Cookie Analytics **(Peter)**
- Item cost to shop display **(Peter)**
- Sprint 4 documentation **(Peter)**

## November 23 (Sprint 3)

### Added

- Achievements **(Andrew)**
- Pop-up for when achievements are completed **(Andrew)**
- Added Temple upgrade (Auto clicker) **(Ian)**
- Added Gambling event and popup (Risk all cookies for a 5x increase of cookies) **(Ian)**
- Added Cookie storm event and popup (2x clicks for 15 seconds) **(Ian)**
- Added Golden cookie event and popup (10x clicks for 10 seconds) **(Ian)**
- Number simplifier that generates latin suffix correlating to size **(Jack)**
- Added Temple upgrade (Auto clicker) **(Ian)**
- Added Gambling event and popup (Risk all cookies for a 5x increase of cookies) **(Ian)**
- Added Cookie storm event and popup (2x clicks for 15 seconds) **(Ian)**
- Added Golden cookie event and popup (10x clicks for 10 seconds) **(Ian)**

## November 22 (Sprint 3)

### Added

- Sprint 3 Documentation **(Peter)**
- Added Background to Main menu and in game **(Jack)**

## November 10 (Sprint 2)

### Added

- Added remaining sprites for upgrades **(Jack)**
- Implemented icons for upgrades **(Peter)**

### Removed

- Rectangle around clicking cookie **(Peter)**

### Modified

- Changed top left counter to be cookies per second instead of cookies per click (CPC is shown by just clicking the cookie) **(Peter)**

## November 10 (Sprint 2)

- Added popup menu **(Mikey)**
- Added ability to toggle sound in popup menu **(Mikey)**

### Modified

- Moved save game to popup menu **(Mikey)**
- changed font size and cleaned up UI element appearing where they should not **(Mikey)**
- Adjusted upgrades to make them more reasonable **(Mikey)**

## November 8 (Sprint 2)

### Added

- Total cookies and cookies per click are now displayed with 3 decimal places **(Andrew)**
- Implemented more cookies per click **(Andrew)**
- Added scrolling to the shop **(Andrew)**
- Added dynamic pricing and display to shop upgrades **(Ian)**

### Modified

- Fixed infinite upgrade bug by adding a lock and unlock for upgrades to prevent outpacing the cookie count calculator **(Ian)** 
- Fixed Cookies per click not tracking between saves **(Ian)**
- Fixed cookies per click upgrades not tracking between saves **(Ian)**

## November 7 (Sprint 2)

### Added

- Added sprites into main menu **(Jack)**

## November 6 (Sprint 2)

### Added

- Added new upgrades for auto clickers **(Peter)**
- Added new upgrades for click multipliers **(Andrew)**

### Modified

- Moved shop items to the shop class file **(Peter)**

## November 5 (Sprint 2)

### Added

- Added custom mouse cursor **(Jack)**
- Attempted to integrate button backgrounds, need to fix centering **(Peter)**

## November 4 (Sprint 2)

### Added

- Added offline production **(Peter)**
- Added sprite assets **(Jack)**

## November 3 (Sprint 2)

### Added

- Added sounds **(Mikey)**
- Sprint 2 documentation

## October 27 (Sprint 1)

### Added

- load_game code to populate upgrades_acquired list so that the upgrades are shown after loading a save **(Jack)**
- Documentation for all of the game's files and functions **(Peter)**

### Modified

- handle_shop_click to check if an item is already in upgrades acquired to avoid filling the UI with duplicate upgrades **(Jack)**
- draw_upgrades to display cpc or cps depending on the item **(Jack)**
- Fixed bug when displaying purchased items of a loaded save file **(Peter)**
- Fixed bug when trying to load a save file which doesn't exist **(Peter)**

## October 26 (Sprint 1)

### Added

- Code for showing cookies obtained per click (needs bugfixing to have text last for more than 1 cycle) **(Peter)**
- Limited game to 20 ticks per second to prevent overutilization of resources **(Peter)**
- Cookies per click upgrade **(Peter)**
- Save game functionality **(Peter)**
- Load game functionality **(Peter)**

### Modified

- Changed format of the directory to provide better readability and segmentation of code **(Peter)**
- Split code into multiple files **(Peter)**

## October 24 (Sprint 1)

### Added

- Starter code for Cookie Clicker Implementation **(Ian)**
- Files and folders for documentation for Sprint 1 **(Andrew)**
        \+ Documentation Folder
        \+ Change Log Files
        \+ Person Hours Record Sheet
        \+ Sprint 1 Requirements File
