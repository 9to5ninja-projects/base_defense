# Project Roadmap & Todo

## Phase 1: Core Mechanics (Completed v0.2.0)
- [x] Cell-based grid system
- [x] Multi-cell building footprints
- [x] Foundation support logic
- [x] Basic Economy (Energy/Credits)
- [x] Basic Combat (Waves, Projectiles, Shield)
- [x] Basic UI (Grid, HUD, Build Menu)

## Phase 2: Visuals & Feedback (Current Priority)
- [ ] **Building Sprites**: Replace colored rectangles with sprite-based rendering.
    - [ ] Power Plants: Implement visuals that reflect the 1x1 -> 2x2 -> 3x3 growth.
    - [ ] Datacenters/Capacitors: Implement "stacking" visuals (server racks, battery cells).
    - [ ] Turrets: Add rotating barrels or distinct bases.
- [ ] **Combat FX**:
    - [ ] Explosion particles when enemies/buildings die.
    - [ ] Shield impact ripples or flashes.
    - [ ] Projectile trails.
- [ ] **UI Polish**:
    - [ ] Better "Invalid Placement" feedback (red highlight on grid cells).
    - [ ] Range indicators for Turrets when hovering.

## Phase 3: Gameplay Depth
- [ ] **Enemy Variety**:
    - [ ] "Shooter" enemies that fire from range.
    - [ ] "Tank" enemies with high HP but slow speed.
- [ ] **Building Tiers**:
    - [ ] Implement Tier 2 and Tier 3 visuals/stats for all buildings.
- [ ] **Progression**:
    - [ ] Unlock new columns with credits.
    - [ ] Tech tree or upgrades between waves?

## Phase 4: Polish & Optimization
- [ ] **Save/Load System**: Persist game state.
- [ ] **Sound Effects**: BGM and SFX.
- [ ] **Performance**: Optimize collision detection if entity count grows large.
