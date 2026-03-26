import pygame
from ui_components import BaseView, Panel, PanelStack, Button, Label, Dropdown, Slider, TextField, ScrollContainer, styles

class SettingsView(BaseView):
    """
    The main Settings menu view.
    Refactored from a monolithic implementation to a modular, widget-based PanelStack.
    Supports real-time display/font updates and persistent user preferences.
    """
    def __init__(self):
        super().__init__()
        self.preview_texts = {
            "H1": "MUREX LAB", 
            "H2": "Header Text Example", 
            "Body": "Standard body text.", 
            "Small": "v0.1.0-alpha"
        }
        self.ui_assets = {} 

        # --- PHASE 1: WIDGET RECONSTRUCTION ---
        
        # 1. DISPLAY PANEL
        self.display_panel = Panel(title="DISPLAY")
        # Layout: Label + Control pairs
        # Note: y coordinates are relative to the Panel content area
        self.display_panel.add_child(Label("RENDER SCALE", x=2, y=2, role="Body"))
        self.drop_scale = Dropdown(x=18, y=2, w=12, options=[1, 2, 3, 4], current_idx=3, on_change=self._on_scale_change)
        self.display_panel.add_child(self.drop_scale)
        
        self.display_panel.add_child(Label("CRT EFFECT", x=2, y=6, role="Body"))
        self.btn_crt = Button(text="ON", x=18, y=6, w=6, callback=self._on_crt_toggle)
        self.display_panel.add_child(self.btn_crt)
        
        self.display_panel.add_child(Label("SCANLINE INTENSITY", x=2, y=10, role="Body"))
        self.slide_scanline = Slider(x=18, y=10, w=24, val_max=255, current=30, on_change=lambda v: self._on_crt_slider('scanline_alpha', v))
        self.display_panel.add_child(self.slide_scanline)
        
        self.display_panel.add_child(Label("GRILLE INTENSITY", x=2, y=14, role="Body"))
        self.slide_grille = Slider(x=18, y=14, w=24, val_max=255, current=12, on_change=lambda v: self._on_crt_slider('grille_alpha', v))
        self.display_panel.add_child(self.slide_grille)
        
        self.display_panel.add_child(Label("BLOOM INTENSITY", x=2, y=18, role="Body"))
        self.slide_bloom = Slider(x=18, y=18, w=24, val_max=255, current=35, on_change=lambda v: self._on_crt_slider('bloom_alpha', v))
        self.display_panel.add_child(self.slide_bloom)
        
        self.display_panel.add_child(Label("BLOOM OFFSET", x=2, y=22, role="Body"))
        self.slide_bloom_off = Slider(x=18, y=22, w=24, val_max=10, current=1, on_change=lambda v: self._on_crt_slider('bloom_offset', v))
        self.display_panel.add_child(self.slide_bloom_off)

        # Bottom Actions
        self.display_panel.add_child(Button("SAVE SETTINGS", x=2, y=26, callback=self._save_settings))
        self.display_panel.add_child(Button("RESTORE DEFAULTS", x=24, y=26, callback=self._restore_defaults))

        # 2. FONTS PANEL
        self.fonts_panel = Panel(title="FONTS")
        roles = ["H1", "H2", "Body", "Small"]
        for i, role in enumerate(roles):
            ry = 2 + i * 5
            self.fonts_panel.add_child(Label(f"{role:5}:", x=2, y=ry, role="Body", color=styles.get_color("accent")))
            # Store dropdown reference to populate later
            drop = Dropdown(x=10, y=ry - 0.5, w=12, options=[], on_change=lambda val, r=role: self._on_font_change(r, val))
            self.fonts_panel.add_child(drop)
            setattr(self, f"drop_{role.lower()}", drop)
            
            lbl_dim = Label("?x?", x=24, y=ry, role="Small", color=styles.get_color("dim"))
            self.fonts_panel.add_child(lbl_dim)
            setattr(self, f"lbl_dim_{role.lower()}", lbl_dim)
            
            self.fonts_panel.add_child(TextField(x=32, y=ry - 0.5, w=24, text=self.preview_texts[role], on_change=lambda t, r=role: self._on_preview_change(r, t), role=role))

        # Bottom Actions
        self.fonts_panel.add_child(Button("SAVE SETTINGS", x=2, y=26, callback=self._save_settings))
        self.fonts_panel.add_child(Button("RESTORE DEFAULTS", x=24, y=26, callback=self._restore_defaults))

        # --- ROOT PANEL STACK ---
        self.stack = PanelStack(x=0, y=0, w=58, h=28, panels=[
            self.display_panel,
            self.fonts_panel
        ])
        self.stack.active_idx = 0 # DEFAULT TO DISPLAY
        self.add_child(self.stack)

    def handle_event(self, event, mx, my):
        # We now use the standard Widget.handle_event which dispatches to children (the PanelStack)
        return super().handle_event(event, mx, my)

    def _sync_ui(self, game_state):
        if getattr(self, '_ui_synced', False): return
        self._ui_synced = True
        
        # Display Sync
        scale = game_state.get('config', {}).get('scale', 4)
        if scale in self.drop_scale.options:
            self.drop_scale.current_idx = self.drop_scale.options.index(scale)
            
        crt = game_state.get('crt_settings', {})
        if crt:
            self.btn_crt.text = "ON" if crt.get('enabled', True) else "OFF"
            self.slide_scanline.current = crt.get('scanline_alpha', 30)
            self.slide_grille.current = crt.get('grille_alpha', 12)
            self.slide_bloom.current = crt.get('bloom_alpha', 35)
            self.slide_bloom_off.current = crt.get('bloom_offset', 1)

    def _on_scale_change(self, val):
        if hasattr(self, 'game_state'):
            self.game_state['config']['scale'] = val

    def _on_crt_toggle(self):
        if hasattr(self, 'game_state'):
            crt = self.game_state.get('crt_settings')
            if crt:
                crt['enabled'] = not crt['enabled']
                self.btn_crt.text = "ON" if crt['enabled'] else "OFF"

    def _on_crt_slider(self, key, val):
        if hasattr(self, 'game_state'):
            crt = self.game_state.get('crt_settings')
            if crt:
                crt[key] = int(val)

    def _on_font_change(self, role, font_name):
        if hasattr(self, 'game_state'):
            all_fonts = self.game_state.get('all_fonts', {})
            if font_name in all_fonts:
                styles.set_font(role, all_fonts[font_name])

    def _on_preview_change(self, role, text):
        """Updates the local preview text state when a TextField is edited."""
        self.preview_texts[role] = text

    def _save_settings(self):
        """Extracts current game state and styles, and persists them via config_manager."""
        if not hasattr(self, 'game_state'): return
        gs = self.game_state
        import config_manager
        
        settings = {
            "config": {
                "scale": gs.get("config", {}).get("scale", 4)
            },
            "crt_settings": gs.get("crt_settings", {}).copy(),
            "fonts": {
                "H1": styles.get_font("H1").name if styles.get_font("H1") else "fixedsys",
                "H2": styles.get_font("H2").name if styles.get_font("H2") else "press-start-2p",
                "Body": styles.get_font("Body").name if styles.get_font("Body") else "minecraftia",
                "Small": styles.get_font("Small").name if styles.get_font("Small") else "silkscreen-400",
            }
        }
        config_manager.save_settings(settings)

    def _restore_defaults(self):
        """Resets all display and font settings to their hardcoded factory defaults."""
        if not hasattr(self, 'game_state'): return
        gs = self.game_state
        import config_manager
        defaults = config_manager.DEFAULT_SETTINGS
        
        gs['config']['scale'] = defaults['config']['scale']
        if 'crt_settings' in gs:
            gs['crt_settings'].update(defaults['crt_settings'])
            
        all_fonts = gs.get('all_fonts', {})
        for role, fname in defaults['fonts'].items():
            if fname in all_fonts:
                styles.set_font(role, all_fonts[fname])
                
        # Force a UI sync next frame
        self._ui_synced = False
        self._sync_ui(gs)

    def draw_view(self, buffer, game_state):
        """Standard draw loop, includes continuous font/dimension synchronization."""
        # We now use the standard Widget.draw_view which renders the Widget tree
        self.game_state = game_state
        self._sync_ui(game_state)
        
        # --- DYNAMIC FONT POPULATION ---
        all_fonts = game_state.get('all_fonts', {})
        if all_fonts:
            font_names = sorted(list(all_fonts.keys()))
            roles = ["H1", "H2", "Body", "Small"]
            for role in roles:
                drop = getattr(self, f"drop_{role.lower()}", None)
                if drop and len(drop.options) != len(font_names):
                    drop.options = font_names
                    # Update current_idx based on current styles
                    current_font = styles.get_font(role)
                    if current_font and current_font.name in font_names:
                        drop.current_idx = font_names.index(current_font.name)
                
                # Sync font dimension labels continuously
                lbl = getattr(self, f"lbl_dim_{role.lower()}", None)
                if lbl:
                    font = styles.get_font(role)
                    if font:
                        w, h = getattr(font, 'effective_w', 0), getattr(font, 'effective_h', 0)
                        dim_str = f"{w}x{h}" if w and h else "?x?"
                        if lbl.text != dim_str:
                            lbl.text = dim_str
        
        super().draw_view(buffer, game_state)

