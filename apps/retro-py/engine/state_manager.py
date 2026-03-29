import json
import os
from modules.crafting import CraftingManager
from modules.inventory import Inventory
from modules.world_map import map_manager
from modules.minions import Minion

class GameStateManager:
    """
    Manages the game's reactive data layer.
    Separates persistent 'World' state (inventory, progress) 
    from transient 'Session' state (UI focus, temporary buffs).
    """
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.world_state = {}     # Saved to disk
        self.session_state = {}   # Volatile
        self.logic = {}           # References to Game Logic Managers (Crafting, Inventory, etc.)
        
        # Ensure save directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def load_world_data(self, file_name="world_state.json"):
        """Loads persistent data from the save directory."""
        path = os.path.join(self.save_dir, file_name)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.world_state.update(json.load(f))
                return True
            except Exception as e:
                print(f"GameStateManager: Error loading {file_name}: {e}")
        return False

    def save_world_data(self, file_name="world_state.json"):
        """Persists the world state to disk."""
        path = os.path.join(self.save_dir, file_name)
        try:
            with open(path, "w") as f:
                json.dump(self.world_state, f, indent=4)
            return True
        except Exception as e:
            print(f"GameStateManager: Error saving {file_name}: {e}")
            return False

    def get(self, key, default=None):
        """
        Retrieves a value or manager, searching order: Session -> Logic -> World.
        """
        if key in self.session_state:
            return self.session_state[key]
        if key in self.logic:
            return self.logic[key]
        return self.world_state.get(key, default)

    def register_logic(self, key, manager_obj):
        """Bind a game logic manager (e.g. 'crafting_system') to the state."""
        self.logic[key] = manager_obj

    def set_session(self, key, value):
        """Sets a transient value (lost on restart)."""
        self.session_state[key] = value

    def set_world(self, key, value, autosave=False):
        """Sets a persistent value."""
        self.world_state[key] = value
        if autosave:
            self.save_world_data()

    def update_world(self, data_dict, autosave=False):
        """Bulk updates persistent state."""
        self.world_state.update(data_dict)
        if autosave:
            self.save_world_data()

    def boot_game_logic(self, data_root):
        """
        Initializes and registers game-specific logic managers (Crafting, Inventory, Map, etc.)
        from the provided data root. These managers handle their own recovery from disk on init.
        """
        # 1. Instantiate & Register (Triggers internal load/recovery)
        self.register_logic("crafting_system", CraftingManager(data_root))
        self.register_logic("player_inventory", Inventory(os.path.join(data_root, 'player_inventory.json')))
        self.register_logic("player_backpack", Inventory(os.path.join(data_root, 'player_backpack.json')))
        self.register_logic("world_map", map_manager(data_root))
        self.register_logic("player_minions", [Minion("m_001", "Lead Artificer")])
        
        print(f"GameStateManager: Game logic managers initialized and loaded from {data_root}")

    def clear_session(self):
        """Flushes all transient data."""
        self.session_state.clear()
