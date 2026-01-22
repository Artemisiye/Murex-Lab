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
        self.load()

    def load(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                    for key, val in data.items():
                        self.items[key] = InventoryItem(
                            val['item_id'], 
                            val['item_type'], 
                            val['quantity'],
                            val.get('data')
                        )
            except Exception as e:
                print(f"Error loading inventory: {e}")
                self.items = {}

    def save(self):
        data = {}
        for key, item in self.items.items():
            data[key] = {
                "item_id": item.item_id,
                "item_type": item.item_type,
                "quantity": item.quantity,
                "data": item.data
            }
        with open(self.save_path, 'w') as f:
            json.dump(data, f, indent=4)

    def add_item(self, item_id, item_type, quantity=1, data=None):
        # Materials and basic components stack by ID
        # Products might need unique IDs if they have unique stats
        key = item_id if item_type != 'product' else f"{item_id}_{len(self.items)}"
        
        if key in self.items and item_type != 'product':
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
