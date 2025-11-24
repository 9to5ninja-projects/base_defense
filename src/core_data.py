from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set, Dict
from enum import Enum
import random

class BuildingType(Enum):
    POWER_PLANT = "power_plant"
    DATACENTER = "datacenter"
    CAPACITOR = "capacitor"
    TURRET = "turret"
    DRONE_FACTORY = "drone_factory"

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
        
        elif self.type in [BuildingType.DATACENTER, BuildingType.CAPACITOR]:
            # Vertical growth only
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
        },
        BuildingType.DATACENTER: {
            'max_hp': 100,
            'energy_production': 0,
            'energy_consumption': 4,
            'shield_hp_bonus': 150,
            'shield_recharge_bonus': 0,
            'cost': 75,
            'upgrade_cost': 60,
        },
        BuildingType.CAPACITOR: {
            'max_hp': 80,
            'energy_production': 0,
            'energy_consumption': 3,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 2.0,
            'cost': 60,
            'upgrade_cost': 50,
        },
        BuildingType.TURRET: {
            'max_hp': 120,
            'energy_production': 0,
            'energy_consumption': 5,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 0,
            'cost': 80,
            'upgrade_cost': 0,  # Cannot upgrade
        },
        BuildingType.DRONE_FACTORY: {
            'max_hp': 130,
            'energy_production': 0,
            'energy_consumption': 8,
            'shield_hp_bonus': 0,
            'shield_recharge_bonus': 0,
            'cost': 130,
            'upgrade_cost': 0,  # Cannot upgrade
        },
    }
    
    base = base_stats[building_type]
    
    # Scale stats by level
    scale = 1 + (level - 1) * 0.3  # 30% increase per level
    
    return BuildingTemplate(
        type=building_type,
        level=level,
        max_hp=int(base['max_hp'] * scale),
        energy_production=int(base['energy_production'] * scale),
        energy_consumption=int(base['energy_consumption'] * scale),
        shield_hp_bonus=int(base['shield_hp_bonus'] * scale),
        shield_recharge_bonus=base['shield_recharge_bonus'] * scale,
        cost=base['cost'],
        upgrade_cost=base['upgrade_cost'],
    )

@dataclass
class Building:
    id: int
    template: BuildingTemplate
    current_hp: int
    column: int  # left-most column position
    row: int  # bottom row position
    
    @property
    def cells(self) -> Set[Tuple[int, int]]:
        """Get all cells occupied by this building"""
        width, height = self.template.footprint
        occupied = set()
        for dx in range(width):
            for dy in range(height):
                occupied.add((self.column + dx, self.row + dy))
        return occupied
    
    def can_upgrade(self) -> bool:
        """Check if building can level up"""
        return self.template.upgrade_cost > 0 and self.template.level < 9

class CityGrid:
    def __init__(self, unlocked_columns: int = 8, max_columns: int = 16):
        self.unlocked_columns = unlocked_columns
        self.max_columns = max_columns
        self.rows = 12
        self.buildings: List[Building] = []
        self.next_building_id = 0
        
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
    
    def can_place(self, building_type: BuildingType, column: int, row: int) -> Tuple[bool, str]:
        """Check if building can be placed at position"""
        
        # Check column unlocked
        if column >= self.unlocked_columns:
            return False, "Column not unlocked"
        
        template = get_building_template(building_type, 1)
        width, height = template.footprint
        
        # Check bounds
        if column + width > self.unlocked_columns:
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
            right_vacant = column + width < self.unlocked_columns
            
            if not (left_vacant or right_vacant):
                return False, "Datacenter needs vacant neighbor column"
        
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
    
    def upgrade_building(self, building_id: int) -> bool:
        """Upgrade building to next level"""
        building = next((b for b in self.buildings if b.id == building_id), None)
        if not building or not building.can_upgrade():
            return False
        
        old_footprint = building.template.footprint
        new_level = building.template.level + 1
        new_template = get_building_template(building.template.type, new_level)
        new_footprint = new_template.footprint
        
        # If footprint grows, need to check if space available
        if new_footprint != old_footprint:
            # Remove building temporarily
            self.buildings.remove(building)
            
            can_place, reason = self.can_place(building.template.type, building.column, building.row)
            
            # Add back
            self.buildings.append(building)
            
            if not can_place:
                return False
        
        # Apply upgrade
        building.template = new_template
        building.current_hp = new_template.max_hp  # Full heal on upgrade
        return True
    
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
GRID_START_X = 50
GRID_SLOT_WIDTH = 60
GRID_CELL_HEIGHT = 40
GROUND_Y = 600
SHIELD_Y = 200
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

@dataclass
class Enemy:
    x: float
    y: float  # starts above shield
    vx: float = 0
    vy: float = 50  # pixels per second downward
    max_hp: int = 50
    current_hp: int = 50
    damage: int = 20  # damage on impact
    radius: int = 15
    behavior: str = "kamikaze"  # or "shooter" later
    alive: bool = True

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
        self.current_wave: Optional[Wave] = None
        self.wave_complete_timer: float = 0
        
    def start_wave(self):
        """Initialize new wave"""
        self.current_wave = Wave(
            wave_number=self.state.wave,
            enemies_remaining=0
        )
        self.current_wave.enemies_remaining = self.current_wave.get_spawn_count()
        
        self.enemies.clear()
        self.projectiles.clear()
        
    def spawn_enemy(self):
        """Spawn a single enemy at random x position"""
        cols = self.state.grid.unlocked_columns
        slot = random.randint(0, cols - 1)
        x = GRID_START_X + slot * GRID_SLOT_WIDTH + GRID_SLOT_WIDTH / 2
        
        # Scale HP with wave number
        hp = 50 + (self.current_wave.wave_number * 10)
        
        enemy = Enemy(
            x=x,
            y=SHIELD_Y - 100,  # spawn above shield
            max_hp=hp,
            current_hp=hp
        )
        self.enemies.append(enemy)
        
    def update(self, dt):
        """Main combat update loop"""
        if not self.current_wave:
            return
            
        # Spawn enemies
        if self.current_wave.enemies_remaining > 0:
            self.current_wave.spawn_timer += dt
            if self.current_wave.spawn_timer >= self.current_wave.spawn_interval:
                self.spawn_enemy()
                self.current_wave.enemies_remaining -= 1
                self.current_wave.spawn_timer = 0
        
        # Update enemies
        self.update_enemies(dt)
        
        # Turrets fire
        self.update_turrets(dt)
        
        # Update projectiles
        self.update_projectiles(dt)
        
        # Check collisions
        self.check_collisions()
        
        # Clean up dead entities
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # Check wave completion
        if self.current_wave.enemies_remaining == 0 and len(self.enemies) == 0:
            self.wave_complete_timer += dt
            if self.wave_complete_timer >= 2.0:  # 2 second delay before build phase
                self.end_wave()
    
    def update_enemies(self, dt):
        """Move enemies toward city"""
        for enemy in self.enemies:
            enemy.y += enemy.vy * dt
            
            # Check if enemy reached ground (destroy bottom building)
            if enemy.y >= GROUND_Y:
                col = int((enemy.x - GRID_START_X) / GRID_SLOT_WIDTH)
                if 0 <= col < self.state.grid.unlocked_columns:
                    building = self.state.grid.get_building_at(col, 0)
                    if building:
                        building.current_hp -= enemy.damage
                        if building.current_hp <= 0:
                            self.state.grid.destroy_building(building.id)
                            self.state.update_economy()
                enemy.alive = False
    
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
                    
                    target = self.find_nearest_enemy(turret_x, turret_y)
                    if target:
                        self.fire_projectile(turret_x, turret_y, target)
                        building.cooldown = 1.0
    
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
    
    def fire_projectile(self, from_x, from_y, target):
        """Create projectile aimed at target"""
        dx = target.x - from_x
        dy = target.y - from_y
        dist = (dx**2 + dy**2)**0.5
        
        if dist == 0:
            return
        
        speed = 300
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        
        projectile = Projectile(
            x=from_x,
            y=from_y,
            vx=vx,
            vy=vy,
            damage=25,
            target=target
        )
        self.projectiles.append(projectile)
    
    def update_projectiles(self, dt):
        """Move projectiles"""
        for proj in self.projectiles:
            proj.x += proj.vx * dt
            proj.y += proj.vy * dt
            
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
                    break
        
        # Enemies vs shield
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            if enemy.y >= SHIELD_Y and enemy.y <= SHIELD_Y + 10:
                if self.state.shield_current_hp > 0:
                    self.state.shield_current_hp -= enemy.damage
                    enemy.alive = False
                    
                    if self.state.shield_current_hp < 0:
                        self.state.shield_current_hp = 0
        
        # Enemies vs buildings
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            if enemy.y < SHIELD_Y:
                continue
                
            col = int((enemy.x - GRID_START_X) / GRID_SLOT_WIDTH)
            if 0 <= col < self.state.grid.unlocked_columns:
                for building in self.state.grid.buildings:
                    width, height = building.template.footprint
                    if building.column <= col < building.column + width:
                        building_y_top = GROUND_Y - (building.row + height) * GRID_CELL_HEIGHT
                        building_y_bottom = GROUND_Y - building.row * GRID_CELL_HEIGHT
                        
                        if building_y_top <= enemy.y <= building_y_bottom:
                            building.current_hp -= enemy.damage
                            enemy.alive = False
                            
                            if building.current_hp <= 0:
                                self.state.grid.destroy_building(building.id)
                                self.state.update_economy()
                            break
    
    def end_wave(self):
        """Transition back to build phase"""
        base_reward = 100 + (self.current_wave.wave_number * 25)
        
        perfect_wave = True
        for building in self.state.grid.buildings:
            if building.current_hp < building.template.max_hp:
                perfect_wave = False
                break
        
        if perfect_wave:
            base_reward = int(base_reward * 1.5)
        
        self.state.credits += base_reward
        self.state.phase = "build"
        self.current_wave = None
        self.wave_complete_timer = 0

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
    
    def __post_init__(self):
        if self.grid is None:
            self.grid = CityGrid()
        if self.combat is None:
            self.combat = CombatManager(self)
    
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
