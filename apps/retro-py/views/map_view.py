import pygame
from ui import *


class WorldRegion:
    """Placeholder for future regional gameplay logic."""
    pass


class MapTile:
    """Render helper for a single world map tile."""
    def __init__(self, rect, cell_type, discovered, is_player, colors, symbol=None):
        self.rect = rect
        self.cell_type = cell_type
        self.discovered = discovered
        self.is_player = is_player
        self.colors = colors or {}
        self.symbol = symbol

    def _get_color(self, key, fallback):
        val = self.colors.get(key)
        return tuple(val) if isinstance(val, list) else fallback

    def _get_type_color(self):
        types = self.colors.get("types", {})
        val = types.get(self.cell_type, types.get("default"))
        return tuple(val) if isinstance(val, list) else (40, 40, 45)

    def render(self, buffer, font=None):
        """Draw the tile and optional symbol to the buffer."""
        if self.discovered:
            pygame.draw.rect(buffer, self._get_type_color(), self.rect)
            if font and self.symbol:
                sym_col = self._get_color("symbol", (180, 180, 180))
                font.draw(buffer, self.symbol, self.rect.x + 3, self.rect.y + 10, sym_col)
        else:
            pygame.draw.rect(buffer, self._get_color("undiscovered_fill", (15, 15, 18)), self.rect)
            pygame.draw.rect(buffer, self._get_color("undiscovered_outline", (5, 5, 5)), self.rect, 1)

        if self.is_player:
            pygame.draw.rect(buffer, self._get_color("player_outline", (255, 255, 100)), self.rect, 1)


class RegionalMapTile:
    """Render helper for a single regional map tile."""
    def __init__(self, rect, colors, is_player=False, has_entity=False, node_id=None):
        self.rect = rect
        self.colors = colors or {}
        self.is_player = is_player
        self.has_entity = has_entity
        self.node_id = node_id

    def _get_color(self, key, fallback):
        val = self.colors.get(key)
        return tuple(val) if isinstance(val, list) else fallback

    def render(self, buffer):
        """Draw the regional tile and any node/entity/player markers."""
        pygame.draw.rect(buffer, self._get_color("base", (30, 30, 35)), self.rect)

        if self.node_id:
            if "node_oak" in self.node_id:
                n_color = self._get_color("node_oak", (0, 200, 0))
            else:
                n_color = self._get_color("node_default", (150, 150, 150))
            pygame.draw.circle(buffer, n_color, self.rect.center, 4)

        if self.has_entity:
            e_color = self._get_color("entity", (200, 50, 50))
            pygame.draw.circle(buffer, e_color, self.rect.center, 3)

        if self.is_player:
            pygame.draw.rect(buffer, self._get_color("player_outline", (255, 255, 100)), self.rect, 1)


class WorldMapWidget(Widget):
    """Panel-contained renderer for the world map."""
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.view = view

    def _get_content_rect(self, abs_rect):
        content_rect = abs_rect.inflate(-16, -16)
        # content_rect.y += 8
        # content_rect.h -= 8
        return content_rect

    def _draw_self(self, buffer, abs_rect):
        if self.view.active_region:
            return
        engine = getattr(self.view, "engine", None)
        state = engine.state if engine else None
        tile_colors = engine.assets.get_json("retro_map_tiles") if engine else {}
        world_colors = tile_colors.get("world", {})
        world_map = state.get('world_map') if state else None
        if not world_map:
            return

        content_rect = self._get_content_rect(abs_rect)
        content_w = content_rect.w
        content_h = content_rect.h

        cell_size = 31
        border = 1

        px, py = world_map.player_pos['x'], world_map.player_pos['y']

        # View dimensions in cells
        view_w = content_w // (cell_size + border) + 2
        view_h = content_h // (cell_size + border) + 2

        # Offset to center player
        off_x = content_rect.x + (content_w // 2) - (px * (cell_size + border)) - (cell_size // 2)
        off_y = content_rect.y + (content_h // 2) - (py * (cell_size + border)) - (cell_size // 2)

        # Clipping
        clip_rect = pygame.Rect(content_rect.x, content_rect.y, content_w, content_h)
        old_clip = buffer.get_clip()
        buffer.set_clip(clip_rect)

        small_f = styles.get_font("Small")

        for y in range(py - view_h // 2, py + view_h // 2 + 1):
            for x in range(px - view_w // 2, px + view_w // 2 + 1):
                if not (0 <= x < world_map.size and 0 <= y < world_map.size):
                    continue

                cell = world_map.get_cell(x, y)
                key = f"{x},{y}"
                discovered = key in world_map.discovered_cells

                rect = pygame.Rect(
                    off_x + x * (cell_size + border),
                    off_y + y * (cell_size + border),
                    cell_size,
                    cell_size,
                )

                symbol = cell.type[0].upper() if cell and cell.type else "?"
                tile = MapTile(
                    rect=rect,
                    cell_type=cell.type if cell else None,
                    discovered=discovered,
                    is_player=(x == px and y == py),
                    colors=world_colors,
                    symbol=symbol,
                )
                tile.render(buffer, font=small_f)

        buffer.set_clip(old_clip)

        # Update location details
        current_cell = world_map.get_cell(px, py)
        if current_cell:
            body_f = styles.get_font("Body")
            if body_f:
                self.view.tile_coord.text = f"POS: {px},{py}"
                self.view.tile_name.text = f"ID: {current_cell.type.upper()[:8]}"


class RegionalMapWidget(Widget):
    """Panel-contained renderer for the regional map."""
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.view = view

    def _get_content_rect(self, abs_rect):
        content_rect = abs_rect.inflate(-8, -8)
        content_rect.y += 12
        content_rect.h -= 12
        return content_rect

    def _draw_self(self, buffer, abs_rect):
        if not self.view.active_region:
            return
        engine = getattr(self.view, "engine", None)
        state = engine.state if engine else None
        tile_colors = engine.assets.get_json("retro_map_tiles") if engine else {}
        regional_colors = tile_colors.get("regional", {})
        world_map = state.get('world_map') if state else None
        if not world_map:
            return

        active_region = self.view.active_region

        content_rect = self._get_content_rect(abs_rect)
        cell_size = 18
        gx, gy = content_rect.x + 20, content_rect.y + 20

        for y in range(active_region.size):
            for x in range(active_region.size):
                rect = pygame.Rect(gx + x * (cell_size + 2), gy + y * (cell_size + 2), cell_size, cell_size)
                node = active_region.grid.get((x, y))
                has_entity = any(ent['x'] == x and ent['y'] == y for ent in active_region.entities)
                tile = RegionalMapTile(
                    rect=rect,
                    colors=regional_colors,
                    is_player=(active_region.player_pos['x'] == x and active_region.player_pos['y'] == y),
                    has_entity=has_entity,
                    node_id=node.id if node else None,
                )
                tile.render(buffer)

        overlay_x = content_rect.x + 240
        h2_f = styles.get_font("H2")
        small_f = styles.get_font("Small")
        if h2_f:
            h2_f.draw(buffer, "REGIONAL SCAN", overlay_x, 70, styles.get_color("accent"))
        if small_f:
            small_f.draw(buffer, "ARROWS TO MOVE", overlay_x, 90, styles.get_color("dim"))
            small_f.draw(buffer, "SPACE TO HARVEST", overlay_x, 105, styles.get_color("dim"))
            small_f.draw(buffer, "BACKSPACE TO EXIT", overlay_x, 120, styles.get_color("dim"))

class MapView(BaseView):
    """Top-level view for world/regional map navigation and panels."""
    def __init__(self, engine=None):
        super().__init__()
        self.engine = engine
        self.selection_index = 0
        self.active_region = None

        # ========================
        # 1. World Map Panel
        # ========================
        self.map_panel = Panel(title="WORLD")
        self.world_map_widget = WorldMapWidget(self, x=0, y=0, w=60, h=30)
        self.map_panel.add_child(self.world_map_widget)
        self.add_child(self.map_panel)

        # ========================
        # 2. World Map
        # ========================



        # ========================
        # 3. Location Details Panel
        # ========================
        self.location_details = Panel(x=48, y=0, w=12, h=8, title="LOC~ DATA")
        self.tile_coord = Label(x=1.5, y=1.5, text="POS: ~,~")
        self.tile_name = Label(x=1.5, y=3.5, text="AREA: ~~~~")
        self.location_details.add_child(self.tile_coord)
        self.location_details.add_child(self.tile_name)
        self.add_child(self.location_details)


        # ========================
        # 4. Navigation Panel
        # ========================
        self.nav_panel = Panel(x=0, y=24, w=8, h=6)
        self.add_child(self.nav_panel)
        self._init_nav_buttons()

        # ========================
        # 5. Regional Map Panel
        # ========================
        self.regional_panel = Panel(title="REGIONAL")
        self.regional_map_widget = RegionalMapWidget(self, x=0, y=0, w=60, h=30)
        self.regional_panel.add_child(self.regional_map_widget)
        self.add_child(self.regional_panel)

        self.map_stack = PanelStack(panels=[self.map_panel, self.regional_panel])
        self.add_child(self.map_stack)

    def do_move(self, dx, dy, world_map):
        if self.active_region:
            self.active_region.move_player(dx, dy)
        else:
            world_map.move_player(dx, dy)

    def _get_world_map(self):
        if self.engine:
            return self.engine.state.get("world_map")
        return None

    def _move_dir(self, dx, dy):
        world_map = self._get_world_map()
        if world_map:
            self.do_move(dx, dy, world_map)

    def _init_nav_buttons(self):
        if not self.engine:
            return
        if hasattr(self, 'arrows') and self.arrows:
            return
        self.arrows = {
            "up": self.engine.assets.get_sprite("ui_arrow_up"),
            "down": self.engine.assets.get_sprite("ui_arrow_down"),
            "left": self.engine.assets.get_sprite("ui_arrow_left"),
            "right": self.engine.assets.get_sprite("ui_arrow_right"),
        }
        if not all(self.arrows.values()):
            self.arrows = None
            return
        btn_up = Button(x=3, y=1, icon=self.arrows["up"], callback=lambda: self._move_dir(0, -1), border=False, has_shadow=False, can_focus=False)
        btn_down = Button(x=3, y=3, icon=self.arrows["down"], callback=lambda: self._move_dir(0, 1), border=False, has_shadow=False, can_focus=False)
        btn_left = Button(x=1, y=3, icon=self.arrows["left"], callback=lambda: self._move_dir(-1, 0), border=False, has_shadow=False, can_focus=False)
        btn_right = Button(x=5, y=3, icon=self.arrows["right"], callback=lambda: self._move_dir(1, 0), border=False, has_shadow=False, can_focus=False)
        self.nav_panel.add_child(btn_up)
        self.nav_panel.add_child(btn_down)
        self.nav_panel.add_child(btn_left)
        self.nav_panel.add_child(btn_right)
    
    def set_panel(self, idx):
        self.map_stack.active_idx = idx
        self.map_stack._sync_active_panel()

    def handle_event(self, event, mx, my):
        # Widget interception only; actions are handled via handle_action.
        return super().handle_event(event, mx, my)

    def handle_action(self, action, engine):
        state = engine.state if engine else None
        world_map = state.get('world_map') if state else None
        if not world_map:
            return False
        

        # Movement
        dx = dy = 0
        if action == "MOVE_UP":
            dy = -1
        elif action == "MOVE_DOWN":
            dy = 1
        elif action == "MOVE_LEFT":
            dx = -1
        elif action == "MOVE_RIGHT":
            dx = 1
        
        if dx or dy:
            self.do_move(dx, dy, world_map)
            return True

        if action == "INTERACT":
            return self.interact(world_map, state)

        if action == "RETURN":
            if self.active_region:
                self.active_region = None
                self.set_panel(0)
                return True

        return False

    def interact(self, world_map, state):
        if self.active_region:
            rx, ry = self.active_region.player_pos['x'], self.active_region.player_pos['y']
            loot = self.active_region.harvest(rx, ry)
            if not loot:
                loot = self.active_region.hunt(rx, ry)

            if loot:
                inv = state.get('player_inventory') if world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).type == 'lab' else state.get('player_backpack')
                import random
                if inv:
                    for item_id in loot:
                        inv.add_item(item_id, random.randint(1, 2))
                    print(f"Looted: {loot}")
            return True

        cell = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y'])
        if cell:
            if cell.type == 'lab':
                return "GOTO_WORKSHOP"
            self.active_region = world_map.enter_regional_map()
            self.set_panel(1)
            return True
        return False

    def draw_view(self, buffer, context):
        self.game_state = context
        state = context.get('state', {})
        world_map = state.get('world_map')

        # ========================
        # 1. Map Content Stack
        # ========================
        self.map_stack.draw(buffer)
        if not world_map:
            return

        if not self.active_region and self.map_panel.visible:
            self.location_details.draw(buffer)
            self.nav_panel.draw(buffer)
