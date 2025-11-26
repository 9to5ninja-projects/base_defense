from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set, Dict
from enum import Enum
import random
import math

class BuildingType(Enum):
    POWER_PLANT = "power_plant"
    DATACENTER = "datacenter"
    CAPACITOR = "capacitor"
    TURRET = "turret"
    DRONE_FACTORY = "drone_factory"
    BARRACKS = "barracks"

@dataclass
class BuildingTemplate:
    type: BuildingType
    level: int
    max_hp: int
    energy_production: int
    energy_consumption: int
    shield_hp_bonus: int
    shield_recharge_bonus: float
    cost: int
    upgrade_cost: int  # cost to level up
    damage: int = 0
    range: int = 0
    ammo_range: int = 0
    capacity: int = 0
    projectile_speed: int = 0
    cooldown: float = 1.0
    
    @property
    def tier(self) -> int:
        """Calculate tier from level"""
        if self.level <= 3:
            return 1
        elif self.level <= 6:
            return 2
        else:
            return 3
    
    @property
    def footprint(self) -> Tuple[int, int]:
        """Get width x height in cells based on type and tier"""
        if self.type == BuildingType.POWER_PLANT:
            if self.tier == 1:
                return (1, 1)
            elif self.tier == 2:
                return (2, 2)
            else:  # tier 3
                return (3, 3)
        
        elif self.type in [BuildingType.DATACENTER, BuildingType.CAPACITOR, BuildingType.BARRACKS]:
            # Datacenters grow horizontally now (Tier x 1)
            if self.type == BuildingType.DATACENTER:
                return (self.tier, 1)
            # Barracks also grow horizontally
            if self.type == BuildingType.BARRACKS:
                return (self.tier, 1)
            # Capacitors still grow vertically? Or should they match?
            # Keeping Capacitors vertical for now as requested only for Datacenter
            return (1, self.tier)
        
        else:  # Defense buildings
            return (1, 1)

# Building stat templates by type and level
def get_building_template(building_type: BuildingType, level: int) -> BuildingTemplate:
    """Generate building stats for given type and level"""
    
    base_stats = {
        BuildingType.POWER_PLANT: {
            'max_hp': 150,
            'energy_production': 15,
            'energy_consumption': 0,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 0,
            'cost': 50,
            'upgrade_cost': 40,
            'damage': 0,
            'range': 0,
            'capacity': 0,
        },
        BuildingType.DATACENTER: {
            'max_hp': 100,
            'energy_production': 0,
            'energy_consumption': 4,
            'shield_hp_bonus': 150,
            'shield_recharge_bonus': 0,
            'cost': 75,
            'upgrade_cost': 60,
            'damage': 0,
            'range': 0,
            'capacity': 0,
        },
        BuildingType.CAPACITOR: {
            'max_hp': 80,
            'energy_production': 0,
            'energy_consumption': 3,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 2.0,
            'cost': 60,
            'upgrade_cost': 50,
            'damage': 0,
            'range': 0,
            'capacity': 0,
        },
        BuildingType.TURRET: {
            'max_hp': 120,
            'energy_production': 0,
            'energy_consumption': 5,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 0,
            'cost': 80,
            'upgrade_cost': 60,
            'damage': 10,
            'range': 300,
            'ammo_range': 450,
            'capacity': 0,
            'cooldown': 1.0,
        },
        BuildingType.DRONE_FACTORY: {
            'max_hp': 130,
            'energy_production': 0,
            'energy_consumption': 8,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 0,
            'cost': 130,
            'upgrade_cost': 100,
            'damage': 8,
            'range': 200,
            'capacity': 2,
            'cooldown': 0.8,
        },
        BuildingType.BARRACKS: {
            'max_hp': 200,
            'energy_production': 0,
            'energy_consumption': 5,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 0,
            'cost': 100,
            'upgrade_cost': 80,
            'damage': 0,
            'range': 0,
            'capacity': 2,
        },
    }
    
    base = base_stats[building_type]
    
    # Scale stats by level
    scale = 1 + (level - 1) * 0.3  # 30% increase per level
    
    # Calculate range scaling
    calc_range = int(base['range'] * (1 + (level - 1) * 0.1))
    
    # Calculate ammo range scaling
    # Basic Turret: Ammo range is 1.5x targeting range (starts at 300/450)
    calc_ammo_range = base.get('ammo_range', 0)
    calc_speed = 0

    if building_type == BuildingType.TURRET:
        # Define explicit stats for Basic Turret Tiers
        # Tier 1 (Levels 1-3): Standard
        # Tier 2 (Levels 4-6): High Velocity (Range+)
        # Tier 3 (Levels 7-9): Heavy Caliber (Damage+)
        
        calc_speed = 300 + (level - 1) * 20

        tier = 1
        if level > 6: tier = 3
        elif level > 3: tier = 2
        
        if tier == 1:
            # Levels 1-3: Linear scaling
            # Lvl 1: 10 dmg, 300 rng
            # Lvl 2: 13 dmg, 330 rng
            # Lvl 3: 16 dmg, 360 rng
            pass # Use default scaling below
            
        elif tier == 2:
            # Levels 4-6: Range Boost
            # Base for Tier 2 (Level 4)
            # Lvl 4: 25 dmg, 450 rng
            base_dmg = 25
            base_rng = 450
            lvl_offset = level - 4
            
            return BuildingTemplate(
                type=building_type,
                level=level,
                max_hp=int(base['max_hp'] * scale),
                energy_production=0,
                energy_consumption=int(base['energy_consumption'] * scale),
                shield_hp_bonus=0,
                shield_recharge_bonus=0,
                cost=base['cost'],
                upgrade_cost=int(base['upgrade_cost'] * scale),
                damage=int(base_dmg + (lvl_offset * 5)),
                range=int(base_rng + (lvl_offset * 30)),
                ammo_range=int((base_rng + (lvl_offset * 30)) * 1.5),
                capacity=0,
                projectile_speed=calc_speed,
                cooldown=1.0
            )
            
        elif tier == 3:
            # Levels 7-9: Damage Boost
            # Base for Tier 3 (Level 7)
            # Lvl 7: 50 dmg, 600 rng
            base_dmg = 50
            base_rng = 600
            lvl_offset = level - 7
            
            return BuildingTemplate(
                type=building_type,
                level=level,
                max_hp=int(base['max_hp'] * scale),
                energy_production=0,
                energy_consumption=int(base['energy_consumption'] * scale),
                shield_hp_bonus=0,
                shield_recharge_bonus=0,
                cost=base['cost'],
                upgrade_cost=int(base['upgrade_cost'] * scale),
                damage=int(base_dmg + (lvl_offset * 10)),
                range=int(base_rng + (lvl_offset * 20)),
                ammo_range=int((base_rng + (lvl_offset * 20)) * 1.5),
                capacity=0,
                projectile_speed=calc_speed,
                cooldown=1.0
            )

        calc_ammo_range = int(calc_range * 1.5)

    return BuildingTemplate(
        type=building_type,
        level=level,
        max_hp=int(base['max_hp'] * scale),
        energy_production=int(base['energy_production'] * scale),
        energy_consumption=int(base['energy_consumption'] * scale),
        shield_hp_bonus=int(base['shield_hp_bonus'] * scale),
        shield_recharge_bonus=base['shield_recharge_bonus'] * scale,
        cost=base['cost'],
        upgrade_cost=int(base['upgrade_cost'] * scale),
        damage=int(base['damage'] * scale),
        range=calc_range,
        ammo_range=calc_ammo_range,
        capacity=int(base['capacity'] * level), # Capacity scales linearly with level (2, 4, 6...)
        projectile_speed=calc_speed,
        cooldown=base.get('cooldown', 1.0)
    )

@dataclass
class Building:
    id: int
    template: BuildingTemplate
    current_hp: int
    column: int  # left-most column position
    row: int  # bottom row position
    spawn_timer: float = 0.0
    
    @property
    def cells(self) -> Set[Tuple[int, int]]:
        """Get all cells occupied by this building"""
        width, height = self.template.footprint
        occupied = set()
        for dx in range(width):
            for dy in range(height):
                occupied.add((self.column + dx, self.row + dy))
        return occupied
    
    def get_total_investment(self) -> int:
        """Calculate total credits invested in this building"""
        total = self.template.cost
        # Sum upgrade costs for all levels prior to current
        for lvl in range(1, self.template.level):
            tmpl = get_building_template(self.template.type, lvl)
            total += tmpl.upgrade_cost
        return total

    def can_upgrade(self) -> bool:
        """Check if building can level up"""
        return self.template.upgrade_cost > 0 and self.template.level < 9

class CityGrid:
    def __init__(self, unlocked_columns: int = 16, max_columns: int = 32):
        self.max_columns = max_columns
        self.unlocked_width = unlocked_columns
        # Start centered
        self.unlocked_start = (max_columns - unlocked_columns) // 2
        
        self.rows = 12
        self.buildings: List[Building] = []
        self.next_building_id = 0
        
    @property
    def unlocked_range(self) -> Tuple[int, int]:
        """Returns start (inclusive) and end (exclusive) indices of unlocked columns"""
        return self.unlocked_start, self.unlocked_start + self.unlocked_width

    def is_unlocked(self, column: int) -> bool:
        start, end = self.unlocked_range
        return start <= column < end
    
    def can_unlock(self, side: str) -> bool:
        """Check if we can unlock a column on the given side"""
        if side == "left":
            return self.unlocked_start > 0
        elif side == "right":
            return (self.unlocked_start + self.unlocked_width) < self.max_columns
        return False

    def unlock_column(self, side: str) -> bool:
        """Unlock a column on the specified side"""
        if not self.can_unlock(side):
            return False
            
        if side == "left":
            self.unlocked_start -= 1
            self.unlocked_width += 1
        elif side == "right":
            self.unlocked_width += 1
        return True

    def is_supporting_others(self, building: Building) -> bool:
        """Check if any building is resting on top of this one"""
        top_row = building.row + building.template.footprint[1]
        building_cols = set(range(building.column, building.column + building.template.footprint[0]))
        
        for other in self.buildings:
            if other.id == building.id:
                continue
            if other.row == top_row:
                other_cols = set(range(other.column, other.column + other.template.footprint[0]))
                if not building_cols.isdisjoint(other_cols):
                    return True
        return False

    def move_building(self, building_id: int, new_col: int, new_row: int) -> Tuple[bool, str]:
        """Try to move an existing building to a new location"""
        building = next((b for b in self.buildings if b.id == building_id), None)
        if not building:
            return False, "Building not found"
            
        # Check if same position (No-op)
        if new_col == building.column and new_row == building.row:
            return True, "No change"
            
        # Check if supporting anything
        if self.is_supporting_others(building):
             return False, "Cannot move: Supporting other buildings"

        # Store old pos
        old_col, old_row = building.column, building.row
        
        # Temporarily remove building to check placement
        self.buildings.remove(building)
        
        # Check if valid at new pos
        can_place, reason = self.can_place(building.template.type, new_col, new_row, level=building.template.level)
        
        if can_place:
            # Update position and re-add
            building.column = new_col
            building.row = new_row
            self.buildings.append(building)
            return True, "Moved"
        else:
            # Revert and re-add
            self.buildings.append(building)
            return False, reason
        
    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """Get all cells occupied by buildings"""
        occupied = set()
        for building in self.buildings:
            occupied.update(building.cells)
        return occupied
    
    def has_foundation(self, column: int, row: int, width: int) -> bool:
        """Check if there's support beneath the building footprint"""
        if row == 0:
            return True  # ground level always supported
        
        occupied = self.get_occupied_cells()
        
        # Check if all cells directly below have foundation
        for dx in range(width):
            below = (column + dx, row - 1)
            if below not in occupied:
                return False
        
        return True
    
    def can_place(self, building_type: BuildingType, column: int, row: int, level: int = 1) -> Tuple[bool, str]:
        """Check if building can be placed at position"""
        
        # Check column unlocked
        if not self.is_unlocked(column):
            return False, "Column not unlocked"
        
        template = get_building_template(building_type, level)
        width, height = template.footprint
        
        # Check bounds
        if column + width > self.unlocked_range[1]:
            return False, "Building too wide for remaining columns"
        if row + height > self.rows:
            return False, "Building too tall"
        
        # Check foundation
        if not self.has_foundation(column, row, width):
            return False, "No foundation support"
        
        # Check cells are empty
        occupied = self.get_occupied_cells()
        for dx in range(width):
            for dy in range(height):
                if (column + dx, row + dy) in occupied:
                    return False, "Space occupied"
        
        # Special rule: Datacenters need vacant neighbor
        if building_type == BuildingType.DATACENTER:
            # Check left and right columns
            left_vacant = column > 0
            right_vacant = column + width < self.max_columns
            
            if not (left_vacant or right_vacant):
                return False, "Datacenter needs vacant neighbor column"
        
        # Special rule: Power Plant placement
        if building_type == BuildingType.POWER_PLANT:
            if row > 0:
                below_building = self.get_building_at(column, row - 1)
                if not below_building or below_building.template.type != BuildingType.POWER_PLANT:
                    return False, "Power Plants must be on Ground or other Power Plants"

        # Special rule: Barracks placement
        if building_type == BuildingType.BARRACKS:
            if row > 0:
                # Must be on top of another Barracks
                below_building = self.get_building_at(column, row - 1)
                if not below_building or below_building.template.type != BuildingType.BARRACKS:
                    return False, "Barracks must be on Ground or other Barracks"
        
        # Special rule: Stacking ON TOP of Barracks
        if row > 0:
            below_building = self.get_building_at(column, row - 1)
            if below_building and below_building.template.type == BuildingType.BARRACKS:
                # Only defensive (Turret) or Barracks allowed
                if building_type not in [BuildingType.TURRET, BuildingType.BARRACKS]:
                    return False, "Only Defensive buildings allowed on Barracks"

        return True, "OK"
    
    def place_building(self, building_type: BuildingType, column: int, row: int) -> Optional[Building]:
        """Place a new building"""
        can_place, reason = self.can_place(building_type, column, row)
        if not can_place:
            return None
        
        template = get_building_template(building_type, 1)
        building = Building(
            id=self.next_building_id,
            template=template,
            current_hp=template.max_hp,
            column=column,
            row=row
        )
        self.next_building_id += 1
        self.buildings.append(building)
        return building
    
    def upgrade_building(self, building_id: int) -> Tuple[bool, str]:
        """Upgrade building to next level"""
        building = next((b for b in self.buildings if b.id == building_id), None)
        if not building or not building.can_upgrade():
            return False, "Cannot upgrade"
        
        old_footprint = building.template.footprint
        new_level = building.template.level + 1
        new_template = get_building_template(building.template.type, new_level)
        new_footprint = new_template.footprint
        
        # If footprint grows, need to check if space available
        if new_footprint != old_footprint:
            # Remove building temporarily
            self.buildings.remove(building)
            
            # Try current position (expanding right/up)
            can_place, reason = self.can_place(building.template.type, building.column, building.row, level=new_level)
            
            if can_place:
                # Add back and proceed
                self.buildings.append(building)
            else:
                # Try shifting left if width grew
                width_diff = new_footprint[0] - old_footprint[0]
                if width_diff > 0:
                    test_col = building.column - width_diff
                    can_place_left, reason_left = self.can_place(building.template.type, test_col, building.row, level=new_level)
                    
                    if can_place_left:
                        building.column = test_col
                        self.buildings.append(building)
                        # Proceed with upgrade
                    else:
                        self.buildings.append(building)
                        return False, f"No space to expand: {reason}"
                else:
                    self.buildings.append(building)
                    return False, f"No space to expand: {reason}"
        
        # Apply upgrade
        building.template = new_template
        building.current_hp = new_template.max_hp  # Full heal on upgrade
        return True, "Upgraded"
    
    def destroy_building(self, building_id: int):
        """Destroy building and handle cascade"""
        building = next((b for b in self.buildings if b.id == building_id), None)
        if not building:
            return
        
        cascade_damage = building.template.max_hp * 0.25
        destroyed_cells = building.cells
        
        # Remove building
        self.buildings = [b for b in self.buildings if b.id != building_id]
        
        # Find buildings that were supported by destroyed cells
        unsupported = []
        for other in self.buildings:
            # Check if this building needs support that was destroyed
            if other.row > 0:  # Not ground level
                needs_support = set((other.column + dx, other.row - 1) 
                                   for dx in range(other.template.footprint[0]))
                if needs_support.intersection(destroyed_cells):
                    unsupported.append(other)
        
        # Destroy unsupported buildings
        for other in unsupported:
            self.destroy_building(other.id)
        
        # Apply cascade damage to buildings below
        if building.row > 0:
            # Find buildings in cells directly below
            for col, row in destroyed_cells:
                below_cell = (col, row - 1)
                for other in self.buildings:
                    if below_cell in other.cells:
                        other.current_hp -= cascade_damage
                        if other.current_hp <= 0:
                            self.destroy_building(other.id)
                        break

    def get_building_at(self, column: int, row: int) -> Optional[Building]:
        """Get building occupying this cell"""
        for building in self.buildings:
            if (column, row) in building.cells:
                return building
        return None

# --- Constants ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 720
UI_WIDTH = 300
GRID_SLOT_WIDTH = 40
GRID_CELL_HEIGHT = 40
MAX_COLS = 32

# Calculate centered grid position
GRID_WIDTH = MAX_COLS * GRID_SLOT_WIDTH
PLAYABLE_WIDTH = SCREEN_WIDTH - UI_WIDTH
GRID_START_X = (PLAYABLE_WIDTH - GRID_WIDTH) // 2  # Should be 10

GROUND_Y = 620  # Moved down to make room for log
SHIELD_Y = 300  # Lowered slightly

@dataclass
class GroundUnit:
    x: float
    y: float
    team: str  # "invader" or "defender"
    hp: int
    max_hp: int
    damage: int
    speed: float
    target: Optional[object] = None # Building or GroundUnit
    attack_cooldown: float = 0.0
    alive: bool = True

@dataclass
class Drone:
    x: float
    y: float
    vx: float
    vy: float
    hp: int
    max_hp: int
    damage: int
    range: int
    speed: float
    home_x: float
    home_y: float
    target: Optional['Enemy'] = None
    cooldown: float = 0.0
    alive: bool = True

@dataclass
class Enemy:
    x: float
    y: float  # starts above shield
    vx: float = 0
    vy: float = 50  # pixels per second downward
    max_hp: int = 50
    current_hp: int = 50
    damage: int = 20  # damage on impact
    radius: int = 20
    behavior: str = "kamikaze"  # or "shooter" later
    alive: bool = True
    is_boss: bool = False

@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    damage: int
    radius: int = 5
    alive: bool = True
    source: str = "turret"  # or "enemy"
    target: Optional[Enemy] = None
    max_range: float = 0
    distance_traveled: float = 0

@dataclass
class Wave:
    wave_number: int
    enemies_remaining: int
    spawn_timer: float = 0
    spawn_interval: float = 1.5  # seconds between spawns
    
    def get_spawn_count(self) -> int:
        """Calculate enemies for this wave"""
        return 5 + (self.wave_number * 2)  # scales with wave number

class CombatManager:
    def __init__(self, game_state):
        self.state = game_state
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        self.ground_units: List[GroundUnit] = []
        self.drones: List[Drone] = []
        self.current_wave: Optional[Wave] = None
        self.wave_complete_timer: float = 0
        self.damage_taken_this_wave: bool = False
        
    def start_wave(self):
        """Initialize new wave"""
        self.damage_taken_this_wave = False
        self.current_wave = Wave(
            wave_number=self.state.wave,
            enemies_remaining=0
        )
        self.current_wave.enemies_remaining = self.current_wave.get_spawn_count()
        
        if self.state.wave % 10 == 0:
            self.state.add_log("WARNING: MASSIVE SIGNAL DETECTED!")
        
        self.enemies.clear()
        self.projectiles.clear()
        self.ground_units.clear()
        self.drones.clear()
        
    def spawn_boss(self):
        """Spawn the Giant Kamikaze Boss"""
        # Center spawn
        x = GRID_START_X + (self.state.grid.max_columns * GRID_SLOT_WIDTH) / 2
        
        # Scale stats
        boss_tier = max(1, self.state.wave // 10)
        hp = 2000 * boss_tier
        
        boss = Enemy(
            x=x,
            y=-100,
            vx=0,
            vy=15, # Very slow
            max_hp=hp,
            current_hp=hp,
            damage=1000, # Instakill
            radius=60, # Giant
            behavior="boss",
            is_boss=True
        )
        self.enemies.append(boss)
        self.state.add_log(f"BOSS INCOMING: GIANT KAMIKAZE (Tier {boss_tier})!")

    def spawn_enemy(self):
        """Spawn a single enemy at random x position"""
        start, end = self.state.grid.unlocked_range
        # Allow spawning slightly outside unlocked range for variance
        spawn_start = max(0, start - 2)
        spawn_end = min(self.state.grid.max_columns, end + 2)
        
        slot = random.randint(spawn_start, spawn_end - 1)
        x = GRID_START_X + slot * GRID_SLOT_WIDTH + GRID_SLOT_WIDTH / 2
        
        # Scale HP with wave number
        hp = 50 + (self.current_wave.wave_number * 10)
        
        enemy = Enemy(
            x=x,
            y=-50,  # Spawn off-screen top for longer descent
            max_hp=hp,
            current_hp=hp
        )
        self.enemies.append(enemy)
        self.state.add_log(f"Enemy detected at sector {slot}!")
        
    def update(self, dt):
        """Main combat update loop"""
        if not self.current_wave:
            return
            
        # Spawn enemies
        if self.current_wave.enemies_remaining > 0:
            self.current_wave.spawn_timer += dt
            if self.current_wave.spawn_timer >= self.current_wave.spawn_interval:
                # Check for Boss Spawn (Last enemy of every 10th wave)
                if self.state.wave % 10 == 0 and self.current_wave.enemies_remaining == 1:
                    self.spawn_boss()
                else:
                    self.spawn_enemy()
                    
                self.current_wave.enemies_remaining -= 1
                self.current_wave.spawn_timer = 0
        
        # Update enemies
        self.update_enemies(dt)
        
        # Update ground units
        self.update_ground_units(dt)
        
        # Turrets fire
        self.update_turrets(dt)
        
        # Barracks produce
        self.update_barracks(dt)

        # Drone Factories produce and Drones act
        self.update_drones(dt)
        
        # Update projectiles
        self.update_projectiles(dt)
        
        # Check collisions
        self.check_collisions()
        
        # Clean up dead entities
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.ground_units = [u for u in self.ground_units if u.alive]
        self.drones = [d for d in self.drones if d.alive]
        
        # Check wave completion
        invaders_alive = any(u.team == "invader" and u.alive for u in self.ground_units)
        if self.current_wave.enemies_remaining == 0 and len(self.enemies) == 0 and not invaders_alive:
            # Prevent wave completion if base is destroyed
            if not self.state.grid.buildings:
                return

            self.wave_complete_timer += dt
            if self.wave_complete_timer >= 2.0:  # 2 second delay before build phase
                self.end_wave()
    
    def explode_enemy(self, enemy, x, y):
        """Handle enemy explosion with AOE damage"""
        blast_radius = 50  # Approx 50-100 range diameter
        if enemy.is_boss:
            blast_radius = 200 # Massive area for boss
            self.state.add_log("BOSS DETONATED! CATASTROPHIC DAMAGE!")
            
        damage = enemy.damage
        
        # Find all buildings in radius
        hit_buildings = []
        for building in self.state.grid.buildings:
            # Building rect
            bx = GRID_START_X + building.column * GRID_SLOT_WIDTH
            by = GROUND_Y - (building.row + building.template.footprint[1]) * GRID_CELL_HEIGHT
            bw = building.template.footprint[0] * GRID_SLOT_WIDTH
            bh = building.template.footprint[1] * GRID_CELL_HEIGHT
            
            # Closest point on rect to circle center
            closest_x = max(bx, min(x, bx + bw))
            closest_y = max(by, min(y, by + bh))
            
            dist_sq = (x - closest_x)**2 + (y - closest_y)**2
            if dist_sq < blast_radius**2:
                hit_buildings.append(building)
        
        if hit_buildings:
            self.damage_taken_this_wave = True
            self.state.add_log(f"Enemy exploded! Hit {len(hit_buildings)} buildings.")
            for building in hit_buildings:
                building.current_hp -= damage
                if building.current_hp <= 0:
                    self.state.grid.destroy_building(building.id)
            self.state.update_economy()
        
        enemy.alive = False

    def update_enemies(self, dt):
        """Move enemies toward city"""
        for enemy in self.enemies:
            prev_y = enemy.y
            enemy.y += enemy.vy * dt
            
            # Check for collision with buildings along the path (Raycast)
            hit_building = None
            for building in self.state.grid.buildings:
                bx = GRID_START_X + building.column * GRID_SLOT_WIDTH
                by = GROUND_Y - (building.row + building.template.footprint[1]) * GRID_CELL_HEIGHT
                bw = building.template.footprint[0] * GRID_SLOT_WIDTH
                bh = building.template.footprint[1] * GRID_CELL_HEIGHT
                
                # Check X overlap (including radius)
                if not (bx - enemy.radius <= enemy.x <= bx + bw + enemy.radius):
                    continue
                    
                # Check Y overlap (path vs building height)
                # Building Y range: [by, by + bh]
                # Enemy Y path: [prev_y, enemy.y]
                if (prev_y < by + bh and enemy.y > by):
                    hit_building = building
                    break
            
            if hit_building:
                self.explode_enemy(enemy, enemy.x, enemy.y)
                continue
            
            # Check if enemy reached ground
            if enemy.y >= GROUND_Y:
                # Check for direct hit on ground level building to decide on invaders
                direct_hit = False
                col = int((enemy.x - GRID_START_X) / GRID_SLOT_WIDTH)
                if 0 <= col < self.state.grid.max_columns:
                     if self.state.grid.get_building_at(col, 0):
                         direct_hit = True
                
                # Explode (AOE)
                self.explode_enemy(enemy, enemy.x, GROUND_Y)
                
                # If no direct hit on a building, spawn invaders
                if not direct_hit:
                    self.spawn_ground_invader(enemy.x, count=2)

    def spawn_ground_invader(self, x, count=1):
        """Spawn invader ground units"""
        for _ in range(count):
            # Add slight offset so they don't stack perfectly
            offset = random.randint(-15, 15)
            invader = GroundUnit(
                x=x + offset,
                y=GROUND_Y,
                team="invader",
                hp=25 + (self.state.wave * 5),
                max_hp=25 + (self.state.wave * 5),
                damage=0, # Damage is based on HP on impact
                speed=45
            )
            self.ground_units.append(invader)
        self.state.add_log(f"{count} Ground Invaders Spawned!")

    def update_ground_units(self, dt):
        """Update movement and combat for ground units"""
        for unit in self.ground_units:
            if not unit.alive:
                continue
                
            if unit.attack_cooldown > 0:
                unit.attack_cooldown -= dt
            
            # Find target
            target = None
            if unit.team == "invader":
                # Target nearest building OR defender
                # Prioritize defenders if close? Or just nearest entity?
                # Let's go with nearest entity (Building or Defender)
                min_dist = 9999
                
                # Check buildings
                for b in self.state.grid.buildings:
                    bx = GRID_START_X + b.column * GRID_SLOT_WIDTH + (b.template.footprint[0] * GRID_SLOT_WIDTH / 2)
                    dist = abs(unit.x - bx)
                    if dist < min_dist:
                        min_dist = dist
                        target = b
                
                # Check defenders
                for other in self.ground_units:
                    if other.team == "defender" and other.alive:
                        dist = abs(unit.x - other.x)
                        if dist < min_dist:
                            min_dist = dist
                            target = other
                            
            else: # defender
                # Target nearest invader
                min_dist = 9999
                for other in self.ground_units:
                    if other.team == "invader" and other.alive:
                        dist = abs(unit.x - other.x)
                        if dist < min_dist:
                            min_dist = dist
                            target = other
            
    def update_ground_units(self, dt):
        """Update movement and combat for ground units"""
        for unit in self.ground_units:
            if not unit.alive:
                continue
                
            if unit.attack_cooldown > 0:
                unit.attack_cooldown -= dt
            
            # Find target
            target = None
            if unit.team == "invader":
                # Target nearest building OR defender
                min_dist = 9999
                
                # Check buildings
                for b in self.state.grid.buildings:
                    bx = GRID_START_X + b.column * GRID_SLOT_WIDTH + (b.template.footprint[0] * GRID_SLOT_WIDTH / 2)
                    dist = abs(unit.x - bx)
                    if dist < min_dist:
                        min_dist = dist
                        target = b
                
                # Check defenders
                for other in self.ground_units:
                    if other.team == "defender" and other.alive:
                        dist = abs(unit.x - other.x)
                        if dist < min_dist:
                            min_dist = dist
                            target = other
                            
            else: # defender
                # Target nearest invader
                min_dist = 9999
                for other in self.ground_units:
                    if other.team == "invader" and other.alive:
                        dist = abs(unit.x - other.x)
                        if dist < min_dist:
                            min_dist = dist
                            target = other
            
            if target:
                # Move or Attack
                target_x = 0
                if isinstance(target, Building):
                    target_x = GRID_START_X + target.column * GRID_SLOT_WIDTH + (target.template.footprint[0] * GRID_SLOT_WIDTH / 2)
                else:
                    target_x = target.x
                
                # Determine direction
                direction = 1 if target_x > unit.x else -1
                
                # Check for collision/attack range
                attack_range = 15 if unit.team == "invader" else 30
                
                # For Invaders vs Buildings, use physical collision check instead of center-to-center distance
                hit_building = None
                if unit.team == "invader":
                    unit_left = unit.x - 5
                    unit_right = unit.x + 5
                    
                    # Check if touching any building
                    for building in self.state.grid.buildings:
                        if building.row == 0: # Only ground level
                            bx = GRID_START_X + building.column * GRID_SLOT_WIDTH
                            bw = building.template.footprint[0] * GRID_SLOT_WIDTH
                            
                            # Check overlap
                            if unit_right >= bx and unit_left <= bx + bw:
                                hit_building = building
                                break
                
                if hit_building:
                    # Explode on contact
                    damage = unit.hp
                    hit_building.current_hp -= damage
                    self.damage_taken_this_wave = True
                    self.state.add_log(f"Invader crashed into building! -{damage} HP")
                    if hit_building.current_hp <= 0:
                        self.state.grid.destroy_building(hit_building.id)
                        self.state.update_economy()
                    unit.alive = False
                    continue

                # Standard distance check for other targets
                dist = abs(unit.x - target_x)
                if dist <= attack_range:
                    # Attack
                    if unit.attack_cooldown <= 0:
                        if unit.team == "invader":
                            # Should be handled by collision above if building, but handle defenders here
                            if not isinstance(target, Building):
                                target.hp -= unit.hp
                                self.state.add_log(f"Invader exploded! -{unit.hp} HP to Defender")
                                if target.hp <= 0:
                                    target.alive = False
                                unit.alive = False
                        else:
                            # Defender behavior: Standard shooting/melee
                            if isinstance(target, Building):
                                pass # Defenders don't attack buildings
                            else:
                                target.hp -= unit.damage
                                if target.hp <= 0:
                                    target.alive = False
                                    self.state.add_log("Invader neutralized.")
                            unit.attack_cooldown = 1.0
                else:
                    # Move
                    move_amount = direction * unit.speed * dt
                    
                    # Check for collision with buildings if moving (Predictive)
                    will_hit_building = False
                    if unit.team == "invader":
                        next_x = unit.x + move_amount
                        next_left = next_x - 5
                        next_right = next_x + 5
                        
                        for building in self.state.grid.buildings:
                            if building.row == 0:
                                bx = GRID_START_X + building.column * GRID_SLOT_WIDTH
                                bw = building.template.footprint[0] * GRID_SLOT_WIDTH
                                
                                if next_right >= bx and next_left <= bx + bw:
                                    will_hit_building = True
                                    # We will hit it next frame, so just move to edge and let next frame handle collision?
                                    # Or explode now? Let's explode now to be responsive.
                                    hit_building = building
                                    break
                    
                    if hit_building:
                         # Explode on contact (Predictive)
                        damage = unit.hp
                        hit_building.current_hp -= damage
                        self.damage_taken_this_wave = True
                        self.state.add_log(f"Invader crashed into building! -{damage} HP")
                        if hit_building.current_hp <= 0:
                            self.state.grid.destroy_building(hit_building.id)
                            self.state.update_economy()
                        unit.alive = False
                    else:
                        unit.x += move_amount

    def update_drones(self, dt):
        """Handle Drone Factory production and Drone behavior"""
        # 1. Production
        # Count drones per factory? Or just global pool for simplicity first?
        # Let's do global pool limit based on total capacity
        total_capacity = sum(b.template.capacity for b in self.state.grid.buildings if b.template.type == BuildingType.DRONE_FACTORY)
        current_drones = len(self.drones)
        
        for building in self.state.grid.buildings:
            if building.template.type == BuildingType.DRONE_FACTORY:
                if self.state.energy_surplus >= 0:
                    if current_drones >= total_capacity:
                        continue
                        
                    building.spawn_timer += dt
                    spawn_interval = 5.0 # Fast production
                    
                    if building.spawn_timer >= spawn_interval:
                        # Spawn Drone
                        width, height = building.template.footprint
                        bx = GRID_START_X + building.column * GRID_SLOT_WIDTH + (width * GRID_SLOT_WIDTH / 2)
                        by = GROUND_Y - building.row * GRID_CELL_HEIGHT - (height * GRID_CELL_HEIGHT)
                        
                        drone = Drone(
                            x=bx,
                            y=by - 20, # Spawn slightly above
                            vx=0,
                            vy=0,
                            hp=30 * building.template.level,
                            max_hp=30 * building.template.level,
                            damage=building.template.damage,
                            range=building.template.range,
                            speed=150,
                            home_x=bx,
                            home_y=by - 50 # Hover point
                        )
                        self.drones.append(drone)
                        current_drones += 1
                        building.spawn_timer = 0
        
        # 2. Behavior
        for drone in self.drones:
            if not drone.alive:
                continue
                
            # Cooldown
            if drone.cooldown > 0:
                drone.cooldown -= dt
            
            # Find Target
            if not drone.target or not drone.target.alive:
                drone.target = self.find_nearest_enemy(drone.x, drone.y, max_range=800) # Wide search
            
            target_x, target_y = drone.home_x, drone.home_y
            
            if drone.target:
                # Move towards target
                # Ideal distance: keep at ~80% of range
                ideal_dist = drone.range * 0.8
                dx = drone.target.x - drone.x
                dy = drone.target.y - drone.y
                dist = (dx**2 + dy**2)**0.5
                
                if dist > 0:
                    if dist > ideal_dist:
                        # Close in
                        drone.vx = (dx / dist) * drone.speed
                        drone.vy = (dy / dist) * drone.speed
                    elif dist < ideal_dist * 0.5:
                        # Back off
                        drone.vx = -(dx / dist) * drone.speed
                        drone.vy = -(dy / dist) * drone.speed
                    else:
                        # Strafe / Hover (simple: stop)
                        drone.vx = 0
                        drone.vy = 0
                        
                    # Fire if in range
                    if dist <= drone.range and drone.cooldown <= 0:
                        self.fire_projectile(drone.x, drone.y, drone.target, 
                                           damage=drone.damage, 
                                           max_range=drone.range * 1.5,
                                           speed=400) # Fast drone shots
                        drone.cooldown = 0.8
            else:
                # Return home
                dx = drone.home_x - drone.x
                dy = drone.home_y - drone.y
                dist = (dx**2 + dy**2)**0.5
                
                if dist > 5:
                    drone.vx = (dx / dist) * drone.speed
                    drone.vy = (dy / dist) * drone.speed
                else:
                    drone.vx = 0
                    drone.vy = 0
                    # Idle hover effect?
                    drone.y += math.sin(self.state.combat.wave_complete_timer * 5) * 0.5 # Hacky access to timer
            
            # Apply movement
            drone.x += drone.vx * dt
            drone.y += drone.vy * dt

    def update_barracks(self, dt):
        """Handle Barracks production"""
        # Calculate total capacity and current defenders
        total_capacity = sum(b.template.capacity for b in self.state.grid.buildings if b.template.type == BuildingType.BARRACKS)
        current_defenders = sum(1 for u in self.ground_units if u.team == "defender" and u.alive)
        
        for building in self.state.grid.buildings:
            if building.template.type == BuildingType.BARRACKS:
                if self.state.energy_surplus >= 0: # Only works if power is on
                    # Check capacity (Global pool for now)
                    if current_defenders >= total_capacity:
                        continue

                    building.spawn_timer += dt
                    spawn_interval = 10.0 / building.template.level
                    
                    if building.spawn_timer >= spawn_interval:
                        # Check cost
                        if self.state.credits < 1:
                            # Not enough credits to spawn
                            continue

                        # Spawn defender
                        width = building.template.footprint[0]
                        bx = GRID_START_X + building.column * GRID_SLOT_WIDTH + (width * GRID_SLOT_WIDTH / 2)
                        
                        defender = GroundUnit(
                            x=bx,
                            y=GROUND_Y,
                            team="defender",
                            hp=40 * building.template.level,
                            max_hp=40 * building.template.level,
                            damage=8 * building.template.level,
                            speed=60
                        )
                        self.ground_units.append(defender)
                        current_defenders += 1 # Increment local count to prevent overspawn in same frame
                        building.spawn_timer = 0
                        self.state.credits -= 1 # Cost 1 credit per unit

    def update_turrets(self, dt):
        """Turrets acquire and fire at enemies"""
        for building in self.state.grid.buildings:
            if building.template.type == BuildingType.TURRET:
                if not hasattr(building, 'cooldown'):
                    building.cooldown = 0.0
                
                if building.cooldown > 0:
                    building.cooldown -= dt
                    continue

                if building.current_hp > 0:
                    width, height = building.template.footprint
                    turret_x = GRID_START_X + building.column * GRID_SLOT_WIDTH + (width * GRID_SLOT_WIDTH) / 2
                    turret_y = GROUND_Y - building.row * GRID_CELL_HEIGHT - (height * GRID_CELL_HEIGHT) / 2
                    
                    # Use building range
                    target = self.find_nearest_enemy(turret_x, turret_y, max_range=building.template.range)
                    if target:
                        self.fire_projectile(turret_x, turret_y, target, 
                                             damage=building.template.damage, 
                                             max_range=building.template.ammo_range,
                                             speed=building.template.projectile_speed)
                        building.cooldown = building.template.cooldown
    
    def find_nearest_enemy(self, x, y, max_range=600):
        """Find closest enemy within range"""
        nearest = None
        min_dist = max_range
        
        for enemy in self.enemies:
            dist = ((enemy.x - x)**2 + (enemy.y - y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        
        return nearest
    
    def fire_projectile(self, from_x, from_y, target, damage=25, max_range=0, speed=300):
        """Create projectile aimed at target"""
        dx = target.x - from_x
        dy = target.y - from_y
        dist = (dx**2 + dy**2)**0.5
        
        if dist == 0:
            return
        
        if speed <= 0: speed = 300
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        
        projectile = Projectile(
            x=from_x,
            y=from_y,
            vx=vx,
            vy=vy,
            damage=damage,
            target=target,
            max_range=max_range
        )
        self.projectiles.append(projectile)
    
    def update_projectiles(self, dt):
        """Move projectiles"""
        for proj in self.projectiles:
            proj.x += proj.vx * dt
            proj.y += proj.vy * dt
            
            # Track distance
            dist_step = (proj.vx**2 + proj.vy**2)**0.5 * dt
            proj.distance_traveled += dist_step
            
            if proj.max_range > 0 and proj.distance_traveled >= proj.max_range:
                proj.alive = False
            
            if proj.y < 0 or proj.y > SCREEN_HEIGHT or proj.x < 0 or proj.x > SCREEN_WIDTH:
                proj.alive = False
    
    def check_collisions(self):
        """Handle all collision detection"""
        # Projectiles vs enemies
        for proj in self.projectiles:
            if not proj.alive or proj.source != "turret":
                continue
                
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                    
                dist = ((proj.x - enemy.x)**2 + (proj.y - enemy.y)**2)**0.5
                if dist < (proj.radius + enemy.radius):
                    enemy.current_hp -= proj.damage
                    proj.alive = False
                    
                    if enemy.current_hp <= 0:
                        enemy.alive = False
                        self.state.credits += 10
                        self.state.add_log(f"Enemy destroyed! +10 Credits")
                    break
        
        # Enemies vs shield
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            # Only check collision if shield is active
            if self.state.shield_is_active and enemy.y >= SHIELD_Y and enemy.y <= SHIELD_Y + 10:
                if self.state.shield_current_hp > 0:
                    self.state.shield_current_hp -= enemy.damage
                    self.state.add_log(f"Shield hit! -{enemy.damage} HP")
                    enemy.alive = False
                    
                    if self.state.shield_current_hp <= 0:
                        self.state.shield_current_hp = 0
                        self.state.shield_is_active = False
                        self.state.add_log("SHIELD COLLAPSED! REBOOTING...")
        
        # Enemies vs buildings
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            # Check collision with any building
            hit_any = False
            for building in self.state.grid.buildings:
                bx = GRID_START_X + building.column * GRID_SLOT_WIDTH
                by = GROUND_Y - (building.row + building.template.footprint[1]) * GRID_CELL_HEIGHT
                bw = building.template.footprint[0] * GRID_SLOT_WIDTH
                bh = building.template.footprint[1] * GRID_CELL_HEIGHT
                
                # Check circle vs rect
                closest_x = max(bx, min(enemy.x, bx + bw))
                closest_y = max(by, min(enemy.y, by + bh))
                
                dist_sq = (enemy.x - closest_x)**2 + (enemy.y - closest_y)**2
                if dist_sq < enemy.radius**2:
                    hit_any = True
                    break
            
            if hit_any:
                self.explode_enemy(enemy, enemy.x, enemy.y)
    
    def end_wave(self):
        """Transition back to build phase"""
        base_reward = 100 + (self.current_wave.wave_number * 25)
        
        perfect_wave = not self.damage_taken_this_wave
        
        perfect_bonus = 0
        if perfect_wave:
            perfect_bonus = int(base_reward * 0.5)
            
        energy_bonus = max(0, self.state.energy_surplus)
        
        total_reward = base_reward + perfect_bonus + energy_bonus
        
        self.state.credits += total_reward
        self.state.last_wave_rewards = WaveRewards(
            base=base_reward,
            perfect_bonus=perfect_bonus,
            energy_bonus=energy_bonus,
            repair_cost=0,
            total=total_reward
        )
        
        self.state.phase = "build"
        self.current_wave = None
        self.wave_complete_timer = 0

@dataclass
class WaveRewards:
    base: int
    perfect_bonus: int
    energy_bonus: int
    repair_cost: int
    total: int

@dataclass
class GameState:
    credits: int = 300
    wave: int = 0
    phase: str = "build"
    grid: CityGrid = None
    shield_max_hp: int = 0
    shield_current_hp: int = 0
    shield_recharge_rate: float = 0
    energy_production: int = 0
    energy_consumption: int = 0
    selected_column: int = 0
    selected_row: int = 0
    combat: Optional[CombatManager] = None
    last_wave_rewards: Optional[WaveRewards] = None
    logs: List[str] = field(default_factory=list)
    shield_is_active: bool = True
    
    def __post_init__(self):
        if self.grid is None:
            self.grid = CityGrid()
        if self.combat is None:
            self.combat = CombatManager(self)
    
    def add_log(self, message: str):
        """Add a message to the persistent log"""
        self.logs.append(message)
        if len(self.logs) > 50: # Keep last 50
            self.logs.pop(0)

    @property
    def energy_surplus(self) -> int:
        return self.energy_production - self.energy_consumption
    
    def update_economy(self):
        """Recalculate energy and shield stats"""
        self.energy_production = 0
        self.energy_consumption = 0
        self.shield_max_hp = 0
        self.shield_recharge_rate = 0
        
        # Base shield stats
        self.shield_max_hp = 100
        self.shield_recharge_rate = 1.0
        
        for building in self.grid.buildings:
            if building.current_hp > 0:
                self.energy_production += building.template.energy_production
                self.energy_consumption += building.template.energy_consumption
                self.shield_max_hp += building.template.shield_hp_bonus
                self.shield_recharge_rate += building.template.shield_recharge_bonus
        
        self.shield_current_hp = min(self.shield_current_hp, self.shield_max_hp)
