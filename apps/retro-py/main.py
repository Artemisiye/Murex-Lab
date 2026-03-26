import pygame
import sys
import os
import importlib
import ctypes
from ctypes import wintypes

# Add murex_lab to path for game logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../murex_lab')))

from renderer import SpriteFont
from ui_components import Widget, Label, Panel, Button, styles, overlays

# Game Logic Imports
from modules.crafting import CraftingManager
from modules.inventory import Inventory
from modules.world_map import map_manager
from modules.minions import Minion

# --- WIN32 RAM MONITORING ---
def get_ram_usage():
    try:
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]
        process_handle = ctypes.windll.kernel32.GetCurrentProcess()
        counters = PROCESS_MEMORY_COUNTERS()
        ctypes.windll.psapi.GetProcessMemoryInfo(process_handle, ctypes.byref(counters), ctypes.sizeof(counters))
        return counters.WorkingSetSize // (1024 * 1024)
    except:
        return 0

def main():
    pygame.init()
    
    import config_manager
    user_settings = config_manager.load_settings()
    
    # Virtual resolution (Retro native)
    V_WIDTH, V_HEIGHT = 480, 270
    config = {
        "scale": user_settings.get("config", {}).get("scale", 4),
        "v_width": V_WIDTH,
        "v_height": V_HEIGHT
    }
    
    screen = pygame.display.set_mode((V_WIDTH * config["scale"], V_HEIGHT * config["scale"]), pygame.RESIZABLE)
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
    font_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../assets/sprite-fonts"))
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
    user_fonts = user_settings.get("fonts", {})
    styles.set_font("H1", fonts.get(user_fonts.get("H1", "fixedsys")))
    styles.set_font("H2", fonts.get(user_fonts.get("H2", "press-start-2p")))
    styles.set_font("Body", fonts.get(user_fonts.get("Body", "minecraftia")))
    styles.set_font("Small", fonts.get(user_fonts.get("Small", "silkscreen-400")))
    
    # UI State
    tabs = ["MAP", "WORKSHOP", "INVENTORY", "MINIONS", "SETTINGS", "TEST"]
    active_tab_index = 0
    active_tab = tabs[active_tab_index]
    
    # View Instances
    from views.map_view import MapView
    from views.workshop_view import WorkshopView
    from views.inventory_view import InventoryView
    from views.minions_view import MinionsView
    from views.settings_view import SettingsView
    from views.test_ui_view import TestUIView
 
    view_instances = {
        "MAP": MapView(),
        "WORKSHOP": WorkshopView(),
        "INVENTORY": InventoryView(),
        "MINIONS": MinionsView(),
        "SETTINGS": SettingsView(),
        "TEST": TestUIView()
    }

    def reload_views():
        """Hot-reloads UI library and view modules without restarting the game."""
        print("--- HOT RELOADING ---")
        global styles, overlays
        try:
            # 1. Reload UI Library
            import ui_components
            importlib.reload(ui_components)
            
            # Re-apply fonts to the new styles object
            ui_components.styles.set_font("H1", styles.get_font("H1"))
            ui_components.styles.set_font("H2", styles.get_font("H2"))
            ui_components.styles.set_font("Body", styles.get_font("Body"))
            ui_components.styles.set_font("Small", styles.get_font("Small"))
            
            # Update main.py's own references to these global instances
            styles = ui_components.styles
            overlays = ui_components.overlays
            
            # 2. Reload View Modules
            import views.map_view
            import views.workshop_view
            import views.inventory_view
            import views.minions_view
            import views.settings_view
            import views.test_ui_view
            
            importlib.reload(views.map_view)
            importlib.reload(views.workshop_view)
            importlib.reload(views.inventory_view)
            importlib.reload(views.minions_view)
            importlib.reload(views.settings_view)
            importlib.reload(views.test_ui_view)
            
            # 3. Re-instantiate Views
            view_instances["MAP"] = views.map_view.MapView()
            view_instances["WORKSHOP"] = views.workshop_view.WorkshopView()
            view_instances["INVENTORY"] = views.inventory_view.InventoryView()
            view_instances["MINIONS"] = views.minions_view.MinionsView()
            view_instances["SETTINGS"] = views.settings_view.SettingsView()
            view_instances["TEST"] = views.test_ui_view.TestUIView()
            
            print("SUCCESS: Reloaded all modules and views.")
        except Exception as e:
            print(f"FAILED: Hot-reload error: {e}")
    
    active_tab = tabs[active_tab_index]
    active_view = view_instances.get(active_tab)
    
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    DEBUG = False
    
    # Standard HD Debug Font (renders above the CRT layer)
    hd_font = pygame.font.SysFont("Consolas", 12)

    # --- CRT Settings & Base State ---
    crt_settings = user_settings.get("crt_settings", {}).copy()
    if not crt_settings:
        crt_settings = config_manager.DEFAULT_SETTINGS["crt_settings"].copy()
    last_crt_settings = crt_settings.copy()
    last_scale = config["scale"]
    crt_overlay = pygame.Surface((V_WIDTH * config["scale"], V_HEIGHT * config["scale"]), pygame.SRCALPHA)

    def update_crt_overlay(surface, settings, scale):
        """Redraws the CRT phosphor and scanline meshes onto the provided surface."""
        surface.fill((0, 0, 0, 0))
        if not settings["enabled"]:
            return
            
        # 1. Softened Phosphor Scanlines
        s_alpha = settings["scanline_alpha"]
        for y in range(0, V_HEIGHT * scale, scale):
            pygame.draw.line(surface, (10, 10, 40, s_alpha), (0, y), (V_WIDTH * scale, y))
            if y + 1 < V_HEIGHT * scale:
                pygame.draw.line(surface, (10, 10, 40, int(s_alpha * 0.4)), (0, y + 1), (V_WIDTH * scale, y + 1))

        # 2. Vertical Aperture Grille
        g_alpha = settings["grille_alpha"]
        for x in range(0, V_WIDTH * scale, 2):
            if (x // 2) % 3 == 0:
                pygame.draw.line(surface, (0, 0, 0, g_alpha), (x, 0), (x, V_HEIGHT * scale))

        # 3. Micro Shadow Mask
        # Optimized: only draw every few pixels for mask effect
        for y in range(0, V_HEIGHT * scale, 2):
            for x in range(0, V_WIDTH * scale, 2):
                if (x // 2 + y // 2) % 2 == 0:
                    surface.set_at((x, y), (0, 0, 0, 8))

    update_crt_overlay(crt_overlay, crt_settings, config["scale"])

    # Test UI Components
    fleet_panel = None
    
    while True:
        active_tab = tabs[active_tab_index]
        active_view = view_instances.get(active_tab)
        
        mx, my = pygame.mouse.get_pos()
        # Scale mouse to virtual coords
        scale = config["scale"]
        
        # --- Handle Scale & Settings Changes ---
        if scale != last_scale:
            screen = pygame.display.set_mode((V_WIDTH * scale, V_HEIGHT * scale), pygame.RESIZABLE)
            crt_overlay = pygame.Surface((V_WIDTH * scale, V_HEIGHT * scale), pygame.SRCALPHA)
            update_crt_overlay(crt_overlay, crt_settings, scale)
            last_scale = scale
            last_crt_settings = crt_settings.copy()
        elif crt_settings != last_crt_settings:
            update_crt_overlay(crt_overlay, crt_settings, scale)
            last_crt_settings = crt_settings.copy()
            
        vmx, vmy = mx // scale, my // scale
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.VIDEORESIZE:
                # Handle window resize if needed, otherwise we override with scale setting
                pass
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1: # Toggle debug
                    DEBUG = not DEBUG
                if event.key == pygame.K_F2: # Hot Reload
                    reload_views()
                
            # Tab Navigation
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    active_tab_index = (active_tab_index - 1) % len(tabs)
                else:
                    active_tab_index = (active_tab_index + 1) % len(tabs)
            
            # Tab Change Side Effects
            active_tab = tabs[active_tab_index]
            active_view = view_instances.get(active_tab)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                if active_view and hasattr(active_view, "selection_index"):
                    active_view.selection_index = 0
            
            # View-specific Handling (Keyboard, Mouse, etc)
            game_state = {
                "world_map": world_map,
                "player_inventory": player_inventory,
                "player_backpack": player_backpack,
                "crafting_system": crafting_system,
                "player_minions": player_minions,
                "fonts": fonts,
                "all_fonts": fonts,
                "scale": scale,
                "config": config,
                "crt_settings": crt_settings,
                "debug": DEBUG
            }
            
            if active_view:
                # Support new BaseView API while keeping legacy handle_event for migration
                if hasattr(active_view, "dispatch_view_event"):
                    result = active_view.dispatch_view_event(event, game_state)
                else:
                    result = active_view.handle_event(event, game_state)
                
                if result == "GOTO_WORKSHOP":
                    active_tab_index = tabs.index("WORKSHOP")
                    active_tab = "WORKSHOP"
                    active_view = view_instances.get(active_tab)

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
        active_view = view_instances.get(active_tab)
        
        # Content Area
        game_state = {
            "world_map": world_map,
            "player_inventory": player_inventory,
            "player_backpack": player_backpack,
            "crafting_system": crafting_system,
            "player_minions": player_minions,
            "fonts": fonts,
            "all_fonts": fonts,
            "scale": scale,
            "config": config,
            "crt_settings": crt_settings,
            "debug": DEBUG
        }
        
        if active_view:
            if hasattr(active_view, "draw_view"):
                active_view.draw_view(video_buffer, game_state)
            else:
                active_view.draw(video_buffer, game_state)
            
        # Draw Overlays (Dropdowns, Tooltips) last
        overlays.draw(video_buffer)

        # Header & Tabs (Overlay)
        pygame.draw.rect(video_buffer, COLOR_PANEL, (0, 0, V_WIDTH, 23))
        h1_f = styles.get_font("H1")
        if h1_f:
            h1_f.draw(video_buffer, "MUREX LAB", 8, 16, COLOR_ACCENT)
        
        tab_x = 94 # 12 columns x 8px = 96px - 2px of padding
        for i, tab in enumerate(tabs):
            is_active = (active_tab_index == i)
            
            tab_f = styles.get_font("H2")
            if not tab_f: continue
            
            # Dynamic Width & Truncation (48px = 6 chars @ 8px each)
            display_name = tab
            if tab_f.get_width(display_name) > 48:
                display_name = tab[:6]
            
            # Button width: Text width + 4px padding (centered, 2px each side)
            tab_w = tab_f.get_width(display_name) + 4
            # Shifted up to match baseline at 16 (12px font needs y=3 to 17)
            tab_rect = pygame.Rect(tab_x, 3, tab_w, 15) 
            
            if is_active:
                pygame.draw.rect(video_buffer, COLOR_ACCENT, tab_rect)
                text_col = COLOR_PANEL
            elif tab_rect.collidepoint(vmx, vmy):
                pygame.draw.rect(video_buffer, (40, 35, 30), tab_rect)
                text_col = COLOR_ACCENT
            else:
                text_col = COLOR_DIM
            
            if click and tab_rect.collidepoint(vmx, vmy):
                active_tab_index = i
                active_tab = tabs[active_tab_index]
                active_view = view_instances.get(active_tab)
                if active_view and hasattr(active_view, "selection_index"):
                    active_view.selection_index = 0
            
            # Center text in button, baseline at y=16 (second line of 24px strip)
            text_x = tab_x + (tab_w - tab_f.get_width(display_name)) // 2
            tab_f.draw(video_buffer, display_name, text_x, 16, text_col)
            
            # Move to next tab with 4px gap
            tab_x += tab_w + 4


        # 2. Scale and Blit to screen
        pygame.transform.scale(video_buffer, (V_WIDTH * scale, V_HEIGHT * scale), screen)
        
        # --- HD DEBUG OVERLAY (Renders above CRT & Scaling) ---
        if DEBUG:
             # 1. Draw 8x8 virtual grid (HD)
             grid_color = (0, 60, 0) 
             for gx in range(0, V_WIDTH, 8):
                 pygame.draw.line(screen, grid_color, (gx * scale, 0), (gx * scale, V_HEIGHT * scale))
             for gy in range(0, V_HEIGHT, 8):
                 pygame.draw.line(screen, grid_color, (0, gy * scale), (V_WIDTH * scale, gy * scale))

             if hd_font:
                 fps = int(clock.get_fps())
             ms = clock.get_rawtime()
             uptime = (pygame.time.get_ticks() - start_time) // 1000
             up_min, up_sec = divmod(uptime, 60)
             
             # Fetch focus/captured state (Lower case)
             focused_name = "none"
             captured_name = "none"
             if active_view:
                 # Check if the view is a BaseView child (Focusable)
                 all_f = active_view.get_focusable_widgets() if hasattr(active_view, "get_focusable_widgets") else []
                 focused = next((w for w in all_f if w.is_focused), None)
                 captured = next((w for w in all_f if w.is_captured), None)
                 if focused: focused_name = focused.__class__.__name__.lower()
                 if captured: captured_name = captured.__class__.__name__.lower()

             # World Position
             wx, wy = world_map.player_pos['x'], world_map.player_pos['y']
             
             # Real RAM usage (Win32)
             ram_val = get_ram_usage()
             ram_str = f"{ram_val}MB"
             
             # Format metrics with stable padding
             ms_str = f"{ms:02}"
             v_name = active_tab.lower()
             
             debug_text = f"FPS {fps} | TIME {ms_str}ms | UP {up_min:02}:{up_sec:02} | VIEW {v_name} | WORLD {wx},{wy} | FOCUS {focused_name} | CAPT {captured_name} | RAM {ram_str} | POS {vmx},{vmy}"
             
             # Solid black background rectangle
             tw, th = hd_font.size(debug_text)
             pygame.draw.rect(screen, (0, 0, 0), (0, screen.get_height() - th - 8, screen.get_width(), th + 8))
             
             txt_surf = hd_font.render(debug_text, True, (0, 255, 0))
             screen.blit(txt_surf, (10, screen.get_height() - th - 4))
        
        # --- RADIANT CRT BLOOM (Phosphor Halation) ---
        if crt_settings["enabled"] and crt_settings["bloom_alpha"] > 0:
            # Capture the scaled output and blit it additively for a soft "hot" glow
            bloom_glow = pygame.transform.scale(video_buffer, (V_WIDTH * scale, V_HEIGHT * scale))
            bloom_glow.set_alpha(crt_settings["bloom_alpha"])
            # Shift slightly for the organic horizontal "tube bleed"
            offset = crt_settings["bloom_offset"]
            screen.blit(bloom_glow, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)

        # --- CRT OVERLAY (Scanlines + Mask) ---
        if crt_settings["enabled"]:
            # Check if settings changed to re-generate overlay
            settings_changed = False
            if config["scale"] != last_scale:
                settings_changed = True
                last_scale = config["scale"]
                screen = pygame.display.set_mode((V_WIDTH * last_scale, V_HEIGHT * last_scale), pygame.RESIZABLE)
                crt_overlay = pygame.Surface((V_WIDTH * last_scale, V_HEIGHT * last_scale), pygame.SRCALPHA)

            for k in ["enabled", "scanline_alpha", "grille_alpha"]:
                if crt_settings[k] != last_crt_settings[k]:
                    settings_changed = True
                    break
            
            if settings_changed:
                update_crt_overlay(crt_overlay, crt_settings, config["scale"])
                last_crt_settings = crt_settings.copy()
            
            screen.blit(crt_overlay, (0, 0))

        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
