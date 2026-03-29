import pygame
from ui import *

class InventoryView(BaseView):
    def __init__(self):
        super().__init__()
        self.selection_index = 0
        
        # Persistent Panel for content
        self.inv_panel = Panel(title="VAULT")
        self.add_child(self.inv_panel)

    def handle_event(self, event, mx, my):
        """Standard handle_event for custom navigation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
                return True
        return False

    def draw_view(self, buffer, context):
        """Rendering loop with dynamic inventory context detection."""
        # 1. Base widget tree draw
        super().draw_view(buffer, context)
        
        state = context.get('state', {})
        world_map = state.get('world_map')
        player_inventory = state.get('player_inventory')
        player_backpack = state.get('player_backpack')

        # Determine if we are in the Lab or Field
        active_inv = player_inventory
        title = "VAULT"
        if world_map and world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).type != 'lab':
            active_inv = player_backpack
            title = "BACKPACK"
        
        self.inv_panel.titles = [{"text": title, "color": styles.get_color("accent")}]
        
        # 2. Dynamic Item List Overlay
        if active_inv:
            items = list(active_inv.get_all().values())
            body_f = styles.get_font("Body")
            if body_f:
                for i, item in enumerate(items):
                    if i > 12: break
                    y_row = 100 + i * 16 # Approx pixel baseline for now
                    color = styles.get_color("accent") if i == self.selection_index else styles.get_color("fg")
                    body_f.draw(buffer, f"- {item.item_id} [x{item.quantity}]", 32, y_row, color)
