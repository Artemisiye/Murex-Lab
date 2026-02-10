import pygame
import sys
import os

# Add murex_lab to path for game logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../murex_lab')))

from renderer import SpriteFont
from ui_components import Widget, Label, Panel, Button, styles

# Game Logic Imports
from modules.crafting import CraftingManager
from modules.inventory import Inventory
from modules.world_map import map_manager
from modules.minions import Minion

def main():
    pygame.init()
    
    # Virtual resolution (Retro native)
    V_WIDTH, V_HEIGHT = 480, 270
    SCALE = 4
    
    screen = pygame.display.set_mode((V_WIDTH * SCALE, V_HEIGHT * SCALE))
    pygame.display.set_caption("Murex Lab - Retro")
    
    video_buffer = pygame.Surface((V_WIDTH, V_HEIGHT))
    
    # --- Initialize Game Logic ---
    data_path = os.path.join(os.path.dirname(__file__), "../murex_lab/data")
    save_path = os.path.join(data_path, 'player_inventory.json')
    backpack_path = os.path.join(data_path, 'player_backpack.json')
    
    crafting_system = CraftingManager(data_path)
    player_inventory = Inventory(save_path)
    player_backpack = Inventory(backpack_path)
    world_map = map_manager(data_path)
    player_minions = [Minion("m_001", "Lead Artificer")]

    # Font Management
    font_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    fonts = {}
    current_font_name = None
    
    if os.path.exists(font_dir):
        files = [f for f in os.listdir(font_dir) if f.endswith(".json")]
        for f in files:
            name = f.replace(".json", "")
            try:
                fonts[name] = SpriteFont(os.path.join(font_dir, f))
                if current_font_name is None:
                    current_font_name = name
            except Exception as e:
                print(f"Error loading {f}: {e}")
    
    # Initialize Standard Font Styles (RETRO_STYLES.md)
    styles.set_font("H1", fonts.get("fixedsys"))
    styles.set_font("H2", fonts.get("press-start-2p"))
    styles.set_font("Body", fonts.get("minecraftia"))
    styles.set_font("Small", fonts.get("silkscreen-400"))
    
    # UI State
    tabs = ["MAP", "WORKSHOP", "INVENTORY", "MINIONS", "SETTINGS"]
    active_tab_index = 0
    active_tab = tabs[active_tab_index]
    
    # View Instances
    from views.map_view import MapView
    from views.workshop_view import WorkshopView
    from views.inventory_view import InventoryView
    from views.minions_view import MinionsView
    from views.settings_view import SettingsView

    view_instances = {
        "MAP": MapView(),
        "WORKSHOP": WorkshopView(),
        "INVENTORY": InventoryView(),
        "MINIONS": MinionsView(),
        "SETTINGS": SettingsView()
    }
    
    clock = pygame.time.Clock()
    DEBUG = False

    # --- CRT Settings & Base State ---
    crt_settings = {
        "enabled": True,
        "scanline_alpha": 30,
        "grille_alpha": 12,
        "bloom_alpha": 35,
        "bloom_offset": 1
    }
    last_crt_settings = crt_settings.copy()
    crt_overlay = pygame.Surface((V_WIDTH * SCALE, V_HEIGHT * SCALE), pygame.SRCALPHA)

    def update_crt_overlay(surface, settings):
        surface.fill((0, 0, 0, 0))
        if not settings["enabled"]:
            return
            
        # 1. Softened Phosphor Scanlines
        s_alpha = settings["scanline_alpha"]
        for y in range(0, V_HEIGHT * SCALE, SCALE):
            pygame.draw.line(surface, (10, 10, 40, s_alpha), (0, y), (V_WIDTH * SCALE, y))
            if y + 1 < V_HEIGHT * SCALE:
                pygame.draw.line(surface, (10, 10, 40, int(s_alpha * 0.4)), (0, y + 1), (V_WIDTH * SCALE, y + 1))

        # 2. Vertical Aperture Grille
        g_alpha = settings["grille_alpha"]
        for x in range(0, V_WIDTH * SCALE, 2):
            if (x // 2) % 3 == 0:
                pygame.draw.line(surface, (0, 0, 0, g_alpha), (x, 0), (x, V_HEIGHT * SCALE))

        # 3. Micro Shadow Mask
        for y in range(0, V_HEIGHT * SCALE, 2):
            for x in range(0, V_WIDTH * SCALE, 2):
                if (x // 2 + y // 2) % 2 == 0:
                    surface.set_at((x, y), (0, 0, 0, 8))

    update_crt_overlay(crt_overlay, crt_settings)

    # Test UI Components
    fleet_panel = None
    
    while True:
        mx, my = pygame.mouse.get_pos()
        # Scale mouse to virtual coords
        vmx, vmy = mx // SCALE, my // SCALE
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1: # Toggle debug
                    DEBUG = not DEBUG
                
            # Tab Navigation
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    active_tab_index = (active_tab_index - 1) % len(tabs)
                else:
                    active_tab_index = (active_tab_index + 1) % len(tabs)
                active_tab = tabs[active_tab_index]
                selection_index = 0 # Reset selection on tab change
            
            # View-specific Handling (Keyboard, Mouse, etc)
            game_state = {
                "world_map": world_map,
                "player_inventory": player_inventory,
                "player_backpack": player_backpack,
                "crafting_system": crafting_system,
                "player_minions": player_minions,
                "fonts": fonts,
                "scale": SCALE,
                "crt_settings": crt_settings
            }
            
            active_view = view_instances.get(active_tab)
            if active_view:
                result = active_view.handle_event(event, game_state)
                if result == "GOTO_WORKSHOP":
                    active_tab_index = tabs.index("WORKSHOP")
                    active_tab = "WORKSHOP"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        # --- RENDER LOGIC ---
        video_buffer.fill((15, 13, 11))
        
        # UI Colors
        COLOR_BG = (15, 13, 11)
        COLOR_PANEL = (25, 22, 19)
        COLOR_ACCENT = (230, 200, 100)
        COLOR_DIM = (100, 90, 80)
        COLOR_FG = (220, 210, 190)

        active_tab = tabs[active_tab_index]
        
        # Content Area
        game_state = {
            "world_map": world_map,
            "player_inventory": player_inventory,
            "player_backpack": player_backpack,
            "crafting_system": crafting_system,
            "player_minions": player_minions,
            "fonts": fonts,
            "scale": SCALE,
            "crt_settings": crt_settings
        }
        
        active_view = view_instances.get(active_tab)
        if active_view:
            active_view.draw(video_buffer, game_state)

        # Header & Tabs (Overlay)
        pygame.draw.rect(video_buffer, COLOR_PANEL, (0, 0, V_WIDTH, 30))
        h1_f = styles.get_font("H1")
        if h1_f:
            h1_f.draw(video_buffer, "MUREX LAB", 10, 20, COLOR_ACCENT)
        
        tab_x = 100
        for i, tab in enumerate(tabs):
            is_active = (active_tab_index == i)
            tab_w = 70
            tab_rect = pygame.Rect(tab_x, 5, tab_w, 20)
            
            if is_active:
                pygame.draw.rect(video_buffer, COLOR_ACCENT, tab_rect, 1)
            
            if tab_rect.collidepoint(vmx, vmy):
                if not is_active:
                    pygame.draw.rect(video_buffer, (40, 35, 30), tab_rect)
                if click:
                    active_tab_index = i
            
            tab_f = styles.get_font("H2")
            if tab_f:
                tab_f.draw(video_buffer, tab, tab_x + 5, 20, COLOR_FG if is_active else COLOR_DIM)
            
            tab_x += tab_w + 5

        # 2. Scale and Blit to screen
        pygame.transform.scale(video_buffer, (V_WIDTH * SCALE, V_HEIGHT * SCALE), screen)
        
        # --- RADIANT CRT BLOOM (Phosphor Halation) ---
        if crt_settings["enabled"] and crt_settings["bloom_alpha"] > 0:
            # Capture the scaled output and blit it additively for a soft "hot" glow
            bloom_glow = pygame.transform.scale(video_buffer, (V_WIDTH * SCALE, V_HEIGHT * SCALE))
            bloom_glow.set_alpha(crt_settings["bloom_alpha"])
            # Shift slightly for the organic horizontal "tube bleed"
            offset = crt_settings["bloom_offset"]
            screen.blit(bloom_glow, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)

        # --- CRT OVERLAY (Scanlines + Mask) ---
        if crt_settings["enabled"]:
            # Check if settings changed to re-generate overlay
            settings_changed = False
            for k in ["enabled", "scanline_alpha", "grille_alpha"]:
                if crt_settings[k] != last_crt_settings[k]:
                    settings_changed = True
                    break
            
            if settings_changed:
                update_crt_overlay(crt_overlay, crt_settings)
                last_crt_settings = crt_settings.copy()
            
            screen.blit(crt_overlay, (0, 0))

        # 3. HIGH-RES DEBUG OVERLAY
        if DEBUG:
            # Draw green 5x5 virtual grid on top of EVERYTHING
            grid_color = (0, 100, 0)
            for x in range(0, V_WIDTH, 5):
                pygame.draw.line(screen, grid_color, (x * SCALE, 0), (x * SCALE, V_HEIGHT * SCALE))
            for y in range(0, V_HEIGHT, 5):
                pygame.draw.line(screen, grid_color, (0, y * SCALE), (V_WIDTH * SCALE, y * SCALE))

            sys_f = pygame.font.SysFont("monospace", 14)
            # Performance stats
            stats = [
                f"FPS: {int(clock.get_fps())}",
                f"POS: {world_map.player_pos['x']},{world_map.player_pos['y']}",
                f"TAB: {active_tab}",
                f"SEL: {selection_index}"
            ]
            for i, line in enumerate(stats):
                txt = sys_f.render(line, True, (255, 255, 255))
                screen.blit(sys_f.render(line, True, (0,0,0)), (12, 12 + i*16))
                screen.blit(txt, (10, 10 + i*16))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
