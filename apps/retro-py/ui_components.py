import pygame
import os

class StyleManager:
    def __init__(self):
        self.fonts = {} # Role -> SpriteFont object
        self.colors = {
            "bg": (15, 13, 11),
            "panel": (25, 22, 19),
            "accent": (230, 200, 100),
            "dim": (100, 90, 80),
            "fg": (220, 210, 190),
            "header": (230, 200, 100)
        }

    def set_font(self, role, font_obj):
        self.fonts[role] = font_obj

    def get_font(self, role):
        return self.fonts.get(role)

    def get_color(self, name):
        return self.colors.get(name, (255, 255, 255))

# Global instance
styles = StyleManager()

class Widget:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_absolute_rect(self):
        if self.parent:
            parent_rect = self.parent.get_absolute_rect()
            return pygame.Rect(parent_rect.x + self.rect.x, parent_rect.y + self.rect.y, self.rect.w, self.rect.h)
        return self.rect.copy()

    def draw(self, surface):
        if not self.visible:
            return
        
        abs_rect = self.get_absolute_rect()
        self._draw_self(surface, abs_rect)
        
        for child in self.children:
            child.draw(surface)

    def _draw_self(self, surface, abs_rect):
        pass

    def handle_event(self, event, mx, my):
        if not self.visible:
            return False
            
        # Handle children first (top-most/last added first)
        for child in reversed(self.children):
            if child.handle_event(event, mx, my):
                return True
                
        return self._handle_self(event, mx, my)

    def _handle_self(self, event, mx, my):
        return False

class Label(Widget):
    def __init__(self, font=None, text="", x=0, y=0, color=None, align="left", role="Body"):
        if font is None:
            font = styles.get_font(role)
        
        # Width/Height will be determined by font
        w = font.get_width(text) if font else 0
        h = font.metadata.get("effective_h", 12) if font else 12
        super().__init__(x, y, w, h)
        self.font = font
        self.text = text
        self.color = color if color else styles.get_color("fg")
        self.align = align

    def _draw_self(self, surface, abs_rect):
        if not self.font: return
        draw_x = abs_rect.x
        if self.align == "center":
            draw_x -= self.rect.w // 2
        elif self.align == "right":
            draw_x -= self.rect.w
            
        # SpriteFont.draw(surface, text, x, y, color)
        # y is baseline in SpriteFont
        # We'll use abs_rect.bottom or center it?
        # Let's assume input y is the baseline for now to match main.py logic
        self.font.draw(surface, self.text, draw_x, abs_rect.y + abs_rect.h, self.color)

class Panel(Widget):
    def __init__(self, x, y, w, h, title=None, font=None, 
                 bg_color=None, border_color=None, title_color=None, title_role="H2"):
        super().__init__(x, y, w, h)
        self.title = title
        self.font = font if font else styles.get_font(title_role)
        self.bg_color = bg_color if bg_color else styles.get_color("panel")
        self.border_color = border_color if border_color else styles.get_color("dim")
        self.title_color = title_color if title_color else styles.get_color("accent")
        self.padding = 5

    def _draw_self(self, surface, abs_rect):
        # Draw background
        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, abs_rect)
        
        # Draw border
        x, y, w, h = abs_rect
        
        # Left, Bottom, Right
        pygame.draw.line(surface, self.border_color, (x, y), (x, y + h)) # Left
        pygame.draw.line(surface, self.border_color, (x, y + h), (x + w, y + h)) # Bottom
        pygame.draw.line(surface, self.border_color, (x + w, y + h), (x + w, y)) # Right
        
        # Top border with optional Title Gap
        if self.title and self.font:
            title_w = self.font.get_width(self.title)
            gap_start = 8 # Offset from left
            gap_end = gap_start + title_w + 4
            
            # Segment 1
            pygame.draw.line(surface, self.border_color, (x, y), (x + gap_start, y))
            # Segment 2
            pygame.draw.line(surface, self.border_color, (x + gap_end, y), (x + w, y))
            
            # Draw Title (centered vertically on the line)
            # We want the middle of the text height to be at y
            # Baseline = y + (cap_h / 2)
            cap_h = self.font.metadata.get("cap_h", 8)
            self.font.draw(surface, self.title, x + gap_start + 2, y + (cap_h // 2), self.title_color)
        else:
            pygame.draw.line(surface, self.border_color, (x, y), (x + w, y))

class Button(Widget):
    def __init__(self, font=None, text="", x=0, y=0, w=None, h=None, callback=None,
                 bg_color=(40, 35, 30), border_color=None, text_color=None, role="Body"):
        if font is None:
            font = styles.get_font(role)
        
        if w is None: w = font.get_width(text) + 10 if font else 60
        if h is None: h = font.metadata.get("effective_h", 12) + 6 if font else 18
        super().__init__(x, y, w, h)
        self.font = font
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.border_color = border_color if border_color else styles.get_color("accent")
        self.text_color = text_color if text_color else styles.get_color("fg")
        self.hovered = False
        self.pressed = False

    def _draw_self(self, surface, abs_rect):
        color = self.bg_color
        if self.hovered:
            # Slightly lighter
            color = tuple(min(c + 20, 255) for c in self.bg_color)
        
        pygame.draw.rect(surface, color, abs_rect)
        if self.hovered or self.pressed:
            pygame.draw.rect(surface, self.border_color, abs_rect, 1)
            
        # Draw label
        text_w = self.font.get_width(self.text)
        text_x = abs_rect.x + (abs_rect.w - text_w) // 2
        cap_h = self.font.metadata.get("cap_h", 8)
        text_y = abs_rect.y + (abs_rect.h + cap_h) // 2
        self.font.draw(surface, self.text, text_x, text_y, self.text_color)

    def _handle_self(self, event, mx, my):
        abs_rect = self.get_absolute_rect()
        was_hovered = self.hovered
        self.hovered = abs_rect.collidepoint(mx, my)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.hovered:
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
            
        return was_hovered != self.hovered
