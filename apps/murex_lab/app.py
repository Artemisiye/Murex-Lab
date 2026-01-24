from flask import Flask, render_template, jsonify, request
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

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'murex_lab_secret_key'

# --- Initialize Modules ---
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
SAVE_PATH = os.path.join(DATA_PATH, 'player_inventory.json')

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
    
    # Gear
    player_inventory.add_item("itm_leather_pouch", "weapon", 1, {"name": "Leather Pouch"})
    player_inventory.add_item("itm_artificer_staff", "weapon", 1, {"name": "Staff"})
    player_inventory.add_item("itm_iron_dagger", "weapon", 1, {"name": "Dagger"})
    
    # Clothes
    player_inventory.add_item("clt_simple_shirt", "equipment", 1, {"name": "Simple Shirt"})
    player_inventory.add_item("clt_simple_pants", "equipment", 1, {"name": "Simple Pants"})
    player_inventory.add_item("clt_simple_shoes", "equipment", 1, {"name": "Simple Shoes"})
    
    player_inventory.save()

# Initial seed for starting equipment if fresh save
if not player_inventory.items and player_inventory.gold == 0:
    initialize_starting_equipment()

# --- Routes ---
@app.route('/')
def home():
    """Main game entry point."""
    return render_template('index.html')

@app.route('/views/<view_name>')
def get_view(view_name):
    """Returns HTML partials for views (workshop, map, etc)."""
    try:
        return render_template(f"views/{view_name}.html")
    except Exception as e:
        return f"<div class='placeholder-message'><h2>Error</h2><p>Could not load view: {view_name}</p></div>"

# --- API Endpoints ---
@app.route('/api/status')
def status():
    """Heartbeat check."""
    return jsonify({"status": "online", "version": "0.1.0"})

@app.route('/api/schematics')
def get_schematics():
    """Returns list of all available schematics."""
    schems = crafting_system.get_all_schematics()
    # Serialize manually for now (or use a serializer class later)
    data = [{"id": s.id, "name": s.name, "type": "Weapon"} for s in schems]
    return jsonify(data)

@app.route('/api/schematic/<schem_id>')
def get_schematic_details(schem_id):
    """Returns full details of a schematic including slots."""
    schem = crafting_system.get_schematic(schem_id)
    if not schem:
        return jsonify({"error": "Not Found"}), 404
        
    slots_data = []
    for slot in schem.slots:
        slots_data.append({
            "id": slot.id,
            "label": slot.label,
            "required": not slot.optional,
            "required_tags": slot.required_tags
        })
    
    return jsonify({
        "id": schem.id,
        "name": schem.name,
        "slots": slots_data,
        "base_stats": schem.base_stats
    })

@app.route('/api/components/<schem_id>/<slot_id>')
def get_valid_components(schem_id, slot_id):
    """Returns valid components currently in player inventory for a specific slot."""
    schem = crafting_system.get_schematic(schem_id)
    if not schem:
        return jsonify([])
    
    target_slot = next((s for s in schem.slots if s.id == slot_id), None)
    if not target_slot:
        return jsonify([])

    inventory_items = []
    inv = player_inventory.get_all()
    
    for key, inv_item in inv.items():
        # Check both components AND materials (for basic processing like Cordage)
        target_obj = None
        if inv_item.item_type == 'component':
            target_obj = crafting_system.components.get(inv_item.item_id)
        elif inv_item.item_type == 'material':
            target_obj = crafting_system.materials.get(inv_item.item_id)
        elif inv_item.item_type == 'product':
            # Check schematics for tags
            target_obj = crafting_system.schematics.get(inv_item.item_id)

        if target_obj and target_slot.accepts(target_obj):
            inventory_items.append({
                "id": inv_item.item_id,
                "inv_key": key,
                "name": target_obj.name,
                "quantity": inv_item.quantity,
                "material": getattr(target_obj, 'material', None).name if hasattr(target_obj, 'material') and target_obj.material else "Raw",
                "stats": getattr(target_obj, 'stats', {})
            })
    return jsonify(inventory_items)

@app.route('/api/inventory')
def get_inventory():
    """Returns the full player inventory and gold."""
    inv = player_inventory.get_all()
    data = []
    for key, item in inv.items():
        name = f"Unknown ({item.item_id})"
        if item.item_type == 'material':
            mat = crafting_system.materials.get(item.item_id)
            if mat: name = mat.name
        elif item.item_type == 'component':
            comp = crafting_system.components.get(item.item_id)
            if comp: name = comp.name
        elif item.item_type in ['product', 'equipment']:
            name = item.data.get('name', f"Item ({item.item_id})")
        
        data.append({
            "key": key,
            "item_id": item.item_id,
            "type": item.item_type,
            "quantity": item.quantity,
            "name": name
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
    data = request.json # {schematic_id: "...", components: {slot_id: inv_key}}
    schem_id = data.get('schematic_id')
    comp_map = data.get('components', {})

    print(f"CRAFTING: {schem_id} with map: {comp_map}")

    # 1. Preview to get stats and validate
    id_map = {}
    for sid, inv_key in comp_map.items():
        item = player_inventory.items.get(inv_key)
        if item:
            id_map[sid] = item.item_id
        else:
            print(f"WARNING: inv_key {inv_key} for slot {sid} not found in inventory!")

    result = crafting_system.preview_craft(schem_id, id_map)
    print(f"PREVIEW RESULT: {result}")
    
    if result.get('success'):
        schem = crafting_system.get_schematic(schem_id)
        
        # 2. Consume items (Filtering out catalysts)
        for sid, inv_key in comp_map.items():
            slot = next((s for s in schem.slots if s.id == sid), None)
            if slot and not slot.catalyst:
                player_inventory.remove_item(inv_key, 1)
        
        # 3. Add product
        
        # Determine output identity
        final_id = schem.output_id if schem.output_id else schem.id
        final_type = schem.output_type if schem.output_type else "product"
        
        product_name = f"Custom {schem.name}" if final_type == "product" else schem.name
        
        player_inventory.add_item(final_id, final_type, 1, {"stats": result['stats'], "name": product_name})
        
        return jsonify({"success": True, "message": f"Forged {product_name}!"})
    
    return jsonify(result)

@app.route('/api/preview_craft', methods=['POST'])
def preview_craft():
    """Calculates outcome for display."""
    data = request.json # {schematic_id: "...", components: {slot_id: inv_key}}
    schem_id = data.get('schematic_id')
    comp_map = data.get('components', {})

    id_map = {}
    for sid, inv_key in comp_map.items():
        item = player_inventory.items.get(inv_key)
        if item:
            id_map[sid] = item.item_id
    
    print(f"PREVIEW: {schem_id} with ID map: {id_map}")
    result = crafting_system.preview_craft(schem_id, id_map)
    return jsonify(result)

@app.route('/api/map/data')
def get_map_data():
    """Returns the full grid, player position, and size."""
    return jsonify(world_map.get_map_data())

@app.route('/api/map/move', methods=['POST'])
def move_player():
    """Moves player one cell. Movement is free per spec."""
    data = request.json
    direction = data.get('direction') # 'up', 'down', 'left', 'right'
    
    lead_minion = player_minions[0]

    moves = {
        'up': (0, -1),
        'down': (0, 1),
        'left': (-1, 0),
        'right': (1, 0)
    }
    
    dx, dy = moves.get(direction, (0, 0))
    success, result = world_map.move_player(dx, dy)
    
    if success:
        # Move is successful, no energy consumed
        return jsonify({
            "success": True, 
            "player_pos": world_map.player_pos,
            "energy": lead_minion.current_energy,
            "current_cell": world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y']).to_dict()
        })
    
    return jsonify({"success": False, "message": result})

@app.route('/api/map/scavenge', methods=['POST'])
def scavenge_location():
    """Scavenges the current user position."""
    loot = world_map.scavenge_current_pos()
    
    # Add loot to inventory
    for item in loot:
        item_type = 'material' # Default to material for simplicity
        player_inventory.add_item(item['id'], item_type, item['quantity'])
    
    return jsonify({"success": True, "loot": loot})

@app.route('/api/map/explore', methods=['POST'])
def explore_location():
    """Enters the high-granularity regional map."""
    regional_map = world_map.enter_regional_map()
    return jsonify({
        "success": True,
        "region_data": regional_map.to_dict()
    })

@app.route('/api/map/region_move', methods=['POST'])
def region_move():
    """Moves player within the regional map."""
    data = request.json
    direction = data.get('direction')
    
    moves = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1,0)}
    dx, dy = moves.get(direction, (0, 0))
    
    cell = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y'])
    if cell and cell.regional_map:
        success = cell.regional_map.move_player(dx, dy)
        return jsonify({
            "success": success,
            "region_data": cell.regional_map.to_dict()
        })
    return jsonify({"success": False})

@app.route('/api/map/harvest', methods=['POST'])
def harvest_node():
    """Harvests a node at specific coordinates in the current regional map."""
    data = request.json
    nx, ny = data.get('x'), data.get('y')
    
    cell = world_map.get_cell(world_map.player_pos['x'], world_map.player_pos['y'])
    if not cell or not cell.regional_map:
        return jsonify({"success": False, "message": "No area active."})
        
    # Security: Check if player is near the node
    px, py = cell.regional_map.player_pos['x'], cell.regional_map.player_pos['y']
    if abs(px - nx) > 1 or abs(py - ny) > 1:
        return jsonify({"success": False, "message": "Too far away to harvest."})
        
    loot = cell.regional_map.harvest(nx, ny)
    if loot:
        for item_id in loot:
            # We determine type based on prefix for now
            itype = 'material'
            if item_id.startswith('comp_'): itype = 'component'
            player_inventory.add_item(item_id, itype, random.randint(1, 3))
            
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
    return jsonify({"success": True, "message": "Vault reset to initial state."})

@app.route('/api/debug/backpack/clear', methods=['POST'])
def debug_clear_backpack():
    """Cheat: empties the backpack."""
    # Logic to clear backpack once backpack object is fully implemented
    # For now, if we use a separate list:
    return jsonify({"success": True, "message": "Backpack emptied."})

@app.route('/api/debug/inventory/add', methods=['POST'])
def debug_add_item():
    """Cheat: adds a specific item to the inventory."""
    data = request.json
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    
    # Simple type determination
    itype = 'material'
    if item_id.startswith('comp_'): itype = 'component'
    elif item_id.startswith('prod_'): itype = 'product'
    
    player_inventory.add_item(item_id, itype, quantity)
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
