import random

class CombatEntity:
    """A logic wrapper for Minions or Monsters in a specific combat session."""
    def __init__(self, source_obj, side):
        self.source = source_obj  # Minion or Monster instance
        self.side = side          # 'player' or 'enemy'
        self.atb = 0
        self.current_hp = source_obj.get_stat("hp")
        self.max_hp = self.current_hp
        self.spd = source_obj.get_stat("spd")
        self.is_dead = False
        self.cooldowns = {}      # skill_id -> turns_remaining

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)
        if self.current_hp <= 0:
            self.is_dead = True
        return amount

    def reset_atb(self):
        """Subtracts turn cost (1000) from ATB, keeping overflow."""
        self.atb = max(0, self.atb - 1000)

    def update_cooldowns(self):
        """Decrements cooldowns at start of turn."""
        for skill_id in list(self.cooldowns.keys()):
            self.cooldowns[skill_id] -= 1
            if self.cooldowns[skill_id] <= 0:
                del self.cooldowns[skill_id]

class CombatEngine:
    def __init__(self, player_team, enemy_team):
        self.entities = []
        for p in player_team:
            self.entities.append(CombatEntity(p, 'player'))
        for e in enemy_team:
            self.entities.append(CombatEntity(e, 'enemy'))
            
        self.log = ["Combat Initiated."]
        self.active_unit = None
        self.is_finished = False
        self.winner = None

    def tick(self):
        """Advances combat in logical ticks until a unit reaches 1000 ATB."""
        if self.is_finished: return None

        while True:
            # 1. Check for ready units
            ready_units = [u for u in self.entities if u.atb >= 1000 and not u.is_dead]
            
            if ready_units:
                # Higher ATB first, then Higher SPD tie-breaker
                ready_units.sort(key=lambda x: (x.atb, x.spd), reverse=True)
                self.active_unit = ready_units[0]
                self.active_unit.update_cooldowns()
                return self.active_unit

            # 2. Advance all non-dead units by 7% of SPD per tick
            for u in self.entities:
                if not u.is_dead:
                    u.atb += u.spd * 0.07

    def execute_skill(self, attacker, skill_id, targets, scaling, cooldown=0):
        """Processes a skill execution and returns results for the UI."""
        results = []
        
        # Basic Cooldown tracking
        if cooldown > 0:
            attacker.cooldowns[skill_id] = cooldown

        for target in targets:
            if target.is_dead: continue
            
            damage = self.calculate_damage(attacker, target, scaling)
            target.take_damage(damage)
            
            results.append({
                "target_id": target.source.id,
                "damage": damage,
                "is_crit": False, # Future: Check if it was a crit
                "target_hp": target.current_hp
            })

            self.log.append(f"{attacker.source.name} used {skill_id} on {target.source.name} for {damage} dmg.")

        attacker.reset_atb()
        self.check_victory()
        return results

    def calculate_damage(self, attacker, defender, scaling):
        """
        Damage Factor = 1000 / (1140 + 3.5 * DEF)
        scaling: { 'atk': 3.5, 'hp': 0.1 } etc.
        """
        raw_damage = 0
        for stat_name, multiplier in scaling.items():
            val = attacker.source.get_stat(stat_name)
            raw_damage += val * multiplier
            
        # Defense Mitigation logic
        target_def = defender.source.get_stat("def")
        damage_factor = 1000 / (1140 + 3.5 * target_def)
        
        final_damage = raw_damage * damage_factor
        
        # Optional: Add small variance (e.g. +/- 5%)
        variance = random.uniform(0.95, 1.05)
        final_damage *= variance
        
        return int(final_damage)

    def check_victory(self):
        player_alive = any(u for u in self.entities if u.side == 'player' and not u.is_dead)
        enemy_alive = any(u for u in self.entities if u.side == 'enemy' and not u.is_dead)
        
        if not enemy_alive:
            self.is_finished = True
            self.winner = 'player'
            self.log.append("Victory! Enemy forces defeated.")
        elif not player_alive:
            self.is_finished = True
            self.winner = 'enemy'
            self.log.append("Defeat! Your team has fallen.")

    def get_state(self):
        """Returns serializable state for the frontend."""
        return {
            "entities": [{
                "id": e.source.id,
                "name": e.source.name,
                "side": e.side,
                "atb": e.atb,
                "hp": e.current_hp,
                "max_hp": e.max_hp,
                "is_dead": e.is_dead,
                "cooldowns": e.cooldowns
            } for e in self.entities],
            "log": self.log[-5:], # Last 5 entries
            "active_unit_id": self.active_unit.source.id if self.active_unit else None,
            "is_finished": self.is_finished,
            "winner": self.winner
        }
# Skill Registry defining multipliers and behaviors
SKILL_REGISTRY = {
    "skill_basic_strike": {
        "name": "Basic Strike",
        "scaling": {"atk": 3.5},
        "target_type": "single",
        "cooldown": 0
    },
    "skill_tusk_charge": {
        "name": "Tusk Charge",
        "scaling": {"atk": 2.0, "def": 1.5},
        "target_type": "single",
        "cooldown": 3
    },
    "skill_dirty_blade": {
        "name": "Dirty Blade",
        "scaling": {"atk": 5.0},
        "target_type": "single",
        "cooldown": 4
    },
    "skill_arcane_bolt": {
        "name": "Arcane Bolt",
        "scaling": {"atk": 4.0},
        "target_type": "single",
        "cooldown": 0
    },
    "skill_quick_slash": {
        "name": "Quick Slash",
        "scaling": {"atk": 2.5, "spd": 0.5},
        "target_type": "single",
        "cooldown": 0
    }
}
