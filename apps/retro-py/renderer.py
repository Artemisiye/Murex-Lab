import pygame
import json
import os

class SpriteFont:
    def __init__(self, json_path):
        self.dir = os.path.dirname(json_path)
        with open(json_path, "r") as f:
            self.metadata = json.load(f)
        
        image_path = os.path.join(self.dir, os.path.basename(json_path).replace(".json", ".png"))
        self.image = pygame.image.load(image_path).convert_alpha()
        self.chars = self.metadata["chars"]

    def draw(self, surface, text, x, y, color=None):
        """
        Draws text aligned to a baseline.
        y is the baseline coordinate.
        """
        current_x = x
        for char in text:
            if char == " ":
                current_x += 4 # Standard space
                continue
            
            if char in self.chars:
                data = self.chars[char]
                glyph_rect = pygame.Rect(data["x"], data["y"], data["w"], data["h"])
                
                # Baseline correction:
                # data["base_y"] is the distance from baseline UP to glyph top.
                # So pixel top = baseline_y - base_y
                draw_y = y - data["base_y"]
                
                if color:
                    char_surf = self.image.subsurface(glyph_rect).copy()
                    temp = pygame.Surface(char_surf.get_size()).convert_alpha()
                    temp.fill(color)
                    char_surf.blit(temp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    surface.blit(char_surf, (current_x, draw_y))
                else:
                    surface.blit(self.image, (current_x, draw_y), glyph_rect)
                
                current_x += data["adv"]

    def get_width(self, text):
        w = 0
        for char in text:
            if char == " ":
                w += 4
            elif char in self.chars:
                w += self.chars[char]["adv"]
        return w
