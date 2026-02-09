import math
from datetime import datetime, timedelta

class Minion:
    """
    Minions are the companions or servants who carry out the player's will.
    Power is derived entirely from Base Stats + attached Engravings and Weapons.
    """
    def __init__(self, id, name, base_stats=None):
        self.id = id
        self.name = name
        
        # Base stats (unmodded) - Adjusted for a pure gear-scaling model
        self.base_stats = base_stats or {
            "hp": 500,
            "atk": 100,
            "def": 100,
            "spd": 100,
            "crit_rate": 0.15,
            "crit_dmg": 0.50
        }
        
        # Energy / Exploration Capacity
        self.max_energy = 100
        self.current_energy = 100
        
        # Gear Slots
        self.engravings = {} # Slot 1-6 { "1": EngravingObject, ... }
        self.weapons = [None, None] # Slot 1 & 2 [WeaponObject, WeaponObject]
        self.trinket = None
        
        # Recovery/Death mechanics
        self.is_defeated = False
        self.recovery_until = None # datetime object
        
    def get_stat(self, stat_name):
        """Calculates final stat including fixed base and gear bonuses."""
        self.update_recovery_status()
        
        base = self.base_stats.get(stat_name, 0)
        
        # 1. Base is fixed (no more level scaling)
        scaled_base = base
        
        # 2. Add Gear Bonuses
        bonus_flat = 0
        bonus_pct = 0
        
        # Engravings logic
        for slot, engraving in self.engravings.items():
            if engraving and hasattr(engraving, 'stats'):
                val = engraving.stats.get(stat_name, 0)
                if isinstance(val, float) and val < 1.0: # Percentage-based (e.g., 0.15 for 15%)
                    bonus_pct += val
                else:
                    bonus_flat += val
        
        # Weapons/Trinkets (future implementation)
        # ...
        
        return (scaled_base * (1 + bonus_pct)) + bonus_flat

    def set_defeated(self):
        """Kicks off the recovery period (standard 3 days)."""
        self.is_defeated = True
        self.recovery_until = datetime.now() + timedelta(days=3)

    def expedite_recovery(self, hours=24):
        """Reduces recovery time, potentially via cost logic in app.py."""
        if self.recovery_until:
            self.recovery_until -= timedelta(hours=hours)
            self.update_recovery_status()

    def update_recovery_status(self):
        """Checks if recovery time has passed."""
        if self.is_defeated and self.recovery_until:
            if datetime.now() >= self.recovery_until:
                self.is_defeated = False
                self.recovery_until = None

    def consume_energy(self, amount):
        if self.current_energy >= amount:
            self.current_energy -= amount
            return True
        return False
        
    def to_dict(self):
        self.update_recovery_status()
        return {
            "id": self.id,
            "name": self.name,
            "is_defeated": self.is_defeated,
            "recovery_until": self.recovery_until.isoformat() if self.recovery_until else None,
            "current_energy": self.current_energy,
            "max_energy": self.max_energy,
            "stats": {k: self.get_stat(k) for k in self.base_stats.keys()},
            "gear": {
                "weapon": self.weapons[0].to_dict() if self.weapons[0] else None,
                "armor": None, # Future placeholder
                "accessory": self.trinket.to_dict() if self.trinket else None
            }
        }
