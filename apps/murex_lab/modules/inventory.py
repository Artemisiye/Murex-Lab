import json
import os

class InventoryItem:
    def __init__(self, item_id, item_type, quantity=1, data=None):
        self.item_id = item_id
        self.item_type = item_type  # 'material', 'component', 'product'
        self.quantity = quantity
        self.data = data or {} # Custom stats for products

class Inventory:
    def __init__(self, save_path):
        self.save_path = save_path
        self.items = {} # Maps item_id -> InventoryItem
        self.gold = 0
        self.load()

    def load(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r') as f:
                    raw_data = json.load(f)
                    
                    # Support both old format (direct dict) and new format (nested)
                    if 'items' in raw_data:
                        items_data = raw_data['items']
                        self.gold = raw_data.get('gold', 0)
                    else:
                        items_data = raw_data
                        self.gold = 0

                    for key, val in items_data.items():
                        self.items[key] = InventoryItem(
                            val['item_id'], 
                            val['item_type'], 
                            val['quantity'],
                            val.get('data')
                        )
            except Exception as e:
                print(f"Error loading inventory: {e}")
                self.items = {}
                self.gold = 0

    def save(self):
        items_dict = {}
        for key, item in self.items.items():
            items_dict[key] = {
                "item_id": item.item_id,
                "item_type": item.item_type,
                "quantity": item.quantity,
                "data": item.data
            }
        
        full_data = {
            "gold": self.gold,
            "items": items_dict
        }
        
        with open(self.save_path, 'w') as f:
            json.dump(full_data, f, indent=4)

    def add_gold(self, amount):
        self.gold += amount
        self.save()

    def remove_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            self.save()
            return True
        return False

    def add_item(self, item_id, item_type, quantity=1, data=None):
        # Materials and basic components stack by ID
        key = item_id if item_type not in ['product', 'equipment'] else f"{item_id}_{len(self.items)}"
        
        if key in self.items and item_type not in ['product', 'equipment']:
            self.items[key].quantity += quantity
        else:
            self.items[key] = InventoryItem(item_id, item_type, quantity, data)
        self.save()

    def remove_item(self, item_id, quantity=1):
        if item_id in self.items:
            if self.items[item_id].quantity >= quantity:
                self.items[item_id].quantity -= quantity
                if self.items[item_id].quantity <= 0:
                    del self.items[item_id]
                self.save()
                return True
        return False

    def get_all(self):
        return self.items
