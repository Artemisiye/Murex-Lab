"""
The Artificer's Codex
A deep component inspector and theorycrafting tool
"""
from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Component Database
COMPONENTS = {
    'handles': [
        {'id': 'oak_handle', 'name': 'Oak Handle', 'weight': 1.2, 'comfort': 7, 'durability': 50, 'material': 'Oak'},
        {'id': 'pine_handle', 'name': 'Pine Handle', 'weight': 0.9, 'comfort': 6, 'durability': 30, 'material': 'Pine'},
        {'id': 'ironwood_handle', 'name': 'Ironwood Handle', 'weight': 1.8, 'comfort': 8, 'durability': 80, 'material': 'Ironwood'},
        {'id': 'leather_grip', 'name': 'Leather Grip', 'weight': 0.5, 'comfort': 9, 'durability': 40, 'material': 'Leather'},
    ],
    'blades': [
        {'id': 'copper_blade', 'name': 'Copper Blade', 'weight': 1.5, 'sharpness': 5, 'damage': 8, 'durability': 40, 'material': 'Copper'},
        {'id': 'bronze_blade', 'name': 'Bronze Blade', 'weight': 1.8, 'sharpness': 6, 'damage': 12, 'durability': 60, 'material': 'Bronze'},
        {'id': 'iron_blade', 'name': 'Iron Blade', 'weight': 2.2, 'sharpness': 7, 'damage': 15, 'durability': 80, 'material': 'Iron'},
        {'id': 'steel_blade', 'name': 'Steel Blade', 'weight': 2.0, 'sharpness': 9, 'damage': 20, 'durability': 100, 'material': 'Steel'},
    ],
    'guards': [
        {'id': 'simple_guard', 'name': 'Simple Guard', 'weight': 0.3, 'defense': 2, 'balance': 5, 'material': 'Iron'},
        {'id': 'crossguard', 'name': 'Crossguard', 'weight': 0.5, 'defense': 5, 'balance': 7, 'material': 'Steel'},
        {'id': 'basket_guard', 'name': 'Basket Guard', 'weight': 0.8, 'defense': 8, 'balance': 4, 'material': 'Steel'},
    ]
}

# Saved builds database (in-memory for prototype)
saved_builds = []

# Active quests and unlocked components
active_quests = []
player_components = {
    'handles': ['oak_handle', 'pine_handle'],  # Start with basic
    'blades': ['copper_blade'],
    'guards': ['simple_guard']
}
completed_quests = 0

# Hero quests database
QUESTS = [
    {'id': 1, 'hero': 'Knight', 'constraints': {'max_weight': 3.5, 'min_damage': 15}, 'reward': {'type': 'blade', 'id': 'bronze_blade'}, 'gold': 100},
    {'id': 2, 'hero': 'Rogue', 'constraints': {'max_weight': 2.5, 'min_attack_speed': 60}, 'reward': {'type': 'handles', 'id': 'leather_grip'}, 'gold': 80},
    {'id': 3, 'hero': 'Paladin', 'constraints': {'min_defense': 5, 'min_durability': 60}, 'reward': {'type': 'guards', 'id': 'crossguard'}, 'gold': 120},
    {'id': 4, 'hero': 'Berserker', 'constraints': {'min_damage': 18, 'set_bonus': True}, 'reward': {'type': 'blade', 'id': 'iron_blade'}, 'gold': 150},
    {'id': 5, 'hero': 'Duelist', 'constraints': {'min_balance': 6, 'min_attack_speed': 55}, 'reward': {'type': 'handles', 'id': 'ironwood_handle'}, 'gold': 130},
    {'id': 6, 'hero': 'Champion', 'constraints': {'min_damage': 20, 'min_defense': 7}, 'reward': {'type': 'blade', 'id': 'steel_blade'}, 'gold': 200},
    {'id': 7, 'hero': 'Assassin', 'constraints': {'max_weight': 2.0, 'min_damage': 12}, 'reward': {'type': 'guards', 'id': 'basket_guard'}, 'gold': 140},
]

quest_queue = QUESTS[:3]  # Start with first 3 quests

def calculate_weapon_stats(handle, blade, guard):
    """Calculate final weapon statistics"""
    # Base stats
    total_weight = handle['weight'] + blade['weight'] + guard['weight']
    
    # Attack Speed (inverse of weight, normalized)
    attack_speed = max(1, 100 - (total_weight * 15))
    
    # Balance (affected by weight distribution)
    balance = (handle['comfort'] + guard['balance']) / 2
    if total_weight > 4:
        balance -= 10
    
    # Damage (from blade, modified by balance)
    damage = blade['damage'] * (1 + balance / 100)
    
    # Durability (average of components)
    durability = (handle['durability'] + blade['durability'] + guard.get('defense', 0) * 5) / 2
    
    # Reach (weight affects reach)
    reach = 5 + (total_weight *0.5)
    
    # Defense
    defense = guard.get('defense', 0)
    
    # Sharpness
    sharpness = blade['sharpness']
    
    # Set bonus
    materials = [handle['material'], blade['material'], guard['material']]
    set_bonus = 0
    if len(set(materials)) == 1:
        set_bonus = 15  # All same material
        
    return {
        'weight': round(total_weight, 2),
        'attack_speed': round(attack_speed, 1),
        'balance': round(balance, 1),
        'damage': round(damage, 1),
        'durability': round(durability, 1),
        'reach': round(reach, 1),
        'defense': defense,
        'sharpness': sharpness,
        'set_bonus': set_bonus,
        'total_score': round(damage + attack_speed + balance + durability/10 + set_bonus, 1)
    }

@app.route('/')
def index():
    return render_template('index.html', components=COMPONENTS)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    handle_id = data.get('handle')
    blade_id = data.get('blade')
    guard_id = data.get('guard')
    
    handle = next((h for h in COMPONENTS['handles'] if h['id'] == handle_id), None)
    blade = next((b for b in COMPONENTS['blades'] if b['id'] == blade_id), None)
    guard = next((g for g in COMPONENTS['guards'] if g['id'] == guard_id), None)
    
    if not (handle and blade and guard):
        return jsonify({'error': 'Invalid components'}), 400
        
    stats = calculate_weapon_stats(handle, blade, guard)
    
    return jsonify({
        'stats': stats,
        'components': {
            'handle': handle,
            'blade': blade,
            'guard': guard
        }
    })

@app.route('/save_build', methods=['POST'])
def save_build():
    data = request.json
    build_name = data.get('name', f'Build #{len(saved_builds) + 1}')
    
    build = {
        'id': len(saved_builds),
        'name': build_name,
        'components': data.get('components'),
        'stats': data.get('stats')
    }
    
    saved_builds.append(build)
    return jsonify({'success': True, 'build_id': build['id']})

@app.route('/builds')
def get_builds():
    return jsonify({'builds': saved_builds})

@app.route('/quests')
def get_quests():
    return jsonify({'quests': quest_queue, 'completed': completed_quests})

@app.route('/submit_quest', methods=['POST'])
def submit_quest():
    global completed_quests, quest_queue
    
    data = request.json
    quest_id = data.get('quest_id')
    stats = data.get('stats')
    
    quest = next((q for q in quest_queue if q['id'] == quest_id), None)
    if not quest:
        return jsonify({'error': 'Quest not found'}), 404
    
    # Check constraints
    constraints = quest['constraints']
    passes = True
    failures = []
    
    for key, required_value in constraints.items():
        if key.startswith('min_'):
            stat_key = key[4:]
            if stats.get(stat_key, 0) < required_value:
                passes = False
                failures.append(f"Need {stat_key} >= {required_value}, got {stats.get(stat_key, 0)}")
        elif key.startswith('max_'):
            stat_key = key[4:]
            if stats.get(stat_key, 999) > required_value:
                passes = False
                failures.append(f"Need {stat_key} <= {required_value}, got {stats.get(stat_key, 0)}")
        elif key == 'set_bonus' and required_value:
            if stats.get('set_bonus', 0) == 0:
                passes = False
                failures.append("Need matching material set")
    
    if passes:
        # Reward component
        reward = quest['reward']
        if reward['id'] not in player_components[reward['type']]:
            player_components[reward['type']].append(reward['id'])
        
        # Remove quest and add new one
        quest_queue.remove(quest)
        completed_quests += 1
        
        # Add next quest
        next_quest_idx = min(completed_quests + 2, len(QUESTS) - 1)
        if QUESTS[next_quest_idx] not in quest_queue:
            quest_queue.append(QUESTS[next_quest_idx])
        
        return jsonify({
            'success': True, 
            'reward': reward,
            'gold': quest['gold'],
            'message': f"Quest Complete! Unlocked {COMPONENTS[reward['type']][next(i for i, c in enumerate(COMPONENTS[reward['type']]) if c['id'] == reward['id'])]['name']}"
        })
    else:
        return jsonify({'success': False, 'failures': failures})

@app.route('/player_components')
def get_player_components():
    return jsonify({'components': player_components})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
