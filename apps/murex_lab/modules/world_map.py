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
    def __init__(self, data_path, size=11):
        self.data_path = data_path
        self.size = size
        self.grid = {} # (x, y) -> map_cell
        self.player_pos = {"x": size // 2, "y": size // 2}
        self.discovered_cells = {f"{self.player_pos['x']},{self.player_pos['y']}"}
        
        # Initial reveal around the lab
        self.reveal_surroundings()
        self.generate_grid()

    def reveal_surroundings(self):
        px, py = self.player_pos["x"], self.player_pos["y"]
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = px + dx, py + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    self.discovered_cells.add(f"{nx},{ny}")

    def generate_grid(self):
        center = self.size // 2
        for y in range(self.size):
            for x in range(self.size):
                if x == center and y == center:
                    cell = map_cell(x, y, "The Lab", "lab")
                else:
                    r = random.random()
                    if r < 0.15:
                        cell = map_cell(x, y, "Ancient Forest", "forest")
                        cell.resources = ["mat_oak_log", "mat_plant_fibers"]
                    elif r < 0.25:
                        cell = map_cell(x, y, "Jagged Peaks", "mountains")
                        cell.resources = ["mat_iron_ore", "mat_rough_stone"]
                    elif r < 0.35:
                        cell = map_cell(x, y, "Stony Outcrop", "mountains")
                        cell.resources = ["mat_rough_stone", "mat_flint_shard"]
                    elif r < 0.45:
                        cell = map_cell(x, y, "Winding River", "river")
                        cell.resources = ["mat_river_water", "mat_raw_clay"]
                    elif r < 0.60:
                        cell = map_cell(x, y, "Wild Meadow", "plains")
                        cell.resources = ["mat_plant_fibers", "mat_wild_seeds"]
                    else:
                        cell = map_cell(x, y, "Dry Wasteland", "plains")
                        cell.resources = ["mat_sand", "mat_rough_stone"]
                self.grid[(x, y)] = cell

    def get_cell(self, x, y):
        return self.grid.get((x, y))

    def move_player(self, dx, dy):
        new_x = self.player_pos["x"] + dx
        new_y = self.player_pos["y"] + dy
        
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            self.player_pos["x"] = new_x
            self.player_pos["y"] = new_y
            # Reveal area around new position
            self.reveal_surroundings()
            return True
        return False

    def get_map_data(self):
        cells = []
        for c in self.grid.values():
            is_discovered = f"{c.x},{c.y}" in self.discovered_cells
            cells.append(c.to_dict(is_discovered))
            
        return {
            "cells": cells,
            "player_pos": self.player_pos,
            "size": self.size
        }

    def scavenge_current_pos(self):
        cell = self.get_cell(self.player_pos["x"], self.player_pos["y"])
        if not cell or cell.type == "lab":
            return []

        loot = []
        for res_id in cell.resources:
            # Simple 50% chance to find 1-3
            if random.random() < 0.5:
                loot.append({"id": res_id, "quantity": random.randint(1, 3)})
        
        return loot
