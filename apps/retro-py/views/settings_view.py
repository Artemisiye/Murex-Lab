import pygame
from ui_components import BaseView, Panel, styles

class SettingsView(BaseView):
    def __init__(self):
        super().__init__()
        self.selection_index = -1 # -1 for Tabs, 0+ for content
        self.selection_col = 0    # 0 for Dropdown/Value, 1 for Preview (Fonts only)
        self.active_section_idx = 0 # 0: DISPLAY, 1: FONTS
        self.sections = ["DISPLAY", "FONTS"]
        self.dragging = None
        self.open_dropdown = None # ID: "SCALE", "H1", "H2", "Body", "Small"
        self.open_dropdown_idx = 0 
        self.editing_preview = False
        self.preview_texts = {
            "H1": "MUREX LAB", 
            "H2": "Header Text Example", 
            "Body": "Standard body text.", 
            "Small": "v0.1.0-alpha"
        }
        self.ui_assets = {} # Shared UI sprites (arrows, etc)

    def handle_event(self, event, mx, my):
        if super().handle_event(event, mx, my):
            return True
            
        crt = self.game_state.get('crt_settings')
        config = self.game_state.get('config')
        all_fonts = self.game_state.get('all_fonts', {})
        if not crt or not config: return False
        
        # --- EDITING PREVIEW INTERCEPTION ---
        if self.editing_preview:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.editing_preview = False
                    return True
                
                roles = ["H1", "H2", "Body", "Small"]
                role = roles[self.selection_index]
                if event.key == pygame.K_BACKSPACE:
                    self.preview_texts[role] = self.preview_texts[role][:-1]
                else:
                    if len(event.unicode) > 0 and ord(event.unicode[0]) >= 32:
                        self.preview_texts[role] += event.unicode
                return True
            return False

        # --- DROPDOWN INTERCEPTION ---
        if self.open_dropdown:
            options = self._get_dropdown_options(config, all_fonts)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.open_dropdown = None
                    return True
                
                if event.key == pygame.K_UP:
                    self.open_dropdown_idx = (self.open_dropdown_idx - 1) % len(options)
                    return True
                if event.key == pygame.K_DOWN:
                    self.open_dropdown_idx = (self.open_dropdown_idx + 1) % len(options)
                    return True
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self._set_dropdown_val(self.open_dropdown, options[self.open_dropdown_idx], config, all_fonts)
                    self.open_dropdown = None
                    return True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # COL_VAL = 80, COL_PREV = 264. Dropdown anchors to COL_VAL or 280
                val_x = 80 if self.active_section_idx == 1 else 280
                row_y = self._get_dropdown_anchor_y()
                drop_w = 104 if self.active_section_idx == 1 else 100
                drop_h = min(len(options), 8) * 16 + 4
                
                if val_x <= mx <= val_x + drop_w and row_y + 14 <= my <= row_y + 14 + drop_h:
                    idx = (my - (row_y + 16)) // 16
                    if 0 <= idx < len(options):
                         self._set_dropdown_val(self.open_dropdown, options[idx], config, all_fonts)
                         self.open_dropdown = None
                    return True
                
                self.open_dropdown = None
                return True
            return False

        # --- NORMAL NAVIGATION ---
        if event.type == pygame.KEYDOWN:
            # Vertical Movement
            max_sel = 5 if self.active_section_idx == 0 else 3
            if event.key == pygame.K_DOWN:
                if self.selection_index < max_sel:
                    self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                if self.selection_index > -1:
                    self.selection_index -= 1
                return True

            # Horizontal Movement
            if self.selection_index == -1: # TABS focused
                if event.key == pygame.K_RIGHT:
                    self.active_section_idx = (self.active_section_idx + 1) % len(self.sections)
                    return True
                if event.key == pygame.K_LEFT:
                    self.active_section_idx = (self.active_section_idx - 1) % len(self.sections)
                    return True
            else: # CONTENT focused
                if self.active_section_idx == 0: # DISPLAY
                    step = 10 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
                    if event.key == pygame.K_RIGHT:
                        if self.selection_index == 0: self._open_menu("SCALE", config, all_fonts)
                        elif self.selection_index == 1: crt["enabled"] = not crt["enabled"]
                        elif self.selection_index >= 2: crt[self._get_crt_key()] = min(255, crt[self._get_crt_key()] + step)
                        return True
                    if event.key == pygame.K_LEFT:
                        if self.selection_index == 0: self._open_menu("SCALE", config, all_fonts)
                        elif self.selection_index == 1: crt["enabled"] = not crt["enabled"]
                        elif self.selection_index >= 2: crt[self._get_crt_key()] = max(0, crt[self._get_crt_key()] - step)
                        return True
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        if self.selection_index == 0: self._open_menu("SCALE", config, all_fonts)
                        elif self.selection_index == 1: crt["enabled"] = not crt["enabled"]
                        return True
                else: # FONTS
                    if event.key == pygame.K_RIGHT:
                        self.selection_col = 1
                        return True
                    if event.key == pygame.K_LEFT:
                        self.selection_col = 0
                        return True
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        role = ["H1", "H2", "Body", "Small"][self.selection_index]
                        if self.selection_col == 0:
                            self._open_menu(role, config, all_fonts)
                        else:
                            self.editing_preview = True
                        return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # TABS area
            if 30 <= my <= 50:
                current_tab_x = 20
                for i, section in enumerate(self.sections):
                    tab_w = styles.get_font("H2").get_width(section) + 10
                    if current_tab_x <= mx <= current_tab_x + tab_w:
                        self.active_section_idx = i
                        self.selection_index = -1
                        return True
                    current_tab_x += tab_w + 20

            # CONTENT area
            if self.active_section_idx == 0:
                for i in range(6):
                    row_y = 80 + i * 25
                    if 15 <= mx <= 465 and row_y - 5 <= my <= row_y + 15:
                        self.selection_index = i
                        if mx > 280:
                            if i == 0: self._open_menu("SCALE", config, all_fonts)
                            elif i == 1: crt["enabled"] = not crt["enabled"]
                            elif i >= 2: 
                                self.dragging = i
                                self._update_slider_from_mouse(mx, crt)
                        return True
            else:
                for i in range(4):
                    row_y = 80 + i * 42
                    if 15 <= mx <= 465 and row_y - 10 <= my <= row_y + 35:
                        self.selection_index = i
                        role = ["H1", "H2", "Body", "Small"][i]
                        if 80 <= mx <= 184:
                            self.selection_col = 0
                            self._open_menu(role, config, all_fonts)
                        elif 264 <= mx <= 444:
                            self.selection_col = 1
                            self.editing_preview = True
                        else:
                            self.selection_col = 0
                        return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = None

        if event.type == pygame.MOUSEMOTION and self.dragging is not None:
            self._update_slider_from_mouse(mx, crt)
            return True

        return False

    def _get_crt_key(self):
        keys = [None, None, "scanline_alpha", "grille_alpha", "bloom_alpha", "bloom_offset"]
        return keys[self.selection_index]

    def _open_menu(self, id, config, all_fonts):
        self.open_dropdown = id
        options = self._get_dropdown_options(config, all_fonts)
        curr_val = config["scale"] if id == "SCALE" else styles.get_font(id).name
        try:
            self.open_dropdown_idx = options.index(curr_val)
        except:
            self.open_dropdown_idx = 0

    def _get_dropdown_anchor_y(self):
        if self.active_section_idx == 0: return 80
        roles = ["H1", "H2", "Body", "Small"]
        return 80 + roles.index(self.open_dropdown) * 42

    def _get_dropdown_options(self, config, all_fonts):
        if self.open_dropdown == "SCALE": return [1, 2, 3, 4]
        return sorted(list(all_fonts.keys()))

    def _set_dropdown_val(self, id, val, config, all_fonts):
        if id == "SCALE": config["scale"] = val
        else: styles.set_font(id, all_fonts[val])

    def _update_slider_from_mouse(self, vx, crt):
        if self.dragging is None: return
        bar_x, bar_w = 280, 100
        percent = max(0, min(bar_w, vx - bar_x)) / bar_w
        key = self._get_crt_key()
        if key == "bloom_offset": crt[key] = int(percent * 10)
        else: crt[key] = int(percent * 255)

    def draw_view(self, buffer, game_state):
        self.game_state = game_state
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        COLOR_PANEL = (25, 22, 19)
        COLOR_SELECT = (40, 35, 30)
        
        crt = game_state.get('crt_settings')
        config = game_state.get('config')
        all_fonts = game_state.get('all_fonts', {})
        
        body_f = styles.get_font("Body")
        h2_f = styles.get_font("H2")
        small_f = styles.get_font("Small")
        if not body_f or not crt: return

        # Load UI Assets if missing
        if "down_arrow" not in self.ui_assets:
            import os
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            asset_path = os.path.join(repo_root, "assets", "ui", "▼-5px.png")
            try:
                self.ui_assets["down_arrow"] = pygame.image.load(asset_path).convert_alpha()
            except:
                self.ui_assets["down_arrow"] = None

        # --- PANEL BASE ---
        px, py, pw, ph = 10, 40, 460, 220
        pygame.draw.rect(buffer, COLOR_PANEL, (px, py, pw, ph))
        pygame.draw.line(buffer, COLOR_DIM, (px, py + ph), (px, py)) 
        pygame.draw.line(buffer, COLOR_DIM, (px, py + ph), (px + pw, py + ph)) 
        pygame.draw.line(buffer, COLOR_DIM, (px + pw, py + ph), (px + pw, py)) 
        
        # --- DUAL H2 TITLES ---
        current_top_x = px
        # Use cap_h to center on the border line
        cap_h = h2_f.metadata.get("cap_h", 8)
        
        # TUI Rule: 8px gaps (character-wide spaces)
        TUI_GAP = 8
        
        for i, section in enumerate(self.sections):
            is_active = (self.active_section_idx == i)
            title_w = h2_f.get_width(section)
            
            gap_start = current_top_x + TUI_GAP
            gap_end = gap_start + title_w + TUI_GAP
            
            # Segment of border line before this title gap
            pygame.draw.line(buffer, COLOR_DIM, (current_top_x, py), (gap_start, py))
            
            # Base background for the title area (erases main border line in the gap)
            pygame.draw.rect(buffer, COLOR_PANEL, (gap_start, py - 5, title_w + TUI_GAP, 10))
            
            # Focus/Selection Highlight
            if is_active and self.selection_index == -1:
                pygame.draw.rect(buffer, COLOR_SELECT, (gap_start, py - (cap_h // 2) - 2, title_w + TUI_GAP, cap_h + 6))

            # Render text centered vertically on the line
            text_color = COLOR_ACCENT if is_active else COLOR_DIM
            # Padding text 4px into the gap
            h2_f.draw(buffer, section, gap_start + 4, py + (cap_h // 2), text_color)
            
            current_top_x = gap_end
        
        pygame.draw.line(buffer, COLOR_DIM, (current_top_x, py), (px + pw, py))

        # --- CONTENT ---
        # Grid Alignment (multiples of 8)
        COL_LBL = 24
        COL_VAL = 80
        COL_SIZE = 200
        COL_PREV = 264

        if self.active_section_idx == 0: # DISPLAY
            options = [("RENDER SCALE", f"x{config['scale']}", None), ("CRT EFFECT", "ON" if crt["enabled"] else "OFF", None),
                       ("SCANLINE INTENSITY", f"{crt['scanline_alpha']}", crt['scanline_alpha']/255),
                       ("GRILLE INTENSITY", f"{crt['grille_alpha']}", crt['grille_alpha']/255),
                       ("BLOOM INTENSITY", f"{crt['bloom_alpha']}", crt['bloom_alpha']/255),
                       ("BLOOM OFFSET", f"{crt['bloom_offset']}px", crt['bloom_offset']/10)]
            for i, (label, val_str, percent) in enumerate(options):
                y = 80 + i * 25
                is_sel = (i == self.selection_index)
                color = COLOR_ACCENT if is_sel else COLOR_FG
                if is_sel: pygame.draw.rect(buffer, COLOR_SELECT, (15, y - 5, 450, 22))
                body_f.draw(buffer, label, COL_LBL, y + 12, color)
                
                val_x = 280 # Keep standard alignment for Display view sliders
                if i == 0:
                    pygame.draw.rect(buffer, (20, 18, 16), (val_x, y - 2, 60, 16))
                    pygame.draw.rect(buffer, color, (val_x, y - 2, 60, 16), 1)
                    body_f.draw(buffer, val_str, val_x + 8, y + 12, color)
                    # Use 5px Arrow Asset
                    if self.ui_assets.get("down_arrow"):
                        # Tint arrow if selected? No, keeping it original or applying color logic if SpriteFont handled it.
                        # For now, blit as is but centered in the 16px row (y is baseline at +12)
                        # Box is (val_x, y-2, 60, 16). Center of box y = (y-2) + 8 = y + 6.
                        # Arrow is 5px high. y = (y+6) - 2.5 = y + 3.5.
                        buffer.blit(self.ui_assets["down_arrow"], (val_x + 48, y + 4))
                    else:
                        pygame.draw.polygon(buffer, color, [(val_x + 48, y + 3), (val_x + 56, y + 3), (val_x + 52, y + 10)])
                elif percent is not None:
                    pygame.draw.rect(buffer, (30, 25, 20), (val_x, y + 2, 100, 10))
                    pygame.draw.rect(buffer, color, (val_x, y + 2, int(100 * percent), 10))
                    body_f.draw(buffer, val_str, val_x + 110, y + 12, color)
                else: body_f.draw(buffer, val_str, val_x, y + 12, color)
        
        else: # FONTS
            roles = ["H1", "H2", "Body", "Small"]
            for i, role in enumerate(roles):
                y = 80 + i * 42
                is_row_sel = (i == self.selection_index)
                
                # Role label (TUI grid: 6 chars + colon)
                label_text = f"{role:5}:"
                body_f.draw(buffer, label_text, COL_LBL, y + 9, COLOR_ACCENT if is_row_sel else COLOR_DIM)
                
                font = styles.get_font(role)
                dim_str = f"{font.effective_w}x{font.effective_h}" if font else "?x?"
                
                # --- [ DROPDOWN ] ---
                is_drop_sel = (is_row_sel and self.selection_col == 0)
                dc = COLOR_ACCENT if is_drop_sel else COLOR_FG
                
                if is_drop_sel: pygame.draw.rect(buffer, COLOR_SELECT, (COL_VAL - 4, y - 6, 112, 22))
                
                # Dropbox Box (Tightened)
                pygame.draw.rect(buffer, (20, 18, 16), (COL_VAL, y - 4, 104, 18))
                pygame.draw.rect(buffer, dc, (COL_VAL, y - 4, 104, 18), 1)
                
                if font:
                    body_f.draw(buffer, font.name[:10].ljust(10), COL_VAL + 5, y + 9, dc)
                    # Use 5px Arrow Asset
                    if self.ui_assets.get("down_arrow"):
                        # Box (COL_VAL, y-4, 104, 18). Center y = (y-4) + 9 = y + 5.
                        # Arrow 5px high. y = (y+5) - 2.5 = y + 2.5.
                        buffer.blit(self.ui_assets["down_arrow"], (COL_VAL + 90, y + 3))
                    else:
                        pygame.draw.polygon(buffer, dc, [(COL_VAL + 90, y + 4), (COL_VAL + 98, y + 4), (COL_VAL + 94, y + 10)])
                
                # --- { SIZE } ---
                small_f.draw(buffer, dim_str, COL_SIZE, y + 9, COLOR_DIM)
                
                # --- [ PREVIEW TEXT ] ---
                is_prev_sel = (is_row_sel and self.selection_col == 1)
                pc = COLOR_ACCENT if is_prev_sel else COLOR_FG
                
                # Preview Textbox height tightened to line height (approx 18-24px)
                prev_h = 24 
                if is_prev_sel: 
                    pygame.draw.rect(buffer, COLOR_SELECT, (COL_PREV - 4, y - 4, 188, prev_h + 4))
                
                pygame.draw.rect(buffer, (15, 12, 10), (COL_PREV, y - 2, 180, prev_h))
                if is_prev_sel:
                    pygame.draw.rect(buffer, pc, (COL_PREV, y - 2, 180, prev_h), 1)
                
                if font:
                    txt = self.preview_texts[role]
                    if self.editing_preview and is_prev_sel:
                        if pygame.time.get_ticks() // 500 % 2 == 0:
                            txt += "_"
                    # Vertical padding into the tightened box
                    font.draw(buffer, txt, COL_PREV + 5, y + (prev_h // 2) + 2, COLOR_FG)

        # --- DROPDOWN (HIGHEST Z-ORDER) ---
        if self.open_dropdown:
            val_x = COL_VAL if self.active_section_idx == 1 else 280
            row_y = self._get_dropdown_anchor_y()
            options = self._get_dropdown_options(config, all_fonts)
            drop_w = 104 if self.active_section_idx == 1 else 100
            drop_h = min(len(options), 8) * 16 + 4
            
            # Shadow
            pygame.draw.rect(buffer, (5, 4, 3), (val_x + 2, row_y + 16, drop_w, drop_h))
            # Main Box
            pygame.draw.rect(buffer, (30, 28, 25), (val_x, row_y + 14, drop_w, drop_h))
            pygame.draw.rect(buffer, COLOR_ACCENT, (val_x, row_y + 14, drop_w, drop_h), 1)
            for i, opt in enumerate(options):
                if i >= 8: break
                opt_y = row_y + 14 + 2 + i * 16
                is_highlight = (i == self.open_dropdown_idx)
                if is_highlight: pygame.draw.rect(buffer, (60, 55, 50), (val_x + 1, opt_y, drop_w - 2, 14))
                txt = f"x{opt}" if self.open_dropdown == "SCALE" else str(opt)[:12]
                body_f.draw(buffer, txt, val_x + 8, opt_y + 11, COLOR_ACCENT if is_highlight else COLOR_FG)
