# Changelog

All notable changes to this project will be documented in this file.

## [0.2.9] - 2025-11-24

### Added
- **HUD Improvements**:
  - **Detailed Stats**: The HUD now displays **Turret Damage**, **Turret Range**, and **Barracks Capacity** when a building is selected.
  - **Shield Regen**: Added Shield Regeneration Rate (per second) to the Economy stats panel.
  - **Range Indicators**: Selecting a Turret in Build Mode now draws a red circle indicating its attack range.
- **Combat Logic**:
  - **Barracks Capacity**: Implemented a global capacity check for Defenders. Barracks will stop spawning units if the total number of active Defenders exceeds the total capacity of all Barracks.

### Changed
- **UI/UX**:
  - **Cursor Visibility**: The grid selection cursor is now hidden during the Combat Phase to reduce visual clutter.

## [0.2.8] - 2025-11-24

### Fixed
- **Wave Completion**: Fixed a bug where the wave would not end if friendly Defenders were still alive. The wave now correctly ends when all Aerial Enemies and Ground Invaders are defeated.
- **Collision Detection**: 
  - Fixed aerial enemy collision logic to check the full width of the enemy against buildings, ensuring wide enemies don't "miss" buildings by having their center point in an empty column.

## [0.2.7] - 2025-11-24

### Changed
- **Combat Logic**:
  - **Collision Detection**: Improved ground collision logic. Enemies now check for building overlap using their full width/radius when hitting the ground, fixing an issue where enemies would miss narrow buildings (like Barracks) and spawn invaders instead of dealing damage.
- **UI/UX**:
  - **Combat HUD**: Expanded the Combat Status panel to show detailed counts for **Aerial Enemies**, **Ground Invaders**, and **Defenders**.

## [0.2.6] - 2025-11-24

### Added
- **Grid Expansion**:
  - Doubled the grid width to **32 columns** (16 unlocked by default) to accommodate wider bases and ground combat.
  - Adjusted rendering to fit the wider grid within the window.
- **Ground War Mechanics**:
  - **Ground Invasion**: Kamikaze enemies that hit the ground now spawn **2 Ground Invaders**.
  - **Invader Behavior**: Invaders move towards the nearest building or defender and **self-destruct** on contact, dealing massive damage.
  - **Barracks**: New building type that automatically spawns **Defenders** (Ground Units) if energy is positive.
  - **Defenders**: Friendly ground units that patrol and engage invaders to protect the base.
- **UI/UX**:
  - Added Barracks to the Build Menu.
  - Added rendering for Ground Units (Red for Invaders, Blue for Defenders).

## [0.2.5] - 2025-11-24

### Added
- **Game Loop**:
  - **Game Over Screen**: Added a proper Game Over state when all buildings are destroyed, allowing the player to restart (Press 'R').
- **Combat Mechanics**:
  - **Shield Collapse**: If the shield HP reaches 0, it now goes "Offline". Enemies pass through it without taking damage.
  - **Shield Reboot**: An offline shield will automatically reboot once it regenerates to 25% of its max HP.

## [0.2.4] - 2025-11-24

### Added
- **Window Management**:
  - Added support for **Fullscreen** (F11) and **Window Resizing**. The game now scales the internal resolution to fit the window.
- **UI/UX**:
  - **Combat Log**: Added a persistent message log at the bottom of the screen to track damage events and game notifications.
  - **Layout**: Adjusted the game layout to provide more vertical space for enemy descent and a dedicated area for the log.

### Changed
- **Combat Balance**:
  - **Enemy Spawning**: Enemies now spawn higher off-screen, giving players more time to react and turrets more time to engage.
  - **Shield Position**: Lowered the shield slightly to increase the playable combat area.
- **Logging**:
  - Damage events (Enemy vs Shield, Turret vs Enemy) are now logged to the new combat log.

## [0.2.3] - 2025-11-24

### Added
- **Economy**:
  - **Energy Bonus**: Finishing a wave with positive Net Energy now rewards 1 Credit per energy unit.
- **UI/UX**:
  - **Wave Complete Popup**: A detailed summary screen now appears after each wave, showing Base Reward, Perfect Wave Bonus, and Energy Bonus.
  - **Safety Warnings**: Added confirmation warnings when building or starting a wave would result in negative energy.

## [0.2.2] - 2025-11-24

### Changed
- **Building Logic**:
  - **Datacenters**: Now grow horizontally (1x1 -> 2x1 -> 3x1) instead of vertically. They no longer get taller with tiers.
  - **Movement**: Added a safety check preventing buildings from being moved if they are supporting other structures.
- **UI/UX**:
  - Added "Next Level" preview stats in the HUD when selecting a building.
  - Improved upgrade feedback messages.

## [0.2.1] - 2025-11-24

### Changed
- **Grid Layout**: 
  - Centered the grid on the screen.
  - Expanded internal grid capacity to 16 columns (currently 8 unlocked by default).
  - Visual improvements to the grid rendering (highlighting unlocked area).
- **UI/UX**:
  - Added an in-game **Message Log** system for better player feedback (e.g., "Not enough credits", "Wave Started").
  - Updated HUD controls text to include missing keys.
  - Added explicit error messages for the "Negative Energy" wave start prevention.
- **Bug Fixes**:
  - Fixed an issue where the game would fail to start a wave silently if energy was negative.

## [0.2.0] - 2025-11-24

### Changed
- **Core System Rewrite**: Transitioned from simple vertical stacks to a full cell-based grid system (`CityGrid`).
  - Buildings now have specific footprints (width x height).
  - Added foundation support logic (buildings must be supported by ground or other buildings).
  - Implemented cascading destruction physics.
- **Building Logic**:
  - Added `BuildingTemplate` for tier-based stats.
  - Power Plants now grow in size (1x1 -> 2x2 -> 3x3) as they tier up.
  - Datacenters and Capacitors grow vertically.
  - Added Upgrade system (`can_upgrade`, `upgrade_cost`).
- **Input & Controls**:
  - Changed from slot selection to cursor-based cell selection (Arrow Keys).
  - Added `U` key to upgrade buildings.
  - Added `Delete`/`Backspace` to destroy buildings.
  - Added `Space`/`Enter` to toggle Build Menu.
- **UI/HUD**:
  - Updated grid rendering to show individual cells.
  - HUD now displays detailed info for the selected cell (Building type, Level, HP, Foundation status).
  - Build Menu now checks placement validity and affordability in real-time.

## [0.1.0] - 2025-11-24

### Added
- **Project Structure**: Initialized repository with `src` folder and `run.py` entry point.
- **Core Data Models**: 
  - `BuildingType`, `BuildingStats`, `Building` classes.
  - `CityGrid` for managing stacked structures.
  - `GameState` for economy and wave tracking.
- **Rendering Engine (Pygame)**:
  - Basic window setup (1280x720).
  - Grid visualization with ground and slot dividers.
  - Building rendering with color coding and HP bars.
- **Economy System**:
  - Credits, Energy Production/Consumption, and Net Energy tracking.
  - Building costs and placement validation.
- **Combat System**:
  - `CombatManager` to handle waves and entities.
  - Enemy spawning logic (scaling difficulty).
  - Projectile physics and homing logic.
  - Turret auto-targeting.
  - Collision detection (Projectile->Enemy, Enemy->Shield, Enemy->Building).
- **Shield System**:
  - Shield HP derived from Datacenters.
  - Recharge rate derived from Capacitors.
  - Visual shield line.
- **UI/HUD**:
  - Build Menu overlay.
  - Real-time stats (Credits, Wave, Energy, Shield).
  - Keyboard controls (Arrows to move, 1-5 to build, W to start wave).

### Changed
- Updated `main.py` to use the new `CombatManager` for cleaner separation of concerns.
