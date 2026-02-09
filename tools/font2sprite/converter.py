import pygame
import json
import os
import argparse
import tkinter as tk
from tkinter import filedialog

# Initialize Tkinter for file dialogs
root = tk.Tk()
root.withdraw()

class FontApp:
    def __init__(self, initial_font=None, initial_size=32):
        pygame.init()
        self.screen_w = 1260
        self.screen_h = 850
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Murex Lab - Font2Sprite Analyzer (Advanced)")
        
        self.font_path = initial_font
        self.font_size = initial_size
        self.font_size_str = str(initial_size)
        
        self.export_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/retro-py/assets/fonts"))
        
        self.char_set = "".join(chr(i) for i in range(32, 127))
        self.selected_char = 'M'
        
        self.colors = {
            "bg": (15, 13, 11),
            "panel": (25, 22, 19),
            "accent": (230, 200, 100),
            "fg": (220, 220, 220),
            "dim": (120, 110, 100),
            "grid": (45, 42, 38),
            "bounds": (255, 60, 60),
            "pixel_box": (60, 150, 255),
            "baseline": (255, 255, 255),
            "advance": (100, 255, 100)
        }
        
        self.ui_font = pygame.font.SysFont("monospace", 14)
        self.ui_font_bold = pygame.font.SysFont("monospace", 16, bold=True)
        
        self.metrics = []
        self.atlas = None
        self.needs_update = True
        self.input_focus = None 
        self.export_success_timer = 0
        
        self.ascent = 0
        self.descent = 0
        self.measured_cap_h = 0
        
        self.threshold = 127
        self.overrides = {} # dict of char -> { 'advance_adj': 0 }

    def browse_font(self):
        val = filedialog.askopenfilename(initialdir=os.path.dirname(self.font_path) if self.font_path else "E:\\Emerald Vimana\\Murex-Lab\\apps\\retro\\static\\fonts")
        if val: 
            self.font_path = val
            self.needs_update = True

    def browse_export(self):
        val = filedialog.askdirectory(initialdir=self.export_path)
        if val: self.export_path = val

    def get_alpha_array(self, surf):
        try:
            arr = pygame.surfarray.array_alpha(surf)
        except:
            temp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            temp.blit(surf, (0,0))
            arr = pygame.surfarray.array_alpha(temp)
        
        # Apply Threshold to find "Solid" pixels
        mask = arr >= self.threshold
        return mask.astype(int) * 255

    def calculate_actual_metrics(self, font):
        test_surf = font.render("M", False, (255, 255, 255))
        arr = self.get_alpha_array(test_surf)
        rows = arr.max(axis=0)
        if rows.any():
            nz = rows.nonzero()[0]
            self.measured_cap_h = nz[-1] - nz[0] + 1
            self.ascent = font.get_ascent()
            self.descent = font.get_descent()
        else:
            self.measured_cap_h = 0

    def update_font(self):
        if not self.font_path or not os.path.exists(self.font_path): return
        try:
            font = pygame.font.Font(self.font_path, self.font_size)
            self.calculate_actual_metrics(font)
        except Exception as e:
            return

        self.metrics = []
        spacing = 4
        total_w = 0
        max_h = 0

        for char in self.char_set:
            raw_surf = font.render(char, False, (255, 255, 255))
            raw_w, raw_h = raw_surf.get_size()
            raw_pixels = self.get_alpha_array(raw_surf)
            
            rows = raw_pixels.max(axis=0)
            cols = raw_pixels.max(axis=1)
            
            if rows.any():
                nz_y = rows.nonzero()[0]
                p_top, p_bottom = nz_y[0], nz_y[-1]
                nz_x = cols.nonzero()[0]
                p_left, p_right = nz_x[0], nz_x[-1]
                
                w, h = p_right - p_left + 1, p_bottom - p_top + 1
                char_metrics = font.metrics(char)[0]
                
                # Baseline is at 'ascent' pixels down from raw_surf top
                dist_to_base = self.ascent - p_top
                
                cropped = pygame.Surface((w, h), pygame.SRCALPHA)
                cropped.blit(raw_surf, (0, 0), (p_left, p_top, w, h))
                
                adv = char_metrics[4]
                if char in self.overrides:
                    adv += self.overrides[char].get('advance_adj', 0)

                m = {
                    "char": char, "w": w, "h": h, 
                    "raw_w": raw_w, "raw_h": raw_h,
                    "p_left": p_left, "p_top": p_top,
                    "advance": adv,
                    "base_y": dist_to_base,
                    "surf": cropped
                }
            else:
                m = {"char": char, "w": 0, "h": 0, "raw_w": raw_w, "raw_h": raw_h, "advance": font.size(char)[0], "base_y": 0, "surf": None}
            
            self.metrics.append(m)
            total_w += m["w"] + spacing
            max_h = max(max_h, m["h"])

        self.atlas = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
        curr_x = 0
        for m in self.metrics:
            if m["surf"]:
                self.atlas.blit(m["surf"], (curr_x, 0))
            m["atlas_x"] = curr_x
            curr_x += m["w"] + spacing
        
        self.needs_update = False

    def draw_text_input(self, rect, value, label, focus=False):
        pygame.draw.rect(self.screen, self.colors["panel"], rect)
        if focus: pygame.draw.rect(self.screen, self.colors["accent"], rect, 1)
        self.screen.blit(self.ui_font.render(label, True, self.colors["dim"]), (rect.x, rect.y - 18))
        txt = self.ui_font.render(value + ("|" if focus and (pygame.time.get_ticks()//500 % 2) else ""), True, self.colors["fg"])
        self.screen.blit(txt, (rect.x+10, rect.y+7))

    def draw_button(self, rect, text, active=False):
        mx, my = pygame.mouse.get_pos()
        hover = rect.collidepoint(mx, my)
        color = self.colors["accent"] if (active or hover) else self.colors["panel"]
        pygame.draw.rect(self.screen, color, rect, border_radius=4)
        if not (active or hover):
            pygame.draw.rect(self.screen, self.colors["dim"], rect, 1, border_radius=4)
        label = text
        if self.ui_font.size(text)[0] > rect.w - 10:
            label = ".." + text[-(int(rect.w/9)):]
        txt = self.ui_font.render(label, True, (0,0,0) if (active or hover) else self.colors["fg"])
        t_rect = txt.get_rect(center=rect.center)
        self.screen.blit(txt, t_rect)
        return hover

    def run(self):
        clock = pygame.time.Clock()
        while True:
            if self.needs_update: self.update_font()
            mx, my = pygame.mouse.get_pos()
            click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: click = True
                if event.type == pygame.KEYDOWN:
                    if self.input_focus == "size":
                        if event.key == pygame.K_RETURN: self.input_focus = None
                        elif event.key == pygame.K_BACKSPACE: self.font_size_str = self.font_size_str[:-1]
                        elif event.unicode.isdigit(): self.font_size_str += event.unicode
                        try:
                            if self.font_size_str:
                                self.font_size = int(self.font_size_str)
                                self.needs_update = True
                        except: pass
                    elif not self.input_focus:
                        if event.key == pygame.K_UP: 
                            self.font_size += 1
                            self.font_size_str = str(self.font_size); self.needs_update = True
                        if event.key == pygame.K_DOWN: 
                            self.font_size = max(1, self.font_size - 1)
                            self.font_size_str = str(self.font_size); self.needs_update = True

            self.screen.fill(self.colors["bg"])
            
            # --- TOP CONTROLS ---
            title = os.path.basename(self.font_path) if self.font_path else "CHOOSE FONT"
            self.screen.blit(self.ui_font_bold.render(f"FONT: {title}", True, self.colors["accent"]), (25, 15))
            
            if self.draw_button(pygame.Rect(25, 45, 300, 30), (self.font_path or "Select Font...")):
                if click: self.browse_font()
            if self.draw_button(pygame.Rect(335, 45, 80, 30), "BROWSE", True):
                if click: self.browse_font()
            
            if self.draw_button(pygame.Rect(440, 45, 300, 30), self.export_path):
                if click: self.browse_export()
            if self.draw_button(pygame.Rect(750, 45, 80, 30), "METADATA", True):
                if click: self.browse_export()

            size_rect = pygame.Rect(860, 45, 60, 30)
            self.draw_text_input(size_rect, self.font_size_str, "SIZE", self.input_focus == "size")
            if click and size_rect.collidepoint(mx,my): self.input_focus = "size"

            # Size Slider (Restored)
            self.screen.blit(self.ui_font.render(f"SIZE SLIDER", True, self.colors["dim"]), (950, 30))
            s_slider = pygame.Rect(950, 45, 200, 10)
            pygame.draw.rect(self.screen, self.colors["panel"], s_slider)
            s_handle_x = s_slider.x + (min(self.font_size, 128) / 128) * s_slider.w
            pygame.draw.rect(self.screen, self.colors["accent"], (s_handle_x-3, 40, 6, 20))
            if pygame.mouse.get_pressed()[0] and s_slider.inflate(0, 30).collidepoint(mx,my):
                self.font_size = int(((mx - s_slider.x) / s_slider.w) * 128)
                self.font_size = max(1, min(128, self.font_size))
                self.font_size_str = str(self.font_size)
                self.needs_update = True

            # --- GRID (RAISED) ---
            char_w, char_h = 32, 45
            cols = 38
            grid_y = 100
            for i, m in enumerate(self.metrics):
                r = pygame.Rect(25 + (i % cols) * char_w, grid_y + (i // cols) * char_h, char_w, char_h)
                is_sel = m["char"] == self.selected_char
                if r.collidepoint(mx,my):
                    pygame.draw.rect(self.screen, self.colors["panel"], r)
                    if click: self.selected_char = m["char"]
                if is_sel:
                    pygame.draw.rect(self.screen, self.colors["panel"], r)
                    pygame.draw.rect(self.screen, self.colors["accent"], r, 1)
                if m["surf"]:
                    self.screen.blit(m["surf"], m["surf"].get_rect(center=r.center))

            # --- DETAIL PANEL (RAISED) ---
            panel = pygame.Rect(25, 400, 1210, 420)
            pygame.draw.rect(self.screen, self.colors["panel"], panel)
            pygame.draw.rect(self.screen, self.colors["dim"], panel, 1)

            sel_m = next((m for m in self.metrics if m["char"] == self.selected_char), None)
            if sel_m:
                view_x, view_y = 60, 440
                zoom = 10
                guide_w, guide_h = 48, 36 
                
                center_x = view_x + (guide_w // 2) * zoom
                fixed_baseline_y = view_y + 24 * zoom
                
                # Visual Grid
                for gx in range(guide_w + 1):
                    pygame.draw.line(self.screen, self.colors["grid"], (view_x + gx*zoom, view_y), (view_x + gx*zoom, view_y + guide_h*zoom))
                for gy in range(guide_h + 1):
                    pygame.draw.line(self.screen, self.colors["grid"], (view_x, view_y + gy*zoom), (view_x + guide_w*zoom, view_y + gy*zoom))
                
                # GUIDES
                red_x = center_x - (sel_m["raw_w"] // 2) * zoom
                red_y = fixed_baseline_y - self.ascent * zoom
                pygame.draw.rect(self.screen, self.colors["bounds"], (red_x, red_y, sel_m["raw_w"]*zoom, sel_m["raw_h"]*zoom), 1)

                blue_x = red_x + sel_m["p_left"] * zoom
                blue_y = red_y + sel_m["p_top"] * zoom
                pygame.draw.rect(self.screen, self.colors["pixel_box"], (blue_x, blue_y, sel_m["w"]*zoom, sel_m["h"]*zoom), 1)

                pygame.draw.line(self.screen, self.colors["baseline"], (view_x, fixed_baseline_y), (view_x + guide_w*zoom, fixed_baseline_y), 2)
                
                # ADVANCE INDICATOR
                adv_x = red_x + sel_m["advance"] * zoom
                pygame.draw.line(self.screen, self.colors["advance"], (adv_x, view_y), (adv_x, view_y + guide_h*zoom), 2)
                self.screen.blit(self.ui_font.render("ADVANCE", True, self.colors["advance"]), (adv_x + 5, view_y + 10))

                if sel_m["surf"]:
                    big_g = pygame.transform.scale(sel_m["surf"], (sel_m["w"] * zoom, sel_m["h"] * zoom))
                    self.screen.blit(big_g, (blue_x, blue_y))

                # --- OVERRIDE UI ---
                ov_x = 550
                self.screen.blit(self.ui_font_bold.render(f"KERNING/ADVANCE OVERRIDE: {self.selected_char}", True, self.colors["accent"]), (ov_x, 440))
                
                adj = self.overrides.get(self.selected_char, {}).get('advance_adj', 0)
                self.screen.blit(self.ui_font.render(f"Correction: {adj}px", True, self.colors["fg"]), (ov_x, 470))
                
                if self.draw_button(pygame.Rect(ov_x, 495, 40, 30), "-1"):
                    if click: self.overrides.setdefault(self.selected_char, {})['advance_adj'] = adj - 1; self.needs_update = True
                if self.draw_button(pygame.Rect(ov_x + 50, 495, 40, 30), "+1"):
                    if click: self.overrides.setdefault(self.selected_char, {})['advance_adj'] = adj + 1; self.needs_update = True
                if self.draw_button(pygame.Rect(ov_x + 100, 495, 60, 30), "RESET"):
                    if click: self.overrides.pop(self.selected_char, None); self.needs_update = True

                # STATS
                stats_y = 550
                is_target = self.measured_cap_h == 14
                lines = [
                    f"Pixel BBox:   {sel_m['w']}x{sel_m['h']} px",
                    f"Base Offset:  {sel_m['base_y']} px",
                    f"Font Advance: {sel_m['advance']} px",
                    "",
                    f"--- PROJECT SYNC ---",
                    f"MEASURED CAP H: {self.measured_cap_h} px" + (" [TARGET-READY]" if is_target else ""),
                    f"Status: " + ("OPTIMAL" if is_target else "SUB-OPTIMAL")
                ]
                for i, line in enumerate(lines):
                    col = self.colors["accent"] if "TARGET" in line else self.colors["fg"]
                    self.screen.blit(self.ui_font.render(line, True, col), (ov_x, stats_y + i*22))

            if self.draw_button(pygame.Rect(1100, 780, 130, 30), "EXPORT ALL"):
                if click and self.font_path:
                    fname = os.path.splitext(os.path.basename(self.font_path))[0] + f"_{self.font_size}"
                    out_p = os.path.join(self.export_path, fname)
                    pygame.image.save(self.atlas, out_p + ".png")
                    meta = {
                        "family": os.path.basename(self.font_path),
                        "req_size": int(self.font_size), "cap_h": int(self.measured_cap_h), "threshold": int(self.threshold),
                        "effective_h": 0,
                        "chars": { m["char"]: {"x": int(m["atlas_x"]), "y": 0, "w": int(m["w"]), "h": int(m["h"]), "adv": int(m["advance"]), "base_y": int(m["base_y"])} for m in self.metrics }
                    }
                    with open(out_p + ".json", "w") as f: json.dump(meta, f, indent=4)
                    print(f"Exported to {out_p}")
                    self.export_success_timer = 180 # 3 seconds at 60fps

            if self.export_success_timer > 0:
                self.screen.blit(self.ui_font_bold.render("BAKED & SAVED!", True, self.colors["advance"]), (950, 785))
                self.export_success_timer -= 1

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", help="Initial font path")
    parser.add_argument("--size", type=int, default=32, help="Initial size")
    args = parser.parse_args()
    app = FontApp(args.font, args.size)
    app.run()
