import json
import os

class DataRegistry:
    """
    Manages access to static game data (JSON files).
    Provides a centralized interface for retrieving item blueprints, 
    monster stats, and other read-only configuration.
    """
    def __init__(self, data_root):
        self.root = data_root
        self.data = {} # category -> dict/list
        self._tag_index = {} # category -> tag -> [items]

    def load_category(self, category_name, file_name=None):
        """
        Loads a JSON file and builds a tag index for faster filtering.
        """
        if file_name is None:
            file_name = f"{category_name}.json"
            
        full_path = os.path.join(self.root, file_name)
        if not os.path.exists(full_path):
            print(f"DataRegistry: Warning - File not found: {full_path}")
            return None
            
        try:
            with open(full_path, "r") as f:
                content = json.load(f)
                self.data[category_name] = content
                
                # Build Tag Index
                if isinstance(content, list):
                    self._tag_index[category_name] = {}
                    for item in content:
                        tags = item.get("tags", [])
                        for tag in tags:
                            if tag not in self._tag_index[category_name]:
                                self._tag_index[category_name][tag] = []
                            self._tag_index[category_name][tag].append(item)
                
            return self.data[category_name]
        except Exception as e:
            print(f"DataRegistry: Error loading {file_name}: {e}")
            return None

    def get(self, category, key=None, default=None):
        """
        Retrieves data for a category. 
        If key is provided, attempts to lookup by 'id' field for lists.
        """
        cat_data = self.data.get(category)
        if cat_data is None: return default
        if key is None: return cat_data
            
        if isinstance(cat_data, dict):
            return cat_data.get(key, default)
        
        if isinstance(cat_data, list):
            for item in cat_data:
                if isinstance(item, dict) and item.get("id") == key:
                    return item
        return default

    def find(self, category, **kwargs):
        """
        Returns a list of items in the category matching all provided filters.
        e.g. registry.find("items", name="Oak Log")
        """
        cat_data = self.data.get(category, [])
        if not isinstance(cat_data, list): return []
        
        results = []
        for item in cat_data:
            match = True
            for k, v in kwargs.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                results.append(item)
        return results

    def filter_by_tag(self, category, tag_prefix):
        """
        Returns items that have at least one tag starting with the given prefix.
        Uses the tag index for O(1) lookups on exact matches, or O(tags) for prefixes.
        """
        cat_index = self._tag_index.get(category, {})
        if not cat_index:
            # Fallback to linear scan if no index exists
            return [item for item in self.data.get(category, []) if any(t.startswith(tag_prefix) for t in item.get("tags", []))]
        
        results = []
        seen_ids = set()
        
        # Collect all indexed tags that match the prefix
        for tag, items in cat_index.items():
            if tag.startswith(tag_prefix):
                for item in items:
                    item_id = item.get("id")
                    if item_id not in seen_ids:
                        results.append(item)
                        seen_ids.add(item_id)
        return results

    def all(self, category):
        """Returns the full data for a category."""
        return self.data.get(category, [])
