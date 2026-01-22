"""
Recipe Manager for Alchemist's Journal
Handles recipe discovery and validation
"""
import json

class RecipeManager:
    def __init__(self, recipe_file):
        with open(recipe_file, 'r') as f:
            data = json.load(f)
        self.recipes = data['recipes']
        self.unlocked_recipes = []
        
    def check_recipe_unlock(self, inventory):
        """Check if new recipes should be unlocked based on discovered items"""
        newly_unlocked = []
        
        for recipe in self.recipes:
            if recipe in self.unlocked_recipes:
                continue
                
            # Check if all ingredients have been discovered
            all_discovered = all(
                inventory.has_discovered(ingredient) 
                for ingredient in recipe['inputs']
            )
            
            if all_discovered:
                self.unlocked_recipes.append(recipe)
                newly_unlocked.append(recipe)
                
        return newly_unlocked
        
    def try_craft(self, item1_id, item2_id, inventory):
        """
        Try to combine two items and see if they make a recipe
        Returns: (success, output_item_id or None, recipe or None)
        """
        # Try both orderings
        for recipe in self.unlocked_recipes:
            inputs = recipe['inputs']
            
            # Check if this combination matches
            if len(inputs) == 2:
                if (inputs[0] == item1_id and inputs[1] == item2_id) or \
                   (inputs[1] == item1_id and inputs[0] == item2_id):
                    
                    # Check if we have the items
                    if inventory.has_item(item1_id) and inventory.has_item(item2_id):
                        return (True, recipe['output'], recipe)
                        
        return (False, None, None)
        
    def get_unlocked_count(self):
        """Get number of unlocked recipes"""
        return len(self.unlocked_recipes)
