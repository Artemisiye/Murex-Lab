import pygame
import os

GRID_SIZE = 8

# --- STYLE SYSTEM ---
class StyleManager:
    def __init__(self):
        self.fonts = {} # Role -> SpriteFont object
        self.colors = {
            "bg": (15, 13, 11),         # Dark Grey
            "panel": (25, 22, 19),      # Slightly lighter
            "accent": (230, 200, 100),  # Gold
            "header": (230, 200, 100),  # Gold          (=accent)
            "dim": (100, 90, 80),       # Grey
            "fg": (220, 210, 190),      # Off-white
            "shadow": (5, 4, 3),        # Near Black
            "select": (60, 55, 50),     # Grey          (panel + highlight)
            "textbox_bg": (15, 12, 10)  # Dark Grey
        }

    def set_font(self, role, font_obj):
        self.fonts[role] = font_obj

    def get_font(self, role):
        return self.fonts.get(role)

    def get_color(self, name):
        return self.colors.get(name, (255, 255, 255))

# Global instance
styles = StyleManager()

# --- OVERLAY MANAGER ---
class OverlayManager:
    def __init__(self):
        self._items = []
        
    def add(self, callback):
        self._items.append(callback)
        
    def draw(self, surface):
        for callback in self._items:
            callback(surface)
        self._items = [] # Flush each frame

overlays = OverlayManager()

# ========================
# Widget 
# ========================
class Widget:
    def __init__(self, x=0, y=0, w=4, h=4, padding=0, children=None, raw_coords=False):
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
        if self.can_focus:
            # Enforce exclusive focus
            root = self
            while root.parent: root = root.parent
            for w in root.get_focusable_widgets():
                w.is_focused = False
            self.is_focused = True
    
    def blur(self):
        self.is_focused = False
        self.is_captured = False
        
    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_absolute_rect(self):
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
        pass

    def get_focusable_widgets(self):
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

        # Coordinate check for performance and containment
        # (Optional: check if mouse is inside absolute rect before passing to children)

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


class FocusManager:
    """Manages spatial UI navigation across the Widget tree."""
    def __init__(self, root_view):
        self.root = root_view

    def navigate(self, direction):
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
        """Draws a red outline around focused, blue around captured, and yellow around focusable widgets."""
        all_focusable = self.root.get_focusable_widgets()
        for w in all_focusable:
            # Decide color priority: Captured > Focused > Focusable
            if getattr(w, 'is_captured', False):
                color = (0, 191, 255) # Deep Sky Blue
            elif w.is_focused:
                color = (255, 0, 0) # Red
            else:
                color = (255, 255, 0) # Yellow
            pygame.draw.rect(surface, color, w.get_absolute_rect(), 1)


# ========================
#  Base View Module
# ========================
class BaseView(Widget):
    """
    A view is a top-level widget starting at y=3 (24px grid aligned).
    Inherits from Widget to leverage grid scaling and child composition.
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
        The Bridge: Entry point from main.py.
        1. Stores game_state for the draw/logic cycle.
        2. Translates raw pixel mouse coordinates to grid coordinates.
        3. Calls self.handle_event() to begin tree traversal.
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
        """
        The Render Bridge: Entry point from main.py.
        1. Updates game_state for reference during drawing.
        2. Calls self.draw() to begin recursive tree rendering.
        """
        self.game_state = game_state
        self.draw(surface)
        
        if game_state.get('debug', False):
            self.focus_manager.draw_debug(surface)


# ========================
# Label
# ========================
class Label(Widget):
    def __init__(self, text="", x=0, y=0, color=None, role="Body", align="left", can_focus=False):
        font = styles.get_font(role)
        # Convert pixel metrics to grid units for the bounding box
        w = (font.get_width(text) / GRID_SIZE) if font else 2
        h = (font.effective_h / GRID_SIZE) if font else 1.5
        
        super().__init__(x, y, w, h)
        self.text = text
        self.color = color or styles.get_color("fg")
        self.role = role
        self.align = align
        self.can_focus = can_focus
        
    def _draw_self(self, surface, abs_rect):
        if self.can_focus:
            # Draw highlight block for focused/hovered labels (e.g. in lists)
            if self.is_focused or getattr(self, 'hovered', False):
                bg = styles.get_color("accent") if self.is_focused else styles.get_color("select")
                pygame.draw.rect(surface, bg, abs_rect)

        font = styles.get_font(self.role)
        if not font: return
        dx = abs_rect.x
        if self.align == "center": dx -= self.rect.w // 2
        elif self.align == "right": dx -= self.rect.w
        
        # Color logic
        if self.is_focused:
            col = styles.get_color("panel") # Inverted
        elif getattr(self, 'hovered', False):
            col = styles.get_color("accent") # Intermediate
        else:
            col = self.color
            
        font.draw(surface, self.text, dx, abs_rect.y + abs_rect.h, col)


# ========================
#  ░░Row Item░░░░░░           
# ========================
class RowItem(Widget):
    """
    A widget that represents a row in a list.
    Can be Hovered.
    Padding defines highlight area.
    """
    def __init__(self, x=0, y=0, w=2, h=2, text="", callback=None, padding=1):
        super().__init__(x, y, w, h, padding=0)
        self.text_padding = padding * GRID_SIZE
        self.text = text
        self.callback = callback
        self.can_focus = True
        self.hovered = False
        
    def _draw_self(self, surface, abs_rect):
        if self.is_focused:
            bg = styles.get_color("accent")
            fg = styles.get_color("panel")
        elif self.hovered:
            bg = styles.get_color("select")
            fg = styles.get_color("accent")
        else:
            bg = styles.get_color("panel")
            fg = styles.get_color("fg")
            
        pygame.draw.rect(surface, bg, abs_rect)
        
        font = styles.get_font("Body")
        if font:
            font.draw(surface, self.text, abs_rect.x + self.text_padding, abs_rect.y + abs_rect.h - self.text_padding/2, fg)

    def on_event(self, event, mx, my):
        abs_rect = self.get_absolute_rect()
        
        # Keyboard submit
        if self.is_focused and event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            if self.callback: self.callback()
            return True
            
        was_hovered = self.hovered
        self.hovered = abs_rect.collidepoint(mx, my)
        
        if self.hovered and not self.is_focused and event.type == pygame.MOUSEMOTION:
            self.focus()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.focus()
            if self.callback: self.callback()
            return True
        return False


# ========================
class Button(Widget):
    def __init__(self, text="", x=0, y=0, w=None, h=None, 
                 callback=None, role="Body", o_padding=0, 
                 i_padding=0.25, icon=None, border=True):
        font = styles.get_font(role)
        
        # Calculate dimensions
        if w is None:
            if text:
                w = (font.get_width(text)/GRID_SIZE + i_padding * 2 if font else 4)
            elif icon:
                w = icon.get_width()/GRID_SIZE + i_padding * 2
            else:
                w = 4
                
        if h is None:
            if text:
                h = (font.effective_h/GRID_SIZE + i_padding * 2 if font else 2)
            elif icon:
                h = icon.get_height()/GRID_SIZE + i_padding * 2
            else:
                h = 2

        super().__init__(x - i_padding,
                         y - i_padding,
                         w,
                         h,
                         padding=o_padding)
        self.text = text
        self.callback = callback
        self.role = role
        self.icon = icon
        self.border = border
        self.hovered = False
        self.is_pressed = False
        self.i_padding = i_padding
        self.o_padding = o_padding
        self.can_focus = True
        self.has_shadow = True

    def _draw_self(self, surface, abs_rect):
        # Color logic
        if self.is_focused:
            bg = styles.get_color("accent")
            fg = styles.get_color("panel")
        elif self.hovered or self.is_pressed:
            bg = styles.get_color("select")
            fg = styles.get_color("accent")
        else:
            bg = styles.get_color("panel")
            fg = styles.get_color("accent")

        pygame.draw.rect(surface, bg, abs_rect)
        
        if self.border:
            border_col = styles.get_color("header") if self.is_focused else styles.get_color("accent")
            pygame.draw.rect(surface, border_col, abs_rect, 1)
        
        # Center Icon
        if self.icon:
            ix = abs_rect.x + (abs_rect.w - self.icon.get_width()) // 2
            iy = abs_rect.y + (abs_rect.h - self.icon.get_height()) // 2
            surface.blit(self.icon, (ix, iy))
        
        # Draw Text if present
        font = styles.get_font(self.role)
        if font and self.text:
            tx = abs_rect.x + (abs_rect.w - font.get_width(self.text)) // 2
            ty = abs_rect.y + self.i_padding*GRID_SIZE + font.effective_h
            font.draw(surface, self.text, tx, ty, fg)

    def on_event(self, event, mx, my):
        # Keyboard Activation
        if self.is_focused and event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            if self.callback: self.callback()
            return True
        
        self.hovered = self.get_absolute_rect().collidepoint(mx, my)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.focus()
                self.is_pressed = True
                if self.callback: self.callback()
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
            
        return False


# ========================
#  | Panel |             |
# ========================
class Panel(Widget):
    def __init__(self, x=0, y=0, w=60, h=30, title=None, titles=None, children=None):
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
        
        # Top Border with Gaps
        font = styles.get_font("H2")
        curr_x = x
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
                
                # Draw border segment before title
                line_w = 4
                pygame.draw.line(surface, styles.get_color("dim"), (curr_x, y), (curr_x + line_w, y))
                curr_x += line_w
                
                if font:
                    if is_active and is_tab:
                        # Draw a solid background block for the active tab (8px above baseline)
                        pygame.draw.rect(surface, styles.get_color("accent"), (curr_x, y - 8, tw + 4, 15))
                        font.draw(surface, t_text, curr_x + 2, y + 4, styles.get_color("panel"))
                    else:
                        font.draw(surface, t_text, curr_x + 2, y + 4, t_col)
                
                curr_x += tw + 4
            
            # Final line segment
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
#                  │
# Scroll content   █
#                  │
# ========================
class ScrollContainer(Widget):
    """A container that clips children and allows vertical scrolling."""
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
        super().add_child(child)
        # Dynamic auto-resize of content height
        if child.rect.bottom > self.content_h:
            self.content_h = child.rect.bottom + 4

    def get_focusable_widgets(self):
        """Only exposes children to the FocusManager if this container is captured."""
        if not self.visible: return []
        
        widgets = []
        if self.can_focus:
            widgets.append(self)
            
        # Hide children from global search unless we have explicitly 'entered' this container
        if self.is_captured:
            for child in self.children:
                widgets.extend(child.get_focusable_widgets())
        return widgets

    def _draw_self(self, surface, abs_rect):
        if self.content_h <= self.rect.h: return
        
        # Scrollbar track
        tx = abs_rect.right - self.scrollbar_w
        pygame.draw.rect(surface, (10, 10, 10), (tx, abs_rect.y, self.scrollbar_w, abs_rect.h))
        
        # Proportional Thumb
        ratio = self.rect.h / self.content_h
        thumb_h = max(8, int(self.rect.h * ratio))
        thumb_y = abs_rect.y + int((self.scroll_offset / self.content_h) * self.rect.h)
        pygame.draw.rect(surface, self.thumb_color, (tx, thumb_y, self.scrollbar_w, thumb_h))

    def handle_event(self, event, mx, my):
        consumed = super().handle_event(event, mx, my)
        
        if not consumed and event.type == pygame.KEYDOWN:
            # Check if any immediate child is focused
            focused_child_idx = next((i for i, child in enumerate(self.children) if child.is_focused), -1)
            
            if focused_child_idx != -1:
                if event.key == pygame.K_DOWN:
                    self.children[focused_child_idx].blur()
                    n = len(self.children)
                    nxt = (focused_child_idx + 1) % n
                    while not self.children[nxt].can_focus and nxt != focused_child_idx:
                        nxt = (nxt + 1) % n
                    self.children[nxt].focus()
                    
                    # Ensure visible
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
                    
                    # Ensure visible
                    child_rect = self.children[nxt].rect
                    if child_rect.top < self.scroll_offset:
                        self.scroll_offset = max(0, child_rect.top - self.padding)
                    elif child_rect.bottom > self.scroll_offset + self.rect.h:
                        self.scroll_offset = child_rect.bottom - self.rect.h + self.padding
                    return True

        return consumed

    def on_event(self, event, mx, my):
        # Keyboard capture toggle
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.is_captured = not self.is_captured
                if self.is_captured:
                    # Focus first focusable child
                    all_c = self.get_focusable_widgets()
                    if all_c:
                        # Skip self (which is at index 0)
                        if len(all_c) > 1: all_c[1].focus()
                return True
            if event.key == pygame.K_ESCAPE and self.is_captured:
                self.is_captured = False
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button in [4, 5]: # Scroll wheel
            if event.button == 4: # Scroll Up
                self.scroll_offset = max(0, self.scroll_offset - 16)
                return True
            if event.button == 5: # Scroll Down
                self.scroll_offset = min(self.content_h - self.rect.h, self.scroll_offset + 16)
                return True
        return False


# ========================
# Slider:  -----█---
# ========================
class Slider(Widget):
    """
    A horizontal slider widget for adjusting numerical values.
    Supports an 'on_change' callback that triggers during interaction.
    """
    def __init__(self, x=0, y=0, w=10, val_min=0, val_max=100, current=50, on_change=None, **kwargs):
        super().__init__(x, y, w, 2, **kwargs)
        self.min = val_min
        self.max = val_max
        self.current = current
        self.dragging = False
        self.can_focus = True
        self.on_change = on_change

    def _draw_self(self, surface, abs_rect):
        y_mid = abs_rect.y + 8
        # Axis line: stop 1px before edge to stay inside
        pygame.draw.line(surface, styles.get_color("dim"), (abs_rect.x, y_mid), (abs_rect.right - 1, y_mid), 2)
        
        # Proportional Handle (inset 4px from each side to stay within bounds)
        inset = 4
        track_w = abs_rect.w - (inset * 2)
        pos_x = abs_rect.x + inset + int(((self.current - self.min) / (self.max - self.min)) * track_w)
        handle_rect = pygame.Rect(pos_x - 4, abs_rect.y + 4, 8, 8) # Smaller square handle
        
        h_col = styles.get_color("accent")
        if self.is_captured: h_col = (255, 255, 255)
        elif self.is_focused: h_col = styles.get_color("header")
        
        pygame.draw.rect(surface, h_col, handle_rect)
        
        if self.dragging or self.is_focused or self.is_captured:
            # Value Tooltip
            font = styles.get_font("Small")
            if font:
                txt = str(int(self.current))
                font.draw(surface, txt, pos_x - 4, abs_rect.y, styles.get_color("fg"))

    def on_event(self, event, mx, my):
        abs_rect = self.get_absolute_rect()
        
        # Keyboard Control
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.is_captured = not self.is_captured
                return True
                
        if self.is_captured and event.type == pygame.KEYDOWN:
            step = (self.max - self.min) / 20 # 5% steps
            if event.key == pygame.K_LEFT:
                self.current = max(self.min, self.current - step)
                if self.on_change: self.on_change(self.current)
                return True
            if event.key == pygame.K_RIGHT:
                self.current = min(self.max, self.current + step)
                if self.on_change: self.on_change(self.current)
                return True
            if event.key == pygame.K_ESCAPE:
                self.is_captured = False
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(mx, my):
                self.focus()
                self.dragging = True
                self._update_val(mx, abs_rect)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_val(mx, abs_rect)
            return True
        return False

    def _update_val(self, mx, abs_rect):
        inset = 4
        track_w = max(1, abs_rect.w - (inset * 2))
        rel_x = max(0, min(track_w, mx - (abs_rect.x + inset)))
        self.current = self.min + (rel_x / track_w) * (self.max - self.min)
        if self.on_change: self.on_change(self.current)


# ========================
#  | Dropdown ▼ | 
# ========================
class Dropdown(Widget):
    """
    A modal dropdown menu widget for selecting from a list of options.
    Toggling the dropdown adds a modal overlay to the screen.
    """
    def __init__(self, x=0, y=0, w=10, options=None, current_idx=0, on_change=None, **kwargs):
        super().__init__(x, y, w, 2, padding=0, **kwargs)
        self.options = options if options is not None else []
        self.current_idx = current_idx
        self.is_open = False
        self.has_shadow = True
        self.can_focus = True
        self.on_change = on_change

    def _draw_self(self, surface, abs_rect):
        pygame.draw.rect(surface, styles.get_color("textbox_bg"), abs_rect)
        col = styles.get_color("accent") if (self.is_focused or self.is_open) else styles.get_color("dim")
        pygame.draw.rect(surface, col, abs_rect, 1)
        
        font = styles.get_font("Body")
        if font:
            txt = str(self.options[self.current_idx])
            font.draw(surface, txt, abs_rect.x + 4, abs_rect.y + 12, styles.get_color("fg"))
        
        # Static Arrow for now
        pygame.draw.polygon(surface, styles.get_color("accent"), 
                            [(abs_rect.right - 12, abs_rect.y + 4), 
                             (abs_rect.right - 4, abs_rect.y + 4), 
                             (abs_rect.right - 8, abs_rect.y + 12)])
        
        if self.is_open:
            # Capture current state for overlay
            def draw_overlay(surf):
                list_h = min(8, len(self.options)) * 16
                list_rect = pygame.Rect(abs_rect.x, abs_rect.bottom, abs_rect.w, list_h)
                
                # Check bounds to avoid drawing off screen? (Optional polish)
                
                pygame.draw.rect(surf, styles.get_color("panel"), list_rect)
                pygame.draw.rect(surf, styles.get_color("accent"), list_rect, 1)
                
                for i, opt in enumerate(self.options[:8]):
                    opt_y = list_rect.y + i * 16
                    opt_inner_rect = pygame.Rect(list_rect.x + 1, opt_y + 1, list_rect.w - 2, 14)
                    
                    if font:
                        if i == self.current_idx:
                            # Inverted highlight for the selected option
                            pygame.draw.rect(surf, styles.get_color("accent"), opt_inner_rect)
                            col = styles.get_color("panel")
                        else:
                            col = styles.get_color("fg")
                            
                        font.draw(surf, str(opt), list_rect.x + 4, opt_y + 12, col)
            
            overlays.add(draw_overlay)

    def on_event(self, event, mx, my):
        # Keyboard Logic
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.is_open = not self.is_open
                self.is_captured = self.is_open
                return True
            if self.is_open:
                if event.key == pygame.K_UP:
                    self.current_idx = (self.current_idx - 1) % len(self.options)
                    if self.on_change: self.on_change(self.options[self.current_idx])
                    return True
                if event.key == pygame.K_DOWN:
                    self.current_idx = (self.current_idx + 1) % len(self.options)
                    if self.on_change: self.on_change(self.options[self.current_idx])
                    return True
                if event.key == pygame.K_ESCAPE:
                    self.is_open = False
                    self.is_captured = False
                    return True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            if abs_rect.collidepoint(mx, my):
                self.focus()
                self.is_open = not self.is_open
                self.is_captured = self.is_open
                return True
            if self.is_open:
                # Check clicks in list
                list_h = min(8, len(self.options)) * 16
                if abs_rect.x <= mx <= abs_rect.right and abs_rect.bottom <= my <= abs_rect.bottom + list_h:
                    idx = (my - abs_rect.bottom) // 16
                    if idx < len(self.options):
                        self.current_idx = idx
                        self.is_open = False
                        self.is_captured = False
                        if self.on_change: self.on_change(self.options[self.current_idx])
                        return True
            self.is_open = False
            self.is_captured = False
        
        # If open, consume all events to behave modally
        if self.is_open:
            return True
        return False


# ========================
#  | Text Field_ |
# ========================
class TextField(Widget):
    """
    An interactive text input widget.
    Requires 'capture' (Enter/Click) to handle keyboard input.
    """
    def __init__(self, x=0, y=0, w=10, text="", on_change=None, role="Body", **kwargs):
        super().__init__(x, y, w, 2, **kwargs)
        self.text = text
        self.role = role
        self.cursor_visible = True
        self.last_blink = 0
        self.can_focus = True
        self.hovered = False
        self.on_change = on_change

    def _draw_self(self, surface, abs_rect):
        pygame.draw.rect(surface, styles.get_color("textbox_bg"), abs_rect)
        
        # Color based on capture/focus
        col = styles.get_color("accent") if (self.is_focused or self.is_captured) else styles.get_color("dim")
        pygame.draw.rect(surface, col, abs_rect, 1)
        
        font = styles.get_font(self.role)
        if font:
            display_text = self.text
            if self.is_captured and (pygame.time.get_ticks() // 500) % 2 == 0:
                display_text += "_"
            font.draw(surface, display_text, abs_rect.x + 4, abs_rect.y + 12, styles.get_color("fg"))

    def on_event(self, event, mx, my):
        abs_rect = self.get_absolute_rect()
        
        # Hover detection for visual cues (if needed, but not forcing focus)
        self.hovered = abs_rect.collidepoint(mx, my)
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(mx, my):
                self.focus()
                self.is_captured = True
                return True
            else:
                self.is_captured = False
                return False
                
        # Toggle capture
        if self.is_focused and not self.is_captured and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.is_captured = True
                return True
                
        # Type into field
        if self.is_captured and event.type == pygame.KEYDOWN:
            old_text = self.text
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.is_captured = False
            else:
                if len(event.unicode) > 0 and ord(event.unicode[0]) >= 32:
                    self.text += event.unicode
                    
            if self.text != old_text and self.on_change:
                self.on_change(self.text)
            return True
            
        return False


# ========================
#  | Panel | Stack |     |
# ========================
class PanelStack(Widget):
    def __init__(self, x=0, y=0, w=60, h=30, panels=None, **kwargs):
        super().__init__(x, y, w, h, **kwargs)
        self.panels = [] # list of {"view": Widget, "name": str}
        self.active_idx = 0
        self.clip_children = False
        
        # Process initial panels
        if panels:
            for p in panels:
                # Support both old mapping format and direct Widgets
                view = p.get("view") if isinstance(p, dict) else p
                name = p.get("name") if isinstance(p, dict) else self._get_panel_name(view)
                if view:
                    self.add_panel(view, name=name)
                    
        self._sync_active_panel()

    def _get_panel_name(self, view):
        """Extracts a display name from a Panel's primary title or object type."""
        # Check if it was a Panel with a title
        if isinstance(view, Panel) and hasattr(view, '_orig_title') and view._orig_title:
            return view._orig_title
        if hasattr(view, 'titles') and view.titles:
            # Avoid picking up already-injected tabs
            return view.titles[0].get("text", "PAGE")
        return view.__class__.__name__

    def add_panel(self, view, name=None):
        if name is None:
            name = self._get_panel_name(view)
        
        # Store original title for Panels to avoid re-extraction loops
        if isinstance(view, Panel) and not hasattr(view, '_orig_title'):
             view._orig_title = name

        view.visible = (len(self.panels) == self.active_idx)
        self.panels.append({"view": view, "name": name})
        
        # Smart sizing behavior
        if self.rect.w == 0 and view.rect.w > 0: self.rect.w = view.rect.w
        if self.rect.h == 0 and view.rect.h > 0: self.rect.h = view.rect.h
        
        if self.rect.w > 0 and view.rect.w == 0: view.rect.w = self.rect.w
        if self.rect.h > 0 and view.rect.h == 0: view.rect.h = self.rect.h

        self.add_child(view)
        self._sync_active_panel()

    def set_panel_name(self, index_or_view, new_name):
        """Dyanmically update a tab's name."""
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
        # Update visibility
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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            # Check for clicks in the title/panel area (top border segment)
            if abs_rect.y <= my <= abs_rect.y + 16:
                font = styles.get_font("H2")
                
                curr_x = abs_rect.x
                for i, entry in enumerate(self.panels):
                    name = entry["name"]
                    tw = font.get_width(name) if font else 40
                    if tw == 0: tw = 40
                    
                    # Match the 4px line_w start offset + 4px total padding in _draw_self
                    if curr_x + 4 <= mx <= curr_x + 4 + tw + 4:
                        self.active_idx = i
                        self._sync_active_panel()
                        return True
                    curr_x += 4 + tw + 4 # Total horizontal span
        return False


