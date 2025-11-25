# Design Document: Ground War Expansion

## Overview
This expansion introduces a new layer of combat: **Ground Warfare**. Enemies that bypass the shield and land on the ground will now spawn ground units that attack buildings from the base. Players must build **Barracks** to produce **Defenders** to counter this threat.

## Core Mechanics

### 1. Ground Invasion
- **Trigger**: When a "Kamikaze" enemy hits the ground (Y >= GROUND_Y) without hitting a building.
- **Effect**: Instead of disappearing harmlessly, the enemy spawns a **Ground Invader**.
- **Invader Behavior**:
  - Moves horizontally towards the nearest building.
  - Attacks the building at its base (Ground Level).
  - Can move "in front" of other buildings (visual layering).

### 2. Player Defense: The Barracks
- **New Building**: `Barracks`
- **Function**: Automatically produces **Defenders** (Ground Units).
- **Production**:
  - Spawns 1 Defender every X seconds (based on level).
  - Max Defender count capped by Barracks level.
  - Cost: Defenders may cost credits to spawn, or be free but limited by cap.
- **Defender Behavior**:
  - Patrols the ground level.
  - Automatically engages nearby Ground Invaders.
  - "Mini-Ant Battle": Defenders and Invaders fight in a separate layer overlaying the building grid.

### 3. Grid Expansion
- **Width Increase**:
  - Max Columns: Increased from 16 to **32**.
  - Starting Unlocked Columns: Increased from 8 to **16**.
- **Impact**:
  - Allows for much wider bases.
  - Increases the travel time for ground units.
  - Requires more strategic placement of Barracks to cover the wider area.

### 4. Combat Layering
- **Aerial Layer**: Existing combat (Kamikazes, Projectiles, Turrets).
- **Ground Layer**: New combat (Invaders vs Defenders).
- **Interaction**:
  - Turrets do **NOT** target ground units (initially).
  - Ground units attack Building HP directly.

## Implementation Plan

### Phase 1: Grid & Engine Updates
- [ ] Update `CityGrid` to support 32 columns.
- [ ] Adjust camera/rendering to handle the wider aspect ratio (or implement scrolling if needed, though scaling is preferred for now).
- [ ] Update `GameState` to track Ground Units.

### Phase 2: Ground Units
- [ ] Create `GroundUnit` class (x, y, hp, damage, team).
- [ ] Implement "Spawn on Ground Hit" logic in `CombatManager`.
- [ ] Implement Ground Unit movement and collision logic.

### Phase 3: Barracks & Defenders
- [ ] Add `BARRACKS` to `BuildingType`.
- [ ] Implement Barracks production logic in `GameState`.
- [ ] Implement Defender AI (seek and destroy invaders).

### Phase 4: UI & Polish
- [ ] Add Barracks to Build Menu.
- [ ] Render Ground Units (small sprites/shapes at bottom of screen).
- [ ] Balance costs and damage values.
