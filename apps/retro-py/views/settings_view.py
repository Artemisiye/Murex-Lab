import pygame
from ui_components import Panel, styles

class SettingsView:
    def __init__(self):
        self.selection_index = 0
        self.dragging = None # Track which setting is being dragged

    def handle_event(self, event, game_state):
        crt = game_state.get('crt_settings')
        if not crt: return False
        scale = game_state.get('scale', 1)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index = (self.selection_index + 1) % 5
                return True
            if event.key == pygame.K_UP:
                self.selection_index = (self.selection_index - 1) % 5
                return True
            
            # Adjust values with Left/Right
            step = 1
            if pygame.key.get_mods() & pygame.KMOD_SHIFT: step = 10

            if event.key == pygame.K_RIGHT:
                if self.selection_index == 0: crt["enabled"] = not crt["enabled"]
                elif self.selection_index == 1: crt["scanline_alpha"] = min(255, crt["scanline_alpha"] + step)
                elif self.selection_index == 2: crt["grille_alpha"] = min(255, crt["grille_alpha"] + step)
                elif self.selection_index == 3: crt["bloom_alpha"] = min(255, crt["bloom_alpha"] + step)
                elif self.selection_index == 4: crt["bloom_offset"] = min(10, crt["bloom_offset"] + 1)
                return True
            if event.key == pygame.K_LEFT:
                if self.selection_index == 0: crt["enabled"] = not crt["enabled"]
                elif self.selection_index == 1: crt["scanline_alpha"] = max(0, crt["scanline_alpha"] - step)
                elif self.selection_index == 2: crt["grille_alpha"] = max(0, crt["grille_alpha"] - step)
                elif self.selection_index == 3: crt["bloom_alpha"] = max(0, crt["bloom_alpha"] - step)
                elif self.selection_index == 4: crt["bloom_offset"] = max(0, crt["bloom_offset"] - 1)
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            vx, vy = mx // scale, my // scale
            
            # 1. Toggle CRT Enabled
            if 20 <= vx <= 460 and 75 <= vy <= 95:
                self.selection_index = 0
                if vx > 280: # Clicked on the value area
                    crt["enabled"] = not crt["enabled"]
                return True

            # 2. Slider Interaction
            for i in range(1, 5):
                row_y = 80 + i * 25
                # Range for the slider bar itself (approx 280 to 380)
                if 280 <= vx <= 385 and row_y - 5 <= vy <= row_y + 15:
                    self.selection_index = i
                    self.dragging = i
                    self._update_slider_from_mouse(vx, crt)
                    return True
                # Selection only if clicking the label
                elif 20 <= vx <= 270 and row_y - 5 <= vy <= row_y + 15:
                    self.selection_index = i
                    return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = None

        if event.type == pygame.MOUSEMOTION and self.dragging is not None:
            mx, my = event.pos
            vx, vy = mx // scale, my // scale
            self._update_slider_from_mouse(vx, crt)
            return True

        return False

    def _update_slider_from_mouse(self, vx, crt):
        if self.dragging is None: return
        
        # Slider bounds: 280 to 380 (width 100)
        bar_x = 280
        bar_w = 100
        rel_x = max(0, min(bar_w, vx - bar_x))
        percent = rel_x / bar_w
        
        if self.dragging == 1: crt["scanline_alpha"] = int(percent * 255)
        elif self.dragging == 2: crt["grille_alpha"] = int(percent * 255)
        elif self.dragging == 3: crt["bloom_alpha"] = int(percent * 255)
        elif self.dragging == 4: crt["bloom_offset"] = int(percent * 10)

    def draw(self, buffer, game_state):
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        crt = game_state.get('crt_settings')
        
        settings_panel = Panel(10, 40, 460, 220, title="SYSTEM CONFIG")
        settings_panel.draw(buffer)
        
        body_f = styles.get_font("Body")
        h2_f = styles.get_font("H2")
        if not body_f or not crt: return

        options = [
            ("CRT EFFECT", "ON" if crt["enabled"] else "OFF", None),
            ("SCANLINE INTENSITY", f"{crt['scanline_alpha']}", crt['scanline_alpha']/255),
            ("GRILLE INTENSITY", f"{crt['grille_alpha']}", crt['grille_alpha']/255),
            ("BLOOM INTENSITY", f"{crt['bloom_alpha']}", crt['bloom_alpha']/255),
            ("BLOOM OFFSET", f"{crt['bloom_offset']}px", crt['bloom_offset']/10),
        ]

        for i, (label, val_str, percent) in enumerate(options):
            y = 80 + i * 25
            is_sel = (i == self.selection_index)
            color = COLOR_ACCENT if is_sel else COLOR_FG
            
            if is_sel:
                pygame.draw.rect(buffer, (40, 35, 30), (15, y - 5, 450, 22))
            
            body_f.draw(buffer, label, 25, y + 12, color)
            
            # Draw value/slider
            val_x = 280
            if percent is not None:
                # Draw bar
                bar_w = 100
                pygame.draw.rect(buffer, (30, 25, 20), (val_x, y + 2, bar_w, 10))
                pygame.draw.rect(buffer, color, (val_x, y + 2, int(bar_w * percent), 10))
                body_f.draw(buffer, val_str, val_x + bar_w + 10, y + 12, color)
            else:
                body_f.draw(buffer, val_str, val_x, y + 12, color)
