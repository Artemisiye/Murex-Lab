import pygame
from ui_components import Panel, styles

class MapView:
    def __init__(self):
        self.selection_index = 0
        self.active_region = None

    def handle_event(self, event, game_state):
        world_map = game_state['world_map']
        
        # Navigation logic (shared between keys and mouse)
        def do_move(dx, dy):
            if self.active_region:
                self.active_region.move_player(dx, dy)
            else:
                world_map.move_player(dx, dy)

        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP: dy = -1
            if event.key == pygame.K_DOWN: dy = 1
            if event.key == pygame.K_LEFT: dx = -1
            if event.key == pygame.K_RIGHT: dx = 1
            
            if dx != 0 or dy != 0:
                do_move(dx, dy)
                return True

            # Confirm / Cancel
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if self.active_region:
                    rx, ry = self.active_region.player_pos['x'], self.active_region.player_pos['y']
                    loot = self.active_region.harvest(rx, ry)
                    if not loot:
                        loot = self.active_region.hunt(rx, ry)
                    
                    if loot:
                        inv = game_state['player_inventory'] if world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).type == 'lab' else game_state['player_backpack']
                        import random
                        for item_id in loot:
                            inv.add_item(item_id, random.randint(1, 2))
                        print(f"Looted: {loot}")
                else:
                    cell = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y'])
                    if cell:
                        if cell.type == 'lab':
                            return "GOTO_WORKSHOP"
                        else:
                            self.active_region = world_map.enter_regional_map()
                return True
            
            if event.key == pygame.K_BACKSPACE:
                if self.active_region:
                    self.active_region = None
                    return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                mx, my = event.pos
                scale = game_state.get('scale', 1)
                vx, vy = mx // scale, my // scale
                
                margin = 5
                py_base = 270 - margin # buffer height is 270
                
                nav_rects = {
                    "up":    pygame.Rect(margin + 21, py_base - 28, 7, 7),
                    "down":  pygame.Rect(margin + 21, py_base - 13, 7, 7),
                    "left":  pygame.Rect(margin + 6,  py_base - 13, 7, 7),
                    "right": pygame.Rect(margin + 36, py_base - 13, 7, 7)
                }
                
                for direction, rect in nav_rects.items():
                    if rect.inflate(4, 4).collidepoint(vx, vy): # Slightly larger hitbox for comfort
                        dx, dy = 0, 0
                        if direction == "up": dy = -1
                        elif direction == "down": dy = 1
                        elif direction == "left": dx = -1
                        elif direction == "right": dx = 1
                        do_move(dx, dy)
                        return True

        return False

    def draw(self, buffer, game_state):
        world_map = game_state['world_map']
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        
        body_f = styles.get_font("Body")
        small_f = styles.get_font("Small")
        h2_f = styles.get_font("H2")

        if not hasattr(self, 'arrows') or self.arrows is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            asset_path = os.path.join(base_dir, "assets", "arrows2.png")
            try:
                self.arrow_atlas = pygame.image.load(asset_path).convert_alpha()
                # Use 7x7 set from the atlas based on exact USER mapping:
                self.arrows = {
                    "down":  self.arrow_atlas.subsurface((1, 10, 7, 7)),
                    "right": self.arrow_atlas.subsurface((9, 10, 7, 7)),
                    "up":    self.arrow_atlas.subsurface((17, 10, 7, 7)),
                    "left":  self.arrow_atlas.subsurface((25, 10, 7, 7))
                }
                print(f"SUCCESS: Loaded 7px arrow sprites (Mapping Fixed) from {asset_path}")
            except Exception as e:
                print(f"ERROR: Sprite load failed from {asset_path}: {e}")
                self.arrow_atlas = None
                self.arrows = None

        margin = 5
        content_w = buffer.get_width() - (margin * 2)
        content_h = buffer.get_height() - (margin + 35) # Below header
        
        if self.active_region:
            reg_panel = Panel(margin, 35, content_w, content_h, 
                             title=f"REGIONAL: {world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).type.upper()}")
            reg_panel.draw(buffer)
            
            cell_size = 18
            gx, gy = margin + 20, 70
            for y in range(self.active_region.size):
                for x in range(self.active_region.size):
                    rect = pygame.Rect(gx + x * (cell_size + 2), gy + y * (cell_size + 2), cell_size, cell_size)
                    pygame.draw.rect(buffer, (30, 30, 35), rect)
                    
                    node = self.active_region.grid.get((x, y))
                    if node:
                        n_color = (0, 200, 0) if "node_oak" in node.id else (150, 150, 150)
                        pygame.draw.circle(buffer, n_color, rect.center, 4)
                    
                    for ent in self.active_region.entities:
                        if ent['x'] == x and ent['y'] == y:
                            pygame.draw.circle(buffer, (200, 50, 50), rect.center, 3)

                    if self.active_region.player_pos['x'] == x and self.active_region.player_pos['y'] == y:
                        pygame.draw.rect(buffer, (255, 255, 100), rect, 1)

            overlay_x = margin + 240
            if h2_f:
                h2_f.draw(buffer, "REGIONAL SCAN", overlay_x, 70, COLOR_ACCENT)
            if small_f:
                small_f.draw(buffer, "ARROWS TO MOVE", overlay_x, 90, COLOR_DIM)
                small_f.draw(buffer, "SPACE TO HARVEST", overlay_x, 105, COLOR_DIM)
                small_f.draw(buffer, "BACKSPACE TO EXIT", overlay_x, 120, COLOR_DIM)
        else:
            # MAP AS BACKGROUND (padded)
            cell_size = 31
            border = 1
            
            px, py = world_map.player_pos['x'], world_map.player_pos['y']
            
            # Draw a dark backing for the padded area
            pygame.draw.rect(buffer, (10, 10, 10), (margin, 35, content_w, content_h))
            
            # View dimensions in cells
            view_w = content_w // (cell_size + border) + 2
            view_h = content_h // (cell_size + border) + 2
            
            # Offset to center player
            off_x = margin + (content_w // 2) - (px * (cell_size + border)) - (cell_size // 2)
            off_y = 35 + (content_h // 2) - (py * (cell_size + border)) - (cell_size // 2)

            # Clipping
            clip_rect = pygame.Rect(margin, 35, content_w, content_h)
            old_clip = buffer.get_clip()
            buffer.set_clip(clip_rect)

            for y in range(py - view_h // 2, py + view_h // 2 + 1):
                for x in range(px - view_w // 2, px + view_w // 2 + 1):
                    if not (0 <= x < world_map.size and 0 <= y < world_map.size):
                        continue
                        
                    cell = world_map.get_cell(x, y)
                    key = f"{x},{y}"
                    discovered = key in world_map.discovered_cells
                    
                    rect = pygame.Rect(off_x + x * (cell_size + border), 
                                       off_y + y * (cell_size + border), 
                                       cell_size, cell_size)
                    
                    if discovered:
                        color = (40, 40, 45)
                        if cell.type == 'forest': color = (30, 60, 30)
                        elif cell.type == 'mountains': color = (60, 60, 60)
                        elif cell.type == 'water': color = (30, 30, 80)
                        elif cell.type == 'lab': color = (80, 80, 255)
                        elif cell.type == 'ocean': color = (20, 20, 40)
                        elif cell.type == 'river': color = (40, 40, 100)
                        elif cell.type == 'beach': color = (100, 100, 60)
                        elif cell.type == 'plains': color = (40, 50, 40)
                        
                        pygame.draw.rect(buffer, color, rect)
                        if small_f:
                            sym = cell.type[0].upper() if cell.type else "?"
                            small_f.draw(buffer, sym, rect.x + 3, rect.y + 10, (180, 180, 180))
                    else:
                        pygame.draw.rect(buffer, (15, 15, 18), rect)
                        pygame.draw.rect(buffer, (5, 5, 5), rect, 1)

                    if x == px and y == py:
                        pygame.draw.rect(buffer, (255, 255, 100), rect, 1)
            
            buffer.set_clip(old_clip)

            # OVERLAY PANELS
            # 1. Location Details (Top Right)
            detail_panel = Panel(buffer.get_width() - 100 - margin, 40, 100, 90, title="Loc~ Det~s")
            detail_panel.draw(buffer)
            current_cell = world_map.get_cell(px, py)
            if current_cell:
                if body_f:
                    body_f.draw(buffer, f"POS: {px},{py}", 385, 75, COLOR_ACCENT)
                    body_f.draw(buffer, f"TYPE: {current_cell.type.upper()}", 385, 95, COLOR_FG)

            # 3. Navigation Arrows (Bottom Left, No Title)
            nav_panel = Panel(margin, buffer.get_height() - 35 - margin, 50, 35, title=None)
            nav_panel.draw(buffer)
            if hasattr(self, 'arrows') and self.arrows:
                py_base = buffer.get_height() - margin
                
                # Mouse Pos for Hover
                mx, my = pygame.mouse.get_pos()
                scale = game_state.get('scale', 1)
                vx, vy = mx // scale, my // scale

                def draw_btn(dir, x, y):
                    rect = pygame.Rect(x, y, 7, 7)
                    is_hover = rect.inflate(4, 4).collidepoint(vx, vy)
                    if is_hover:
                        # Draw a subtle hover glow
                        pygame.draw.rect(buffer, (60, 55, 50), rect.inflate(2, 2), 0, 1)
                    buffer.blit(self.arrows[dir], (x, y))

                draw_btn("up",    margin + 21, py_base - 28)
                draw_btn("down",  margin + 21, py_base - 13)
                draw_btn("left",  margin + 6,  py_base - 13)
                draw_btn("right", margin + 36, py_base - 13)
            elif h2_f:
                h2_f.draw(buffer, "+", margin + 25, buffer.get_height() - 30 - margin, COLOR_FG)
