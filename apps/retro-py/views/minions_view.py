import pygame
from ui_components import Panel, styles

class MinionsView:
    def __init__(self):
        self.selection_index = 0

    def handle_event(self, event, game_state):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
                return True
        return False

    def draw(self, buffer, game_state):
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        
        # Grid Alignment (multiples of 8)
        px, py, pw, ph = 8, 32, 464, 232
        
        # Chunky TUI Shadow
        pygame.draw.rect(buffer, (5, 4, 3), (px + 4, py + 4, pw, ph))
        minion_panel = Panel(px, py, pw, ph, title="MINIONS")
        minion_panel.draw(buffer)
        
        player_minions = game_state['player_minions']
        m = player_minions[0]
        body_f = styles.get_font("Body")
        small_f = styles.get_font("Small")
        
        if body_f:
            # Baseline y=72, y=88 for info
            body_f.draw(buffer, f"NAME:  {m.name.upper()}", px + 16, 72, COLOR_ACCENT)
            body_f.draw(buffer, f"CLASS: ARTIFICER", px + 16, 88, COLOR_FG)
            
            # Health Bar (Aligned to y=112 row)
            max_hp = m.get_stat("hp")
            pygame.draw.rect(buffer, (50, 20, 20), (px + 16, 106, 120, 12))
            hp_w = int((m.current_hp / max_hp) * 120) if max_hp > 0 else 0
            pygame.draw.rect(buffer, (200, 50, 50), (px + 16, 106, hp_w, 12))
            
            if small_f:
                small_f.draw(buffer, f"HP: {int(m.current_hp)}/{int(max_hp)}", px + 144, 114, COLOR_FG)

            # Energy Bar (Aligned to y=136 row)
            pygame.draw.rect(buffer, (20, 50, 70), (px + 16, 130, 120, 12))
            en_w = int((m.current_energy / m.max_energy) * 120)
            pygame.draw.rect(buffer, (50, 150, 255), (px + 16, 130, en_w, 12))
            
            if small_f:
                small_f.draw(buffer, f"EN: {int(m.current_energy)}/{int(m.max_energy)}", px + 144, 138, COLOR_FG)
