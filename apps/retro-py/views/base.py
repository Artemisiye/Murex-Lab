class BaseView:
    def __init__(self, styles):
        self.styles = styles
        self.selection_index = 0

    def handle_event(self, event, game_state):
        """Handle view-specific events. Return True if event was consumed."""
        if event.type == 1024: # KEYDOWN
            if event.key == 1073741905: # DOWN
                self.selection_index += 1
                return True
            if event.key == 1073741906: # UP
                self.selection_index = max(0, self.selection_index - 1)
                return True
        return False

    def draw(self, surface, game_state):
        """Draw the view to the surface."""
        pass
