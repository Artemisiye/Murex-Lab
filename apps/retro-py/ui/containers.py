import pygame
from .style import styles
from .base import Widget, GRID_SIZE

# ========================
#  | Panel |             |
# ========================
class Panel(Widget):
    """
    A structural container with a border, optional title tabs, and dividers.
    """
    def __init__(self, x=0, y=0, w=60, h=30, title=None, titles=None, children=None):
        """
        Args:
            title: A simple string for a single title.
            titles: A list of dicts for multi-title tabs: {"text": str, "color": tuple, "active": bool}.
        """
        super().__init__(x, y, w, h, padding=0.5, children=children)
        self.titles = titles if titles else []
        if title: self.titles.append({"text": title, "color": styles.get_color("accent")})
        self.dividers = [] # list of (x_pos, is_vertical, color)
        self.has_shadow = True
        self.clip_children = True

    def _draw_self(self, surface, abs_rect):
        x, y, w, h = abs_rect
        pygame.draw.rect(surface, styles.get_color("panel"), abs_rect)
        
        # Border Segments
        pygame.draw.line(surface, styles.get_color("dim"), (x, y), (x, y + h)) # L
        pygame.draw.line(surface, styles.get_color("dim"), (x, y + h), (x + w, y + h)) # B
        pygame.draw.line(surface, styles.get_color("dim"), (x + w, y + h), (x + w, y)) # R
        
        # Top Border with Gaps for Titles
        font = styles.get_font("H2")
        if not self.titles:
            pygame.draw.line(surface, styles.get_color("dim"), (x, y), (x + w, y))
        else:
            curr_x = x
            for t_data in self.titles:
                t_text = t_data.get("text", "")
                t_col = t_data.get("color", styles.get_color("accent"))
                is_active = t_data.get("active", False)
                is_tab = t_data.get("is_tab", False)
                tw = font.get_width(t_text) if font else 0
                
                line_w = 4
                pygame.draw.line(surface, styles.get_color("dim"), (curr_x, y), (curr_x + line_w, y))
                curr_x += line_w
                
                if font:
                    if is_active and is_tab:
                        # Active tab highlight
                        pygame.draw.rect(surface, styles.get_color("accent"), (curr_x, y - 8, tw + 4, 15))
                        font.draw(surface, t_text, curr_x + 2, y + 4, styles.get_color("panel"))
                    else:
                        font.draw(surface, t_text, curr_x + 2, y + 4, t_col)
                curr_x += tw + 4
            
            if curr_x < x + w:
                pygame.draw.line(surface, styles.get_color("dim"), (curr_x, y), (x + w, y))

        # Dividers
        for div_pos, is_vert, div_col in self.dividers:
            color = div_col if div_col else styles.get_color("dim")
            if is_vert:
                pygame.draw.line(surface, color, (x + div_pos, y + 1), (x + div_pos, y + h - 1))
            else:
                pygame.draw.line(surface, color, (x + 1, y + div_pos), (x + w - 1, y + div_pos))


# ========================
# Scroll Container
# ========================
class ScrollContainer(Widget):
    """
    A container that clips children and allows vertical scrolling.
    Requires capture to enable spatial navigation within its items.
    """
    def __init__(self, x=0, y=0, w=30, h=18):
        super().__init__(x, y, w, h, padding=0)
        self.scroll_offset = 0
        self.content_h = 0
        self.can_focus = True
        self.is_captured = False
        self.scrollbar_w = 4
        self.thumb_color = styles.get_color("dim")
        self.clip_children = True

    def add_child(self, child):
        """Append a child and recalculate total content height."""
        super().add_child(child)
        if child.rect.bottom > self.content_h:
            self.content_h = child.rect.bottom + 4

    def get_focusable_widgets(self):
        """Only exposes children to FocusManager if the container is captured."""
        if not self.visible: return []
        widgets = []
        if self.can_focus:
            widgets.append(self)
        if self.is_captured:
            for child in self.children:
                widgets.extend(child.get_focusable_widgets())
        return widgets

    def _draw_self(self, surface, abs_rect):
        if self.content_h <= self.rect.h: return
        
        # Draw Scrollbar
        tx = abs_rect.right - self.scrollbar_w
        pygame.draw.rect(surface, (10, 10, 10), (tx, abs_rect.y, self.scrollbar_w, abs_rect.h))
        
        ratio = self.rect.h / self.content_h
        thumb_h = max(8, int(self.rect.h * ratio))
        thumb_y = abs_rect.y + int((self.scroll_offset / self.content_h) * self.rect.h)
        pygame.draw.rect(surface, self.thumb_color, (tx, thumb_y, self.scrollbar_w, thumb_h))

    def handle_event(self, event, mx, my):
        consumed = super().handle_event(event, mx, my)
        if not consumed and event.type == pygame.KEYDOWN:
            # Automatic scrolling when child focus changes
            focused_child_idx = next((i for i, child in enumerate(self.children) if child.is_focused), -1)
            if focused_child_idx != -1:
                if event.key == pygame.K_DOWN:
                    self.children[focused_child_idx].blur()
                    n = len(self.children)
                    nxt = (focused_child_idx + 1) % n
                    while not self.children[nxt].can_focus and nxt != focused_child_idx:
                        nxt = (nxt + 1) % n
                    self.children[nxt].focus()
                    
                    child_rect = self.children[nxt].rect
                    if child_rect.bottom > self.scroll_offset + self.rect.h:
                        self.scroll_offset = child_rect.bottom - self.rect.h + self.padding
                    elif child_rect.top < self.scroll_offset:
                         self.scroll_offset = max(0, child_rect.top - self.padding)
                    return True
                elif event.key == pygame.K_UP:
                    self.children[focused_child_idx].blur()
                    n = len(self.children)
                    nxt = (focused_child_idx - 1) % n
                    while not self.children[nxt].can_focus and nxt != focused_child_idx:
                        nxt = (nxt - 1) % n
                    self.children[nxt].focus()
                    
                    child_rect = self.children[nxt].rect
                    if child_rect.top < self.scroll_offset:
                        self.scroll_offset = max(0, child_rect.top - self.padding)
                    elif child_rect.bottom > self.scroll_offset + self.rect.h:
                        self.scroll_offset = child_rect.bottom - self.rect.h + self.padding
                    return True
        return consumed

    def on_event(self, event, mx, my):
        # Keyboard toggle for container capture
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.is_captured = not self.is_captured
                if self.is_captured:
                    # Focus first child
                    all_c = self.get_focusable_widgets()
                    if len(all_c) > 1: all_c[1].focus()
                return True
            if event.key == pygame.K_ESCAPE and self.is_captured:
                self.is_captured = False
                return True

        # Mouse scroll support
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in [4, 5]:
            if event.button == 4: # UP
                self.scroll_offset = max(0, self.scroll_offset - 16)
                return True
            if event.button == 5: # DOWN
                self.scroll_offset = min(self.content_h - self.rect.h, self.scroll_offset + 16)
                return True
        return False


# ========================
#  | Panel | Stack |     |
# ========================
class PanelStack(Widget):
    """
    Manages multiple sub-panels as tabs. Automatically handles visibility 
    and tab-header rendering/switching.
    """
    def __init__(self, x=0, y=0, w=60, h=30, panels=None, **kwargs):
        """
        Args:
            panels: List of Widgets or dicts {"view": Widget, "name": str}.
        """
        super().__init__(x, y, w, h, **kwargs)
        self.panels = [] # list of {"view": Widget, "name": str}
        self.active_idx = 0
        self.clip_children = False
        
        if panels:
            for p in panels:
                view = p.get("view") if isinstance(p, dict) else p
                name = p.get("name") if isinstance(p, dict) else self._get_panel_name(view)
                if view:
                    self.add_panel(view, name=name)
        self._sync_active_panel()

    def _get_panel_name(self, view):
        """Automatic extraction of a display name from nested Panel titles."""
        if isinstance(view, Panel) and hasattr(view, '_orig_title') and view._orig_title:
            return view._orig_title
        if hasattr(view, 'titles') and view.titles:
            return view.titles[0].get("text", "PAGE")
        return view.__class__.__name__

    def add_panel(self, view, name=None):
        """Register a new tab in the stack."""
        if name is None:
            name = self._get_panel_name(view)
        
        if isinstance(view, Panel) and not hasattr(view, '_orig_title'):
             view._orig_title = name

        view.visible = (len(self.panels) == self.active_idx)
        self.panels.append({"view": view, "name": name})
        self.add_child(view)
        self._sync_active_panel()

    def set_panel_name(self, index_or_view, new_name):
        """Dynamically update a tab's display name."""
        target = None
        if isinstance(index_or_view, int) and 0 <= index_or_view < len(self.panels):
            target = self.panels[index_or_view]
        else:
            for p in self.panels:
                if p["view"] == index_or_view:
                    target = p
                    break
        if target:
            target["name"] = new_name
            if isinstance(target["view"], Panel):
                target["view"]._orig_title = new_name
            self._sync_active_panel()

    def _sync_active_panel(self):
        """Refresh visibility state and inject tab headers into the active Panel."""
        for i, entry in enumerate(self.panels):
            view = entry["view"]
            view.visible = (i == self.active_idx)
            
            if view.visible and isinstance(view, Panel):
                titles = []
                for j, e in enumerate(self.panels):
                    is_active = (j == self.active_idx)
                    color = styles.get_color("accent") if is_active else styles.get_color("dim")
                    titles.append({"text": e["name"], "color": color, "active": is_active, "is_tab": True})
                view.titles = titles

    def on_event(self, event, mx, my):
        # Click detection for tab headers
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            if abs_rect.y <= my <= abs_rect.y + 16:
                font = styles.get_font("H2")
                curr_x = abs_rect.x
                for i, entry in enumerate(self.panels):
                    name = entry["name"]
                    tw = font.get_width(name) if font else 40
                    if tw == 0: tw = 40
                    if curr_x + 4 <= mx <= curr_x + 4 + tw + 4:
                        self.active_idx = i
                        self._sync_active_panel()
                        return True
                    curr_x += 4 + tw + 4
        return False
