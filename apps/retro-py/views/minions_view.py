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
        
        minion_panel = Panel(10, 40, 460, 220, title="MINION STATUS")
        minion_panel.draw(buffer)
        
        player_minions = game_state['player_minions']
        m = player_minions[0]
        body_f = styles.get_font("Body")
        small_f = styles.get_font("Small")
        
        if body_f:
            body_f.draw(buffer, f"NAME: {m.name}", 25, 70, COLOR_ACCENT)
            body_f.draw(buffer, f"CLASS: ARTIFICER", 25, 90, COLOR_FG)
            
            # Health Bar
            max_hp = m.get_stat("hp")
            pygame.draw.rect(buffer, (50, 20, 20), (25, 110, 100, 10))
            hp_w = int((m.current_hp / max_hp) * 100) if max_hp > 0 else 0
            pygame.draw.rect(buffer, (200, 50, 50), (25, 110, hp_w, 10))
            small_f.draw(buffer, f"HP: {int(m.current_hp)}/{int(max_hp)}", 130, 120, COLOR_FG)

            # Energy Bar
            pygame.draw.rect(buffer, (20, 50, 70), (25, 130, 100, 10))
            en_w = int((m.current_energy / m.max_energy) * 100)
            pygame.draw.rect(buffer, (50, 150, 255), (25, 130, en_w, 10))
            small_f.draw(buffer, f"EN: {m.current_energy}/{m.max_energy}", 130, 140, COLOR_FG)
