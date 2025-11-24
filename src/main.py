import pygame
import sys
import random
import math
from src.core_data import GameState, BuildingType, get_building_template, Enemy, Projectile, GRID_START_X, GRID_SLOT_WIDTH, GRID_CELL_HEIGHT, GROUND_Y, SHIELD_Y, SCREEN_WIDTH, SCREEN_HEIGHT

# Constants
FPS = 60

# Layout Constants
GRID_WIDTH = GRID_SLOT_WIDTH * 16 # Max columns
UI_START_X = GRID_START_X + (GRID_SLOT_WIDTH * 8) + 20 # Start UI after unlocked columns initially, or just fixed
UI_START_X = 800 # Fixed right side
UI_WIDTH = SCREEN_WIDTH - UI_START_X - 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Missile Defense - Cell Grid")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = GameState()
        # Ensure grid is initialized
        if self.state.grid is None:
            from src.core_data import CityGrid
            self.state.grid = CityGrid()
            
        self.show_menu = False
        
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state.phase == "build":
                    self.handle_build_input(event.key)
    
    def handle_build_input(self, key):
        if key == pygame.K_LEFT:
            self.state.selected_column = max(0, self.state.selected_column - 1)
        elif key == pygame.K_RIGHT:
            self.state.selected_column = min(self.state.grid.unlocked_columns - 1, self.state.selected_column + 1)
        elif key == pygame.K_UP:
            self.state.selected_row = min(self.state.grid.rows - 1, self.state.selected_row + 1)
        elif key == pygame.K_DOWN:
            self.state.selected_row = max(0, self.state.selected_row - 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.show_menu = not self.show_menu
        elif key == pygame.K_1:  # Quick build power plant
            if self.try_build(BuildingType.POWER_PLANT):
                self.show_menu = False
        elif key == pygame.K_2:  # Quick build datacenter
            if self.try_build(BuildingType.DATACENTER):
                self.show_menu = False
        elif key == pygame.K_3:  # Quick build capacitor
            if self.try_build(BuildingType.CAPACITOR):
                self.show_menu = False
        elif key == pygame.K_4:  # Quick build turret
            if self.try_build(BuildingType.TURRET):
                self.show_menu = False
        elif key == pygame.K_5:  # Quick build drone factory
            if self.try_build(BuildingType.DRONE_FACTORY):
                self.show_menu = False
        elif key == pygame.K_u: # Upgrade
            self.try_upgrade()
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE: # Destroy
            self.try_destroy()
        elif key == pygame.K_w:  # Start wave
            self.start_wave()
    
    def try_build(self, building_type: BuildingType) -> bool:
        """Attempt to build at selected position"""
        col = self.state.selected_column
        row = self.state.selected_row
        
        # Check if can place
        can_place, reason = self.state.grid.can_place(building_type, col, row)
        if not can_place:
            print(f"Cannot place: {reason}")
            return False
        
        template = get_building_template(building_type, 1)
        if self.state.credits < template.cost:
            print("Not enough credits")
            return False
        
        self.state.credits -= template.cost
        self.state.grid.place_building(building_type, col, row)
        self.state.update_economy()
        return True

    def try_upgrade(self):
        """Try to upgrade building at selected position"""
        building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
        if not building:
            return
            
        if not building.can_upgrade():
            print("Cannot upgrade (max level or not upgradable)")
            return
            
        if self.state.credits < building.template.upgrade_cost:
            print("Not enough credits for upgrade")
            return
            
        if self.state.grid.upgrade_building(building.id):
            self.state.credits -= building.template.upgrade_cost
            self.state.update_economy()
            print(f"Upgraded to Level {building.template.level}")
        else:
            print("Upgrade failed (space blocked?)")

    def try_destroy(self):
        """Destroy building at selected position"""
        building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
        if building:
            self.state.grid.destroy_building(building.id)
            self.state.update_economy()
    
    def start_wave(self):
        if self.state.energy_surplus < 0:
            print("Cannot start wave: negative energy!")
            return
        self.state.phase = "combat"
        self.state.wave += 1
        self.state.combat.start_wave()
    
    def update(self, dt):
        if self.state.phase == "combat":
            self.state.combat.update(dt)
            
        # Shield recharge (always active)
        if self.state.shield_current_hp < self.state.shield_max_hp and self.state.energy_surplus >= 0:
            recharge = self.state.shield_recharge_rate * dt
            self.state.shield_current_hp = min(
                self.state.shield_max_hp,
                self.state.shield_current_hp + recharge
            )
        
        # Check loss condition
        if not self.state.grid.buildings and self.state.wave > 0 and self.state.phase == "combat":  # No buildings left
             # Only game over if we had buildings and lost them all? 
             # Or maybe if we have 0 credits and 0 buildings?
             pass

    def draw(self):
        self.screen.fill(BLACK)
        
        self.draw_grid()
        self.draw_buildings()
        self.draw_shield()
        
        if self.state.phase == "combat":
            self.draw_enemies()
            self.draw_projectiles()
        
        self.draw_hud()
        
        if self.show_menu and self.state.phase == "build":
            self.draw_build_menu()
        
        pygame.display.flip()

    def draw_enemies(self):
        """Draw all active enemies"""
        for enemy in self.state.combat.enemies:
            if not enemy.alive:
                continue
                
            # Main body
            pygame.draw.circle(self.screen, RED, (int(enemy.x), int(enemy.y)), enemy.radius)
            
            # HP bar
            hp_ratio = enemy.current_hp / enemy.max_hp
            bar_width = enemy.radius * 2
            bar_height = 4
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (enemy.x - enemy.radius, enemy.y - enemy.radius - 8, bar_width, bar_height))
            pygame.draw.rect(self.screen, GREEN,
                           (enemy.x - enemy.radius, enemy.y - enemy.radius - 8, bar_width * hp_ratio, bar_height))
    
    def draw_projectiles(self):
        """Draw all active projectiles"""
        for proj in self.state.combat.projectiles:
            if not proj.alive:
                continue
            
            color = YELLOW if proj.source == "turret" else RED
            pygame.draw.circle(self.screen, color, (int(proj.x), int(proj.y)), proj.radius)
    
    def draw_hud(self):
        """Draw UI elements in the right-side panel"""
        # Draw Panel Background
        pygame.draw.rect(self.screen, (30, 30, 30), 
                        (UI_START_X, 0, UI_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, GRAY, (UI_START_X, 0), (UI_START_X, SCREEN_HEIGHT), 2)
        
        # 1. Global Stats Section (Top)
        y = 20
        x = UI_START_X + 20
        
        # Credits
        credits_text = self.font_large.render(f"Credits: {self.state.credits}", True, GREEN)
        self.screen.blit(credits_text, (x, y))
        y += 40
        
        # Wave Info
        wave_text = self.font.render(f"Wave: {self.state.wave}", True, WHITE)
        self.screen.blit(wave_text, (x, y))
        y += 30
        
        # Phase
        phase_color = YELLOW if self.state.phase == "build" else RED
        phase_text = self.font.render(f"Phase: {self.state.phase.upper()}", True, phase_color)
        self.screen.blit(phase_text, (x, y))
        y += 40
        
        # Separator
        pygame.draw.line(self.screen, GRAY, (x, y), (UI_START_X + UI_WIDTH - 20, y), 1)
        y += 20

        # 2. Economy Section
        energy_color = GREEN if self.state.energy_surplus >= 0 else RED
        self.screen.blit(self.font.render("Energy Grid:", True, WHITE), (x, y))
        y += 25
        self.screen.blit(self.font.render(f"Prod: {self.state.energy_production}", True, GREEN), (x, y))
        y += 20
        self.screen.blit(self.font.render(f"Cons: {self.state.energy_consumption}", True, RED), (x, y))
        y += 20
        self.screen.blit(self.font.render(f"Net:  {self.state.energy_surplus}", True, energy_color), (x, y))
        y += 40

        # Separator
        pygame.draw.line(self.screen, GRAY, (x, y), (UI_START_X + UI_WIDTH - 20, y), 1)
        y += 20

        # 3. Context Section (Combat Stats or Build Info)
        if self.state.phase == "combat" and self.state.combat.current_wave:
            self.screen.blit(self.font.render("Combat Status:", True, RED), (x, y))
            y += 30
            self.screen.blit(self.font.render(f"Enemies Active: {len(self.state.combat.enemies)}", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render(f"Incoming: {self.state.combat.current_wave.enemies_remaining}", True, WHITE), (x, y))
            y += 20
            
            # Shield Status
            shield_pct = int((self.state.shield_current_hp / self.state.shield_max_hp) * 100) if self.state.shield_max_hp > 0 else 0
            self.screen.blit(self.font.render(f"Shield Integrity: {shield_pct}%", True, (0, 200, 255)), (x, y))
            
        elif self.state.phase == "build":
            self.screen.blit(self.font.render("Build Mode:", True, YELLOW), (x, y))
            y += 30
            self.screen.blit(self.font.render("Controls:", True, GRAY), (x, y))
            y += 20
            self.screen.blit(self.font.render("Arrows: Move Cursor", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render("1-5: Place Building", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render("U: Upgrade | Del: Destroy", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render("W: Start Wave", True, WHITE), (x, y))
            y += 40
            
            # Show selected cell info
            col, row = self.state.selected_column, self.state.selected_row
            building = self.state.grid.get_building_at(col, row)
            
            self.screen.blit(self.font.render(f"Cell ({col}, {row}):", True, WHITE), (x, y))
            y += 25
            
            if building:
                self.screen.blit(self.font.render(f"{building.template.type.value.title()}", True, GREEN), (x, y))
                y += 20
                self.screen.blit(self.font.render(f"Level: {building.template.level}", True, WHITE), (x, y))
                y += 20
                self.screen.blit(self.font.render(f"HP: {building.current_hp}/{building.template.max_hp}", True, WHITE), (x, y))
                y += 20
                if building.can_upgrade():
                    self.screen.blit(self.font.render(f"Upgrade: ${building.template.upgrade_cost}", True, YELLOW), (x, y))
                else:
                    self.screen.blit(self.font.render("Max Level", True, GRAY), (x, y))
            else:
                self.screen.blit(self.font.render("Empty", True, GRAY), (x, y))
                # Show foundation status
                width = 1 # Assume 1 for check
                has_foundation = self.state.grid.has_foundation(col, row, width)
                color = GREEN if has_foundation else RED
                self.screen.blit(self.font.render(f"Foundation: {'Yes' if has_foundation else 'No'}", True, color), (x, y + 20))
    
    def draw_build_menu(self):
        """Draw building menu overlay (centered on grid)"""
        menu_width = 350
        menu_height = 450
        # Center over the grid area
        grid_center_x = GRID_START_X + (self.state.grid.unlocked_columns * GRID_SLOT_WIDTH // 2)
        menu_x = grid_center_x - (menu_width // 2)
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        # Background
        pygame.draw.rect(self.screen, (30, 30, 30), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title = self.font_large.render("Build Menu", True, WHITE)
        self.screen.blit(title, (menu_x + 20, menu_y + 20))
        
        # Building options
        y_offset = menu_y + 70
        for i, building_type in enumerate([
            BuildingType.POWER_PLANT,
            BuildingType.DATACENTER,
            BuildingType.CAPACITOR,
            BuildingType.TURRET,
            BuildingType.DRONE_FACTORY
        ], 1):
            template = get_building_template(building_type, 1)
            text = f"[{i}] {building_type.value.replace('_', ' ').title()} - ${template.cost}"
            
            # Check if affordable
            affordable = self.state.credits >= template.cost
            # Check if placeable at current cursor
            can_place, reason = self.state.grid.can_place(building_type, self.state.selected_column, self.state.selected_row)
            
            color = WHITE if affordable and can_place else GRAY
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (menu_x + 20, y_offset))
            
            # Show reason if selected but invalid
            if not can_place:
                reason_surf = pygame.font.Font(None, 18).render(f"  ({reason})", True, RED)
                self.screen.blit(reason_surf, (menu_x + 20, y_offset + 20))
                y_offset += 15
                
            y_offset += 40
    
    def draw_grid(self):
        """Draw the city grid"""
        cols = self.state.grid.unlocked_columns
        rows = self.state.grid.rows
        
        # Draw vertical lines
        for i in range(cols + 1):
            x = GRID_START_X + i * GRID_SLOT_WIDTH
            pygame.draw.line(self.screen, DARK_GRAY, (x, GROUND_Y), (x, GROUND_Y - (rows * GRID_CELL_HEIGHT)), 1)
            
        # Draw horizontal lines
        for j in range(rows + 1):
            y = GROUND_Y - j * GRID_CELL_HEIGHT
            pygame.draw.line(self.screen, DARK_GRAY, (GRID_START_X, y), (GRID_START_X + cols * GRID_SLOT_WIDTH, y), 1)
            
        # Ground line
        pygame.draw.line(self.screen, GRAY, 
                        (GRID_START_X, GROUND_Y), 
                        (GRID_START_X + cols * GRID_SLOT_WIDTH, GROUND_Y), 3)
            
        # Selection highlight
        sel_x = GRID_START_X + self.state.selected_column * GRID_SLOT_WIDTH
        sel_y = GROUND_Y - (self.state.selected_row + 1) * GRID_CELL_HEIGHT
        pygame.draw.rect(self.screen, YELLOW, 
                       (sel_x, sel_y, GRID_SLOT_WIDTH, GRID_CELL_HEIGHT), 2)
    
    def draw_buildings(self):
        """Draw all buildings in the grid"""
        for building in self.state.grid.buildings:
            x = GRID_START_X + building.column * GRID_SLOT_WIDTH
            # y is top-left of the rect
            # building.row is bottom row index. 
            # If row=0, bottom is GROUND_Y. Top is GROUND_Y - height.
            height_px = building.template.footprint[1] * GRID_CELL_HEIGHT
            width_px = building.template.footprint[0] * GRID_SLOT_WIDTH
            
            y = GROUND_Y - (building.row * GRID_CELL_HEIGHT) - height_px
            
            # Color based on type
            if building.template.type == BuildingType.POWER_PLANT:
                color = BLUE
            elif building.template.type == BuildingType.DATACENTER:
                color = GREEN
            elif building.template.type == BuildingType.CAPACITOR:
                color = (0, 255, 255)  # Cyan
            elif building.template.type == BuildingType.TURRET:
                color = RED
            else:
                color = WHITE
            
            # Draw building rectangle
            pygame.draw.rect(self.screen, color, 
                           (x + 2, y + 2, width_px - 4, height_px - 4))
            
            # Draw border/details
            pygame.draw.rect(self.screen, WHITE, 
                           (x + 2, y + 2, width_px - 4, height_px - 4), 1)
            
            # HP bar
            hp_ratio = building.current_hp / building.template.max_hp
            hp_bar_width = (width_px - 10) * hp_ratio
            pygame.draw.rect(self.screen, GREEN, 
                           (x + 5, y + 5, hp_bar_width, 4))
    
    def draw_shield(self):
        """Draw shield line with variable thickness based on HP"""
        if self.state.shield_max_hp <= 0:
            return

        # Calculate thickness based on current HP
        thickness = max(2, min(50, int(self.state.shield_current_hp / 5)))
        
        # Draw the shield
        cols = self.state.grid.unlocked_columns
        pygame.draw.line(self.screen, (0, 200, 255), 
                        (GRID_START_X, SHIELD_Y), 
                        (GRID_START_X + cols * GRID_SLOT_WIDTH, SHIELD_Y), thickness)
        
        # Shield HP text
        shield_text = f"Shield: {int(self.state.shield_current_hp)}/{self.state.shield_max_hp}"
        text_surf = self.font.render(shield_text, True, WHITE)
        self.screen.blit(text_surf, (GRID_START_X, SHIELD_Y - 30))
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_input()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
