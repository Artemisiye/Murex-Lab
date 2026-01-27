import json
import os
from .tag_system import TagContainer

class Item:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.tags = TagContainer(data.get('tags', []))
        self.stats = data.get('stats', {})

class BlueprintSlot:
    def __init__(self, data):
        self.id = data['id']
        self.label = data['label']
        self.required_tags = data.get('required_tags', [])
        self.forbidden_tags = data.get('forbidden_tags', [])
        self.optional = data.get('optional', False)
        self.catalyst = data.get('catalyst', False) # If true, item is NOT consumed

    def accepts(self, item: Item) -> bool:
        """Checks if an item fits this slot."""
        return item.tags.matches_query(self.required_tags, self.forbidden_tags)

class Blueprint:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.station_id = data.get('station_id', 'station_none')
        self.output_id = data.get('output_id') # If it produces a specific item
        self.tags = TagContainer(data.get('tags', []))
        self.slots = [BlueprintSlot(s) for s in data.get('slots', [])]
        self.base_stats = data.get('base_stats', {})

class CraftingManager:
    def __init__(self, data_path):
        self.data_path = data_path
        self.items = {}
        self.blueprints = {}
        self.load_data()

    def load_data(self):
        """Loads JSON definitions."""
        # Load Unified Items
        item_path = os.path.join(self.data_path, 'items.json')
        if os.path.exists(item_path):
            with open(item_path, 'r') as f:
                for data in json.load(f):
                    self.items[data['id']] = Item(data)
        
        # Load Blueprints
        blueprint_path = os.path.join(self.data_path, 'blueprints.json')
        if os.path.exists(blueprint_path):
            with open(blueprint_path, 'r') as f:
                for data in json.load(f):
                    self.blueprints[data['id']] = Blueprint(data)

        print(f"Loaded {len(self.items)} Items, {len(self.blueprints)} Blueprints.")

    def get_blueprint(self, blueprint_id):
        return self.blueprints.get(blueprint_id)

    def get_all_blueprints(self):
        return list(self.blueprints.values())

    def get_valid_components_for_slot(self, blueprint_id, slot_id):
        """Returns a list of all defined items that fit a specific slot."""
        bp = self.blueprints.get(blueprint_id)
        if not bp:
            return []
        
        target_slot = next((s for s in bp.slots if s.id == slot_id), None)
        if not target_slot:
            return []

        valid_objs = []
        for obj in self.items.values():
            if target_slot.accepts(obj):
                valid_objs.append(obj)
        
        return valid_objs

    def preview_craft(self, blueprint_id, component_ids_map):
        """
        Calculates result stats.
        component_ids_map: dict of {slot_id: item_id}
        """
        bp = self.blueprints.get(blueprint_id)
        if not bp:
            return {"error": "Invalid Blueprint"}

        result_stats = bp.base_stats.copy()
        
        # Simple Sum Logic for now
        for slot in bp.slots:
            item_id = component_ids_map.get(slot.id)
            if item_id:
                # Check items, then blueprints (for tags/stats if recursive)
                item = self.items.get(item_id) or self.blueprints.get(item_id)
                if item:
                    stats_source = getattr(item, 'stats', getattr(item, 'base_stats', {}))
                    for stat, value in stats_source.items():
                        result_stats[stat] = result_stats.get(stat, 0) + value
            elif not slot.optional:
                return {"error": f"Missing required slot: {slot.label}"}

        final_id = bp.output_id if bp.output_id else bp.id
        final_obj = self.items.get(final_id) or bp
        
        return {
            "success": True, 
            "stats": result_stats,
            "output_name": final_obj.name,
            "output_id": final_id
        }

    def get_raw_data(self, file_type):
        """Returns the raw JSON list for a specific data file."""
        filename = f"{file_type}.json"
        path = os.path.join(self.data_path, filename)
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            return json.load(f)

    def save_raw_data(self, file_type, data_list):
        """Saves a raw list back to JSON and reloads system."""
        if file_type not in ['blueprints', 'items']:
            return False
            
        filename = f"{file_type}.json"
        path = os.path.join(self.data_path, filename)
        with open(path, 'w') as f:
            json.dump(data_list, f, indent=4)
            
        self.load_data() # Hot reload
        return True

    def update_item(self, file_type, item_data):
        """Updates or adds an item in the specified data file."""
        data = self.get_raw_data(file_type)
        item_id = item_data.get('id')
        
        # Check for existing
        existing_idx = next((i for i, item in enumerate(data) if item.get('id') == item_id), -1)
        if existing_idx >= 0:
            data[existing_idx] = item_data
        else:
            data.append(item_data)
            
        return self.save_raw_data(file_type, data)
