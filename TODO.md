# Project Roadmap & Todo

## Phase 2: UI & Polish (Immediate Focus)
- [x] **HUD Improvements**:
    - [x] Display Turret Attack Damage when highlighting.
    - [x] Display Barracks Ground Troop Capacity when highlighting.
    - [x] Display Shield Regen/Sec in side panel stats.
    - [x] Hide cursor when in Combat Phase (only show in Build Phase).
    - [x] Range indicators for Turrets when hovering.
- [ ] **Visuals**:
    - [ ] Replace colored rectangles with sprite-based rendering.
    - [ ] Explosion particles and Shield impact effects.

## Phase 3: Economy & Balance
- [x] **Cost Scaling**:
    - [x] Implement scaling costs for building upgrades.
    - [x] Apply credit reduction for generated units (1cr per Ground Unit).
- [x] **Wave Mechanics**:
    - [x] **Repair Bill**: Manual repair system implemented.
    - [x] **Spawn Variance**: Enemies spawn slightly outside the city edges.
    - [x] **Retry Wave**: Added ability to retry the current wave.

## Phase 4: New Units & Mechanics
- [ ] **Drones**:
    - [ ] **Drone Factory**: New building with capacity/generation logic.
    - [ ] **Drone Unit**: Flying defender that moves within range X of nearest enemy.
    - [ ] **Stats**: Deals ~50% of basic turret damage.
- [ ] **Turret Branching**:
    - [ ] **Basic Tier Progression**: Establish distinct stats for Basic Turret Tiers 1-3.
    - [ ] Implement branching paths at Tier II:
        1.  **Basic+**: Increased Range & Rate of Fire.
        2.  **Direct Laser**: Continuous beam (High RoF, Lower per-tick damage).
        3.  **Homing Missile**: Slow projectile, high damage, blast radius.
- [x] **Boss Waves**:
    - [x] Implement Boss logic for every 10th wave.
    - [x] **Wave 10 Boss**: Giant Kamikaze (High HP, Slow, Large Blast Radius).

## Phase 5: System & Meta
- [ ] **Game Loop**:
    - [ ] **Main Menu**: Proper beginning interface.
    - [ ] **Save/Load**: Persist game progress.
- [ ] **Audio**:
    - [ ] Sound effects and Background music.
- [ ] **Refactoring**:
    - [ ] Modularize scripts (split `core_data.py` if needed) to keep codebase manageable.

## Completed
- [x] Cell-based grid system
- [x] Foundation support logic
- [x] Basic Economy & Combat
- [x] Ground War (Barracks, Invaders, Defenders)
- [x] Window Management (Fullscreen/Resize)
- [x] Message Log & Game Over Screen
- [x] Physics & Collision Fixes (Raycasting, AABB)
