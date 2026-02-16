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
        
        # Grid Alignment (multiples of 8)
        px, py, pw, ph = 8, 32, 464, 232
        
        # Chunky TUI Shadow
        pygame.draw.rect(buffer, (5, 4, 3), (px + 4, py + 4, pw, ph))
        inv_panel = Panel(px, py, pw, ph, title="VAULT")
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
                body_f.draw(buffer, "INVENTORY EMPTY", px + 24, 80, COLOR_DIM)
        else:
            for i, item in enumerate(items):
                if i > 10: break
                
                y_row = 36 + i * 16
                is_sel = (i == self.selection_index)
                color = COLOR_ACCENT if is_sel else COLOR_FG
                
                if is_sel:
                    pygame.draw.rect(buffer, (40, 35, 30), (px + 8, y_row, pw - 16, 16))
                
                if body_f:
                    # x align: Qty at x=24, Name at x=64
                    qty_str = f"x{item.quantity}"
                    body_f.draw(buffer, qty_str, px + 16, y_row + 12, COLOR_DIM)
                    body_f.draw(buffer, f"{item.item_id.upper()}", px + 64, y_row + 12, color)
