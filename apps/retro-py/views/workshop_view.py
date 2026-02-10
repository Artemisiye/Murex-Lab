import pygame
from ui_components import Panel, styles

class WorkshopView:
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
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                blueprints = game_state['crafting_system'].get_all_blueprints()
                if 0 <= self.selection_index < len(blueprints):
                    bp = blueprints[self.selection_index]
                    print(f"Crafting selected: {bp.name}")
                return True
        return False

    def draw(self, buffer, game_state):
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        
        workshop_panel = Panel(10, 40, 460, 220, title="STATION: FORGE-V1")
        workshop_panel.draw(buffer)
        
        blueprints = game_state['crafting_system'].get_all_blueprints()
        body_f = styles.get_font("Body")
        small_f = styles.get_font("Small")
        
        for i, bp in enumerate(blueprints):
            if i > 10: break
            color = COLOR_FG
            if i == self.selection_index:
                color = COLOR_ACCENT
                pygame.draw.rect(buffer, (40, 35, 30), (15, 60 + i*16, 450, 16))
            
            if body_f:
                body_f.draw(buffer, f"{bp.name.upper()}", 25, 72 + i*16, color)
                if small_f:
                    small_f.draw(buffer, f"[{bp.station_id}]", 300, 72 + i*16, COLOR_DIM)
