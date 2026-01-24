import random

class Combatant:
    def __init__(self, minion, is_player=True):
        self.minion = minion
        self.is_player = is_player
        self.current_hp = minion.get_stat("hp")
        self.atb = 0 # Attack Bar (0-1000)
        self.spd = minion.get_stat("spd")
        
    def tick(self):
        """Increase ATB based on speed."""
        self.atb += self.spd
        return self.atb >= 1000

class CombatEngine:
    """
    Active Turn Combat (ATC) based on Speed-Tick logic.
    """
    def __init__(self, player_team, enemy_team):
        self.player_units = [Combatant(m, True) for m in player_team]
        self.enemy_units = [Combatant(m, False) for m in enemy_team]
        self.all_units = self.player_units + self.enemy_units
        self.is_over = False
        self.winner = None

    def run_tick(self):
        """Simulates one tick. Returns unit whose turn it is, or None."""
        # Sort by ATB to handle priority if multiple are > 1000
        ready_units = [u for u in self.all_units if u.tick()]
        if not ready_units:
            return None
            
        # Select unit with highest ATB overflow
        ready_units.sort(key=lambda x: x.atb, reverse=True)
        active_unit = ready_units[0]
        
        # Reset ATB (keeping overflow like SW)
        active_unit.atb -= 1000
        return active_unit

    def execute_move(self, source, target, skill_id):
        """Applies damage/effects based on skill and stats."""
        # Simplified: Damage = ATK * multiplier
        atk = source.minion.get_stat("atk")
        damage = atk * random.uniform(0.9, 1.1) 
        
        # Defense reduction: Dmg * 100 / (100 + DEF)
        defense = target.minion.get_stat("def")
        damage = damage * (100 / (100 + defense))
        
        target.current_hp -= int(damage)
        print(f"{source.minion.name} uses {skill_id} on {target.minion.name} for {int(damage)} dmg!")
        
        if target.current_hp <= 0:
            target.current_hp = 0
            print(f"{target.minion.name} has fallen!")
            self.check_victory()

    def check_victory(self):
        player_alive = any(u.current_hp > 0 for u in self.player_units)
        enemy_alive = any(u.current_hp > 0 for u in self.enemy_units)
        
        if not player_alive:
            self.is_over = True
            self.winner = "Enemy"
        elif not enemy_alive:
            self.is_over = True
            self.winner = "Player"
