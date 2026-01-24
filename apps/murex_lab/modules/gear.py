class Gear:
    """Base class for all equippable items."""
    def __init__(self, id, name, gear_type, stats=None):
        self.id = id
        self.name = name
        self.gear_type = gear_type # 'engraving', 'weapon', 'trinket'
        self.stats = stats or {}

class Engraving(Gear):
    """
    Matrix-based stat boosts. Slots 1-6.
    Inspired by SW Runes.
    """
    def __init__(self, id, name, slot, set_name, level=0, stats=None):
        super().__init__(id, name, 'engraving', stats)
        self.slot = slot # 1-6
        self.set_name = set_name # 'Energy', 'Assault', etc.
        self.level = level # +0 to +15
        
    def upgrade(self):
        if self.level < 15:
            self.level += 1
            # Logistic: Main stat increases every level, 
            # Substat added/boosted at 3, 6, 9, 12.
            return True
        return False

class Weapon(Gear):
    """
    Weapons bind active skills to the minion.
    """
    def __init__(self, id, name, skills=None, stats=None):
        super().__init__(id, name, 'weapon', stats)
        self.skills = skills or [] # List of skill IDs (e.g. ['skill_bash', 'skill_stun'])

class Trinket(Gear):
    """
    Trinkets provide passive bonuses, primarily for exploration/efficiency.
    """
    def __init__(self, id, name, passive_id, stats=None):
        super().__init__(id, name, 'trinket', stats)
        self.passive_id = passive_id # e.g. 'eagle_eye', 'energy_saver'
