import pygame

class StyleManager:
    """
    Centralized theme management for the Retro-Py UI.
    Handles color palettes and sprite-font roles.
    """
    def __init__(self):
        self.fonts = {} # Role -> SpriteFont object
        self.colors = {
            "bg": (15, 13, 11),         # Dark Grey
            "panel": (25, 22, 19),      # Slightly lighter
            "accent": (230, 200, 100),  # Gold
            "header": (230, 200, 100),  # Gold          (=accent)
            "dim": (100, 90, 80),       # Grey
            "fg": (220, 210, 190),      # Off-white
            "shadow": (5, 4, 3),        # Near Black
            "select": (60, 55, 50),     # Grey          (panel + highlight)
            "textbox_bg": (15, 12, 10)  # Dark Grey
        }

    def set_font(self, role, font_obj):
        """Register a SpriteFont object for a specific UI role (e.g., 'H1', 'Body')."""
        self.fonts[role] = font_obj

    def get_font(self, role):
        """Retrieve the SpriteFont object for the given role."""
        return self.fonts.get(role)

    def get_color(self, name):
        """Retrieve a theme color by name. Returns white if not found."""
        return self.colors.get(name, (255, 255, 255))

# Global instance
styles = StyleManager()
