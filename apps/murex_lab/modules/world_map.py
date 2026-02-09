import json
import os
import random

class map_cell:
    def __init__(self, x, y, name="Wilderness", cell_type="plains"):
        self.x = x
        self.y = y
        self.name = name
        self.type = cell_type # 'plains', 'forest', 'mountains', 'lab'
        self.resources = [] # List of material_ids
        self.regional_map = None # Created on first exploration
        
        # Randomize resources based on type
        if cell_type == "forest":
            self.resources = ["mat_oak_log"]
        elif cell_type == "mountains":
            self.resources = ["mat_iron_ingot"]
        elif cell_type == "lab":
            self.name = "The Artificer's Lab"
            self.resources = []

    def to_dict(self, discovered=False):
        data = {
            "x": self.x,
            "y": self.y,
            "name": self.name if discovered else "Unknown Location",
            "type": self.type if discovered else "unknown",
            "resources": self.resources if discovered else [],
            "discovered": discovered
        }
        return data

class map_manager:
    def __init__(self, data_path, size=30):
        """Initializes the map manager, with the player starting at the center of the map."""
        self.data_path = data_path
        self.size = size
        self.grid = {} # (x, y) -> map_cell
        self.player_pos = {"x": size // 2, "y": size // 2}
        self.discovered_cells = set()
        
        self.generate_grid()
        self.reveal_surroundings(radius=2)

    def reveal_surroundings(self, radius=2):
        """Reveals the cells around the player. Returns list of newly revealed cells."""
        px, py = self.player_pos["x"], self.player_pos["y"]
        newly_revealed = []
        
        # Symmetrical range (-radius to +radius)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = px + dx, py + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    key = f"{nx},{ny}"
                    if key not in self.discovered_cells:
                        self.discovered_cells.add(key)
                        cell = self.get_cell(nx, ny)
                        if cell:
                            newly_revealed.append(cell.to_dict(True))
        return newly_revealed

    def generate_grid(self):
        center = self.size // 2
        for y in range(self.size):
            for x in range(self.size):
                # Border/Ocean logic
                dist_to_center = max(abs(x - center), abs(y - center))
                
                if dist_to_center > (self.size // 2) - 3:
                     # Far edges are Ocean
                     cell = map_cell(x, y, "Deep Waters", "ocean")
                elif dist_to_center > (self.size // 2) - 5:
                     # Buffer is Sea
                     cell = map_cell(x, y, "Open Sea", "sea")
                     cell.resources = ["sea_salt", "fish"]
                elif dist_to_center > (self.size // 2) - 6:
                     # Transition is Beach
                     cell = map_cell(x, y, "Sanded Shore", "beach")
                     cell.resources = ["sand", "raw_clay"]
                elif x == center and y == center:
                    cell = map_cell(x, y, "The Lab", "lab")
                else:
                    r = random.random()
                    if r < 0.12:
                        cell = map_cell(x, y, "Ancient Forest", "forest")
                        cell.resources = ["mat_oak_log", "mat_plant_fibers"]
                    elif r < 0.22:
                        cell = map_cell(x, y, "Jagged Peaks", "mountains")
                        cell.resources = ["iron_ore", "rough_stone", "native_copper", "tin_ore"]
                    elif r < 0.30:
                        cell = map_cell(x, y, "Winding River", "river")
                        cell.resources = ["river_water", "raw_clay"]
                    else:
                        cell = map_cell(x, y, "Wild Meadow", "plains")
                        cell.resources = ["plant_fibers", "wild_seeds"]
                self.grid[(x, y)] = cell

    def get_cell(self, x, y):
        return self.grid.get((x, y))

    def move_player(self, dx, dy):
        """Moves player and returns (success, newly_revealed_cells or error_msg)."""
        new_x = self.player_pos["x"] + dx
        new_y = self.player_pos["y"] + dy
        
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            target_cell = self.get_cell(new_x, new_y)
            if target_cell and target_cell.type == "ocean":
                return False, "ocean_blocked" 
                
            self.player_pos["x"] = new_x
            self.player_pos["y"] = new_y
            newly_revealed = self.reveal_surroundings()
            
            # Check if we just entered the Lab
            entered_lab = False
            if target_cell and target_cell.type == "lab":
                entered_lab = True
                
            return True, {"revealed": newly_revealed, "entered_lab": entered_lab}
        return False, "invalid_path"

    def enter_regional_map(self):
        """Returns the regional map for the current position, generating if needed."""
        from .regional_map import RegionalMap
        cell = self.get_cell(self.player_pos["x"], self.player_pos["y"])
        if not cell.regional_map:
            cell.regional_map = RegionalMap(cell.type)
        return cell.regional_map

    def get_map_data(self):
        """Returns only the discovered cells to reduce payload size."""
        cells = []
        for key in self.discovered_cells:
            x, y = map(int, key.split(','))
            cell = self.get_cell(x, y)
            if cell:
                cells.append(cell.to_dict(True))
            
        return {
            "cells": cells,
            "player_pos": self.player_pos,
            "size": self.size
        }

    # def scavenge_current_pos(self):
    #     cell = self.get_cell(self.player_pos["x"], self.player_pos["y"])
    #     if not cell or cell.type == "lab":
    #         return []

    #     loot = []
    #     for res_id in cell.resources:
    #         # Simple 50% chance to find 1-3
    #         if random.random() < 0.5:
    #             loot.append({"id": res_id, "quantity": random.randint(1, 3)})
        
    #     return loot
