import pygame
import os

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
        for cb in self._items:
            cb(surface)
        self._items = []

overlays = OverlayManager()

# ========================
# Widget 
# ========================
class Widget:
    def __init__(self, x=0, y=0, w=32, h=32, padding=0):
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
        self.clip_children = False

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
        if not self.visible:
            return False
            
        # Global Focus Traversal (Intercept TAB at root or container level)
        # Note: Ideally this should be handled by a UIManager, but we inject here for simplicity in Phase 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
             # Only the root widget or a container processing the event bubble should handle this
             # We can't easily distinguish 'root', so individual widgets shouldn't consume Tab 
             # unless they are the active container. 
             # Simpler Approach: If this widget has no parent, it acts as the focus controller.
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

        for child in reversed(self.children):
            if child.handle_event(event, mx, my):
                return True
                
        # If we reach here and it was a click on the root, blur all
        if self.parent is None and event.type == pygame.MOUSEBUTTONDOWN:
            for w in self.get_focusable_widgets():
                w.blur()

        return self._handle_self(event, mx, my)

    def _handle_self(self, event, mx, my):
        return False


# ========================
# Label
# ========================
class Label(Widget):
    def __init__(self, text="", x=0, y=0, color=None, role="Body", align="left", padding=0):
        font = styles.get_font(role)
        w = font.get_width(text) if font else 0
        h = font.effective_h if font else 12
        super().__init__(x, y, w, h)
        self.text = text
        self.color = color if color else styles.get_color("fg")
        self.role = role
        self.align = align
        self.padding = padding

    def _draw_self(self, surface, abs_rect):
        font = styles.get_font(self.role)
        if not font: return
        dx = abs_rect.x
        if self.align == "center": dx -= self.rect.w // 2
        elif self.align == "right": dx -= self.rect.w
        font.draw(surface, self.text, dx, abs_rect.y + abs_rect.h, self.color)


# ========================
#  ░░Row Item░░░░░░           
# ========================
class RowItem(Widget):
    def __init__(self, x=0, y=0, w=16, h=16, text="", callback=None, padding=8):
        super().__init__(x, y, w, h, padding=0)
        self.text = text
        self.callback = callback
        self.can_focus = True
        self.hovered = False
        self.padding = padding
        
    def _draw_self(self, surface, abs_rect):
        bg = styles.get_color("select") if (self.hovered or self.is_focused) else styles.get_color("panel")
        if self.hovered or self.is_focused:
             pygame.draw.rect(surface, bg, abs_rect)
        
        font = styles.get_font("Body")
        if font:
            col = styles.get_color("accent") if (self.hovered or self.is_focused) else styles.get_color("fg")
            font.draw(surface, self.text, abs_rect.x + self.padding, abs_rect.y + self.padding/2, col)

    def _handle_self(self, event, mx, my):
        abs_rect = self.get_absolute_rect()
        self.hovered = abs_rect.collidepoint(mx, my)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.focus()
            if self.callback: self.callback()
            return True
        return False


# ========================
#      | Button |
# ========================
class Button(Widget):
    def __init__(self, text="", x=0, y=0, w=None, h=None, callback=None, role="Body", o_padding=0, i_padding=2, icon=None, border=True):
        font = styles.get_font(role)
        
        # Calculate dimensions
        if w is None:
            if text:
                w = (font.get_width(text) + i_padding * 2 if font else 32)
            elif icon:
                w = icon.get_width() + i_padding * 2
            else:
                w = 32
                
        if h is None:
            if text:
                h = (font.effective_h + i_padding * 2 if font else 16)
            elif icon:
                h = icon.get_height() + i_padding * 2
            else:
                h = 16

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

    def _draw_self(self, surface, abs_rect):
        # Visual color base
        bg_color = styles.get_color("select") if (self.hovered or self.is_pressed) else styles.get_color("panel")
        pygame.draw.rect(surface, bg_color, abs_rect)
        
        if self.border:
            # Highlight border if focused else normal accent
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
            ty = abs_rect.y + self.i_padding + font.effective_h
            font.draw(surface, self.text, tx, ty, styles.get_color("fg"))

    def _handle_self(self, event, mx, my):
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
    def __init__(self, x=0, y=0, w=480, h=240, title=None, titles=None):
        super().__init__(x, y, w, h, padding=4)
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
            for t_data in self.titles:
                t_text = t_data.get("text", "")
                t_col = t_data.get("color", styles.get_color("accent"))
                tw = font.get_width(t_text) if font else 0
                
                # Gap segment
                gap_start = curr_x + 4
                pygame.draw.line(surface, styles.get_color("dim"), (curr_x, y), (gap_start, y))
                
                if font:
                    font.draw(surface, t_text, gap_start + 2, y + 5, t_col)
                
                curr_x = gap_start + tw + 4
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
    def __init__(self, x=0, y=0, w=240, h=144, content_h=None):
        super().__init__(x, y, w, h, padding=0)
        self.content_h = content_h if content_h is not None else 0
        self.scroll_offset = 0
        self.scrollbar_w = 4
        self.thumb_color = styles.get_color("dim")
        self.clip_children = True

    def add_child(self, child):
        super().add_child(child)
        # Dynamic auto-resize of content height
        if child.rect.bottom > self.content_h:
            self.content_h = child.rect.bottom + 4

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: # Scroll Up
                self.scroll_offset = max(0, self.scroll_offset - 16)
                return True
            if event.button == 5: # Scroll Down
                self.scroll_offset = min(self.content_h - self.rect.h, self.scroll_offset + 16)
                return True
        return super().handle_event(event, mx, my)


# ========================
# Slider:  -----█---
# ========================
class Slider(Widget):
    def __init__(self, x, y, w, val_min=0, val_max=100, current=50):
        super().__init__(x, y, w, 16)
        self.min = val_min
        self.max = val_max
        self.current = current
        self.dragging = False
        self.can_focus = True

    def _draw_self(self, surface, abs_rect):
        y_mid = abs_rect.y + 8
        pygame.draw.line(surface, styles.get_color("dim"), (abs_rect.x, y_mid), (abs_rect.right, y_mid), 2)
        
        # Proportional Handle
        pos_x = abs_rect.x + int(((self.current - self.min) / (self.max - self.min)) * abs_rect.w)
        handle_rect = pygame.Rect(pos_x - 4, abs_rect.y + 2, 8, 12)
        
        h_col = styles.get_color("accent")
        if self.is_focused: h_col = styles.get_color("header")
        
        pygame.draw.rect(surface, h_col, handle_rect)
        
        if self.dragging or self.is_focused:
            # Value Tooltip
            font = styles.get_font("Small")
            if font:
                txt = str(int(self.current))
                font.draw(surface, txt, pos_x - 4, abs_rect.y, styles.get_color("fg"))

    def _handle_self(self, event, mx, my):
        abs_rect = self.get_absolute_rect()
        
        # Keyboard Control
        if self.is_focused and event.type == pygame.KEYDOWN:
            step = (self.max - self.min) / 20 # 5% steps
            if event.key == pygame.K_LEFT:
                self.current = max(self.min, self.current - step)
                return True
            if event.key == pygame.K_RIGHT:
                self.current = min(self.max, self.current + step)
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
        rel_x = max(0, min(abs_rect.w, mx - abs_rect.x))
        self.current = self.min + (rel_x / abs_rect.w) * (self.max - self.min)


# ========================
#  | Dropdown ▼ | 
# ========================
class Dropdown(Widget):
    def __init__(self, x, y, w, options, current_idx=0):
        super().__init__(x, y, w, 16, padding=0)
        self.options = options
        self.current_idx = current_idx
        self.is_open = False
        self.has_shadow = True
        self.can_focus = True

    def _draw_self(self, surface, abs_rect):
        pygame.draw.rect(surface, styles.get_color("textbox_bg"), abs_rect)
        col = styles.get_color("accent") if self.is_focused else styles.get_color("dim")
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
                    if font:
                        col = styles.get_color("accent") if i == self.current_idx else styles.get_color("fg")
                        font.draw(surf, str(opt), list_rect.x + 4, opt_y + 12, col)
            
            overlays.add(draw_overlay)

    def _handle_self(self, event, mx, my):
        # Keyboard Logic
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.is_open = not self.is_open
                return True
            if self.is_open:
                if event.key == pygame.K_UP:
                    self.current_idx = (self.current_idx - 1) % len(self.options)
                    return True
                if event.key == pygame.K_DOWN:
                    self.current_idx = (self.current_idx + 1) % len(self.options)
                    return True
                if event.key == pygame.K_ESCAPE:
                    self.is_open = False
                    return True
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            if abs_rect.collidepoint(mx, my):
                self.focus()
                self.is_open = not self.is_open
                return True
            if self.is_open:
                # Check clicks in list
                list_h = min(8, len(self.options)) * 16
                if abs_rect.x <= mx <= abs_rect.right and abs_rect.bottom <= my <= abs_rect.bottom + list_h:
                    idx = (my - abs_rect.bottom) // 16
                    if idx < len(self.options):
                        self.current_idx = idx
                        self.is_open = False
                        return True
            self.is_open = False
        return False


# ========================
#  | Text Field_ |
# ========================
class TextField(Widget):
    def __init__(self, x, y, w, text=""):
        super().__init__(x, y, w, 16)
        self.text = text
        self.cursor_visible = True
        self.last_blink = 0

    def _draw_self(self, surface, abs_rect):
        pygame.draw.rect(surface, styles.get_color("textbox_bg"), abs_rect)
        color = styles.get_color("accent") if self.is_focused else styles.get_color("dim")
        pygame.draw.rect(surface, color, abs_rect, 1)
        
        font = styles.get_font("Body")
        if font:
            display_text = self.text
            if self.is_focused and (pygame.time.get_ticks() // 500) % 2 == 0:
                display_text += "_"
            font.draw(surface, display_text, abs_rect.x + 4, abs_rect.y + 12, styles.get_color("fg"))

    def _handle_self(self, event, mx, my):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            if abs_rect.collidepoint(mx, my):
                self.is_focused = True
                return True
            else:
                self.is_focused = False
                return False
        if self.is_focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.is_focused = False
            else:
                if len(event.unicode) > 0 and ord(event.unicode[0]) >= 32:
                    self.text += event.unicode
            return True
        return False


# ========================
#  | Panel | Stack |     |
# ========================
class PanelStack(Widget):
    def __init__(self, x=0, y=0, w=480, h=240, panels=None):
        super().__init__(x, y, w, h, padding=0)
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
                # Inject Tabs into the Child Panel
                titles = []
                for j, e in enumerate(self.panels):
                    color = styles.get_color("accent") if j == self.active_idx else styles.get_color("dim")
                    titles.append({"text": e["name"], "color": color})
                view.titles = titles

    def _handle_self(self, event, mx, my):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            # Check for clicks in the title/panel area (top border segment)
            if abs_rect.y <= my <= abs_rect.y + 16:
                font = styles.get_font("H2")
                
                curr_x = abs_rect.x + 4 
                for i, entry in enumerate(self.panels):
                    name = entry["name"]
                    tw = font.get_width(name) if font else 40
                    if tw == 0: tw = 40
                    
                    if curr_x <= mx <= curr_x + tw + 4:
                        self.active_idx = i
                        self._sync_active_panel()
                        return True
                    curr_x += tw + 4 + 4 # Gap + Text + Gap
        return False
