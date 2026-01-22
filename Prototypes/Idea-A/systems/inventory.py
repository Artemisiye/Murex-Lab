"""
Inventory Manager for Alchemist's Journal
Handles item discovery and storage
"""

class Inventory:
    def __init__(self):
        self.items = {}  # {item_id: count}
        self.discovered = set()  # Set of discovered item IDs
        
    def add_item(self, item_id, count=1):
        """Add items to inventory and mark as discovered"""
        if item_id not in self.items:
            self.items[item_id] = 0
        self.items[item_id] += count
        self.discovered.add(item_id)
        
    def remove_item(self, item_id, count=1):
        """Remove items from inventory"""
        if item_id in self.items and self.items[item_id] >= count:
            self.items[item_id] -= count
            if self.items[item_id] == 0:
                del self.items[item_id]
            return True
        return False
        
    def has_item(self, item_id, count=1):
        """Check if inventory has enough of an item"""
        return self.items.get(item_id, 0) >= count
        
    def get_count(self, item_id):
        """Get count of specific item"""
        return self.items.get(item_id, 0)
        
    def has_discovered(self, item_id):
        """Check if item has been discovered"""
        return item_id in self.discovered
