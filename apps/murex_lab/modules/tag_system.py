from typing import List, Union

class Tag:
    """Represents a single Gameplay Tag (e.g., 'Item.Material.Iron')."""
    def __init__(self, tag_string: str):
        self.tag_string = tag_string
    
    def matches(self, required_tag: str) -> bool:
        """
        Checks if this tag matches the required tag.
        Matches if exact match or if this tag is a child of required_tag.
        Example: 'Item.Material.Iron' matches 'Item.Material'
        """
        return self.tag_string == required_tag or self.tag_string.startswith(required_tag + ".")

    def __str__(self):
        return self.tag_string

    def __repr__(self):
        return f"<Tag: {self.tag_string}>"

class TagContainer:
    """Holds a collection of tags for an object."""
    def __init__(self, tags: List[str] = None):
        if tags is None:
            self.tags = []
        else:
            self.tags = [Tag(t) for t in tags]

    def add_tag(self, tag_string: str):
        if not any(t.tag_string == tag_string for t in self.tags):
            self.tags.append(Tag(tag_string))

    def has_tag(self, required_tag: str) -> bool:
        """Returns True if ANY tag in the container matches the required tag."""
        return any(t.matches(required_tag) for t in self.tags)

    def has_all_tags(self, required_tags: List[str]) -> bool:
        """Returns True if the container has matches for ALL required tags."""
        return all(self.has_tag(req) for req in required_tags)

    def has_any_tag(self, required_tags: List[str]) -> bool:
        """Returns True if the container has matches for AT LEAST ONE of the required tags."""
        return any(self.has_tag(req) for req in required_tags)

    def matches_query(self, required: List[str] = None, forbidden: List[str] = None) -> bool:
        """
        Complex query.
        - Must have ALL 'required' tags.
        - Must have NONE of the 'forbidden' tags.
        """
        if forbidden and self.has_any_tag(forbidden):
            return False
            
        if required and not self.has_all_tags(required):
            return False
            
        return True
