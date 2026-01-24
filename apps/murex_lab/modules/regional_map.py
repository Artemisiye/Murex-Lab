import random

class RegionalNode:
    def __init__(self, id, name, tool_required, loot_items):
        self.id = id
        self.name = name
        self.tool_required = tool_required # e.g. 'stone_axe'
        self.loot_items = loot_items # list of item_ids

class RegionalMap:
    """
    A granular grid (e.g. 5x5) representing the interior of a Global Map cell.
    Contains resource nodes and roaming entities.
    """
    def __init__(self, parent_cell_type, size=5):
        self.size = size
        self.grid = {} # (x, y) -> node or None
        self.entities = [] # List of roaming enemies/animals
        self.player_pos = {"x": size // 2, "y": size // 2} # Start at center
        self.generate(parent_cell_type)
        
    def generate(self, cell_type):
        # Fill the regional grid with nodes based on the parent biome
        node_count = random.randint(3, 6)
        
        possible_nodes = []
        if cell_type == "forest":
            possible_nodes = [
                RegionalNode("node_oak", "Oak Tree", "stone_axe", ["mat_oak_log", "mat_tree_bark"]),
                RegionalNode("node_herbs", "Wild Herbs", "flint_knife", ["mat_bitter_herbs", "mat_wild_seeds"])
            ]
        elif cell_type == "mountains":
            possible_nodes = [
                RegionalNode("node_iron", "Iron Vein", "stone_pickaxe", ["mat_iron_ore"]),
                RegionalNode("node_stone", "Rock Outcrop", "stone_pickaxe", ["mat_rough_stone", "mat_flint_shard"])
            ]
        elif cell_type == "river":
            possible_nodes = [
                RegionalNode("node_clay", "Clay Deposit", "stone_shovel", ["mat_raw_clay"]),
                RegionalNode("node_fish", "Fishing Spot", "fishing_rod", ["mat_fish"])
            ]
            
        for _ in range(node_count):
            if not possible_nodes: break
            x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
            node = random.choice(possible_nodes)
            self.grid[(x, y)] = node
            
        # Add a few roaming entities
        for _ in range(random.randint(1, 2)):
            self.entities.append({
                "id": "animal_boar" if cell_type == "forest" else "enemy_bandit",
                "x": random.randint(0, self.size-1),
                "y": random.randint(0, self.size-1)
            })

    def move_player(self, dx, dy):
        new_x = self.player_pos["x"] + dx
        new_y = self.player_pos["y"] + dy
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            self.player_pos["x"] = new_x
            self.player_pos["y"] = new_y
            return True
        return False

    def harvest(self, x, y):
        """Removes the node at (x, y) and returns its loot."""
        node = self.grid.get((x, y))
        if node:
            del self.grid[(x, y)]
            return node.loot_items
        return []

    def to_dict(self):
        nodes_data = []
        for (x, y), node in self.grid.items():
            nodes_data.append({
                "x": x, "y": y, 
                "id": node.id, 
                "name": node.name, 
                "tool": node.tool_required
            })
        return {
            "size": self.size,
            "player_pos": self.player_pos,
            "nodes": nodes_data,
            "entities": self.entities
        }
