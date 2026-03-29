import pygame
import os
from engine.config_manager import ConfigManager
from engine.asset_manager import AssetManager
from engine.data_registry import DataRegistry
from engine.state_manager import GameStateManager
from engine.input_manager import InputManager
from engine.post_processor import PostProcessor
from ui import overlays, styles

class MurexEngine:
    """
    The heart of MurexLab-Retro.
    Coordinates all managers and runs the main game loop.
    Decoupled from gameplay logic.
    """
    def __init__(self, asset_root=None, data_root=None, save_dir=None):
        """
        Engine initialization. Establishes manager relationships (Dormant).
        """
        self.running = True
        self.debug_mode = False
        self.clock = pygame.time.Clock()
        
        # 1. Paths & Resolution Setup
        base_dir = os.path.dirname(__file__)
        self.v_width = 480
        self.v_height = 270
        self.asset_root = asset_root or os.path.abspath(os.path.join(base_dir, "../../../assets"))
        self.data_root = data_root or os.path.abspath(os.path.join(base_dir, "../../murex_lab/data"))
        self.save_dir = save_dir or os.path.abspath(os.path.join(base_dir, "../saves"))
        
        # 2. Manager Initialization (Dormant Phase)
        self.config = ConfigManager(self.data_root)
        self.assets = AssetManager(self.asset_root)
        self.data = DataRegistry(self.data_root)
        self.state = GameStateManager(self.save_dir)
        self.input = InputManager()
        self.post = PostProcessor()
        
        self.video_buffer = pygame.Surface((self.v_width, self.v_height))
        self.screen = None

    def boot(self, title="Murex Lab - Retro Engine"):
        """
        The "Wake Up" Protocol. Starts managers in strict dependency order.
        """
        pygame.init()

        # 1. Wake Up CONFIG (Source of Truth)
        self.config.load()
        self.scale = self.config.get("config", {}).get("scale", 4)
        
        # 2. Window Setup
        size = (self.v_width * self.scale, self.v_height * self.scale)
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(title)
        
        # High-res debug font
        try:
            self.hd_font = pygame.font.SysFont("Consolas", 14)
        except:
            self.hd_font = None

        # 3. Wake Up ASSETS
        font_dir = os.path.join(self.asset_root, "sprite-fonts")
        self.assets.load_fonts_from_dir(font_dir)
        self.assets.setup_font_styles(self.config.get("fonts", {}))
        
        # 4. Wake Up STATE (Game Logic & Persistence)
        self.state.boot_game_logic(self.data_root)
        self.state.load_world_data()

        # 5. Wake Up POST-PROCESSOR (Visual Pipeline)
        crt_cfg = self.config.get("crt_settings", {})
        if crt_cfg:
            from engine.post_processor import CrtEffect, BloomEffect
            self.post.add_effect(BloomEffect(crt_cfg))
            self.post.add_effect(CrtEffect(crt_cfg))

        print("Engine: Full system wake-up complete.")

    def set_scale(self, new_scale):
        """Update render scale and resize the window."""
        try:
            new_scale = int(new_scale)
        except (TypeError, ValueError):
            return
        if new_scale <= 0 or new_scale == self.scale:
            return
        self.scale = new_scale
        size = (self.v_width * self.scale, self.v_height * self.scale)
        self.screen = pygame.display.set_mode(size)

    def handle_events(self, active_view=None, tabs=None):
        """
        Processes the Pygame event queue.
        Handles header tab mouse clicks when tabs are provided.
        Returns a list of logical actions triggered this frame.
        """
        actions = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ["QUIT"]
            
            # 1. Header tab mouse handling (engine-level)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and tabs:
                mx, my = pygame.mouse.get_pos()
                vmx, vmy = mx // self.scale, my // self.scale
                tab_x = 94
                tab_f = styles.get_font("H2")
                if tab_f:
                    for i, tab in enumerate(tabs):
                        display_name = tab[:6] if tab_f.get_width(tab) > 48 else tab
                        tab_w = tab_f.get_width(display_name) + 4
                        tab_rect = pygame.Rect(tab_x, 3, tab_w, 15)
                        if tab_rect.collidepoint(vmx, vmy):
                            actions.append(("SET_TAB", i))
                            break
                        tab_x += tab_w + 4

            # 2. Manager-level handling
            action = self.input.handle_raw_event(event)
            if action:
                actions.append(action)
                
            # 3. View-level handling
            if active_view:
                # Support the reactive state dictionary for now
                # In Phase 5, views will access self.engine.state directly
                context = {
                    "engine": self,
                    "state": self.state,
                    "assets": self.assets,
                    "scale": self.scale,
                    "debug": self.debug_mode
                }
                
                if hasattr(active_view, "dispatch_view_event"):
                    active_view.dispatch_view_event(event, context)
                else:
                    # Fallback for widgets that aren't full views
                    active_view.handle_event(event, context)
                    
        return actions

    def _get_ram_usage(self):
        """Win32 specific RAM monitoring (Ported from legacy main.py)."""
        try:
            import ctypes
            from ctypes import wintypes
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            process_handle = ctypes.windll.kernel32.GetCurrentProcess()
            counters = PROCESS_MEMORY_COUNTERS()
            ctypes.windll.psapi.GetProcessMemoryInfo(process_handle, ctypes.byref(counters), ctypes.sizeof(counters))
            return counters.WorkingSetSize // (1024 * 1024)
        except:
            return 0

    def _render_header(self, buffer, active_tab, tabs):
        """Draws the global top bar with branding and tab navigation."""
        
        # Theme colors from central styles
        COLOR_PANEL = styles.get_color("panel")
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_DIM = styles.get_color("dim")
        COLOR_SELECT = styles.get_color("select")
        
        # 1. Background Bar
        pygame.draw.rect(buffer, COLOR_PANEL, (0, 0, self.v_width, 23))
        
        # 2. Branding
        h1_f = styles.get_font("H1")
        if h1_f:
            h1_f.draw(buffer, "MUREX LAB", 8, 16, COLOR_ACCENT)
            
        # 3. Tabs
        # TODO: use widgets
        tab_x = 94
        mx, my = pygame.mouse.get_pos()
        vmx, vmy = mx // self.scale, my // self.scale
        
        for i, tab in enumerate(tabs):
            is_active = (active_tab == tab)
            tab_f = styles.get_font("H2")
            if not tab_f: continue
            
            display_name = tab[:6] if tab_f.get_width(tab) > 48 else tab
            tab_w = tab_f.get_width(display_name) + 4
            tab_rect = pygame.Rect(tab_x, 3, tab_w, 15)
            
            if is_active:
                pygame.draw.rect(buffer, COLOR_ACCENT, tab_rect)
                text_col = COLOR_PANEL
            elif tab_rect.collidepoint(vmx, vmy):
                pygame.draw.rect(buffer, (40, 35, 30), tab_rect)
                text_col = COLOR_ACCENT
            else:
                text_col = COLOR_DIM
                
            text_x = tab_x + (tab_w - tab_f.get_width(display_name)) // 2
            tab_f.draw(buffer, display_name, text_x, 16, text_col)
            tab_x += tab_w + 4

    def render(self, active_view, active_tab=None, tabs=None):
        """
        The standard rendering pipeline:
        1. Clear virtual buffer
        2. Draw active view
        3. Draw Global Header (Tabs)
        4. Global Overlays (Tooltips, Dropdowns)
        5. Upscale to Physical Screen
        6. Flip display
        """
        if not self.screen: return

        # 1. Clear Virtual Buffer
        self.video_buffer.fill((15, 13, 11))
        
        # 2. Draw View Context
        context = {
            "engine": self,
            "state": self.state,
            "assets": self.assets,
            "scale": self.scale,
            "debug": self.debug_mode
        }

        if active_view:
            active_view.draw_view(self.video_buffer, context)
            
        # 3. Global Header (Tabs)
        if tabs:
            self._render_header(self.video_buffer, active_tab, tabs)
            
        # 4. Global Overlays (Tooltips, Dropdowns)
        overlays.draw(self.video_buffer)
            
        # 5. Upscale to Physical Screen
        scaled_size = (self.v_width * self.scale, self.v_height * self.scale)
        scaled_surface = pygame.transform.scale(self.video_buffer, scaled_size)
        self.screen.blit(scaled_surface, (0, 0))
        
        # 6. HD Debug Overlay (Drawn on screen)
        if self.debug_mode:
            self._draw_debug_overlays(self.screen, self.scale, active_view)
        
        # 7. Post-Processing
        self.post.process(self.screen, self.scale)
        
        # 7. Flip
        pygame.display.flip()
        self.clock.tick(60)

    def _draw_debug_overlays(self, screen, scale, active_view):
        """
        HD Debug Overlay drawn on the physical screen.
        Ported from legacy main.py with enhanced metrics.
        """
        if not self.hd_font: return
        
        # 1. Draw 8x8 virtual grid (HD)
        grid_color = (0, 60, 0) 
        for gx in range(0, self.v_width, 8):
            pygame.draw.line(screen, grid_color, (gx * scale, 0), (gx * scale, self.v_height * scale))
        for gy in range(0, self.v_height, 8):
            pygame.draw.line(screen, grid_color, (0, gy * scale), (self.v_width * scale, gy * scale))

        # 2. Collect Metrics
        fps = int(self.clock.get_fps())
        ms = self.clock.get_rawtime()
        uptime_ticks = pygame.time.get_ticks() # Should ideally be from engine start
        up_min, up_sec = divmod(uptime_ticks // 1000, 60)
        mx, my = pygame.mouse.get_pos()
        vmx, vmy = mx // scale, my // scale
        
        # Focus/Captured state
        focused_name = "none"
        captured_name = "none"
        if active_view:
            all_f = active_view.get_focusable_widgets() if hasattr(active_view, "get_focusable_widgets") else []
            focused = next((w for w in all_f if w.is_focused), None)
            captured = next((w for w in all_f if w.is_captured), None)
            if focused: focused_name = focused.__class__.__name__.lower()
            if captured: captured_name = captured.__class__.__name__.lower()

        # Engine context
        v_name = "unknown"
        if hasattr(self, 'active_tab_index') and hasattr(self, '_last_tabs'):
             v_name = self._last_tabs[self.active_tab_index].lower()
        
        # RAM usage (placeholder or helper)
        try:
            import psutil
            process = psutil.Process(os.getpid())
            ram_val = process.memory_info().rss // 1024 // 1024
        except:
            ram_val = 0
            
        debug_text = f"FPS {fps} | TIME {ms:02}ms | UP {up_min:02}:{up_sec:02} | VIEW {v_name} | FOCUS {focused_name} | CAPT {captured_name} | RAM {ram_val}MB | POS {vmx},{vmy}"
        
        # 3. Render Solid Bar
        tw, th = self.hd_font.size(debug_text)
        pygame.draw.rect(screen, (0, 0, 0), (0, screen.get_height() - th - 8, screen.get_width(), th + 8))
        
        # 4. Render Text
        txt_surf = self.hd_font.render(debug_text, True, (0, 255, 0))
        screen.blit(txt_surf, (10, screen.get_height() - th - 4))

    def run(self, view_instances, tabs, initial_index=0, on_hot_reload=None):
        """
        The definitive MurexLab game loop.
        Harmonizes views, input, and rendering.
        """
        self.active_tab_index = initial_index
        self._last_tabs = tabs # Store for debug overlay
        
        while self.running:
            # 1. Identify Active View
            active_tab = tabs[self.active_tab_index]
            active_view = view_instances.get(active_tab)
            
            # 2. Handle Logic & Events
            actions = self.handle_events(active_view, tabs)
            
            # 3. Resolve Engine-Level Actions
            for action in actions:
                if action == "QUIT":
                    self.running = False
                    break
                
                # Tab Navigation
                if action == "NEXT_TAB":
                    self.active_tab_index = (self.active_tab_index + 1) % len(tabs)
                elif action == "PREV_TAB":
                    self.active_tab_index = (self.active_tab_index - 1) % len(tabs)
                elif isinstance(action, tuple) and action[0] == "SET_TAB":
                    self.active_tab_index = action[1] % len(tabs)
                
                elif action == "TOGGLE_DEBUG":
                    self.debug_mode = not self.debug_mode
                    print(f"Engine: Debug Mode {'ENABLED' if self.debug_mode else 'DISABLED'}")
                
                # Hot Reload (F2) - passed through handle_events
                if action == "HOT_RELOAD" and on_hot_reload:
                    print("Engine: Triggering Hot Reload Callback...")
                    new_views, new_tabs = on_hot_reload()
                    if new_views and new_tabs:
                        view_instances = new_views
                        tabs = new_tabs
                        self._last_tabs = tabs
                        print("Engine: Hot Reload Successful")

            # 4. Global Rendering Pipeline
            self.render(active_view, active_tab, tabs)
