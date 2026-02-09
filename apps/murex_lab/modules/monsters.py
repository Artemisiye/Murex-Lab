class Monster:
    """
    Enemies and wild creatures for combat. 
    Compatible with Minion's get_stat interface for CombatEngine.
    """
    def __init__(self, id, name, stats=None, skill_ids=None):
        self.id = id
        self.name = name
        # Base stats for a generic enemy
        self.stats = stats or {
            "hp": 400,
            "atk": 80,
            "def": 80,
            "spd": 90,
            "crit_rate": 0.10,
            "crit_dmg": 0.20
        }
        self.skill_ids = skill_ids or ["skill_basic_strike"]

    def get_stat(self, stat_name):
        return self.stats.get(stat_name, 0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "stats": self.stats,
            "skills": self.skill_ids
        }

# Pre-defined Monster Templates
MONSTER_TEMPLATES = {
    "animal_boar": {
        "name": "Wild Boar",
        "stats": {"hp": 500, "atk": 70, "def": 120, "spd": 85, "crit_rate": 0.05, "crit_dmg": 0.10},
        "skills": ["skill_tusk_charge", "skill_basic_strike"]
    },
    "enemy_bandit": {
        "name": "Highway Bandit",
        "stats": {"hp": 450, "atk": 110, "def": 70, "spd": 105, "crit_rate": 0.15, "crit_dmg": 0.40},
        "skills": ["skill_dirty_blade", "skill_basic_strike"]
    }
}
