import json
import os
from .tag_system import TagContainer

class Material:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.tags = TagContainer(data.get('tags', []))
        self.stats = data.get('stats', {})

class Component:
    def __init__(self, data, material: Material = None):
        self.id = data['id']
        self.name = data['name']
        self.material = material
        self.tags = TagContainer(data.get('tags', []))
        self.stats = data.get('stats', {})
        
        # Inherit tags from material (optional design choice, helps with queries)
        if self.material:
            for t in self.material.tags.tags:
                self.tags.add_tag(t.tag_string)

class SchematicSlot:
    def __init__(self, data):
        self.id = data['id']
        self.label = data['label']
        self.required_tags = data.get('required_tags', [])
        self.forbidden_tags = data.get('forbidden_tags', [])
        self.optional = data.get('optional', False)
        self.catalyst = data.get('catalyst', False) # If true, item is NOT consumed

    def accepts(self, component: Component) -> bool:
        """Checks if a component fits this slot."""
        return component.tags.matches_query(self.required_tags, self.forbidden_tags)

class Schematic:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type = data.get('type', 'product') # Category for UI
        self.station_id = data.get('station_id', 'station_none')
        self.output_id = data.get('output_id') # If it produces a specific material
        self.output_type = data.get('output_type', 'product') # material, component, or product
        self.tags = TagContainer(data.get('tags', []))
        self.slots = [SchematicSlot(s) for s in data.get('slots', [])]
        self.base_stats = data.get('base_stats', {})

class CraftingManager:
    def __init__(self, data_path):
        self.data_path = data_path
        self.materials = {}
        self.components = {}
        self.schematics = {}
        self.load_data()

    def load_data(self):
        """Loads JSON definitions."""
        # Load Materials
        with open(os.path.join(self.data_path, 'materials.json'), 'r') as f:
            for item in json.load(f):
                self.materials[item['id']] = Material(item)
        
        # Load Components (And link materials)
        with open(os.path.join(self.data_path, 'components.json'), 'r') as f:
            for item in json.load(f):
                mat = self.materials.get(item.get('material_id'))
                self.components[item['id']] = Component(item, mat)

        # Load Schematics
        with open(os.path.join(self.data_path, 'schematics.json'), 'r') as f:
            for item in json.load(f):
                self.schematics[item['id']] = Schematic(item)

        print(f"Loaded {len(self.materials)} Materials, {len(self.components)} Components, {len(self.schematics)} Schematics.")

    def get_schematic(self, schematic_id):
        return self.schematics.get(schematic_id)

    def get_all_schematics(self):
        return list(self.schematics.values())

    def get_valid_components_for_slot(self, schematic_id, slot_id):
        """Returns a list of all defined components that fit a specific slot."""
        schem = self.schematics.get(schematic_id)
        if not schem:
            return []
        
        target_slot = next((s for s in schem.slots if s.id == slot_id), None)
        if not target_slot:
            return []

        valid_objs = []
        # Check both registries
        for obj in list(self.components.values()) + list(self.materials.values()):
            if target_slot.accepts(obj):
                valid_objs.append(obj)
        
        return valid_objs

    def preview_craft(self, schematic_id, component_ids_map):
        """
        Calculates result stats.
        component_ids_map: dict of {slot_id: component_id}
        """
        schem = self.schematics.get(schematic_id)
        if not schem:
            return {"error": "Invalid Schematic"}

        result_stats = schem.base_stats.copy()
        
        # Simple Sum Logic for now
        for slot in schem.slots:
            comp_id = component_ids_map.get(slot.id)
            if comp_id:
                # Check components, then materials, then schematics (for products)
                comp = self.components.get(comp_id) or self.materials.get(comp_id) or self.schematics.get(comp_id)
                if comp:
                    # Support both Material/Component 'stats' and Schematic 'base_stats'
                    stats_source = getattr(comp, 'stats', getattr(comp, 'base_stats', {}))
                    for stat, value in stats_source.items():
                        result_stats[stat] = result_stats.get(stat, 0) + value
            elif not slot.optional:
                return {"error": f"Missing required slot: {slot.label}"}

        return {"success": True, "stats": result_stats}
