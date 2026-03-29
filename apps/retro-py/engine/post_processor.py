import pygame

class Effect:
    """Base class for all screen-space post-processing effects."""
    def __init__(self):
        self.enabled = True

    def apply(self, surface, scale):
        """Override this to modify the surface or blit overlays."""
        pass


class CrtEffect(Effect):
    """
    Simulation of CRT phosphor bleed and scanlines.
    Refactored from legacy main.py logic.
    """
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.overlay = None
        self.last_params = None

    def apply(self, screen, scale):
        if not self.settings.get("enabled", True):
            return
            
        # Check for cache invalidation (scale change or settings shift)
        params = (screen.get_size(), self.settings.get("scanline_alpha"), self.settings.get("grille_alpha"))
        if params != self.last_params:
            self._generate_overlay(screen.get_size(), scale)
            self.last_params = params
            
        if self.overlay:
            screen.blit(self.overlay, (0, 0))

    def _generate_overlay(self, size, scale):
        w, h = size
        self.overlay = pygame.Surface(size, pygame.SRCALPHA)
        
        # 1. Scanlines
        s_alpha = self.settings.get("scanline_alpha", 40)
        for y in range(0, h, scale):
            pygame.draw.line(self.overlay, (10, 10, 40, s_alpha), (0, y), (w, y))
            if y + 1 < h:
                pygame.draw.line(self.overlay, (10, 10, 40, int(s_alpha * 0.4)), (0, y + 1), (w, y + 1))

        # 2. Aperture Grille
        g_alpha = self.settings.get("grille_alpha", 15)
        for x in range(0, w, 2):
            if (x // 2) % 3 == 0:
                pygame.draw.line(self.overlay, (0, 0, 0, g_alpha), (x, 0), (x, h))


class BloomEffect(Effect):
    """Additive bloom/glow effect (Phosphor Halation)."""
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def apply(self, screen, scale):
        alpha = self.settings.get("bloom_alpha", 0)
        if alpha <= 0: return
        
        # Capture screen, scale down/up to blur (cheap bloom)
        # In a real engine we'd use shaders, but this fits the retro heritage
        bloom_glow = pygame.transform.scale(screen, screen.get_size())
        bloom_glow.set_alpha(alpha)
        offset = self.settings.get("bloom_offset", 1)
        screen.blit(bloom_glow, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)


class PostProcessor:
    """Manages a stack of screen-space effects."""
    def __init__(self):
        self.effects = []

    def add_effect(self, effect):
        self.effects.append(effect)

    def process(self, screen, scale):
        """Applies all enabled effects in order."""
        for effect in self.effects:
            if effect.enabled:
                effect.apply(screen, scale)
