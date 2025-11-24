# Changelog

All notable changes to this project will be documented in this file.

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
