import pygame
from ui_components import Panel, styles

class InventoryView:
    def __init__(self):
        self.selection_index = 0

    def handle_event(self, event, game_state):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
                return True
        return False

    def draw(self, buffer, game_state):
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        
        inv_panel = Panel(10, 40, 460, 220, title="RESOURCE VAULT")
        inv_panel.draw(buffer)
        
        world_map = game_state['world_map']
        player_inventory = game_state['player_inventory']
        player_backpack = game_state['player_backpack']

        active_inv = player_inventory
        if world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).type != 'lab':
            active_inv = player_backpack
        
        items = list(active_inv.get_all().values())
        body_f = styles.get_font("Body")
        if not items:
            if body_f:
                body_f.draw(buffer, "INVENTORY EMPTY", 30, 70, COLOR_DIM)
        else:
            for i, item in enumerate(items):
                if i > 10: break
                color = COLOR_FG
                if i == self.selection_index:
                    color = COLOR_ACCENT
                    pygame.draw.rect(buffer, (40, 35, 30), (15, 60 + i*16, 450, 16))
                
                if body_f:
                    body_f.draw(buffer, f"x{item.quantity} {item.item_id.upper()}", 25, 72 + i*16, color)
