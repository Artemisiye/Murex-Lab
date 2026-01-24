import math

class Minion:
    """
    Minions are the primary 'shells' for gear and exploration in Murex Lab.
    Inspired by Summoners War monster progression.
    """
    def __init__(self, id, name, star_rating=1, level=1, base_stats=None):
        self.id = id
        self.name = name
        self.star_rating = star_rating
        self.level = level
        
        # Base stats (unmodded)
        self.base_stats = base_stats or {
            "hp": 100,
            "atk": 10,
            "def": 10,
            "spd": 100,
            "crit_rate": 0.15,
            "crit_dmg": 0.50,
            "res": 0.15,
            "acc": 0.00
        }
        
        # Progression
        self.experience = 0
        self.max_level = self.star_rating * 10
        
        # Energy / Exploration Capacity
        self.max_energy = 100
        self.current_energy = 100
        
        # Gear Slots
        self.engravings = {} # Slot 1-6
        self.weapons = [None, None] # Slot 1 & 2
        self.trinket = None
        
    def get_stat(self, stat_name):
        """Calculates final stat including level scaling and gear bonuses."""
        base = self.base_stats.get(stat_name, 0)
        
        # 1. Level Scaling (Simplified: +5% per level)
        scaled_base = base * (1 + (self.level - 1) * 0.05)
        
        # 2. Add Gear Bonuses (To be implemented in gear.py)
        bonus_flat = 0
        bonus_pct = 0
        
        # Engravings
        for slot, engraving in self.engravings.items():
            if stat_name in engraving.stats:
                val = engraving.stats[stat_name]
                if isinstance(val, float) and val < 1.0: # Percentage
                    bonus_pct += val
                else:
                    bonus_flat += val
        
        return (scaled_base * (1 + bonus_pct)) + bonus_flat

    def earn_experience(self, amount):
        """Standard RPG leveling logic."""
        self.experience += amount
        xp_needed = self.level * 100
        while self.experience >= xp_needed and self.level < self.max_level:
            self.experience -= xp_needed
            self.level += 1
            xp_needed = self.level * 100
            print(f"{self.name} leveled up to {self.level}!")

    def evolve(self, sacrifices):
        """
        Increase star rating by sacrificing other minions of the same star rating.
        Requirements: Max Level and (Star Rating) number of sacrifices.
        """
        if self.level < self.max_level:
            return False, "Minion must be at Max Level to evolve."
        
        if self.star_rating >= 6:
            return False, "Minion is already at Max Star Rating."
            
        valid_sacrifices = [s for s in sacrifices if s.star_rating == self.star_rating]
        if len(valid_sacrifices) < self.star_rating:
            return False, f"Need {self.star_rating} sacrifices of {self.star_rating} stars."
            
        self.star_rating += 1
        self.level = 1
        self.max_level = self.star_rating * 10
        return True, f"{self.name} evolved to {self.star_rating}⭐!"

    def consume_energy(self, amount):
        if self.current_energy >= amount:
            self.current_energy -= amount
            return True
        return False
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "star_rating": self.star_rating,
            "level": self.level,
            "current_energy": self.current_energy,
            "max_energy": self.max_energy,
            "stats": {k: self.get_stat(k) for k in self.base_stats.keys()}
        }
