"""
The Alchemist's Journal - Enhanced
Discovery puzzle with expedition and economy
"""
import pygame
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'systems'))

from inventory import Inventory
from recipe_manager import RecipeManager

pygame.init()

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

# Colors
BG_COLOR = (45, 35, 25)
PARCHMENT = (230, 220, 190)
DARK_BROWN = (80, 60, 40)
GOLD = (218, 165, 32)
GREEN = (100, 200, 100)
RED = (200, 100, 100)
GRAY = (120, 120, 120)
BLUE = (80, 120, 180)

FONT_TITLE = None
FONT_NORMAL = None
FONT_SMALL = None

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The Alchemist's Journal")
        self.clock = pygame.time.Clock()
        self.running = True
        
        global FONT_TITLE, FONT_NORMAL, FONT_SMALL
        FONT_TITLE = pygame.font.Font(None, 48)
        FONT_NORMAL = pygame.font.Font(None, 28)
        FONT_SMALL = pygame.font.Font(None, 20)
        
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, 'data', 'items.json'), 'r') as f:
            self.items_data = json.load(f)
            
        self.inventory = Inventory()
        self.recipe_manager = RecipeManager(os.path.join(base_path, 'data', 'recipes.json'))
        
        # Economy
        self.gold = 100
        self.expedition_cooldown = 0
        self.expedition_duration = 5.0
        
        # Give minimal starting items
        for item_id in ['copper_ore', 'coal']:
            self.inventory.add_item(item_id, 2)
            
        self.selected_item = None
        self.message = "Gather ingredients on expeditions, craft potions, sell for gold!"
        self.message_timer = 0
        self.message_color = GOLD
        
        self.recipe_manager.check_recipe_unlock(self.inventory)
        self.show_expedition = False
        
    def draw_inventory_grid(self):
        grid_x = 50
        grid_y = 150
        slot_size = 80
        slots_per_row = 8
        padding = 10
        
        items_list = sorted(self.inventory.items.items())
        
        for idx, (item_id, count) in enumerate(items_list):
            row = idx // slots_per_row
            col = idx % slots_per_row
            
            x = grid_x + col * (slot_size + padding)
            y = grid_y + row * (slot_size + padding)
            
            is_selected = (self.selected_item == item_id)
            slot_color = GOLD if is_selected else PARCHMENT
            border_color = DARK_BROWN if not is_selected else (255, 215, 0)
            
            pygame.draw.rect(self.screen, slot_color, (x, y, slot_size, slot_size))
            pygame.draw.rect(self.screen, border_color, (x, y, slot_size, slot_size), 3)
            
            item_name = self.items_data[item_id]['name']
            name_lines = item_name.split()
            
            for line_idx, word in enumerate(name_lines[:2]):
                text = FONT_SMALL.render(word, True, DARK_BROWN)
                text_rect = text.get_rect(center=(x + slot_size//2, y + 15 + line_idx * 18))
                self.screen.blit(text, text_rect)
            
            # Sell value
            value = self.items_data[item_id].get('value', 5)
            value_text = FONT_SMALL.render(f"${value}", True, GREEN)
            self.screen.blit(value_text, (x + 5, y + 50))
            
            count_text = FONT_NORMAL.render(str(count), True, DARK_BROWN)
            count_rect = count_text.get_rect(bottomright=(x + slot_size - 5, y + slot_size - 5))
            self.screen.blit(count_text, count_rect)
            
            if not hasattr(self, 'item_rects'):
                self.item_rects = {}
            self.item_rects[item_id] = pygame.Rect(x, y, slot_size, slot_size)
    
    def draw_workbench(self):
        bench_x = 50
        bench_y = 500
        bench_width = 600
        bench_height = 150
        
        pygame.draw.rect(self.screen, PARCHMENT, (bench_x, bench_y, bench_width, bench_height))
        pygame.draw.rect(self.screen, DARK_BROWN, (bench_x, bench_y, bench_width, bench_height), 4)
        
        title = FONT_NORMAL.render("WORKBENCH: Craft or Sell", True, DARK_BROWN)
        self.screen.blit(title, (bench_x + 20, bench_y + 10))
        
        if self.selected_item:
            selected_name = self.items_data[self.selected_item]['name']
            text = FONT_SMALL.render(f"Selected: {selected_name}", True, GREEN)
            self.screen.blit(text, (bench_x + 20, bench_y + 50))
            
            # Sell button
            sell_rect = pygame.Rect(bench_x + 400, bench_y + 80, 180, 50)
            pygame.draw.rect(self.screen, GREEN, sell_rect)
            sell_text = FONT_NORMAL.render("SELL", True, PARCHMENT)
            self.screen.blit(sell_text, (sell_rect.centerx - 30, sell_rect.centery - 15))
            if not hasattr(self, 'sell_rect'):
                self.sell_rect = sell_rect
            
            hint = FONT_SMALL.render("Click another to combine, or SELL", True, GRAY)
            self.screen.blit(hint, (bench_x + 20, bench_y + 90))
    
    def draw_expedition_panel(self):
        panel_x = 670
        panel_y = 500
        panel_width = 300
        panel_height = 150
        
        pygame.draw.rect(self.screen, BLUE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, PARCHMENT, (panel_x, panel_y, panel_width, panel_height), 4)
        
        title = FONT_NORMAL.render("EXPEDITION", True, PARCHMENT)
        self.screen.blit(title, (panel_x + 60, panel_y + 10))
        
        if self.expedition_cooldown > 0:
            cooldown_text = FONT_SMALL.render(f"Exploring... {int(self.expedition_cooldown)}s", True, PARCHMENT)
            self.screen.blit(cooldown_text, (panel_x + 60, panel_y + 60))
        else:
            button_rect = pygame.Rect(panel_x + 50, panel_y + 60, 200, 60)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            btn_text = FONT_NORMAL.render("EXPLORE", True, DARK_BROWN)
            self.screen.blit(btn_text, (button_rect.centerx - 60, button_rect.centery - 15))
            self.expedition_rect = button_rect
    
    def draw_header(self):
        title = FONT_TITLE.render("The Alchemist's Journal", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 40))
        self.screen.blit(title, title_rect)
        
        recipes_count = self.recipe_manager.get_unlocked_count()
        total_recipes = len(self.recipe_manager.recipes)
        stats_text = f"Recipes: {recipes_count}/{total_recipes} | Gold: {self.gold}"
        stats = FONT_NORMAL.render(stats_text, True, PARCHMENT)
        self.screen.blit(stats, (50, 90))
        
    def draw_message(self):
        if self.message_timer > 0:
            message_surf = FONT_NORMAL.render(self.message, True, self.message_color)
            message_rect = message_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
            self.screen.blit(message_surf, message_rect)
            
    def show_message(self, text, color=GOLD, duration=180):
        self.message = text
        self.message_color = color
        self.message_timer = duration
        
    def start_expedition(self):
        if self.expedition_cooldown > 0:
            return
        
        # Costs gold to explore
        if self.gold < 20:
            self.show_message("Need 20 gold to explore!", RED)
            return
            
        self.gold -= 20
        self.expedition_cooldown = self.expedition_duration
        self.show_message("Exploring...", BLUE)
    
    def complete_expedition(self):
        # Grant 3 random ingredients
        import random
        possible_items = ['copper_ore', 'tin_ore', 'iron_ore', 'coal', 'water', 'salt']
        found_items = random.sample(possible_items, 3)
        
        for item in found_items:
            self.inventory.add_item(item, random.randint(1, 3))
        
        self.recipe_manager.check_recipe_unlock(self.inventory)
        self.show_message(f"Found: {', '.join([self.items_data[i]['name'] for i in found_items])}", GREEN)
    
    def sell_item(self):
        if not self.selected_item:
            return
        
        value = self.items_data[self.selected_item].get('value', 5)
        self.inventory.remove_item(self.selected_item, 1)
        self.gold += value
        self.show_message(f"Sold for {value} gold!", GREEN)
        self.selected_item = None
        
    def handle_click(self, pos):
        # Check sell button
        if hasattr(self, 'sell_rect') and self.sell_rect.collidepoint(pos) and self.selected_item:
            self.sell_item()
            return
        
        # Check expedition button
        if hasattr(self, 'expedition_rect') and self.expedition_rect.collidepoint(pos):
            self.start_expedition()
            return
            
        if not hasattr(self, 'item_rects'):
            return
            
        for item_id, rect in self.item_rects.items():
            if rect.collidepoint(pos):
                if self.selected_item is None:
                    self.selected_item = item_id
                    self.show_message(f"Selected {self.items_data[item_id]['name']}", GREEN)
                else:
                    success, output, recipe = self.recipe_manager.try_craft(
                        self.selected_item, item_id, self.inventory
                    )
                    
                    if success:
                        self.inventory.remove_item(self.selected_item, 1)
                        self.inventory.remove_item(item_id, 1)
                        self.inventory.add_item(output, 1)
                        
                        new_unlocks = self.recipe_manager.check_recipe_unlock(self.inventory)
                        
                        output_name = self.items_data[output]['name']
                        if new_unlocks:
                            self.show_message(f"Created {output_name}! +{len(new_unlocks)} recipes!", GREEN)
                        else:
                            self.show_message(f"Created {output_name}!", GREEN)
                    else:
                        self.show_message("These don't combine...", RED)
                    
                    self.selected_item = None
                break
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
            
            # Update expedition cooldown
            if self.expedition_cooldown > 0:
                self.expedition_cooldown -= dt
                if self.expedition_cooldown <= 0:
                    self.complete_expedition()
            
            if self.message_timer > 0:
                self.message_timer -= 1
            
            self.screen.fill(BG_COLOR)
            self.draw_header()
            self.draw_inventory_grid()
            self.draw_workbench()
            self.draw_expedition_panel()
            self.draw_message()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
