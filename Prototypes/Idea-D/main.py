"""
The Crucible - Roguelike Survival Crafter
Wave-based combat with crafting between rounds
"""
import pygame
import math
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

# Colors
BG_COLOR = (20, 20, 30)
PLAYER_COLOR = (100, 200, 255)
ENEMY_COLOR = (255, 80, 80)
WEAPON_COLOR = (200, 200, 50)
UI_BG = (40, 40, 50)
UI_TEXT = (220, 220, 220)
DAY_TINT = (255, 240, 200)
NIGHT_TINT = (100, 100, 150)

class GamePhase(Enum):
    DAY = 1
    NIGHT = 2
    GAME_OVER = 3

class Weapon:
    def __init__(self, name, damage, attack_speed, durability, weight):
        self.name = name
        self.damage = damage
        self.attack_speed = attack_speed  # Attacks per second
        self.durability = durability
        self.max_durability = durability
        self.weight = weight
        self.attack_timer = 0
        
    def can_attack(self, dt):
        self.attack_timer += dt
        cooldown = 1.0 / self.attack_speed
        if self.attack_timer >= cooldown:
            self.attack_timer = 0
            self.durability -= 1
            return True
        return False
    
    def is_broken(self):
        return self.durability <= 0

class Enemy:
    def __init__(self, x, y, health, speed, damage):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.radius = 15
        self.alive = True
        
    def move_towards(self, target_x, target_y, dt):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.health = 100
        self.max_health = 100
        self.speed = 200
        self.radius = 20
        self.weapon = Weapon("Fists", 5, 1.0, 999, 0.5)
        
    def move(self, dx, dy, dt):
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        
        # Keep in bounds
        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health > 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The Crucible - Roguelike Crafter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.phase = GamePhase.DAY
        self.player = Player()
        self.enemies = []
        self.wave_number = 1
        self.day_timer = 30.0
        self.best_wave = 0
        
        # Recipes
        self.recipes = {
            "1": {"name": "Copper Sword", "damage": 15, "speed": 1.5, "dur": 50, "weight": 2.0},
            "2": {"name": "Bronze Axe", "damage": 25, "speed": 0.8, "dur": 60, "weight": 3.5},
            "3": {"name": "Iron Blade", "damage": 20, "speed": 2.0, "dur": 40, "weight": 1.8},
        }
    
    def start_night_phase(self):
        self.phase = GamePhase.NIGHT
        self.spawn_wave()
    
    def spawn_wave(self):
        self.enemies = []
        enemy_count = 3 + self.wave_number * 2
        
        for i in range(enemy_count):
            # Spawn at edges
            side = random.randint(0, 3)
            if side == 0:  # Top
                x, y = random.randint(0, WINDOW_WIDTH), 0
            elif side == 1:  # Right
                x, y = WINDOW_WIDTH, random.randint(0, WINDOW_HEIGHT)
            elif side == 2:  # Bottom
                x, y = random.randint(0, WINDOW_WIDTH), WINDOW_HEIGHT
            else:  # Left
                x, y = 0, random.randint(0, WINDOW_HEIGHT)
            
            health = 20 + self.wave_number * 5
            speed = 50 + self.wave_number * 10
            damage = 5 + self.wave_number * 2
            
            self.enemies.append(Enemy(x, y, health, speed, damage))
    
    def start_day_phase(self):
        self.phase = GamePhase.DAY
        self.day_timer = 30.0
        self.wave_number += 1
        self.player.health = min(self.player.max_health, self.player.health + 20)  # Heal a bit
    
    def craft_weapon(self, recipe_key):
        if recipe_key in self.recipes:
            recipe = self.recipes[recipe_key]
            self.player.weapon = Weapon(
                recipe["name"],
                recipe["damage"],
                recipe["speed"],
                recipe["dur"],
                recipe["weight"]
            )
    
    def update(self, dt):
        if self.phase == GamePhase.DAY:
            self.day_timer -= dt
            if self.day_timer <= 0:
                self.start_night_phase()
        
        elif self.phase == GamePhase.NIGHT:
            # Move enemies
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.move_towards(self.player.x, self.player.y, dt)
                    
                    # Check collision with player
                    dx = self.player.x - enemy.x
                    dy = self.player.y - enemy.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < self.player.radius + enemy.radius:
                        if not self.player.take_damage(enemy.damage * dt):
                            self.phase = GamePhase.GAME_OVER
                            self.best_wave = max(self.best_wave, self.wave_number)
            
            # Check if wave complete
            if all(not e.alive for e in self.enemies):
                self.start_day_phase()
    
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        # Movement
        dx = dy = 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        self.player.move(dx, dy, dt)
        
        # Crafting during day
        if self.phase == GamePhase.DAY:
            if keys[pygame.K_1]: self.craft_weapon("1")
            if keys[pygame.K_2]: self.craft_weapon("2")
            if keys[pygame.K_3]: self.craft_weapon("3")
        
        # Attack during night
        if self.phase == GamePhase.NIGHT:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0]:  # Left click
                if self.player.weapon.can_attack(dt):
                    self.attack_nearest_enemy(mouse_x, mouse_y)
    
    def attack_nearest_enemy(self, aim_x, aim_y):
        # Find enemy in attack direction
        closest = None
        closest_dist = 150  # Attack range
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Check if enemy is in direction of aim
            aim_dx = aim_x - self.player.x
            aim_dy = aim_y - self.player.y
            aim_dist = math.sqrt(aim_dx*aim_dx + aim_dy*aim_dy)
            
            if aim_dist > 0:
                dot = (dx * aim_dx + dy * aim_dy) / (dist * aim_dist)
                if dot > 0.7 and dist < closest_dist:  # Within cone
                    closest = enemy
                    closest_dist = dist
        
        if closest:
            closest.take_damage(self.player.weapon.damage)
    
    def draw(self):
        # Background
        tint = DAY_TINT if self.phase == GamePhase.DAY else NIGHT_TINT
        bg = tuple(int(BG_COLOR[i] * tint[i] / 255) for i in range(3))
        self.screen.fill(bg)
        
        # Player
        pygame.draw.circle(self.screen, PLAYER_COLOR, (int(self.player.x), int(self.player.y)), self.player.radius)
        
        # Weapon indicator
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.player.y, mouse_x - self.player.x)
        weapon_x = self.player.x + math.cos(angle) * 30
        weapon_y = self.player.y + math.sin(angle) * 30
        pygame.draw.line(self.screen, WEAPON_COLOR, (self.player.x, self.player.y), (weapon_x, weapon_y), 5)
        
        # Enemies
        for enemy in self.enemies:
            if enemy.alive:
                pygame.draw.circle(self.screen, ENEMY_COLOR, (int(enemy.x), int(enemy.y)), enemy.radius)
                # Health bar
                bar_width = 30
                health_pct = enemy.health / enemy.max_health
                pygame.draw.rect(self.screen, (100, 100, 100), (enemy.x - 15, enemy.y - 25, bar_width, 5))
                pygame.draw.rect(self.screen, (0, 255, 0), (enemy.x - 15, enemy.y - 25, bar_width * health_pct, 5))
        
        # UI
        self.draw_ui()
    
    def draw_ui(self):
        # Top bar
        pygame.draw.rect(self.screen, UI_BG, (0, 0, WINDOW_WIDTH, 80))
        
        # Health
        health_text = self.font_medium.render(f"HP: {int(self.player.health)}/{self.player.max_health}", True, UI_TEXT)
        self.screen.blit(health_text, (20, 20))
        
        # Wave
        wave_text = self.font_medium.render(f"Wave: {self.wave_number}", True, UI_TEXT)
        self.screen.blit(wave_text, (250, 20))
        
        # Weapon
        weapon_text = self.font_small.render(f"{self.player.weapon.name} | DMG:{self.player.weapon.damage} SPD:{self.player.weapon.attack_speed:.1f} DUR:{self.player.weapon.durability}/{self.player.weapon.max_durability}", True, UI_TEXT)
        self.screen.blit(weapon_text, (500, 25))
        
        # Phase indicator
        if self.phase == GamePhase.DAY:
            timer_text = self.font_large.render(f"DAY - Craft! {int(self.day_timer)}s", True, (255, 200, 100))
            self.screen.blit(timer_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 250))
            
            # Recipe hints
            y_offset = WINDOW_HEIGHT - 150
            hint_text = self.font_small.render("Press 1-3 to craft:", True, UI_TEXT)
            self.screen.blit(hint_text, (20, y_offset))
            
            for key, recipe in self.recipes.items():
                y_offset += 30
                recipe_text = self.font_small.render(f"[{key}] {recipe['name']} - DMG:{recipe['damage']} SPD:{recipe['speed']}", True, UI_TEXT)
                self.screen.blit(recipe_text, (40, y_offset))
        
        elif self.phase == GamePhase.NIGHT:
            enemies_left = sum(1 for e in self.enemies if e.alive)
            night_text = self.font_medium.render(f"NIGHT - Enemies: {enemies_left}", True, (255, 100, 100))
            self.screen.blit(night_text, (20, 50))
        
        elif self.phase == GamePhase.GAME_OVER:
            game_over = self.font_large.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(game_over, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50))
            
            wave_reached = self.font_medium.render(f"Wave Reached: {self.wave_number}", True, UI_TEXT)
            self.screen.blit(wave_reached, (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2))
            
            best = self.font_medium.render(f"Best: {self.best_wave}", True, (100, 255, 100))
            self.screen.blit(best, (WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 40))
            
            restart = self.font_small.render("Press R to restart", True, UI_TEXT)
            self.screen.blit(restart, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 100))
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r and self.phase == GamePhase.GAME_OVER:
                        self.__init__()  # Restart
            
            # Update
            if self.phase != GamePhase.GAME_OVER:
                self.handle_input(dt)
                self.update(dt)
            
            # Draw
            self.draw()
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
