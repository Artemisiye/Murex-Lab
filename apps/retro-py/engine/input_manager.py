import pygame

class InputManager:
    """
    Translates physical hardware events into logical game actions.
    Supports mode-aware mappings (e.g., 'UP' does different things in Map vs Combat).
    """
    def __init__(self):
        self.mode = "MENU"
        self.mappings = {
            "MENU": {
                pygame.K_UP: "NAV_UP",
                pygame.K_DOWN: "NAV_DOWN",
                pygame.K_LEFT: "NAV_LEFT",
                pygame.K_RIGHT: "NAV_RIGHT",
                pygame.K_RETURN: "CONFIRM",
                # pygame.K_SPACE: "CONFIRM",
                pygame.K_ESCAPE: "CANCEL",
                pygame.K_BACKSPACE: "CANCEL",
                pygame.K_TAB: "NEXT_TAB"
                # how do we handle Shift+Tab?
                # , pygame.K_TAB: "PREV_TAB",
            },
            "MAP": {
                pygame.K_w:         "MOVE_UP",
                pygame.K_UP:        "MOVE_UP",

                pygame.K_s:         "MOVE_DOWN",
                pygame.K_DOWN:      "MOVE_DOWN",

                pygame.K_a:         "MOVE_LEFT",
                pygame.K_LEFT:      "MOVE_LEFT",

                pygame.K_d:         "MOVE_RIGHT",
                pygame.K_RIGHT:     "MOVE_RIGHT",

                pygame.K_RETURN:    "INTERACT",
                pygame.K_SPACE:     "INTERACT",

                pygame.K_BACKSPACE: "RETURN",
                pygame.K_ESCAPE:    "RETURN",

                pygame.K_m:         "TOGGLE_MAP",
                pygame.K_i:         "OPEN_INVENTORY"
            },
            "COMBAT": {
                pygame.K_1: "SKILL_1",
                pygame.K_2: "SKILL_2",
                pygame.K_3: "SKILL_3",
                # pygame.K_SPACE: "END_TURN"
            }
        }

    def set_mode(self, mode):
        """Switches the active input mapping profile."""
        if mode in self.mappings:
            self.mode = mode

    def get_action(self, event):
        """
        Translates a pygame event into a logical action string.
        Returns None if the event is not mapped in the current mode.
        """
        if event.type == pygame.KEYDOWN:
            mode_map = self.mappings.get(self.mode, {})
            return mode_map.get(event.key)
        return None

    def handle_raw_event(self, event):
        """
        Entry point for Pygame event loop.
        Can handle common global shortcuts (F1, F2, etc) 
        before mode-specific translation.
        """
        if event.type == pygame.KEYDOWN:
            # 1. Global Navigation Shortcuts
            if event.key == pygame.K_TAB:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    return "PREV_TAB"
                return "NEXT_TAB"

            # 2. Global Engine Shortcuts
            if event.key == pygame.K_F1: return "TOGGLE_DEBUG"
            if event.key == pygame.K_F2: return "HOT_RELOAD"
            
        return self.get_action(event)
