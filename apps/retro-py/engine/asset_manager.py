import pygame
import os
from renderer import SpriteFont

class AssetManager:
    """
    Centralized repository for all static game resources.
    Handles loading, caching, and retrieval of fonts, sprites, and sounds.
    """
    def __init__(self, asset_root):
        self.root = asset_root
        self.cache = {
            "fonts": {},
            "sprites": {},
            "sounds": {}
        }

    def load_font(self, name, json_path):
        """Loads and caches a SpriteFont."""
        if name not in self.cache["fonts"]:
            print(f"AssetManager: Loading font '{name}' from {json_path}")
            self.cache["fonts"][name] = SpriteFont(json_path)
        return self.cache["fonts"][name]

    def load_fonts_from_dir(self, dir_path):
        """Batch loads all .json sprite fonts from a directory."""
        if not os.path.exists(dir_path): return
        for f in os.listdir(dir_path):
            if f.endswith(".json"):
                name = f.replace(".json", "")
                self.load_font(name, os.path.join(dir_path, f))

    def load_sprites_from_dir(self, dir_path, category=""):
        """Batch loads all .png images from a directory."""
        full_dir = os.path.join(dir_path, category)
        if not os.path.exists(full_dir): return
        for f in os.listdir(full_dir):
            if f.endswith(".png"):
                name = f.replace(".png", "")
                self.load_sprite(name, os.path.join(category, f))

    def get_font(self, name):
        """Retrieves a cached font."""
        return self.cache["fonts"].get(name)

    def load_sprite(self, name, sub_path):
        """Loads and caches a pygame surface."""
        if name not in self.cache["sprites"]:
            full_path = os.path.join(self.root, "sprites", sub_path)
            self.cache["sprites"][name] = pygame.image.load(full_path).convert_alpha()
        return self.cache["sprites"][name]

    def get_sprite(self, name):
        """Retrieves a cached sprite."""
        return self.cache["sprites"].get(name)

    def load_sound(self, name, sub_path):
        """Loads and caches a pygame sound."""
        if name not in self.cache["sounds"]:
            full_path = os.path.join(self.root, "sounds", sub_path)
            self.cache["sounds"][name] = pygame.mixer.Sound(full_path)
        return self.cache["sounds"][name]

    def get_sound(self, name):
        """Retrieves a cached sound."""
        return self.cache["sounds"].get(name)

    def flush_cache(self, asset_type=None):
        """Clears memory for a specific category or the entire cache."""
        if asset_type:
            if asset_type in self.cache:
                self.cache[asset_type].clear()
        else:
            for category in self.cache:
                self.cache[category].clear()

    def setup_font_styles(self, user_fonts_config):
        """
        Maps font roles (H1, H2, Body, Small) to loaded fonts.
        Config format: {"H1": "name", "H2": "name", ...}
        """
        from ui import styles
        
        # Default fallback mapping
        defaults = {
            "H1": "fixedsys",
            "H2": "press-start-2p",
            "Body": "minecraftia",
            "Small": "silkscreen-400"
        }
        
        for role, default_name in defaults.items():
            font_name = user_fonts_config.get(role, default_name)
            font_obj = self.get_font(font_name)
            if font_obj:
                print(f"AssetManager: Mapping role '{role}' -> '{font_name}'")
                styles.set_font(role, font_obj)
            else:
                print(f"AssetManager: WARNING - Failed to find font '{font_name}' for role '{role}'")
