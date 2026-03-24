import pygame
from ui_components import BaseView, Panel, Label, styles

class MinionsView(BaseView):
    def __init__(self):
        super().__init__()
        self.selection_index = 0
        
        # Persistent UI Layout
        self.main_panel = Panel(x=0, y=0, w=40, h=30, title="MINIONS")
        self.stats_panel = Panel(x=40, y=0, w=20, h=30, title="STATS")
        
        self.add_child(self.main_panel)
        self.add_child(self.stats_panel)

    def handle_event(self, event, mx, my):
        if super().handle_event(event, mx, my):
            return True
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
                return True
        return False

    def draw(self, buffer):
        
        super().draw(buffer)

        # Draw dynamic content
        player_minions = self.game_state.get('player_minions', [])
        if player_minions:
            m = player_minions[0]
            body_f = styles.get_font("Body")
            small_f = styles.get_font("Small")
            
            if body_f:
                body_f.draw(buffer, f"NAME:  {m.name.upper()}", 32, 72, styles.get_color("accent"))
                body_f.draw(buffer, f"CLASS: ARTIFICER", 32, 88, styles.get_color("fg"))
                
            if small_f:
                small_f.draw(buffer, "LEVEL 1 (INITIATE)", 32, 110, styles.get_color("dim"))
