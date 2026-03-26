import pygame
from .style import styles
from .base import Widget, overlays, GRID_SIZE

# ========================
# Label
# ========================
class Label(Widget):
    """
    A static text widget. Can optionally display a highlight block when 
    focused if 'can_focus' is True.
    """
    def __init__(self, text="", x=0, y=0, color=None, role="Body", align="left", can_focus=False):
        """
        Args:
            text: String to display.
            color: Text color (defaults to theme 'fg').
            role: SpriteFont role to use (e.g., 'H1', 'Small').
            align: Text alignment ('left', 'center', 'right').
            can_focus: If True, this label acts as a selectable list item.
        """
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
    A interactive list item widget that occupies a full row width.
    Commonly used in settings or inventory menus.
    """
    def __init__(self, x=0, y=0, w=2, h=2, text="", callback=None, padding=1):
        """
        Args:
            text: Label text for the row.
            callback: Function to call when the row is clicked or activated.
        """
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
            
        self.hovered = abs_rect.collidepoint(mx, my)
        
        if self.hovered and not self.is_focused and event.type == pygame.MOUSEMOTION:
            self.focus()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            self.focus()
            if self.callback: self.callback()
            return True
        return False


# ========================
#      | Button |
# ========================
class Button(Widget):
    """
    A standard pressable button widget. Supports text, icons, and automated 
    dimension calculation based on content.
    """
    def __init__(self, text="", x=0, y=0, w=None, h=None, 
                 callback=None, role="Body", o_padding=0, 
                 i_padding=0.25, icon=None, border=True):
        """
        Args:
            text: Button label text.
            w, h: Fixed dimensions (optional). If None, calculated from text/icon.
            callback: Function to call when activated.
            icon: Optional Pygame Surface to draw in the center.
            i_padding: Inner padding between text/icon and the button border.
            o_padding: Outer padding for the widget bounds.
        """
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
# Slider:  -----█---
# ========================
class Slider(Widget):
    """
    A horizontal slider widget for adjusting numerical values.
    Supports keyboard capture (Enter to lock cursor to slider).
    """
    def __init__(self, x=0, y=0, w=10, val_min=0, val_max=100, current=50, on_change=None, **kwargs):
        """
        Args:
            val_min, val_max: Range of possible values.
            current: Initial value.
            on_change: Callback triggered with the new value on every update.
        """
        super().__init__(x, y, w, 2, **kwargs)
        self.min = val_min
        self.max = val_max
        self.current = current
        self.dragging = False
        self.can_focus = True
        self.on_change = on_change

    def _draw_self(self, surface, abs_rect):
        y_mid = abs_rect.y + 8
        pygame.draw.line(surface, styles.get_color("dim"), (abs_rect.x, y_mid), (abs_rect.right - 1, y_mid), 2)
        
        inset = 4
        track_w = abs_rect.w - (inset * 2)
        pos_x = abs_rect.x + inset + int(((self.current - self.min) / (self.max - self.min)) * track_w)
        handle_rect = pygame.Rect(pos_x - 4, abs_rect.y + 4, 8, 8)
        
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
        """Internal method to map mouse X to the value range."""
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
    A list-selection widget that expands into a modal overlay.
    """
    # TODO: 
    # - Add scroll support for long lists
    # - Modulate into `draw_list_overlay`, `on_list_event`
    # - Replace arrow with sprite
    def __init__(self, x=0, y=0, w=10, options=None, current_idx=0, on_change=None, **kwargs):
        """
        Args:
            options: List of strings or items to select from.
            current_idx: Initial selection index.
            on_change: Callback triggered with the new selected item.
        """
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
        
        # Draw Arrow
        pygame.draw.polygon(surface, styles.get_color("accent"), 
                            [(abs_rect.right - 12, abs_rect.y + 4), 
                             (abs_rect.right - 4, abs_rect.y + 4), 
                             (abs_rect.right - 8, abs_rect.y + 12)])
        
        if self.is_open:
            # Dropdown menu overlay
            def draw_overlay(surf):
                list_h = min(8, len(self.options)) * 16
                list_rect = pygame.Rect(abs_rect.x, abs_rect.bottom, abs_rect.w, list_h)
                
                pygame.draw.rect(surf, styles.get_color("panel"), list_rect)
                pygame.draw.rect(surf, styles.get_color("accent"), list_rect, 1)
                
                for i, opt in enumerate(self.options[:8]):
                    opt_y = list_rect.y + i * 16
                    opt_inner_rect = pygame.Rect(list_rect.x + 1, opt_y + 1, list_rect.w - 2, 14)
                    
                    if font:
                        if i == self.current_idx:
                            # Inverted highlight
                            pygame.draw.rect(surf, styles.get_color("accent"), opt_inner_rect)
                            col = styles.get_color("panel")
                        else:
                            col = styles.get_color("fg")
                            
                        font.draw(surf, str(opt), list_rect.x + 4, opt_y + 12, col)
            
            overlays.add(draw_overlay)

    def on_event(self, event, mx, my):
        # Keyboard Selection logic
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
        
        if self.is_open:
            return True
        return False


# ========================
#  | Text Input_ |
# ========================
class TextField(Widget):
    """
    An interactive text input widget. Supports focus-based capturing.
    """
    def __init__(self, x=0, y=0, w=10, text="", on_change=None, role="Body", **kwargs):
        """
        Args:
            text: Initial text.
            on_change: Callback triggered on every keystroke.
        """
        super().__init__(x, y, w, 2, **kwargs)
        self.text = text
        self.role = role
        self.can_focus = True
        self.on_change = on_change

    def _draw_self(self, surface, abs_rect):
        pygame.draw.rect(surface, styles.get_color("textbox_bg"), abs_rect)
        
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
