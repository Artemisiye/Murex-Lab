import json
import os
import copy

class ConfigManager:
    """
    Manager for Retro-Py configuration and user settings.
    Handles persistent settings (Scale, CRT alphas, Fonts) via JSON.
    """
    DEFAULT_SETTINGS = {
        "config": {
            "scale": 4
        },
        "crt_settings": {
            "enabled": True,
            "scanline_alpha": 30,
            "grille_alpha": 12,
            "bloom_alpha": 35,
            "bloom_offset": 1
        },
        "fonts": {
            "H1": "fixedsys",
            "H2": "press-start-2p",
            "Body": "minecraftia",
            "Small": "silkscreen-400"
        }
    }

    def __init__(self, data_root):
        self.data_root = data_root
        self.settings = copy.deepcopy(self.DEFAULT_SETTINGS)

    def get_settings_path(self):
        """Returns the absolute path to the user_settings.json file."""
        if not os.path.exists(self.data_root):
            os.makedirs(self.data_root, exist_ok=True)
        return os.path.join(self.data_root, "user_settings.json")

    def load(self):
        """Loads user settings from disk, merging with defaults if keys are missing."""
        path = self.get_settings_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Merge loaded data over defaults
                    for k in self.settings:
                        if k in data and isinstance(data[k], dict):
                            self.settings[k].update(data[k])
                    return True
            except Exception as e:
                print(f"ConfigManager: Failed to load user settings: {e}")
        return False

    def save(self):
        """Saves the current settings to disk."""
        path = self.get_settings_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            print(f"ConfigManager: Settings saved to {path}")
            return True
        except Exception as e:
            print(f"ConfigManager: Failed to save user settings: {e}")
            return False

    def get(self, key, default=None):
        """Retrieve a setting value (e.g. 'config' or 'fonts')."""
        return self.settings.get(key, default)
