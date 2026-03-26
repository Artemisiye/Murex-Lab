# ENGINE MODULATION SPECS

This document outlines the responsibilities and API structure for each module in the `retro-py` refactor.

---

# High Level Architecture

## 1. Engine Layer (`engine/`)

### `core.py` -> `MurexEngine`
**Responsibility**: The heartbeat of the application. Manages initialization, the main loop, and top-level state.
- `init(v_width, v_height, scale)`: Setup Pygame and the virtual buffer.
- `run()`: The `while True` loop.
- `_handle_events()`: Routes events to `InputManager` and the active view.
- `_render()`: Drawing sequence (Clear -> View Draw -> Overlays -> Post-Process -> Flip).

### `state_manager.py` -> `SessionState` & `WorldState`
**Responsibility**: Separation of transient session data from persistent gameplay data.

#### `SessionState` (Transient)
- Tracks the current application state: `active_view_id`, `hovered_tab`, `debug_mode`.
- This state is reset on application launch.

#### `WorldState` (Persistent)
- Tracks the actual gameplay progress: `player_inventory`, `map_manager`, `minion_list`.
- Interfaces with the `modules/` in `murex_lab`.
- **Reactive Saving**: Provides interface methods that trigger persistence upon state change.
    - `modify_inventory(action_fn)`: Wraps an inventory change and triggers a save.
    - `update_player_pos(x, y)`: Updates position and periodically syncs to disk.
    - `save_all()`: Force a full synchronization of all modules.

### `config_manager.py` (Existing)
- Tracks user-level preferences (Meta-data): `ui_scale`, `crt_enabled`, `font_face`.
- Persists across multiple "World" saves.

### `asset_manager.py` -> `AssetManager`
**Responsibility**: Handling disk-to-memory resources for all visual and auditory assets.
- `fonts`: Dictionary of `SpriteFont` objects.
- `sprites`: Dictionary of `pygame.Surface` objects.
- `sounds`: Dictionary of `pygame.mixer.Sound` objects.
- `load_sprite_font(role, name)`: Loads and caches a font for a specific UI role.
- `get_sprite(name, path)`: Loads and returns a cached sprite image.
- `get_sound(name, path)`: Loads and returns a cached sound effect.
- `clear_cache()`: Flushes memory for hot-reloading or scene transitions.

### `audio_manager.py` -> `AudioManager`
**Responsibility**: Global playback control.
- `play_sfx(name)`: Plays a sound effect with optional volume/panning.
- `play_bgm(name)`: Handles music looping and cross-fading.

### `data_registry.py` -> `DataRegistry`
**Responsibility**: Centralized access to static game definitions.
- Loads and parses `items.json`, `blueprints.json`, and `monsters.json`.
- Provides lookup methods (e.g., `get_blueprint(id)`).

### `post_processor.py` -> `PostProcessor` & `Effects`
**Responsibility**: Modular framebuffer manipulation pipeline.
- **`PostProcessor`**: Container for effect passes.
    - `add_effect(effect)`: Registers a new shader/effect.
    - `apply(buffer_surface, screen_surface)`: Executes the pipeline.
    - `start_transition(type, duration)`: Triggers a view-transition effect (Fade, Slide, etc.).
- **`CrtEffect`**: Handles scanlines, aperture grille, and shadow mask.
- **`BloomEffect`**: Handles phosphor halation and additive glow.

### `input_manager.py` -> `InputManager`
**Responsibility**: Context-sensitive semantic input mapping.
- **Input Modes**: Supports different mapping profiles (`MENU`, `MAP`, `COMBAT`).
- `set_mode(mode)`: Switches the active mapping profile.
- `process(event)`: Translates raw keys into semantic actions based on the current mode.
    - *Example*: In `MAP` mode, `K_UP` -> `ACT_MOVE_NORTH`. In `MENU` mode, `K_UP` -> `ACT_UI_UP`.

#### Mode-Aware Logic
- **Combat Mode**: Re-maps inputs for tactical actions and can explicitly block view navigation (disabling `TAB` switching).
- **Map Mode**: Directs directional inputs to the world movement system.

---

## 2. UI Layer (`ui/`)

### `__init__.py`
**Responsibility**: The "Packer". Exports all UI classes to simplify imports.
- `from .base import Widget, BaseView, overlays`
- `from .style import styles`
- `from .widgets import Label, Button, Slider, Dropdown, TextField`
- `from .containers import Panel, ScrollContainer, PanelStack`

### `base.py` -> Core Logic
**Responsibility**: Foundation for the entire widget tree.
- `Widget`: Base class for coordinates, clipping, and recursive drawing.
- `BaseView`: Interface for top-level screen modules.
- `FocusManager`: Handles 4-way spatial navigation.
- `OverlayManager`: Manages modal draws (dropdowns, tooltips).

### `style.py` -> `StyleManager`
**Responsibility**: Design System and Theming.
- `StyleManager`: Central registry for colors and font roles.
- `styles`: Global instance.

### `widgets.py` -> Actionable Elements
**Responsibility**: Atomic interactive components.
- `Label`, `Button`, `RowItem`, `Slider`, `TextField`, `Dropdown`.

### `containers.py` -> Structural Elements
**Responsibility**: Composition and layout management.
- `Panel`: Titled border container.
- `ScrollContainer`: Vertically scrollable viewport.
- `PanelStack`: Tab-based panel switcher.

---

## 3. Bootstrap Layer (`main.py`)

**Responsibility**: Minimal launcher.
- Initialize `MurexEngine`.
- Start the engine with `engine.run()`.


---

# Outline

## 1. Engine Modules (`engine/`)

### `core.py`
```python
class MurexEngine:
    def __init__(self, v_width: int, v_height: int, scale: int):
        """Initializes Pygame, screen, buffers, and system managers."""
    def run(self):
        """Main game loop."""
    def _process_input(self):
        """Centralized event processing and routing."""
    def _update(self, dt: float):
        """Update game state and view logic."""
    def _render(self):
        """Sequence drawing from buffer to screen with post-processing."""
```

### `state_manager.py`
```python
class SessionState:
    def __init__(self):
        self.active_view: str = "MAP"
        self.debug: bool = False
        self.input_mode: str = "MENU"

class WorldState:
    def __init__(self, data_path: str):
        """Initializes and loads inventory, map, and minions."""
        self.active_combat: CombatEngine = None
    def modify_inventory(self, action_fn: callable):
        """Executes action, updates local state, and triggers reactive save."""
    def update_player_pos(self, x: int, y: int):
        """Updates position and syncs to disk periodically or on trigger."""
    def save_all(self):
        """Trigger JSON persistence for all sub-modules."""
```

### `asset_manager.py`
```python
class AssetManager:
    def __init__(self, font_dir: str):
        """Scans and prepares font registry."""
    def get_font(self, role: str) -> SpriteFont:
        """Returns the font associated with a specific UI role (H1, Body, etc)."""
    def get_sprite(self, name: str, path: str = None) -> pygame.Surface:
        """Loads and returns a cached sprite image."""
    def get_sound(self, name: str, path: str = None) -> pygame.mixer.Sound:
        """Loads and returns a cached sound effect."""
    def clear_cache(self):
        """Flushes memory for hot-reloading or scene transitions."""
```

### `audio_manager.py`
```python
class AudioManager:
    def play_sfx(self, name: str): ...
    def play_bgm(self, name: str, loop: bool = True): ...
```

### `data_registry.py`
```python
class DataRegistry:
    def __init__(self, data_path: str):
        """Loads blueprints, items, and monster data."""
    def get_item(self, id: str) -> dict: ...
    def get_blueprint(self, id: str) -> dict: ...
```

### `post_processor.py`
```python
class Effect:
    def apply(self, surface: pygame.Surface):
        """Base interface for a post-process pass."""

class CrtEffect(Effect):
    def __init__(self, width, height, scale): ...
    def apply(self, surface): ...
    def _draw_scanlines(self, surface): ...
    def _draw_mask(self, surface): ...

class BloomEffect(Effect):
    def __init__(self, alpha, offset): ...
    def apply(self, surface, buffer): ...

class PostProcessor:
    def __init__(self, width: int, height: int, scale: int):
        self.effects: list[Effect] = []
    def add_effect(self, effect: Effect): ...
    def apply(self, buffer: pygame.Surface, screen: pygame.Surface, settings: dict):
        """Sequentially applies all effects to the buffer before blitting to screen."""
```

### `input_manager.py`
```python
class InputManager:
    def __init__(self):
        self.mode: str = "MENU"
    def set_mode(self, mode: str): ...
    def translate(self, event: pygame.event.Event) -> str:
        """Converts raw keys to semantic action strings based on mode."""
```

---

## 2. UI Modules (`ui/`)

### `__init__.py`
```python
# Re-exports:
# from .base import Widget, BaseView, overlays
# from .style import styles
# from .widgets import Label, Button, RowItem, Slider, TextField, Dropdown
# from .containers import Panel, ScrollContainer, PanelStack
```

### `base.py`
```python
class OverlayManager:
    def __init__(self):
        self._items = []
    def add(self, callback): ...
    def draw(self, surface): ...

class Widget:
    def __init__(self, x, y, w, h, padding, children, raw_coords): ...
    def focus(self): ...
    def blur(self): ...
    def add_child(self, child): ...
    def get_absolute_rect(self): ...
    def draw(self, surface): ...
    def _draw_self(self, surface, abs_rect): ...
    def get_focusable_widgets(self): ...
    def handle_event(self, event, mx, my): ...
    def on_event(self, event, mx, my): ...

class FocusManager:
    def __init__(self, root_view): ...
    def navigate(self, direction): ...
    def draw_debug(self, surface): ...

class BaseView(Widget):
    def __init__(self, **kwargs): ...
    def dispatch_view_event(self, event, game_state): ...
    def draw_view(self, surface, game_state): ...
```

### `style.py`
```python
class StyleManager:
    def __init__(self):
        self.fonts: dict = {}
        self.colors: dict = {}
    def set_font(self, role, font_obj): ...
    def get_font(self, role): ...
    def get_color(self, name): ...
```

### `widgets.py`
```python
class Label(Widget):
    def __init__(self, text, x, y, color, role, align, can_focus): ...
    def _draw_self(self, surface, abs_rect): ...

class RowItem(Widget):
    def __init__(self, x, y, w, h, text, callback, padding): ...
    def _draw_self(self, surface, abs_rect): ...
    def on_event(self, event, mx, my): ...

class Button(Widget):
    def __init__(self, text, x, y, w, h, callback, role, o_padding, i_padding, icon, border): ...
    def _draw_self(self, surface, abs_rect): ...
    def on_event(self, event, mx, my): ...

class Slider(Widget):
    def __init__(self, x, y, w, val_min, val_max, current, on_change, **kwargs): ...
    def _draw_self(self, surface, abs_rect): ...
    def _update_val(self, mx, abs_rect): ...
    def on_event(self, event, mx, my): ...

class TextField(Widget):
    def __init__(self, x, y, w, text, on_change, role, **kwargs): ...
    def _draw_self(self, surface, abs_rect): ...
    def on_event(self, event, mx, my): ...

class Dropdown(Widget):
    def __init__(self, x, y, w, options, current_idx, on_change, **kwargs): ...
    def _draw_self(self, surface, abs_rect): ...
    def on_event(self, event, mx, my): ...
```

### `containers.py`
```python
class Panel(Widget):
    def __init__(self, x, y, w, h, title, titles, children): ...
    def _draw_self(self, surface, abs_rect): ...

class ScrollContainer(Widget):
    def __init__(self, x, y, w, h): ...
    def add_child(self, child): ...
    def get_focusable_widgets(self): ...
    def _draw_self(self, surface, abs_rect): ...
    def handle_event(self, event, mx, my): ...
    def on_event(self, event, mx, my): ...

class PanelStack(Widget):
    def __init__(self, x, y, w, h, panels, **kwargs): ...
    def _get_panel_name(self, view): ...
    def add_panel(self, view, name): ...
    def set_panel_name(self, index_or_view, new_name): ...
    def _sync_active_panel(self): ...
    def on_event(self, event, mx, my): ...
```
