import pygame
from .style import styles

GRID_SIZE = 8

# ========================
# --- Overlay Manager ---
# ========================
class OverlayManager:
    """
    Manages transient UI elements that should draw on top of everything else
    (e.g., tooltips, dropdown lists). Callbacks are cleared after each frame.
    """
    def __init__(self):
        self._items = []
        
    def add(self, callback):
        """Schedule a drawing function to be called at the end of the frame."""
        self._items.append(callback)
        
    def draw(self, surface):
        """Execute all scheduled overlay drawing functions and flush the queue."""
        for callback in self._items:
            callback(surface)
        self._items = [] # Flush each frame

overlays = OverlayManager()

# ========================
# Widget 
# ========================
class Widget:
    """
    The fundamental building block of the Retro-Py UI.
    Supports a hierarchical tree structure, grid-based positioning, 
    event dispatching, and spatial focus management.
    """
    def __init__(self, x=0, y=0, w=4, h=4, padding=0, children=None, raw_coords=False):
        """
        Initialize a new Widget.
        
        Args:
            x, y: Position in grid units (8px blocks).
            w, h: Dimensions in grid units.
            padding: Inward offset for content/children in grid units.
            children: Optional list of Widgets to add as children.
            raw_coords: If True, x, y, w, h are treated as literal pixels instead of grid units.
        """
        # Scale by Grid Size
        if not raw_coords:
            x, y, w, h = x * GRID_SIZE, y * GRID_SIZE, w * GRID_SIZE, h * GRID_SIZE
            padding = padding * GRID_SIZE

        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True
        self.children = []
        self.parent = None
        self.padding = padding
        self.has_shadow = False
        self.shadow_offset = 3
        self.shadow_color = styles.get_color("shadow")
        self.is_focused = False
        self.can_focus = False
        self.is_captured = False
        self.clip_children = False

        if children:
            for child in children:
                self.add_child(child)

    def focus(self):
        """Grant exclusive focus to this widget within its hierarchy."""
        if self.can_focus:
            # Enforce exclusive focus
            root = self
            while root.parent: root = root.parent
            for w in root.get_focusable_widgets():
                w.is_focused = False
            self.is_focused = True
    
    def blur(self):
        """Remove focus and capture state from this widget."""
        self.is_focused = False
        self.is_captured = False
        
    def add_child(self, child):
        """Add a child widget and set its parent reference."""
        child.parent = self
        self.children.append(child)

    def get_absolute_rect(self):
        """Calculate the widget's Rect in screen-space coordinates."""
        if self.parent:
            parent_rect = self.parent.get_absolute_rect()
            # If the parent is a ScrollContainer, children are offset by scroll
            scroll_off = getattr(self.parent, 'scroll_offset', 0) if hasattr(self.parent, 'scroll_offset') else 0
            return pygame.Rect(parent_rect.x + self.rect.x + self.padding, 
                             parent_rect.y + self.rect.y - scroll_off + self.padding, 
                             self.rect.w - self.padding * 2, 
                             self.rect.h - self.padding * 2)
        return self.rect.copy()

    def draw(self, surface):
        """Recursive draw call for the widget and its children."""
        if not self.visible:
            return
        
        abs_rect = self.get_absolute_rect()
        
        # Shadow first
        if self.has_shadow:
            pygame.draw.rect(surface, self.shadow_color, 
                             (abs_rect.x + self.shadow_offset, 
                             abs_rect.y + self.shadow_offset, 
                             abs_rect.w, 
                             abs_rect.h))

        # Draw self (backgrounds, borders)
        self._draw_self(surface, abs_rect)
        
        # Clip for children
        content_rect = abs_rect.inflate(-self.padding * 2, -self.padding * 2)
        old_clip = surface.get_clip()
        
        if self.clip_children:
            clip_rect = content_rect.clip(old_clip)
            surface.set_clip(clip_rect)
        
        for child in self.children:
            child.draw(surface)
            
        if self.clip_children:
            surface.set_clip(old_clip)

    def _draw_self(self, surface, abs_rect):
        """Internal drawing method for subclasses to override."""
        pass

    def get_focusable_widgets(self):
        """Flattened list of all visible and focusable widgets in the tree."""
        focusable = []
        if self.can_focus and self.visible:
            focusable.append(self)
        for child in self.children:
            if child.visible:
                focusable.extend(child.get_focusable_widgets())
        return focusable

    def handle_event(self, event, mx, my):
        """
        The Dispatcher: Routes events through the UI tree.
        1. Checks for global focus/tab traversal.
        2. Passes the event to children (back-to-front) for interception.
        3. If no child consumes the event, it calls self.on_event().
        
        Args:
            event: The Pygame event object.
            mx, my: 8px grid-aligned mouse coordinates.
        Returns: True if the event was consumed.
        """
        if not self.visible:
            return False
            
        # Global Focus Traversal
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
             if self.parent is None:
                 all_focusable = self.get_focusable_widgets()
                 if not all_focusable: return False
                 
                 current_focus_idx = -1
                 for i, w in enumerate(all_focusable):
                     if w.is_focused:
                         current_focus_idx = i
                         break
                 
                 step = -1 if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                 next_idx = (current_focus_idx + step) % len(all_focusable)
                 
                 if current_focus_idx != -1:
                     all_focusable[current_focus_idx].blur()
                 all_focusable[next_idx].focus()
                 return True

        # 1. Prioritize captured widgets (modal behavior)
        for child in reversed(self.children):
            if child.visible and getattr(child, 'is_captured', False):
                if child.handle_event(event, mx, my):
                    return True
                    
        # 2. Normal Dispatch (excluding captured to avoid double-process)
        for child in reversed(self.children):
            if child.visible and not getattr(child, 'is_captured', False):
                if child.handle_event(event, mx, my):
                    return True
                
        if self.parent is None and event.type == pygame.MOUSEBUTTONDOWN:
            for w in self.get_focusable_widgets():
                w.blur()

        return self.on_event(event, mx, my)

    def on_event(self, event, mx, my):
        """
        The Handler: Specific widget interaction logic.
        Override this in subclasses (Button, Slider, etc.) to define 
        how the widget reacts to clicks or key presses.
        """
        return False

# ========================
# --- Focus Manager ---
# ========================
class FocusManager:
    """Manages spatial UI navigation across the Widget tree using arrow keys."""
    def __init__(self, root_view):
        self.root = root_view

    def navigate(self, direction):
        """
        Move focus to the nearest logical neighbor in the given direction.
        
        Args:
            direction: One of [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        Returns: True if focus changed.
        """
        all_focusable = self.root.get_focusable_widgets()
        if not all_focusable: return False
        
        current = next((w for w in all_focusable if w.is_focused), None)
        if not current:
            all_focusable[0].focus()
            return True

        # Scoping: If current or an ancestor is captured, stay inside.
        capture_root = self.root
        is_escaping = False
        
        if getattr(current, 'is_captured', False):
            capture_root = current
        else:
            node = current.parent
            while node:
                if getattr(node, 'is_captured', False):
                    capture_root = node
                    break
                node = node.parent

        def find_best(scope_widget, exclude_widget=None):
            scope_focusable = scope_widget.get_focusable_widgets()
            origin_rect = current.get_absolute_rect()
            origin_cx = origin_rect.centerx
            origin_cy = origin_rect.centery
            
            candidates = []
            for w in scope_focusable:
                if w == current or (exclude_widget and w in exclude_widget.get_focusable_widgets()):
                    continue
                    
                w_rect = w.get_absolute_rect()
                w_cx = w_rect.centerx
                w_cy = w_rect.centery
                
                dx = w_cx - origin_cx
                dy = w_cy - origin_cy
                valid = False
                
                if direction == pygame.K_RIGHT and dx > 0: valid = True
                elif direction == pygame.K_LEFT and dx < 0: valid = True
                elif direction == pygame.K_DOWN and dy > 0: valid = True
                elif direction == pygame.K_UP and dy < 0: valid = True

                if valid:
                    if direction in [pygame.K_LEFT, pygame.K_RIGHT]:
                        primary = abs(dx)
                        secondary = abs(dy) * 3
                    else:
                        primary = abs(dy)
                        secondary = abs(dx) * 3
                        
                    score = primary + secondary
                    candidates.append((score, w))
            
            if candidates:
                candidates.sort(key=lambda c: c[0])
                return candidates[0][1]
            return None

        # Container Search: Look inside current container. Fallback to outer (unless captured).
        node = current.parent
        prev_node = None
        best = find_best(current) if current == capture_root else None
        
        if not best:
            while node:
                best = find_best(node, exclude_widget=prev_node)
                if best: break
                if node == capture_root:
                    # We hit the capture boundary and found nothing.
                    is_escaping = True
                    break
                prev_node = node
                node = node.parent
            
        if not best and not is_escaping:
             best = find_best(self.root, exclude_widget=prev_node)
             
        if best:
            current.blur()
            best.focus()
            return True
        elif is_escaping and capture_root != self.root:
            # User navigated "out" of a captured container
            current.blur()
            capture_root.is_captured = False
            capture_root.focus()
            return True
            
        return False

    def draw_debug(self, surface):
        """Draws spatial navigation bounds and state color hints for debugging."""
        all_focusable = self.root.get_focusable_widgets()
        for w in all_focusable:
            if getattr(w, 'is_captured', False):
                color = (0, 191, 255) # Deep Sky Blue
            elif w.is_focused:
                color = (255, 0, 0) # Red
            else:
                color = (255, 255, 0) # Yellow
            pygame.draw.rect(surface, color, w.get_absolute_rect(), 1)

# ========================
# Base View
# ========================
class BaseView(Widget):
    """
    A specialized Widget representing a top-level application state (View).
    Standardizes viewport dimensions and provides focus management.
    """
    def __init__(self, **kwargs):
        # Default view bounds: x=0, y=3, w=60, h=30 (480x240 @ 8px grid)
        # Note: main header ends at y=3 (24px)
        kwargs.setdefault('x', 0)
        kwargs.setdefault('y', 3)
        kwargs.setdefault('w', 60)
        kwargs.setdefault('h', 30)
        super().__init__(**kwargs)
        self.focus_manager = FocusManager(self)

    def dispatch_view_event(self, event, game_state):
        """
        EntryPoint for Pygame events. Translates pixel-mouse to grid-mouse 
        and initiates event propagation.
        """
        self.game_state = game_state

        mx, my = pygame.mouse.get_pos()
        scale = game_state.get('scale', 1)
        vx, vy = mx // scale, my // scale
        
        consumed = self.handle_event(event, vx, vy)
        
        # Unconsumed Arrow Keys -> FocusManager Spatial Navigation
        if not consumed and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                consumed = self.focus_manager.navigate(event.key)
                
        return consumed

    def draw_view(self, surface, game_state):
        """Main rendering EntryPoint for the View."""
        self.game_state = game_state
        self.draw(surface)
        
        if game_state.get('debug', False):
            self.focus_manager.draw_debug(surface)
