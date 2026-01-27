from flask import Flask, render_template, jsonify, request, send_from_directory
import sys
import os
import random

# Add project root to path so we can find _engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from _engine.game_client import launch

from modules.crafting import CraftingManager
from modules.inventory import Inventory
from modules.world_map import map_manager
from modules.minions import Minion

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
SAVE_PATH = os.path.join(DATA_PATH, 'player_inventory.json')

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'murex_lab_secret_key'

# --- Initialize Modules ---
crafting_system = CraftingManager(DATA_PATH)
player_inventory = Inventory(SAVE_PATH)
world_map = map_manager(DATA_PATH)

# Player Team (Starting Minion)
player_minions = [
    Minion("m_001", "Lead Artificer", star_rating=3, level=10)
]

def initialize_starting_equipment():
    """Wipes inventory and sets up the starting gear per TECHNICAL_SPECS."""
    player_inventory.items = {}
    player_inventory.gold = 15
    
    # Starting gear is loaded from items.json for tags, but added as unique instances if needed
    starter_ids = [
        ("pouch", "equipment"),
        ("staff", "weapon"),
        ("iron_dagger", "weapon"),
        ("simple_shirt", "equipment"),
        ("simple_pants", "equipment"),
        ("simple_shoes", "equipment")
    ]
    
    for item_id, category in starter_ids:
        # We fetch the base item name for the metadata
        base = crafting_system.items.get(item_id)
        name = base.name if base else item_id.replace("_", " ").title()
        player_inventory.add_item(item_id, 1, {"name": name})
    
    player_inventory.save()

# Initial seed for starting equipment if fresh save
if not player_inventory.items and player_inventory.gold == 0:
    initialize_starting_equipment()

# --- Helpers ---
def classify_item_by_tags(item_obj):
    """Returns a UI-friendly category string based on item tags following design convention."""
    tags = item_obj.tags
    # Higher priority/specificity first
    if tags.has_tag("Item.Class.Weapon"): return "weapon"
    if tags.has_tag("Item.Class.Armor"): return "equipment"
    if tags.has_tag("Item.Class.Equipment"): return "equipment"
    if tags.has_tag("Item.Class.Tool"): return "tool"
    if tags.has_tag("Item.Trait.Fuel"): return "fuel"
    if tags.has_tag("Item.Trait.Consumable"): return "consumable"
    if tags.has_tag("Item.Class.Component"): return "component"
    if tags.has_tag("Item.Class.Material"): return "material"
    return "item"

# --- Routes ---
@app.route('/')
def home():
    """Main game entry point."""
    return render_template('index.html')

@app.route('/views/<view_name>')
def get_view(view_name):
    """Returns HTML partials for views (workshop, map, etc)."""
    try:
        return render_template(f'views/{view_name}.html')
    except Exception as e:
        return f"<div class='placeholder-message'><h2>Error</h2><p>Could not load view: {view_name}</p></div>"

# --- API Endpoints ---
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/status')
def status():
    """Heartbeat check."""
    return jsonify({"status": "online", "version": "0.1.0"})

@app.route('/api/blueprints')
def get_blueprints():
    """Returns list of all available blueprints categorized by tags."""
    bps = crafting_system.get_all_blueprints()
    data = []
    for bp in bps:
        data.append({
            "id": bp.id, 
            "name": bp.name, 
            "type": classify_item_by_tags(bp),
            "station_id": bp.station_id
        })
    return jsonify(data)

@app.route('/api/blueprint/<bp_id>')
def get_blueprint_details(bp_id):
    """Returns full details of a blueprint including slots."""
    bp = crafting_system.get_blueprint(bp_id)
    if not bp:
        return jsonify({"error": "Not Found"}), 404
        
    slots_data = []
    for slot in bp.slots:
        slots_data.append({
            "id": slot.id,
            "label": slot.label,
            "required": not slot.optional,
            "required_tags": slot.required_tags
        })
    
    return jsonify({
        "id": bp.id,
        "name": bp.name,
        "slots": slots_data,
        "base_stats": bp.base_stats
    })

@app.route('/api/components/<bp_id>/<slot_id>')
def get_valid_components(bp_id, slot_id):
    """Returns valid components currently in player inventory for a specific slot."""
    bp = crafting_system.get_blueprint(bp_id)
    if not bp:
        return jsonify([])
    
    target_slot = next((s for s in bp.slots if s.id == slot_id), None)
    if not target_slot:
        return jsonify([])

    inventory_items = []
    inv = player_inventory.get_all()
    
    for key, inv_item in inv.items():
        # Check unified registry or recursive blueprint tags
        target_obj = crafting_system.items.get(inv_item.item_id) or crafting_system.blueprints.get(inv_item.item_id)

        if target_obj and target_slot.accepts(target_obj):
            inventory_items.append({
                "id": inv_item.item_id,
                "inv_key": key,
                "name": target_obj.name,
                "quantity": inv_item.quantity,
                "stats": inv_item.data.get('stats', getattr(target_obj, 'stats', getattr(target_obj, 'base_stats', {})))
            })
    return jsonify(inventory_items)

@app.route('/api/inventory')
def get_inventory():
    """Returns the full player inventory and gold."""
    inv = player_inventory.get_all()
    data = []
    for key, item in inv.items():
        name = f"Unknown ({item.item_id})"
        category = "item"
        
        target_obj = crafting_system.items.get(item.item_id)
        if target_obj:
            name = target_obj.name
            category = classify_item_by_tags(target_obj)
        else:
            # Check if it was produced from a blueprint
            bp = crafting_system.blueprints.get(item.item_id)
            if bp:
                name = item.data.get('name', bp.name)
                category = classify_item_by_tags(bp)
        
        data.append({
            "key": key,
            "item_id": item.item_id,
            "type": category, # Mapped for UI classification
            "quantity": item.quantity,
            "name": name,
            "stats": item.data.get('stats', {})
        })
    return jsonify({
        "gold": player_inventory.gold,
        "items": data
    })

@app.route('/api/minions')
def get_minions():
    """Returns the player's minion team data."""
    return jsonify([m.to_dict() for m in player_minions])

@app.route('/api/craft_item', methods=['POST'])
def craft_item():
    """Assembles the item, consumes components, and adds the product back to inventory."""
    data = request.json # {blueprint_id: "...", components: {slot_id: inv_key}}
    bp_id = data.get('blueprint_id')
    comp_map = data.get('components', {})\

    # 1. Preview to get stats and validate
    id_map = {}
    for sid, inv_key in comp_map.items():
        item = player_inventory.items.get(inv_key)
        if item:
            id_map[sid] = item.item_id

    result = crafting_system.preview_craft(bp_id, id_map)
    
    if result.get('success'):
        bp = crafting_system.get_blueprint(bp_id)
        
        # 2. Consume items (Filtering out catalysts)
        for sid, inv_key in comp_map.items():
            slot = next((s for s in bp.slots if s.id == sid), None)
            if slot and not slot.catalyst:
                player_inventory.remove_item(inv_key, 1)
        
        # 3. Add product
        final_id = bp.output_id if bp.output_id else bp.id
        
        # Get category of output
        final_obj = crafting_system.items.get(final_id) or bp
        category = classify_item_by_tags(final_obj)
        
        product_name = f"Custom {bp.name}" if category in ["weapon", "equipment"] else bp.name
        
        player_inventory.add_item(final_id, 1, {"stats": result['stats'], "name": product_name})
        
        return jsonify({
            "success": True, 
            "message": f"Forged {product_name}!",
            "item_name": product_name
        })
    
    return jsonify(result)

@app.route('/api/preview_craft', methods=['POST'])
def preview_craft():
    """Calculates outcome for display."""
    data = request.json
    bp_id = data.get('blueprint_id')
    comp_map = data.get('components', {})

    id_map = {}
    for sid, inv_key in comp_map.items():
        item = player_inventory.items.get(inv_key)
        if item:
            id_map[sid] = item.item_id

    result = crafting_system.preview_craft(bp_id, id_map)
    return jsonify(result)

@app.route('/api/debug/data/<file_type>', methods=['GET', 'POST'])
def debug_data_sync(file_type):
    """Syncs raw data files with the debug tool."""
    if file_type not in ['blueprints', 'items']:
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'POST':
        item_data = request.json
        success = crafting_system.update_item(file_type, item_data)
        return jsonify({"success": success, "message": "Data saved and reloaded." if success else "Save failed."})

    return jsonify(crafting_system.get_raw_data(file_type))

@app.route('/api/debug/stations')
def get_debug_stations():
    """Returns list of stations currently in use by any blueprint (to aid discovery)."""
    bps = crafting_system.get_raw_data('blueprints')
    stations = list(set(bp.get('station_id', 'station_none') for bp in bps))
    return jsonify(stations)

@app.route('/api/map/data')
def get_map_data():
    """Returns the full grid, player position, and size."""
    return jsonify(world_map.get_map_data())

@app.route('/api/map/move', methods=['POST'])
def move_player():
    """Moves player one cell. Movement is free per spec."""
    data = request.json
    direction = data.get('direction')
    
    dx, dy = 0, 0
    if direction == 'up': dy = -1
    elif direction == 'down': dy = 1
    elif direction == 'left': dx = -1
    elif direction == 'right': dx = 1
    
    success, result = world_map.move_player(dx, dy)
    
    if success:
        return jsonify({
            "success": True,
            "new_cells": result, # Newly discovered cells if any
            "player_pos": world_map.player_pos
        })
    else:
        return jsonify({"success": False, "message": result})

@app.route('/api/map/explore', methods=['POST'])
def explore_location():
    """Enters the high-granularity regional map."""
    cell = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y'])
    if cell and cell.type == 'lab':
        return jsonify({"success": False, "message": "The Lab is fully mapped. Use the Workshop for facilities."})
        
    regional = world_map.enter_regional_map()
    return jsonify({"success": True, "region_data": regional.to_dict()})

@app.route('/api/map/region_move', methods=['POST'])
def region_move():
    """Moves player within the regional map."""
    data = request.json
    direction = data.get('direction')
    
    dx, dy = 0, 0
    if direction == 'up': dy = -1
    elif direction == 'down': dy = 1
    elif direction == 'left': dx = -1
    elif direction == 'right': dx = 1
    
    regional = world_map.enter_regional_map()
    if regional.move_player(dx, dy):
        return jsonify({"success": True, "region_data": regional.to_dict()})
    return jsonify({"success": False})

@app.route('/api/map/harvest', methods=['POST'])
def harvest_node():
    """Harvests a node at specific coordinates in the current regional map."""
    data = request.json
    nx, ny = data.get('x'), data.get('y')
    
    cell = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y'])
    if not cell or not cell.regional_map:
        return jsonify({"success": False, "message": "No area active."})
        
    # Check if node exists
    node = cell.regional_map.grid.get((nx, ny))
    if not node:
        return jsonify({"success": False, "message": "No resource here."})

    # Proximity Check (Standing directly on it)
    px, py = cell.regional_map.player_pos['x'], cell.regional_map.player_pos['y']
    if px != nx or py != ny:
        return jsonify({"success": False, "message": "You must stand directly on the resource to harvest."})
        
    # Tool Check
    if node.tool_required:
        has_tool = False
        for inv_id, inv_item in player_inventory.get_all().items():
            # Check tags of base item
            base = crafting_system.items.get(inv_item.item_id) or crafting_system.blueprints.get(inv_item.item_id)
            if base and base.tags.has_tag(node.tool_required):
                has_tool = True
                break
        
        if not has_tool:
            tool_name = node.tool_required.split('.')[-1]
            return jsonify({"success": False, "message": f"Requires tool: {tool_name}"})

    loot = cell.regional_map.harvest(nx, ny)
    if loot:
        for item_id in loot:
            player_inventory.add_item(item_id, random.randint(1, 3))
            
        return jsonify({
            "success": True, 
            "loot": loot,
            "region_data": cell.regional_map.to_dict()
        })
        
    return jsonify({"success": False, "message": "Resource exhausted or missing."})

# --- Debugging & Tools API ---
@app.route('/debug')
def debug_tools():
    """Serves the standalone Tools Window interface."""
    return render_template('debug.html')

@app.route('/api/debug/inventory/clear', methods=['POST'])
def debug_clear_inventory():
    """Cheat: resets the inventory to starting equipment state."""
    initialize_starting_equipment()
    return jsonify({"success": True, "message": "Vault contents reset to starting gear."})

@app.route('/api/debug/backpack/clear', methods=['POST'])
def debug_clear_backpack():
    """Cheat: empties the backpack."""
    # System has no backpack yet, clearing inventory
    player_inventory.items = {}
    player_inventory.save()
    return jsonify({"success": True, "message": "Vault Purged."})

@app.route('/api/debug/inventory/add', methods=['POST'])
def debug_add_item():
    """Cheat: adds a specific item to the inventory."""
    data = request.json
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    
    player_inventory.add_item(item_id, quantity)
    return jsonify({"success": True, "message": f"Added x{quantity} {item_id}"})

if __name__ == "__main__":
    # Launch via Capsule Engine
    launch(
        app, 
        title="Murex Lab", 
        width=1920, 
        height=1080, 
        resizable=False,
        fullscreen=False
    )
