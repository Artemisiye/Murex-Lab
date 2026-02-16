import pygame
from ui_components import Widget, Label, Panel, PanelStack, Button, styles

class MapView:
    def __init__(self):
        self.selection_index = 0
        self.active_region = None

        # ========================
        # 0. Root Canvas
        # ========================
        self.root = Widget(0, 24, 480, 240)
        

        # ========================
        # 1. World Map Panel
        # ========================
        self.map_panel = Panel(title="WORLD")


        # ========================
        # 2. World Map
        # ========================



        # ========================
        # 3. Location Details Panel
        # ========================
        self.location_details = Panel(x=384, y=0, w=96, h=64, title="LOC~ DATA")
        self.tile_coord = Label(x=12, y=12, text=f"POS: ~,~")
        self.tile_name = Label(x=12, y=28, text=f"AREA: ~~~~")
        self.location_details.add_child(self.tile_coord)
        self.location_details.add_child(self.tile_name)

        self.root.add_child(self.location_details)


        # ========================
        # 4. Navigation Panel
        # ========================
        self.nav_panel = Panel(x=0, y=192, w=64, h=48)

        self.root.add_child(self.nav_panel)

        # ========================
        # 5. Regional Map Panel
        # ========================
        self.regional_panel = Panel(title="REGIONAL")

        self.map_stack = PanelStack(panels=[self.map_panel, self.regional_panel])
        self.root.add_child(self.map_stack)

    def do_move(self, dx, dy, world_map):
        if self.active_region:
            self.active_region.move_player(dx, dy)
        else:
            world_map.move_player(dx, dy)

    def handle_event(self, event, game_state):
        world_map = game_state['world_map']
        
        # Scale mouse for widgets
        mx, my = pygame.mouse.get_pos()
        scale = game_state.get('scale', 1)
        vx, vy = mx // scale, my // scale

        # 1. Widget Interception (Tab, Buttons, etc)
        if self.root.handle_event(event, vx, vy):
            return True

        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP: dy = -1
            if event.key == pygame.K_DOWN: dy = 1
            if event.key == pygame.K_LEFT: dx = -1
            if event.key == pygame.K_RIGHT: dx = 1
            
            if dx != 0 or dy != 0:
                self.do_move(dx, dy, world_map)
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
                            self.map_stack.active_idx = 1 # REGIONAL
                return True
            
            if event.key == pygame.K_BACKSPACE:
                if self.active_region:
                    self.active_region = None
                    self.map_stack.active_idx = 0 # WORLD
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

        # ========================
        # 0. Load Assets
        # ========================
        if not hasattr(self, 'arrows') or self.arrows is None:
            import os
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            ui_dir = os.path.join(repo_root, "assets", "ui")

            try:
                self.arrows = {
                    "up":    pygame.image.load(os.path.join(ui_dir, "▲-7px.png")).convert_alpha(),
                    "down":  pygame.image.load(os.path.join(ui_dir, "▼-7px.png")).convert_alpha(),
                    "left":  pygame.image.load(os.path.join(ui_dir, "◀-7px.png")).convert_alpha(),
                    "right": pygame.image.load(os.path.join(ui_dir, "▶-7px.png")).convert_alpha()
                }
                
                # Initialize Nav Buttons
                self.nav_panel.add_child(Button(x=24, y=8, icon=self.arrows["up"], callback=lambda: self.do_move(0, -1, world_map), border=False))
                self.nav_panel.add_child(Button(x=24, y=24, icon=self.arrows["down"], callback=lambda: self.do_move(0, 1, world_map), border=False))
                self.nav_panel.add_child(Button(x=8, y=24, icon=self.arrows["left"], callback=lambda: self.do_move(-1, 0, world_map), border=False))
                self.nav_panel.add_child(Button(x=40, y=24, icon=self.arrows["right"], callback=lambda: self.do_move(1, 0, world_map), border=False))

                print(f"SUCCESS: Loaded individual 7px arrow sprites and initialized nav buttons from {ui_dir}")
            except Exception as e:
                print(f"ERROR: Sprite load failed from {ui_dir}: {e}")
                self.arrows = None
        
        # ========================
        # 1. Map Content Stack
        # ========================
        self.map_stack.draw(buffer)

        # ========================
        # 2. World Map
        # ========================
        margin = 5
        content_w = buffer.get_width() - (margin * 2)
        content_h = buffer.get_height() - (margin + 36) # Below header
        
        if not self.active_region:
            # MAP AS BACKGROUND (padded)
            cell_size = 31
            border = 1
            
            px, py = world_map.player_pos['x'], world_map.player_pos['y']
            
            # Draw a dark backing for the padded area
            # pygame.draw.rect(buffer, (10, 10, 10), (margin, 32, content_w, content_h))
            
            # View dimensions in cells
            view_w = content_w // (cell_size + border) + 2
            view_h = content_h // (cell_size + border) + 2
            
            # Offset to center player
            off_x = margin + (content_w // 2) - (px * (cell_size + border)) - (cell_size // 2)
            off_y = 31 + (content_h // 2) - (py * (cell_size + border)) - (cell_size // 2)

            # Clipping
            clip_rect = pygame.Rect(margin, 31, content_w, content_h)
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

            # ========================
            # 3. Location Details (Top Right)
            # ========================
            # Update location details
            current_cell = world_map.get_cell(px, py)
            if current_cell:
                if body_f:
                    self.tile_coord.text = f"POS: {px},{py}"
                    self.tile_name.text = f"ID: {current_cell.type.upper()[:8]}"
            # Render
            self.location_details.draw(buffer)


            # ========================
            # 4. Navigation Arrows ("D-Pad", Bottom Left)
            # ========================
            self.nav_panel.draw(buffer)

        else:
            # ========================
            # 5. Regional Map
            # ========================
            # Update tab name dynamically
            biome_name = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).type.upper()
            self.map_stack.set_panel_name(self.regional_panel, f"REGIONAL: {biome_name}")
            # self.regional_panel is already drawn by the stack
            
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
