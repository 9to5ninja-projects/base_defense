# Changelog

All notable changes to this project will be documented in this file.

## [0.2.17] - 2025-11-25

### Added
- **System & Meta**:
  - **Main Menu**: Added a start screen with "New Game", "Load Game", and "Quit" options.
  - **Save/Load System**: Implemented full game state persistence using `pickle`. Games can be saved and loaded from the `saves/` directory.
  - **Pause Menu**: Added an in-game pause menu (ESC) with options to Resume, Save, Return to Main Menu, or Quit.
  - **State Machine**: Refactored the game loop to support distinct states (MAIN_MENU, PLAYING, PAUSED).

## [0.2.16] - 2025-11-25

### Added
- **Boss Waves**:
  - **Wave 10 Boss**: Implemented the "Giant Kamikaze" boss which spawns as the final enemy of every 10th wave.
  - **Boss Stats**:
    - **HP**: 2000 (Scales with Boss Tier/Wave).
    - **Speed**: Very slow (15 px/s).
    - **Size**: Massive (3x normal radius).
    - **Damage**: 1000 (Instantly destroys most buildings).
    - **Blast Radius**: 200 (Catastrophic area of effect).
  - **Visuals**: Boss renders as a large Dark Violet circle with a thicker HP bar.

### Fixed
- **Turret Progression**:
  - **Upgrade Cost**: Fixed a bug where Turrets had an upgrade cost of 0, preventing them from leveling up. Set base upgrade cost to 60.
  - **Upgrade Calculation**: Fixed a bug where the player was charged the *next* level's upgrade cost instead of the current level's cost when upgrading a building.
- **UI/UX**:
  - **Upgrade Preview**: The HUD now displays detailed stat changes (Damage, Range, Capacity) when previewing an upgrade.

## [0.2.15] - 2025-11-24

### Added
- **Boss Waves**:
  - **Wave 10 Boss**: Implemented the "Giant Kamikaze" boss which spawns as the final enemy of every 10th wave.
  - **Boss Stats**:
    - **HP**: 2000 (Scales with Boss Tier/Wave).
    - **Speed**: Very slow (15 px/s).
    - **Size**: Massive (3x normal radius).
    - **Damage**: 1000 (Instantly destroys most buildings).
    - **Blast Radius**: 200 (Catastrophic area of effect).
  - **Visuals**: Boss renders as a large Dark Violet circle with a thicker HP bar.

## [0.2.14] - 2025-11-24

### Added
- **Turret Progression**:
  - **Tiered Stats**: Implemented distinct stat progression for the Basic Turret across its 3 tiers (Levels 1-9).
    - **Tier 1 (Lvl 1-3)**: Standard scaling.
    - **Tier 2 (Lvl 4-6)**: **High Velocity**. Significant jump in Range (450+) and Damage (25+).
    - **Tier 3 (Lvl 7-9)**: **Heavy Caliber**. Massive jump in Damage (50+) and Range (600+).

## [0.2.13] - 2025-11-24

### Fixed
- **Visual Sync**:
  - **Grid Alignment**: Fixed a critical desync between the logical grid position and the visual grid position. The logic assumed the grid started at X=50, while the renderer drew it at X=10 (centered). This caused enemies approaching from the right to hit buildings ~40 pixels (1 cell) before visually touching them.
  - **Constants**: Centralized layout constants (`GRID_START_X`, `UI_WIDTH`, `MAX_COLS`) in `core_data.py` to ensure logic and rendering always agree.

## [0.2.12] - 2025-11-24

### Fixed
- **Ground Combat**:
  - **Collision Physics**: Refined Ground Invader collision detection to use explicit edge-to-edge checking (AABB) rather than center-point checking. Invaders now reliably explode when their leading edge touches a building's wall, preventing them from clipping inside before detonating.

## [0.2.11] - 2025-11-24

### Fixed
- **Retry Logic**:
  - **State Restoration**: The "Retry Wave" feature now correctly restores the game state to the **beginning of the Build Phase** (before any buildings were placed or credits spent for that wave), rather than the start of the Combat Phase. This allows players to rethink their strategy completely upon failure.
- **Ground Combat**:
  - **Collision Detection**: Ground Invaders now physically collide with buildings they run into, exploding on contact with the building's side walls. Previously, they would only explode if they reached the center point of their target.
- **UI/UX**:
  - **Game Over**: Fixed a bug where the "CRITICAL FAILURE" message would spam continuously on the Game Over screen.

## [0.2.10] - 2025-11-24

### Fixed
- **Collision Physics**:
  - **Hitbox Improvements**: Completely rewrote enemy collision detection to use a raycast-based system. This prevents fast-moving enemies from "tunneling" through buildings without exploding.
  - **Blast Radius**: Increased the effective blast radius of Kamikaze enemies to match their visual impact (approx 50-100 range).
  - **Collision Consistency**: Enemies now reliably explode upon touching any part of a building's footprint, including the top and sides.

## [0.2.9] - 2025-11-24

### Added
- **Economy & Balance**:
  - **Manual Repair**: Removed auto-repair at the end of waves. Players must now manually repair damaged buildings using the **'R'** key.
  - **Repair Cost**: Repairing costs **1 Credit per HP**. Partial repairs are allowed if credits are insufficient.
  - **Repair Bill**: End-of-wave rewards no longer deduct repair costs automatically.
  - **Unit Production Costs**: Barracks now consume **1 Credit** for every Defender spawned.
- **UI/UX**:
  - **Repair Feedback**: Added a "No building selected" message when attempting to repair an empty cell.
  - **Game Over**: Fixed an issue where the "Wave Complete" popup would appear behind the "Game Over" screen if the last enemy died simultaneously with the base destruction.
  - **Retry Wave**: Added a **"Retry Wave" (T)** option to the Game Over screen, allowing players to restart the current wave from the last build phase instead of resetting the entire game.
  - **Spawn Variance**: Enemies can now spawn slightly outside the unlocked grid area (+/- 2 columns), increasing the threat to edge buildings.
  - **Ammo Range**: Implemented projectile lifetime/range physics. Basic Turrets have an effective ammo range of **600**.
- **HUD Improvements**:
  - **Detailed Stats**: The HUD now displays **Turret Damage**, **Turret Range**, and **Barracks Capacity** when a building is selected.
  - **Shield Regen**: Added Shield Regeneration Rate (per second) to the Economy stats panel.
  - **Range Indicators**: Selecting a Turret in Build Mode now draws a red circle indicating its attack range.
  - **Custom Cursor**: Added a custom crosshair cursor for better visibility.
- **Combat Logic**:
  - **Barracks Capacity**: Implemented a global capacity check for Defenders. Barracks will stop spawning units if the total number of active Defenders exceeds the total capacity of all Barracks.

### Changed
- **Balance**:
  - **Turret Stats**: Basic Turret range set to **300** (Targeting) and **450** (Ammo). Ammo range now scales at 1.5x the targeting range.
  - **Turret Nerf**: Reduced basic Turret damage to **10** (was 25).
  - **Upgrade Costs**: Building upgrade costs now scale with level, making high-tier buildings significantly more expensive.
- **Building Logic**:
  - **Power Plants**: Can now only be placed on Ground or other Power Plants (fixed bug allowing placement on Turrets).
  - **Move Validation**: Fixed a bug where picking up a building that supports others would trap the player in the moving state. Added checks to prevent moving supporting structures and allowed placing back in the same spot as a cancel action.
- **UI/UX**:
  - **Range Indicators**: Selecting a Turret now displays two range circles: **Blue** for Targeting Range and **Red** for Effective Ammo Range.
  - **HUD**: Added "Ammo Rng" to the Turret stats panel.
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
