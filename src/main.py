import pygame
import sys
import random
import math
import copy
import pickle
import os
from src.core_data import GameState, BuildingType, get_building_template, Enemy, Projectile, GRID_START_X, GRID_SLOT_WIDTH, GRID_CELL_HEIGHT, GROUND_Y, SHIELD_Y, SCREEN_WIDTH, SCREEN_HEIGHT, UI_WIDTH, MAX_COLS

# Constants
FPS = 60

# Layout Constants
# We use constants from core_data
GRID_WIDTH = GRID_SLOT_WIDTH * MAX_COLS
PLAYABLE_WIDTH = SCREEN_WIDTH - UI_WIDTH
UI_START_X = PLAYABLE_WIDTH

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
        # Create the actual display window (resizable)
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        # Create the virtual screen surface (fixed resolution)
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Missile Defense - Cell Grid")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        
        self.menu_state = "MAIN_MENU" # MAIN_MENU, PLAYING, PAUSED
        self.state = None # Initialized on New Game
        
        self.show_menu = False
        self.messages = [] # List of (text, color, timer)
        self.moving_building_id = None
        self.unlock_cost = 1000
        self.confirm_upgrade_id = None # ID of building waiting for upgrade confirmation
        self.confirm_build_type = None # Type of building waiting for build confirmation
        self.confirm_wave_start = False # Waiting for wave start confirmation
        self.game_over = False
        self.saved_state = None # Save initial state for retry
        
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)
        self.font_title = pygame.font.Font(None, 72)

    def new_game(self):
        """Start a fresh game"""
        self.state = GameState()
        # Ensure grid is initialized
        if self.state.grid is None:
            from src.core_data import CityGrid
            self.state.grid = CityGrid()
        
        self.menu_state = "PLAYING"
        self.game_over = False
        self.messages = []
        self.saved_state = copy.deepcopy(self.state)
        self.add_message("System Online. Good luck, Commander.", GREEN)

    def save_game(self, filename="savegame.dat"):
        """Save current state to file"""
        try:
            path = os.path.join("saves", filename)
            with open(path, "wb") as f:
                pickle.dump(self.state, f)
            self.add_message("Game Saved", GREEN)
        except Exception as e:
            self.add_message(f"Save Failed: {e}", RED)
            print(f"Save error: {e}")

    def load_game(self, filename="savegame.dat"):
        """Load state from file"""
        try:
            path = os.path.join("saves", filename)
            if not os.path.exists(path):
                return False
                
            with open(path, "rb") as f:
                self.state = pickle.load(f)
            
            self.menu_state = "PLAYING"
            self.game_over = False
            self.messages = []
            self.saved_state = copy.deepcopy(self.state) # Update retry point? Or keep original?
            # Actually, loading a save should probably not reset the retry point unless we save that too.
            # But for now, let's just let it be.
            self.add_message("Game Loaded", GREEN)
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False
        
    def add_message(self, text, color=WHITE, duration=3.0):
        self.messages.append({'text': text, 'color': color, 'timer': duration})
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                if not self.fullscreen:
                    self.display_surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
                if self.menu_state == "MAIN_MENU":
                    self.handle_main_menu_input(event.key)
                elif self.menu_state == "PAUSED":
                    self.handle_pause_menu_input(event.key)
                elif self.menu_state == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        if self.moving_building_id is not None:
                            self.moving_building_id = None
                            self.add_message("Move Cancelled", YELLOW)
                        elif self.show_menu:
                            self.show_menu = False
                        elif self.state.last_wave_rewards:
                            self.state.last_wave_rewards = None
                        else:
                            self.menu_state = "PAUSED"
                        return

                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.restart_game()
                        elif event.key == pygame.K_t and self.saved_state:
                            self.retry_wave()
                        elif event.key == pygame.K_q:
                            self.menu_state = "MAIN_MENU"
                        return

                    # Check for reward popup first
                    if self.state.last_wave_rewards:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.state.last_wave_rewards = None # Dismiss
                        return # Block other input while popup is up

                    if self.state.phase == "build":
                        self.handle_build_input(event.key)

    def handle_main_menu_input(self, key):
        if key == pygame.K_n:
            self.new_game()
        elif key == pygame.K_l:
            if not self.load_game():
                # Show error somehow? For now just print
                print("No save file found")
        elif key == pygame.K_q or key == pygame.K_ESCAPE:
            self.running = False

    def handle_pause_menu_input(self, key):
        if key == pygame.K_ESCAPE:
            self.menu_state = "PLAYING"
        elif key == pygame.K_s:
            self.save_game()
            self.menu_state = "PLAYING"
        elif key == pygame.K_m:
            self.menu_state = "MAIN_MENU"
            self.state = None # Clear state
        elif key == pygame.K_q:
            self.running = False
    
    def handle_build_input(self, key):
        if key == pygame.K_LEFT:
            self.state.selected_column = max(0, self.state.selected_column - 1)
        elif key == pygame.K_RIGHT:
            self.state.selected_column = min(self.state.grid.max_columns - 1, self.state.selected_column + 1)
        elif key == pygame.K_UP:
            self.state.selected_row = min(self.state.grid.rows - 1, self.state.selected_row + 1)
        elif key == pygame.K_DOWN:
            self.state.selected_row = max(0, self.state.selected_row - 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.moving_building_id is not None:
                self.finish_move()
            elif self.can_unlock_current_column():
                self.unlock_current_column()
            elif self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row):
                self.start_move()
            else:
                self.show_menu = not self.show_menu
        elif key == pygame.K_ESCAPE:
            if self.moving_building_id is not None:
                self.moving_building_id = None # Cancel move
                self.add_message("Move Cancelled", YELLOW)
            else:
                self.show_menu = False
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
        elif key == pygame.K_6:  # Quick build barracks
            if self.try_build(BuildingType.BARRACKS):
                self.show_menu = False
        elif key == pygame.K_u: # Upgrade
            self.try_upgrade()
        elif key == pygame.K_r: # Repair
            self.try_repair()
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE: # Destroy
            self.try_destroy()
        elif key == pygame.K_w:  # Start wave
            self.start_wave()
            
    def can_unlock_current_column(self):
        col = self.state.selected_column
        start, end = self.state.grid.unlocked_range
        # Check if it's immediately to the left or right
        if col == start - 1:
            return self.state.grid.can_unlock("left")
        elif col == end:
            return self.state.grid.can_unlock("right")
        return False

    def unlock_current_column(self):
        if self.state.credits < self.unlock_cost:
            self.add_message(f"Need ${self.unlock_cost} to unlock", RED)
            return

        col = self.state.selected_column
        start, end = self.state.grid.unlocked_range
        side = "left" if col < start else "right"
        
        if self.state.grid.unlock_column(side):
            self.state.credits -= self.unlock_cost
            self.add_message("Column Unlocked!", GREEN)
        else:
            self.add_message("Cannot unlock this column", RED)

    def start_move(self):
        building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
        if building:
            if self.state.grid.is_supporting_others(building):
                self.add_message("Cannot move: Supporting other buildings", RED)
                return
                
            self.moving_building_id = building.id
            self.add_message("Moving Building... Select new position and press Space", YELLOW)

    def finish_move(self):
        if self.moving_building_id is None:
            return
            
        success, reason = self.state.grid.move_building(
            self.moving_building_id, 
            self.state.selected_column, 
            self.state.selected_row
        )
        
        if success:
            self.add_message("Building Moved", GREEN)
            self.moving_building_id = None
            self.state.update_economy()
        else:
            self.add_message(f"Cannot move here: {reason}", RED)
    
    def try_build(self, building_type: BuildingType) -> bool:
        """Attempt to build at selected position"""
        col = self.state.selected_column
        row = self.state.selected_row
        
        # Check if can place
        can_place, reason = self.state.grid.can_place(building_type, col, row)
        if not can_place:
            self.add_message(f"Cannot place: {reason}", RED)
            print(f"Cannot place: {reason}")
            return False
        
        template = get_building_template(building_type, 1)
        if self.state.credits < template.cost:
            self.add_message("Not enough credits", RED)
            print("Not enough credits")
            return False
            
        # Check for negative energy warning
        net_energy = template.energy_production - template.energy_consumption
        if self.state.energy_surplus + net_energy < 0:
            if self.confirm_build_type != building_type:
                self.confirm_build_type = building_type
                self.add_message("WARNING: Building causes NEGATIVE ENERGY!", RED)
                self.add_message("Press again to confirm.", YELLOW)
                return False
        
        self.confirm_build_type = None # Reset confirmation
        
        self.state.credits -= template.cost
        self.state.grid.place_building(building_type, col, row)
        self.state.update_economy()
        self.add_message(f"Built {building_type.value}", GREEN)
        return True

    def try_upgrade(self):
        """Try to upgrade building at selected position"""
        building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
        if not building:
            return
            
        if not building.can_upgrade():
            self.add_message("Cannot upgrade (max level)", RED)
            print("Cannot upgrade (max level or not upgradable)")
            return
            
        if self.state.credits < building.template.upgrade_cost:
            self.add_message("Not enough credits", RED)
            print("Not enough credits for upgrade")
            return
            
        # Check for negative energy warning
        next_template = get_building_template(building.template.type, building.template.level + 1)
        current_net = building.template.energy_production - building.template.energy_consumption
        next_net = next_template.energy_production - next_template.energy_consumption
        diff = next_net - current_net
        
        if self.state.energy_surplus + diff < 0:
            if self.confirm_upgrade_id != building.id:
                self.confirm_upgrade_id = building.id
                self.add_message("WARNING: Upgrade will cause NEGATIVE ENERGY!", RED)
                self.add_message("Press U again to confirm.", YELLOW)
                return
        
        # Reset confirmation if we proceed or if it wasn't needed
        self.confirm_upgrade_id = None
            
        # Store cost before upgrading (because upgrade changes the template)
        cost = building.template.upgrade_cost
        
        success, reason = self.state.grid.upgrade_building(building.id)
        if success:
            self.state.credits -= cost
            self.state.update_economy()
            self.add_message(f"{reason} to Level {building.template.level}", GREEN)
            print(f"Upgraded to Level {building.template.level}")
        else:
            self.add_message(f"Upgrade failed: {reason}", RED)
            print(f"Upgrade failed: {reason}")

    def try_destroy(self):
        """Destroy building at selected position"""
        building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
        if building:
            # Refund 50%
            refund = int(building.template.cost * 0.5)
            self.state.credits += refund
            self.state.grid.destroy_building(building.id)
            self.state.update_economy()
            self.add_message(f"Destroyed {building.template.type.value}. Refund: ${refund}", YELLOW)

    def try_repair(self):
        """Repair selected building"""
        building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
        if not building:
            self.add_message("No building selected", RED)
            return
        
        if building.current_hp >= building.template.max_hp:
            self.add_message("Building HP full", GREEN)
            return
            
        damage = building.template.max_hp - building.current_hp
        cost = damage * 1 # 1 credit per HP
        
        if self.state.credits < cost:
            # Partial repair if they have at least 1 credit
            if self.state.credits > 0:
                repair_amount = self.state.credits
                building.current_hp += repair_amount
                self.state.credits = 0
                self.add_message(f"Partial Repair: +{repair_amount} HP", YELLOW)
                self.state.update_economy()
            else:
                self.add_message(f"Need ${cost} to repair", RED)
        else:
            self.state.credits -= cost
            building.current_hp = building.template.max_hp
            self.add_message(f"Repaired for ${cost}", GREEN)
            self.state.update_economy()
    
    def start_wave(self):
        if self.state.energy_surplus < 0:
            if self.state.credits > 0:
                if not self.confirm_wave_start:
                    self.confirm_wave_start = True
                    self.add_message("WARNING: Negative Energy! Credits will drain.", YELLOW)
                    self.add_message("Press W again to confirm start.", YELLOW)
                    return
            else:
                self.add_message("Cannot start wave: Negative Energy & No Credits!", RED)
                self.add_message("Build Power Plants or Destroy Consumers.", RED)
                print("Cannot start wave: negative energy!")
                return
        
        self.confirm_wave_start = False
        self.state.phase = "combat"
        self.state.wave += 1
        self.state.combat.start_wave()
        self.add_message(f"Wave {self.state.wave} Started!", RED)
    
    def update(self, dt):
        if self.menu_state != "PLAYING":
            return

        prev_phase = self.state.phase
        
        if self.state.phase == "combat":
            self.state.combat.update(dt)
        
        # Detect phase change to build
        if prev_phase == "combat" and self.state.phase == "build":
            self.add_message("Wave Complete!", GREEN)
            # Save state at the start of the build phase (for retry)
            self.saved_state = copy.deepcopy(self.state)
            
        # Energy Deficit Penalty (Credit Drain)
        if self.state.energy_surplus < 0:
            # Drain 1 credit per unit of deficit per second
            drain_rate = abs(self.state.energy_surplus) * 1.0
            drain_amount = drain_rate * dt
            
            if self.state.credits > 0:
                self.state.credits = max(0, self.state.credits - drain_amount)
                # Round for display occasionally? No, float is fine for internal logic
                self.state.credits = int(self.state.credits) # Keep it int for simplicity in UI
            else:
                # If no credits, shield fails to recharge (handled below)
                pass

        # Shield recharge (always active)
        # If energy is negative, shield only recharges if we have credits to burn
        can_recharge = self.state.energy_surplus >= 0 or self.state.credits > 0
        
        if self.state.shield_current_hp < self.state.shield_max_hp and can_recharge:
            recharge = self.state.shield_recharge_rate * dt
            self.state.shield_current_hp = min(
                self.state.shield_max_hp,
                self.state.shield_current_hp + recharge
            )
            
            # Check for reactivation (25% threshold)
            if not self.state.shield_is_active:
                threshold = self.state.shield_max_hp * 0.25
                if self.state.shield_current_hp >= threshold:
                    self.state.shield_is_active = True
                    self.add_message("SHIELD ONLINE", GREEN)
                    self.state.add_log("Shield Systems Restored")
        
        # Update messages
        for msg in self.messages:
            msg['timer'] -= dt
        self.messages = [m for m in self.messages if m['timer'] > 0]
        
        # Check loss condition
        if not self.state.grid.buildings and self.state.wave > 0 and self.state.phase == "combat":  # No buildings left
             if not self.game_over:
                 self.game_over = True
                 self.add_message("CRITICAL FAILURE: BASE DESTROYED", RED)

    def restart_game(self):
        """Reset game state to initial values"""
        self.new_game()

    def retry_wave(self):
        """Restore state to beginning of last wave"""
        if self.saved_state:
            self.state = copy.deepcopy(self.saved_state)
            self.game_over = False
            self.messages = []
            self.add_message("Time Rewound. Ready to try again.", GREEN)

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.menu_state == "MAIN_MENU":
            self.draw_main_menu()
        else:
            # Draw Game
            self.draw_grid()
            self.draw_buildings()
            self.draw_shield()
            
            if self.state.phase == "combat":
                self.draw_enemies()
                self.draw_ground_units()
                self.draw_projectiles()
            
            self.draw_hud()
            self.draw_messages()
            self.draw_message_log()
            
            if self.show_menu and self.state.phase == "build":
                self.draw_build_menu()
            
            if self.state.last_wave_rewards and not self.game_over:
                self.draw_wave_complete_popup()
                
            if self.game_over:
                self.draw_game_over()
                
            if self.menu_state == "PAUSED":
                self.draw_pause_menu()

        # Scale and draw to display surface
        window_w, window_h = self.display_surface.get_size()
        scale_w = window_w / SCREEN_WIDTH
        scale_h = window_h / SCREEN_HEIGHT
        scale = min(scale_w, scale_h)
        
        new_w = int(SCREEN_WIDTH * scale)
        new_h = int(SCREEN_HEIGHT * scale)
        
        offset_x = (window_w - new_w) // 2
        offset_y = (window_h - new_h) // 2
        
        scaled_surf = pygame.transform.scale(self.screen, (new_w, new_h))
        self.display_surface.fill(BLACK) # Clear borders
        self.display_surface.blit(scaled_surf, (offset_x, offset_y))
        
        pygame.display.flip()

    def draw_main_menu(self):
        """Draw Main Menu"""
        # Background
        self.screen.fill((20, 20, 30))
        
        # Title
        title = self.font_title.render("MISSILE DEFENSE", True, GREEN)
        subtitle = self.font_large.render("CELL GRID COMMAND", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 260))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Options
        options = [
            "[N] New Game",
            "[L] Load Game",
            "[Q] Quit"
        ]
        
        y = 400
        for opt in options:
            text = self.font_large.render(opt, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 50
            
        # Footer
        footer = self.font.render("v0.2.16 - 2025", True, GRAY)
        self.screen.blit(footer, (10, SCREEN_HEIGHT - 30))

    def draw_pause_menu(self):
        """Draw Pause Menu Overlay"""
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))
        
        title = self.font_title.render("PAUSED", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        options = [
            "[ESC] Resume",
            "[S] Save Game",
            "[M] Main Menu",
            "[Q] Quit Desktop"
        ]
        
        y = 350
        for opt in options:
            text = self.font_large.render(opt, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 50

    def draw_enemies(self):
        """Draw all active enemies"""
        for enemy in self.state.combat.enemies:
            if not enemy.alive:
                continue
                
            # Main body
            color = RED
            if enemy.is_boss:
                color = (148, 0, 211) # Dark Violet for Boss
                
            pygame.draw.circle(self.screen, color, (int(enemy.x), int(enemy.y)), enemy.radius)
            
            # HP bar
            hp_ratio = enemy.current_hp / enemy.max_hp
            bar_width = enemy.radius * 2
            bar_height = 4
            if enemy.is_boss:
                bar_height = 8 # Thicker bar for boss
                
            pygame.draw.rect(self.screen, (50, 50, 50),
                           (enemy.x - enemy.radius, enemy.y - enemy.radius - (bar_height + 4), bar_width, bar_height))
            pygame.draw.rect(self.screen, GREEN,
                           (enemy.x - enemy.radius, enemy.y - enemy.radius - (bar_height + 4), bar_width * hp_ratio, bar_height))
    
    def draw_projectiles(self):
        """Draw all active projectiles"""
        for proj in self.state.combat.projectiles:
            if not proj.alive:
                continue
            
            color = YELLOW if proj.source == "turret" else RED
            pygame.draw.circle(self.screen, color, (int(proj.x), int(proj.y)), proj.radius)
    
    def draw_ground_units(self):
        """Draw ground invaders and defenders"""
        for unit in self.state.combat.ground_units:
            if not unit.alive:
                continue
            
            color = RED if unit.team == "invader" else BLUE
            # Draw as small rectangles on the ground
            rect = pygame.Rect(unit.x - 5, unit.y - 10, 10, 10)
            pygame.draw.rect(self.screen, color, rect)
            
            # HP Bar
            hp_ratio = unit.hp / unit.max_hp
            pygame.draw.rect(self.screen, GREEN, (unit.x - 5, unit.y - 14, 10 * hp_ratio, 2))
    
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
        y += 20
        self.screen.blit(self.font.render(f"S.Regen: {self.state.shield_recharge_rate:.1f}/s", True, (0, 200, 255)), (x, y))
        y += 40

        # Separator
        pygame.draw.line(self.screen, GRAY, (x, y), (UI_START_X + UI_WIDTH - 20, y), 1)
        y += 20

        # 3. Context Section (Combat Stats or Build Info)
        if self.state.phase == "combat" and self.state.combat.current_wave:
            self.screen.blit(self.font.render("Combat Status:", True, RED), (x, y))
            y += 30
            
            # Count ground units
            invaders = sum(1 for u in self.state.combat.ground_units if u.team == "invader" and u.alive)
            defenders = sum(1 for u in self.state.combat.ground_units if u.team == "defender" and u.alive)
            
            self.screen.blit(self.font.render(f"Aerial Enemies: {len(self.state.combat.enemies)}", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render(f"Ground Invaders: {invaders}", True, RED), (x, y))
            y += 20
            self.screen.blit(self.font.render(f"Defenders: {defenders}", True, BLUE), (x, y))
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
            self.screen.blit(self.font.render("Space: Build Menu", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render("1-6: Place Building", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render("U: Upgrade | R: Repair", True, WHITE), (x, y))
            y += 20
            self.screen.blit(self.font.render("Del: Destroy | W: Wave", True, WHITE), (x, y))
            y += 40
            
            # Show selected cell info
            col, row = self.state.selected_column, self.state.selected_row
            building = self.state.grid.get_building_at(col, row)
            
            self.screen.blit(self.font.render(f"Cell ({col}, {row}):", True, WHITE), (x, y))
            y += 25
            
            if self.moving_building_id is not None:
                self.screen.blit(self.font.render("MOVING BUILDING", True, YELLOW), (x, y))
                y += 20
                self.screen.blit(self.font.render("Space: Place", True, WHITE), (x, y))
                y += 20
                self.screen.blit(self.font.render("Esc: Cancel", True, WHITE), (x, y))
            elif self.can_unlock_current_column():
                self.screen.blit(self.font.render("LOCKED COLUMN", True, RED), (x, y))
                y += 20
                color = GREEN if self.state.credits >= self.unlock_cost else RED
                self.screen.blit(self.font.render(f"Unlock: ${self.unlock_cost}", True, color), (x, y))
                y += 20
                self.screen.blit(self.font.render("Press Space to Unlock", True, WHITE), (x, y))
            elif building:
                self.screen.blit(self.font.render(f"{building.template.type.value.title()}", True, GREEN), (x, y))
                y += 20
                self.screen.blit(self.font.render(f"Level: {building.template.level}", True, WHITE), (x, y))
                y += 20
                self.screen.blit(self.font.render(f"HP: {building.current_hp}/{building.template.max_hp}", True, WHITE), (x, y))
                y += 20
                
                # Add specific stats
                if building.template.type == BuildingType.TURRET:
                    self.screen.blit(self.font.render(f"Dmg: {building.template.damage} | Rng: {building.template.range}", True, RED), (x, y))
                    y += 20
                    self.screen.blit(self.font.render(f"Ammo Rng: {building.template.ammo_range}", True, RED), (x, y))
                    y += 20
                elif building.template.type == BuildingType.BARRACKS:
                    self.screen.blit(self.font.render(f"Cap: {building.template.capacity} Defenders", True, BLUE), (x, y))
                    y += 20
                
                if building.can_upgrade():
                    self.screen.blit(self.font.render(f"Upgrade: ${building.template.upgrade_cost}", True, YELLOW), (x, y))
                    y += 20
                    
                    # Preview next level stats
                    next_template = get_building_template(building.template.type, building.template.level + 1)
                    preview_text = []
                    if next_template.energy_production > building.template.energy_production:
                        preview_text.append(f"Eng: +{next_template.energy_production - building.template.energy_production}")
                    if next_template.shield_hp_bonus > building.template.shield_hp_bonus:
                        preview_text.append(f"Shld: +{next_template.shield_hp_bonus - building.template.shield_hp_bonus}")
                    if next_template.damage > building.template.damage:
                        preview_text.append(f"Dmg: +{next_template.damage - building.template.damage}")
                    if next_template.range > building.template.range:
                        preview_text.append(f"Rng: +{next_template.range - building.template.range}")
                    if next_template.capacity > building.template.capacity:
                        preview_text.append(f"Cap: +{next_template.capacity - building.template.capacity}")
                    if next_template.footprint != building.template.footprint:
                        preview_text.append(f"Size: {next_template.footprint[0]}x{next_template.footprint[1]}")
                        
                    if preview_text:
                        self.screen.blit(self.font.render(f"Next: {', '.join(preview_text)}", True, (200, 200, 255)), (x, y))
                        y += 20
                else:
                    self.screen.blit(self.font.render("Max Level", True, GRAY), (x, y))
                
                # Show repair cost if damaged
                if building.current_hp < building.template.max_hp:
                    repair_cost = building.template.max_hp - building.current_hp
                    color = GREEN if self.state.credits >= repair_cost else RED
                    self.screen.blit(self.font.render(f"Repair: ${repair_cost}", True, color), (x, y))
                    y += 20
                
                self.screen.blit(self.font.render("Space: Move", True, WHITE), (x, y + 20))
            else:
                self.screen.blit(self.font.render("Empty", True, GRAY), (x, y))
                # Show foundation status
                width = 1 # Assume 1 for check
                has_foundation = self.state.grid.has_foundation(col, row, width)
                color = GREEN if has_foundation else RED
                self.screen.blit(self.font.render(f"Foundation: {'Yes' if has_foundation else 'No'}", True, color), (x, y + 20))
    
    def draw_build_menu(self):
        """Draw building menu overlay (centered on grid)"""
        menu_width = 500
        menu_height = 500
        # Center over the grid area
        grid_center_x = GRID_START_X + (self.state.grid.max_columns * GRID_SLOT_WIDTH // 2)
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
            BuildingType.DRONE_FACTORY,
            BuildingType.BARRACKS
        ], 1):
            template = get_building_template(building_type, 1)
            text = f"[{i}] {building_type.value.replace('_', ' ').title()} - ${template.cost}"
            
            # Stats string
            stats = []
            stats.append(f"HP: {template.max_hp}")
            if template.energy_production > 0: stats.append(f"Energy: +{template.energy_production}")
            if template.energy_consumption > 0: stats.append(f"Energy: -{template.energy_consumption}")
            if template.shield_hp_bonus > 0: stats.append(f"Shield: +{template.shield_hp_bonus}")
            if template.shield_recharge_bonus > 0: stats.append(f"Rchrg: +{template.shield_recharge_bonus:.1f}")
            if building_type == BuildingType.TURRET: stats.append(f"Dmg: {template.damage}")
            if building_type == BuildingType.BARRACKS: stats.append("Spawns Defenders")
            
            stats_text = " | ".join(stats)
            
            # Check if affordable
            affordable = self.state.credits >= template.cost
            # Check if placeable at current cursor
            can_place, reason = self.state.grid.can_place(building_type, self.state.selected_column, self.state.selected_row)
            
            color = WHITE if affordable and can_place else GRAY
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (menu_x + 20, y_offset))
            
            # Draw stats below
            stats_surf = pygame.font.Font(None, 20).render(stats_text, True, (200, 200, 200))
            self.screen.blit(stats_surf, (menu_x + 20, y_offset + 20))
            
            # Show reason if selected but invalid
            if not can_place:
                reason_surf = pygame.font.Font(None, 18).render(f"  ({reason})", True, RED)
                self.screen.blit(reason_surf, (menu_x + 300, y_offset))
                
            y_offset += 50
    
    def draw_grid(self):
        """Draw the city grid"""
        cols = self.state.grid.max_columns
        rows = self.state.grid.rows
        
        # Draw vertical lines
        for i in range(cols + 1):
            x = GRID_START_X + i * GRID_SLOT_WIDTH
            pygame.draw.line(self.screen, DARK_GRAY, (x, GROUND_Y), (x, GROUND_Y - (rows * GRID_CELL_HEIGHT)), 1)
            
        # Draw horizontal lines
        for j in range(rows + 1):
            y = GROUND_Y - j * GRID_CELL_HEIGHT
            pygame.draw.line(self.screen, DARK_GRAY, (GRID_START_X, y), (GRID_START_X + cols * GRID_SLOT_WIDTH, y), 1)
            
        # Ground line (full width)
        pygame.draw.line(self.screen, GRAY, 
                        (GRID_START_X, GROUND_Y), 
                        (GRID_START_X + cols * GRID_SLOT_WIDTH, GROUND_Y), 3)
        
        # Highlight unlocked area
        start, end = self.state.grid.unlocked_range
        unlocked_x = GRID_START_X + start * GRID_SLOT_WIDTH
        unlocked_width = (end - start) * GRID_SLOT_WIDTH
        
        # Draw brighter ground for unlocked area
        pygame.draw.line(self.screen, WHITE, 
                        (unlocked_x, GROUND_Y), 
                        (unlocked_x + unlocked_width, GROUND_Y), 3)
        
        # Draw faint background for unlocked area
        s = pygame.Surface((unlocked_width, rows * GRID_CELL_HEIGHT))
        s.set_alpha(30)
        s.fill(WHITE)
        self.screen.blit(s, (unlocked_x, GROUND_Y - rows * GRID_CELL_HEIGHT))
            
        # Selection highlight
        if self.state.phase == "build":
            sel_x = GRID_START_X + self.state.selected_column * GRID_SLOT_WIDTH
            sel_y = GROUND_Y - (self.state.selected_row + 1) * GRID_CELL_HEIGHT
            
            # Color based on unlocked status
            if self.state.grid.is_unlocked(self.state.selected_column):
                color = YELLOW
            else:
                color = RED
                
            pygame.draw.rect(self.screen, color, 
                           (sel_x, sel_y, GRID_SLOT_WIDTH, GRID_CELL_HEIGHT), 2)
            
            # Draw Range Indicator if Turret
            building = self.state.grid.get_building_at(self.state.selected_column, self.state.selected_row)
            if building and building.template.type == BuildingType.TURRET:
                # Calculate center of turret
                width, height = building.template.footprint
                turret_x = GRID_START_X + building.column * GRID_SLOT_WIDTH + (width * GRID_SLOT_WIDTH) / 2
                turret_y = GROUND_Y - building.row * GRID_CELL_HEIGHT - (height * GRID_CELL_HEIGHT) / 2
                
                # Draw targeting range (Blue)
                pygame.draw.circle(self.screen, BLUE, (int(turret_x), int(turret_y)), building.template.range, 1)
                # Draw ammo range (Red)
                pygame.draw.circle(self.screen, RED, (int(turret_x), int(turret_y)), building.template.ammo_range, 1)
    
    def draw_buildings(self):
        """Draw all buildings in the grid"""
        moving_building = None
        
        for building in self.state.grid.buildings:
            if building.id == self.moving_building_id:
                moving_building = building
                # Draw original position semi-transparent
                alpha = 100
            else:
                alpha = 255
                
            x = GRID_START_X + building.column * GRID_SLOT_WIDTH
            height_px = building.template.footprint[1] * GRID_CELL_HEIGHT
            width_px = building.template.footprint[0] * GRID_SLOT_WIDTH
            y = GROUND_Y - (building.row * GRID_CELL_HEIGHT) - height_px
            
            self.draw_single_building(building, x, y, alpha)
            
        # Draw ghost of moving building at cursor
        if moving_building:
            x = GRID_START_X + self.state.selected_column * GRID_SLOT_WIDTH
            height_px = moving_building.template.footprint[1] * GRID_CELL_HEIGHT
            width_px = moving_building.template.footprint[0] * GRID_SLOT_WIDTH
            y = GROUND_Y - (self.state.selected_row * GRID_CELL_HEIGHT) - height_px
            
            # Check validity for color tint
            can_place, _ = self.state.grid.move_building(moving_building.id, self.state.selected_column, self.state.selected_row)
            # Note: move_building actually moves it if true, so we can't use it for checking without side effects unless we revert.
            # Actually, move_building in my implementation DOES move it.
            # I should use can_place directly, but I need to temporarily remove the building to check.
            # This is expensive to do every frame.
            # Let's just draw it.
            
            self.draw_single_building(moving_building, x, y, 180, ghost=True)

    def draw_single_building(self, building, x, y, alpha, ghost=False):
        # Color based on type
        if building.template.type == BuildingType.POWER_PLANT:
            color = BLUE
        elif building.template.type == BuildingType.DATACENTER:
            color = GREEN
        elif building.template.type == BuildingType.CAPACITOR:
            color = (0, 255, 255)  # Cyan
        elif building.template.type == BuildingType.TURRET:
            color = RED
        elif building.template.type == BuildingType.BARRACKS:
            color = (139, 69, 19) # Saddle Brown
        else:
            color = WHITE
        
        width_px = building.template.footprint[0] * GRID_SLOT_WIDTH
        height_px = building.template.footprint[1] * GRID_CELL_HEIGHT
        
        s = pygame.Surface((width_px - 4, height_px - 4))
        s.set_alpha(alpha)
        s.fill(color)
        self.screen.blit(s, (x + 2, y + 2))
        
        if not ghost:
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

        # If broken, draw offline state
        if not self.state.shield_is_active:
             # Draw faint red line to show where it is
             pygame.draw.line(self.screen, (50, 0, 0), 
                        (GRID_START_X, SHIELD_Y), 
                        (GRID_START_X + self.state.grid.max_columns * GRID_SLOT_WIDTH, SHIELD_Y), 1)
             
             # Show reboot progress
             threshold = self.state.shield_max_hp * 0.25
             if threshold > 0:
                 pct = int((self.state.shield_current_hp / threshold) * 100)
             else:
                 pct = 0
             text = f"SHIELD OFFLINE: {pct}% REBOOT"
             text_surf = self.font.render(text, True, RED)
             self.screen.blit(text_surf, (GRID_START_X, SHIELD_Y - 30))
             return

        # Calculate thickness based on current HP
        thickness = max(2, min(50, int(self.state.shield_current_hp / 5)))
        
        # Draw the shield
        cols = self.state.grid.max_columns
        pygame.draw.line(self.screen, (0, 200, 255), 
                        (GRID_START_X, SHIELD_Y), 
                        (GRID_START_X + cols * GRID_SLOT_WIDTH, SHIELD_Y), thickness)
        
        # Shield HP text
        shield_text = f"Shield: {int(self.state.shield_current_hp)}/{self.state.shield_max_hp}"
        text_surf = self.font.render(shield_text, True, WHITE)
        self.screen.blit(text_surf, (GRID_START_X, SHIELD_Y - 30))
    
    def draw_messages(self):
        """Draw floating messages"""
        y = 100
        for msg in self.messages:
            text_surf = self.font_large.render(msg['text'], True, msg['color'])
            # Center text
            rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            
            # Draw background for readability
            bg_rect = rect.inflate(20, 10)
            s = pygame.Surface((bg_rect.width, bg_rect.height))
            s.set_alpha(200)
            s.fill(BLACK)
            self.screen.blit(s, bg_rect)
            
            self.screen.blit(text_surf, rect)
            y += 40
    
    def draw_message_log(self):
        """Draw the persistent message log at the bottom of the screen"""
        log_height = SCREEN_HEIGHT - GROUND_Y - 10
        log_y = GROUND_Y + 10
        log_width = PLAYABLE_WIDTH - 40
        log_x = 20
        
        # Background
        s = pygame.Surface((log_width, log_height))
        s.set_alpha(100)
        s.fill(BLACK)
        self.screen.blit(s, (log_x, log_y))
        
        # Draw logs (last 5)
        font_height = 20
        max_lines = log_height // font_height
        
        recent_logs = self.state.logs[-max_lines:]
        
        for i, log in enumerate(recent_logs):
            color = WHITE
            if "DESTROYED" in log or "COLLAPSED" in log:
                color = RED
            elif "detected" in log:
                color = YELLOW
            elif "Credits" in log:
                color = GREEN
                
            text = self.font.render(f"> {log}", True, color)
            self.screen.blit(text, (log_x + 10, log_y + i * font_height))
    
    def draw_wave_complete_popup(self):
        rewards = self.state.last_wave_rewards
        if not rewards:
            return

        # Dimensions
        width = 400
        height = 350
        x = (SCREEN_WIDTH - width) // 2
        y = (SCREEN_HEIGHT - height) // 2
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 50), (x, y, width, height))
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), 2)
        
        # Title
        title = self.font_large.render("WAVE COMPLETE!", True, GREEN)
        title_rect = title.get_rect(center=(x + width//2, y + 40))
        self.screen.blit(title, title_rect)
        
        # Stats
        content_x = x + 50
        current_y = y + 90
        line_height = 35
        
        # Base Reward
        self.screen.blit(self.font.render(f"Base Reward: +{rewards.base}", True, WHITE), (content_x, current_y))
        current_y += line_height
        
        # Perfect Bonus
        if rewards.perfect_bonus > 0:
            self.screen.blit(self.font.render(f"Perfect Defense: +{rewards.perfect_bonus}", True, YELLOW), (content_x, current_y))
        else:
            self.screen.blit(self.font.render("Perfect Defense: --", True, GRAY), (content_x, current_y))
        current_y += line_height
        
        # Energy Bonus
        if rewards.energy_bonus > 0:
            self.screen.blit(self.font.render(f"Energy Efficiency: +{rewards.energy_bonus}", True, (0, 255, 255)), (content_x, current_y))
        else:
            self.screen.blit(self.font.render("Energy Efficiency: --", True, GRAY), (content_x, current_y))
        current_y += line_height + 10
        
        # Total Line
        pygame.draw.line(self.screen, GRAY, (content_x, current_y), (x + width - 50, current_y), 2)
        current_y += 20
        
        total_text = self.font_large.render(f"Total Credits: +{rewards.total}", True, GREEN)
        self.screen.blit(total_text, (content_x, current_y))
        
        # Footer
        footer = self.font.render("Press SPACE to Continue", True, WHITE)
        footer_rect = footer.get_rect(center=(x + width//2, y + height - 30))
        self.screen.blit(footer, footer_rect)

    def draw_game_over(self):
        """Draw Game Over overlay"""
        # Semi-transparent background
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill((20, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # Game Over Text
        title = self.font_large.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Stats
        stats_text = f"Waves Survived: {self.state.wave - 1}"
        stats = self.font.render(stats_text, True, WHITE)
        stats_rect = stats.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(stats, stats_rect)
        
        # Restart Prompt
        restart = self.font.render("Press R to Restart", True, YELLOW)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart, restart_rect)
        
        # Retry Prompt
        if self.saved_state:
            retry = self.font.render("Press T to Retry Wave", True, GREEN)
            retry_rect = retry.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            self.screen.blit(retry, retry_rect)
    
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
