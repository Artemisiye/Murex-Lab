"""
Configuration Manager for Retro-Py.
Handles persistent user settings (Scale, CRT alphas, Fonts) via JSON.
"""

import json
import os
import copy

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

def get_settings_path():
    """Returns the absolute path to the user_settings.json file."""
    # Store settings in Murex-Lab/apps/murex_lab/data/user_settings.json
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../murex_lab/data"))
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
    return os.path.join(data_path, "user_settings.json")

def load_settings():
    """Loads user settings from disk, merging with defaults if keys are missing."""
    path = get_settings_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Merge loaded data over a fresh copy of defaults
                merged = copy.deepcopy(DEFAULT_SETTINGS)
                for k in merged:
                    if k in data and isinstance(data[k], dict):
                        merged[k].update(data[k])
                return merged
        except Exception as e:
            print(f"Failed to load user settings: {e}")
            
    return copy.deepcopy(DEFAULT_SETTINGS)

def save_settings(settings):
    """Saves the provided settings dictionary to user_settings.json."""
    path = get_settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        print(f"User settings saved to {path}")
    except Exception as e:
        print(f"Failed to save user settings: {e}")
