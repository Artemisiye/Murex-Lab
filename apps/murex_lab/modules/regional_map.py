import random

class RegionalNode:
    def __init__(self, id, name, tool_required, loot_items, weight=1):
        self.id = id
        self.name = name
        self.tool_required = tool_required # tag query like 'Item.Class.Tool.Axe'
        self.loot_items = loot_items # list of item_ids
        self.weight = weight

class RegionalMap:
    """
    A granular grid (10x10) representing the interior of a Global Map cell.
    Contains resource nodes and roaming entities.
    """
    def __init__(self, parent_cell_type, size=10):
        self.size = size
        self.grid = {} # (x, y) -> node or None
        self.entities = [] # List of roaming enemies/animals
        self.player_pos = {"x": size // 2, "y": size // 2} # Start at center
        self.generate(parent_cell_type)
        
    def generate(self, cell_type):
        # Increased density for 10x10 grid
        node_density = 0.25 # 25% of tiles have nodes
        
        possible_nodes = []
        if cell_type == "forest":
            possible_nodes = [
                RegionalNode("node_oak", "Oak Tree", "Item.Class.Tool.Axe", ["oak_log", "tree_bark"], weight=3),
                RegionalNode("node_herbs", "Wild Herbs", "", ["bitter_herbs", "wild_seeds"], weight=2),
                RegionalNode("node_shrub", "Wild Shrub", "", ["plant_fibers"], weight=5),
                RegionalNode("node_loose_stone", "Loose Stone", "", ["rough_stone"], weight=4),
                RegionalNode("node_fallen_branches", "Fallen Branches", "", ["oak_log"], weight=6)
            ]
        elif cell_type == "plains":
            possible_nodes = [
                RegionalNode("node_grass", "Tall Grass", "", ["plant_fibers"], weight=10),
                RegionalNode("node_seeds", "Seed Pods", "", ["wild_seeds"], weight=4),
                RegionalNode("node_bush", "Berry Bush", "", ["wild_seeds"], weight=3),
                RegionalNode("node_loose_stone", "Loose Stone", "", ["rough_stone"], weight=2)
            ]
        elif cell_type == "mountains":
            possible_nodes = [
                RegionalNode("node_iron", "Iron Vein", "Item.Class.Tool.Pickaxe", ["iron_ore"], weight=3),
                RegionalNode("node_stone", "Rock Outcrop", "Item.Class.Tool.Pickaxe", ["rough_stone", "flint_shard"], weight=5),
                RegionalNode("node_loose_stone", "Loose Stone", "", ["rough_stone"], weight=8)
            ]
        elif cell_type == "river":
            possible_nodes = [
                RegionalNode("node_clay", "Clay Deposit", "Item.Class.Tool.Shovel", ["raw_clay"], weight=5),
                RegionalNode("node_fish", "Fishing Spot", "Item.Class.Tool.FishingRod", ["fish"], weight=3),
                RegionalNode("node_reeds", "River Reeds", "", ["plant_fibers"], weight=6),
                RegionalNode("node_driftwood", "Driftwood", "", ["oak_log"], weight=4)
            ]
            
        if not possible_nodes: return

        # Fill grid based on density
        for y in range(self.size):
            for x in range(self.size):
                if random.random() < node_density:
                    # Choose node based on weight
                    total_weight = sum(n.weight for n in possible_nodes)
                    r = random.uniform(0, total_weight)
                    cursor = 0
                    for node in possible_nodes:
                        cursor += node.weight
                        if r <= cursor:
                            self.grid[(x, y)] = node
                            break
            
        # Add roaming entities
        entity_count = random.randint(2, 4)
        for _ in range(entity_count):
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
