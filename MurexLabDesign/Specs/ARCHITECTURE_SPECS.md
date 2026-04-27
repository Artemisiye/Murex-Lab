# Murex Lab Architecture (Cleanroom Blueprint)

This document is a **design-complete skeleton** for the refactor. It defines module structure, classes, methods, DTOs, response shapes, and helper contracts **without implementation logic**. It is intended to be ripe for static review and verification before porting code.

---

## 0) Scope and Intent

- We are porting all existing code into the new architecture.
- The goal is **decoupling** and **reshaping modules** while preserving behavior.
- **Facade + HTTP adapter** is the core integration strategy.
- The spec should be sufficient for static debugging (symbol existence, signatures, DTOs, contract shapes).

---

## 1) System Roles and Naming

### Folders (runtime apps)
- `apps/murex-engine` ? server implementation (local simulation)
- `apps/retro-client` ? pygame retro UI client
- `apps/web-client` ? Flask UI client

### Python Packages (underscore modules)
- `murex_engine/` inside `apps/murex-engine`
- `retro_client/` inside `apps/retro-client`
- `web_client/` inside `apps/web-client`

### Shared package (data-only)
- `src/murex_common/`
  - `dto.py` (request/response DTOs)
  - `events.py` (event types)
  - `errors.py` (error codes/envelopes)
  - `helpers.py` (envelope helpers and event constructors)

Constraint: **no gameplay logic** in `murex_common`.

Decision: DTOs are **dataclasses** for rapid prototyping.

---

## 2) Directory Map (Target Layout)

```
/ (repo root)
|-- apps/
|   |-- murex-engine/
|   |   |-- murex_engine/
|   |       |-- __init__.py
|   |       |-- facade.py
|   |       |-- state.py
|   |       |-- bootstrap.py
|   |       |-- services/
|   |       |   |-- world.py
|   |       |   |-- region.py
|   |       |   |-- inventory.py
|   |       |   |-- crafting.py
|   |       |   |-- combat.py
|   |       |   |-- minions.py
|   |       |-- repositories/
|   |       |   |-- saves.py
|   |       |   |-- data_registry.py
|   |       |-- adapters/
|   |           |-- http.py  (optional)
|   |
|   |-- retro-client/
|   |   |-- retro_client/
|   |       |-- main.py
|   |       |-- client/
|   |       |   |-- engine.py
|   |       |   |-- config_manager.py
|   |       |   |-- asset_manager.py
|   |       |   |-- data_registry.py
|   |       |   |-- state_manager.py
|   |       |   |-- input_manager.py
|   |       |   |-- post_processor.py
|   |       |   |-- renderer.py
|   |       |-- views/
|   |       |-- ui/
|   |
|   |-- web-client/
|       |-- web_client/
|           |-- app.py
|           |-- routes/
|           |-- templates/
|           |-- static/
|
|-- src/
|   |-- murex_common/
|       |-- dto.py
|       |-- events.py
|       |-- errors.py
|       |-- helpers.py
```

Note: during porting, legacy code may still live in current locations. This map describes the target structure.

---

## 3) Core Architecture Overview

```
+----------------------+       +-------------------------+
|   murex-engine       |<----->|  Clients (retro/web)    |
|  GameSession facade  |       |  render + input         |
+----------------------+       +-------------------------+
```

- **murex-engine** is authoritative and owns all state changes.
- **retro-client** calls the facade directly (in-process).
- **web-client** uses an HTTP adapter that maps to the same facade.

---

## 4) Shared Contracts (murex_common)

### 4.1 Response Envelope (standard)
```python
@dataclass
class ResponseEnvelope[T]:
    """Standard response wrapper for all commands and queries."""
    ok: bool
    data: T | None
    events: list[Event]
    error: ErrorDetail | None
```

### 4.2 Errors
```python
class ErrorCode(Enum):
    """Canonical error codes for server responses."""
    NOT_FOUND = "not_found"
    INVALID_INPUT = "invalid_input"
    FORBIDDEN = "forbidden"
    CONFLICT = "conflict"
    INTERNAL = "internal"

@dataclass
class ErrorDetail:
    """Human-readable error detail with optional context."""
    code: ErrorCode
    message: str
    details: dict | None = None
```

### 4.3 Events
```python
class EventType(Enum):
    """Domain events emitted by facade commands."""
    ENTERED_LAB = "EnteredLab"
    BACKPACK_STASHED = "BackpackStashed"
    REGION_ENTERED = "RegionEntered"
    REGION_EXITED = "RegionExited"
    COMBAT_STARTED = "CombatStarted"
    COMBAT_ENDED = "CombatEnded"
    INVENTORY_CHANGED = "InventoryChanged"
    MINION_ENERGY_CHANGED = "MinionEnergyChanged"

@dataclass
class Event:
    """Typed event with payload for UI updates."""
    type: EventType
    data: dict
```

### 4.4 Helper functions
```python
def ok(data: T | None = None, events: list[Event] | None = None) -> ResponseEnvelope[T]:
    """Create a success envelope with optional data and events."""


def fail(code: ErrorCode, message: str, details: dict | None = None) -> ResponseEnvelope[None]:
    """Create a failure envelope with structured error detail."""


def event(evt_type: EventType, data: dict | None = None) -> Event:
    """Create a typed event with optional payload."""
```

### 4.5 DTOs (complete list)
```python
# Core / status
@dataclass
class StatusDTO:
    """Server status snapshot."""
    status: str
    version: str

# Direction / position
@dataclass
class DirectionDTO:
    """Cardinal direction for movement."""
    direction: Literal["up", "down", "left", "right"]

@dataclass
class PositionDTO:
    """Grid coordinate."""
    x: int
    y: int

# Inventory / items
@dataclass
class InventoryItemDTO:
    """Inventory line item."""
    key: str
    item_id: str
    quantity: int
    name: str
    type: str
    stats: dict

@dataclass
class InventoryDTO:
    """Inventory snapshot (vault or backpack)."""
    gold: int
    items: list[InventoryItemDTO]
    is_backpack: bool
    energy: int

@dataclass
class AddItemDTO:
    """Debug or internal add-item request."""
    item_id: str
    quantity: int = 1

@dataclass
class RemoveItemDTO:
    """Debug or internal remove-item request."""
    inv_key: str
    quantity: int = 1

# Blueprints / crafting
@dataclass
class BlueprintDTO:
    """Blueprint list entry."""
    id: str
    name: str
    type: str
    station_id: str

@dataclass
class BlueprintSlotDTO:
    """Blueprint slot definition."""
    id: str
    label: str
    required: bool
    required_tags: list[str]

@dataclass
class BlueprintDetailDTO:
    """Blueprint details with slots and base stats."""
    id: str
    name: str
    slots: list[BlueprintSlotDTO]
    base_stats: dict

@dataclass
class ComponentDTO:
    """Valid component entry for a blueprint slot."""
    id: str
    inv_key: str
    name: str
    quantity: int
    stats: dict

@dataclass
class CraftRequestDTO:
    """Crafting request payload."""
    blueprint_id: str
    components: dict[str, str]  # slot_id -> inv_key

@dataclass
class CraftPreviewDTO:
    """Preview response payload for crafting."""
    success: bool
    stats: dict

@dataclass
class CraftResultDTO:
    """Crafting result payload."""
    success: bool
    item_name: str | None
    message: str

# World / map
@dataclass
class MapCellDTO:
    """World map cell snapshot."""
    x: int
    y: int
    type: str
    discovered: bool

@dataclass
class MapDTO:
    """Full world map snapshot."""
    size: int
    player_pos: PositionDTO
    cells: list[MapCellDTO]

# Region
@dataclass
class RegionNodeDTO:
    """Regional node entry."""
    id: str
    x: int
    y: int
    tool_required: str | None

@dataclass
class RegionEntityDTO:
    """Regional entity entry."""
    id: str
    x: int
    y: int

@dataclass
class RegionDTO:
    """Regional map snapshot."""
    size: int
    player_pos: PositionDTO
    nodes: list[RegionNodeDTO]
    entities: list[RegionEntityDTO]

@dataclass
class MoveResultDTO:
    """Move result with discovery changes."""
    player_pos: PositionDTO
    revealed_cells: list[PositionDTO]
    energy: int
    entered_lab: bool | None = None

@dataclass
class InteractResultDTO:
    """Interact result for world/region."""
    redirect: str | None
    region_data: RegionDTO | None
    loot: list[str] | None

@dataclass
class RegionMoveResultDTO:
    """Region move result with updated region data."""
    region_data: RegionDTO
    energy: int

@dataclass
class HarvestResultDTO:
    """Harvest result payload."""
    loot: list[str]
    region_data: RegionDTO
    energy: int

@dataclass
class HuntResultDTO:
    """Hunt result payload."""
    loot: list[str]
    combat_started: bool
    region_data: RegionDTO
    energy: int

# Minions
@dataclass
class MinionDTO:
    """Minion snapshot."""
    id: str
    name: str
    level: int
    current_energy: int
    status: str

# Combat
@dataclass
class CombatEntityDTO:
    """Combat entity snapshot."""
    id: str
    name: str
    stats: dict
    status: str

@dataclass
class CombatStateDTO:
    """Combat state snapshot."""
    entities: list[CombatEntityDTO]
    active_unit_id: str | None
    is_finished: bool
    winner: str | None

@dataclass
class CombatTickDTO:
    """Combat tick response payload."""
    ready_unit: str | None
    state: CombatStateDTO

@dataclass
class CombatActDTO:
    """Combat action request payload."""
    skill_id: str
    target_id: str

@dataclass
class CombatResultDTO:
    """Combat action response payload."""
    results: dict
    state: CombatStateDTO
    rewards: dict | None

# Debug / tools
@dataclass
class DebugAddItemDTO:
    """Debug add-item payload."""
    item_id: str
    quantity: int

@dataclass
class DebugDataSyncDTO:
    """Debug data sync payload."""
    file_type: Literal["blueprints", "items"]
    payload: dict | None = None
```

---

## 5) murex-engine ? Module Architecture and Symbols

### 5.1 facade.py
```python
class GameSession:
    """Authoritative facade for commands and queries."""

    # Commands
    def move_player(self, dto: DirectionDTO) -> ResponseEnvelope[MoveResultDTO]:
        """Move the player in the world map."""

    def interact(self) -> ResponseEnvelope[InteractResultDTO]:
        """Interact with the current tile (enter region or open lab)."""

    def enter_region(self) -> ResponseEnvelope[RegionDTO]:
        """Enter a regional map if available."""

    def region_move(self, dto: DirectionDTO) -> ResponseEnvelope[RegionMoveResultDTO]:
        """Move within the regional map."""

    def harvest(self, pos: PositionDTO) -> ResponseEnvelope[HarvestResultDTO]:
        """Harvest a resource node at a position."""

    def hunt(self, pos: PositionDTO) -> ResponseEnvelope[HuntResultDTO]:
        """Hunt an entity at a position, possibly starting combat."""

    def craft_item(self, dto: CraftRequestDTO) -> ResponseEnvelope[CraftResultDTO]:
        """Craft an item using provided components."""

    def preview_craft(self, dto: CraftRequestDTO) -> ResponseEnvelope[CraftPreviewDTO]:
        """Preview crafting results without consuming items."""

    def combat_tick(self) -> ResponseEnvelope[CombatTickDTO]:
        """Advance the combat loop and return ready unit."""

    def combat_act(self, dto: CombatActDTO) -> ResponseEnvelope[CombatResultDTO]:
        """Execute a combat action."""

    # Queries
    def get_status(self) -> ResponseEnvelope[StatusDTO]:
        """Return server status and version."""

    def get_inventory(self) -> ResponseEnvelope[InventoryDTO]:
        """Return the active inventory snapshot."""

    def get_minions(self) -> ResponseEnvelope[list[MinionDTO]]:
        """Return the player's minion roster."""

    def get_blueprints(self) -> ResponseEnvelope[list[BlueprintDTO]]:
        """Return all blueprint list entries."""

    def get_blueprint_details(self, bp_id: str) -> ResponseEnvelope[BlueprintDetailDTO]:
        """Return blueprint details and slot definitions."""

    def get_valid_components(self, bp_id: str, slot_id: str) -> ResponseEnvelope[list[ComponentDTO]]:
        """Return valid components for a blueprint slot."""

    def get_debug_stations(self) -> ResponseEnvelope[list[str]]:
        """Return list of station ids used by blueprints."""

    def get_map_data(self) -> ResponseEnvelope[MapDTO]:
        """Return world map snapshot."""

    def get_region_data(self) -> ResponseEnvelope[RegionDTO | None]:
        """Return regional map snapshot if active."""

    def get_combat_state(self) -> ResponseEnvelope[CombatStateDTO | None]:
        """Return current combat snapshot if active."""

    # Debug
    def debug_clear_inventory(self) -> ResponseEnvelope[dict]:
        """Reset vault inventory to starting state."""

    def debug_clear_backpack(self) -> ResponseEnvelope[dict]:
        """Empty the backpack inventory."""

    def debug_add_item(self, dto: DebugAddItemDTO) -> ResponseEnvelope[dict]:
        """Add an item to the active inventory for debugging."""

    def debug_data_sync(self, file_type: str, payload: dict | None = None) -> ResponseEnvelope[dict]:
        """Read or write data files for debugging tools."""
```

Open questions:
- Should the facade be singleton or instantiated per session?
- Should commands return partial deltas only, or always include the updated snapshot for their domain?

### 5.2 state.py
```python
@dataclass
class GameState:
    """Authoritative state container for all subsystems."""
    world: WorldState
    region: RegionState | None
    inventory: InventoryState
    crafting: CraftingState
    combat: CombatState | None
    minions: MinionsState
```

### 5.3 services (behavioral modules)
```python
class WorldService:
    """World map navigation and discovery logic."""
    def move(self, state: GameState, dto: DirectionDTO) -> ResponseEnvelope[MoveResultDTO]:
        """Move on the world map and emit discovery events."""

    def interact(self, state: GameState) -> ResponseEnvelope[InteractResultDTO]:
        """Resolve interaction on current world tile."""

class RegionService:
    """Regional map interactions."""
    def enter(self, state: GameState) -> ResponseEnvelope[RegionDTO]:
        """Enter regional map for the current tile."""

    def move(self, state: GameState, dto: DirectionDTO) -> ResponseEnvelope[RegionMoveResultDTO]:
        """Move within the active regional map."""

    def harvest(self, state: GameState, pos: PositionDTO) -> ResponseEnvelope[HarvestResultDTO]:
        """Harvest a node at a position within the regional map."""

    def hunt(self, state: GameState, pos: PositionDTO) -> ResponseEnvelope[HuntResultDTO]:
        """Hunt an entity at a position within the regional map."""

class InventoryService:
    """Inventory routing and transfers between vault/backpack."""
    def get_active_inventory(self, state: GameState) -> InventoryState:
        """Return the active inventory based on player location."""

    def stash_backpack(self, state: GameState) -> int:
        """Transfer eligible backpack items to the vault and return count."""

    def add_item(self, state: GameState, dto: AddItemDTO) -> ResponseEnvelope[dict]:
        """Add an item to the active inventory."""

    def remove_item(self, state: GameState, dto: RemoveItemDTO) -> ResponseEnvelope[dict]:
        """Remove an item from the active inventory."""

class CraftingService:
    """Blueprint queries and crafting pipeline."""
    def get_blueprints(self, state: GameState) -> list[BlueprintDTO]:
        """Return list of available blueprints."""

    def preview(self, state: GameState, dto: CraftRequestDTO) -> ResponseEnvelope[CraftPreviewDTO]:
        """Preview crafting output without side effects."""

    def craft(self, state: GameState, dto: CraftRequestDTO) -> ResponseEnvelope[CraftResultDTO]:
        """Craft an item and consume components."""

class CombatService:
    """Combat loop orchestration."""
    def get_state(self, state: GameState) -> CombatStateDTO | None:
        """Return the current combat state if active."""

    def tick(self, state: GameState) -> ResponseEnvelope[CombatTickDTO]:
        """Advance combat and return the ready unit."""

    def act(self, state: GameState, dto: CombatActDTO) -> ResponseEnvelope[CombatResultDTO]:
        """Execute a combat action and resolve results."""

class MinionsService:
    """Minion roster and energy management."""
    def get_minions(self, state: GameState) -> list[MinionDTO]:
        """Return the player's minion roster."""

    def update_energy(self, state: GameState, delta: int) -> ResponseEnvelope[dict]:
        """Apply energy change to active minions."""
```

Open questions:
- Do we want services to be stateless functions or stateful objects?
- Should Region be modeled as a sub-state or a separate aggregate?

### 5.4 repositories
```python
class SaveRepository:
    """Persistence for save files."""
    def load_inventory(self) -> InventoryState: ...
    def save_inventory(self, state: InventoryState) -> None: ...
    def load_backpack(self) -> InventoryState: ...
    def save_backpack(self, state: InventoryState) -> None: ...
    def load_world(self) -> WorldState: ...
    def save_world(self, state: WorldState) -> None: ...

class DataRegistryRepository:
    """Static data file loading for items/blueprints."""
    def load_category(self, category_name: str, file_name: str | None = None) -> dict | list | None:
        """Load a JSON category and build a tag index."""

    def get(self, category: str, key: str | None = None, default: object | None = None) -> object | None:
        """Get a category or item by id."""

    def find(self, category: str, **kwargs: object) -> list[dict]:
        """Return items matching all provided filters."""

    def filter_by_tag(self, category: str, tag_prefix: str) -> list[dict]:
        """Return items with at least one tag matching the prefix."""

    def all(self, category: str) -> list:
        """Return all items in a category."""
```

---

## 6) HTTP Adapter (web-client)

The HTTP adapter is a thin translation layer over the facade. Endpoints map 1:1 to facade methods.

Decision: HTTP adapter always wraps responses into `{ok, events, data, error}` while making minimal changes needed for successful porting.

(Endpoint mapping table remains as previously defined.)

Open questions:
- Should HTTP adapter support batch commands to reduce chatter?

---

## 7) Client Interaction Model

retro-client (pygame)
- Sends commands to facade, renders from cached state.
- Per-frame render uses cached data; commands return deltas + events.

web-client (Flask)
- Each endpoint delegates to facade and returns the standardized envelope.

### 7.1 Update Model (Pragmatic Middle Ground)
- Command-driven updates (deltas + events)
- Periodic snapshots every 500-1000ms
- Dirty flags for inventory/map/combat
- Client controls UX (no forced tab switch)

### 7.2 retro-client ? Module Architecture and Symbols (full outline)

The retro-client is a **pygame UI runtime** that renders cached state and submits facade commands. It never owns authoritative gameplay state.

#### 7.2.1 retro_client/main.py
```python
def main() -> None:
    """Entry point for the retro client."""

def bootstrap_views(engine: RetroEngine) -> dict[str, BaseView]:
    """Create and return view instances keyed by tab id."""
```

#### 7.2.2 retro_client/client/engine.py
```python
class RetroEngine:
    """Retro UI runtime: input, rendering, and view orchestration."""

    def __init__(self, asset_root: str | None = None, data_root: str | None = None, save_dir: str | None = None) -> None:
        """Initialize pygame, managers, and runtime defaults."""

    def boot(self, title: str = "Murex Lab - Retro Engine") -> None:
        """Wake all managers in dependency order and open the window."""

    def run(self, views: dict[str, BaseView], tabs: list[str], on_hot_reload: Callable[[], None]) -> None:
        """Run the main loop with the given views and header tabs."""

    def handle_events(self, active_view: BaseView, tabs: list[str]) -> list[str]:
        """Poll pygame events and return high-level action strings."""

    def handle_action(self, action: str, active_view: BaseView, tabs: list[str]) -> bool:
        """Dispatch an action to the active view and return whether it was consumed."""

    def render(self, active_view: BaseView, tabs: list[str]) -> None:
        """Render the frame for the active view and UI chrome."""

    def set_scale(self, scale: int) -> None:
        """Apply pixel scaling to the display surface."""

    def toggle_debug(self) -> None:
        """Toggle legacy debug overlay."""

    def update_debug_overlay(self, active_view: BaseView) -> None:
        """Refresh debug overlay with world/mouse coordinates."""

    def _get_ram_usage(self) -> int:
        """Return current RAM usage in MB (best-effort)."""

    def _render_header(self, buffer: pygame.Surface, active_tab: str, tabs: list[str]) -> None:
        """Draw the global header with branding and tabs."""

    def _draw_debug_overlays(self, screen: pygame.Surface, scale: int, active_view: BaseView) -> None:
        """Draw debug overlays on the physical screen."""
```

#### 7.2.3 retro_client/client/input_manager.py
```python
class InputMode(Enum):
    """Input mapping mode for UI vs map navigation."""
    MENU = "menu"
    MAP = "map"

class InputManager:
    """Maps pygame events to action strings by mode."""

    def __init__(self) -> None:
        """Initialize mode and action maps."""

    def set_mode(self, mode: InputMode) -> None:
        """Set the active input mode."""

    def get_action(self, event: pygame.event.Event) -> str | None:
        """Translate a pygame event into an action string if mapped."""

    def handle_raw_event(self, event: pygame.event.Event) -> str | None:
        """Handle global shortcuts then return the mapped action, if any."""
```

#### 7.2.4 retro_client/client/asset_manager.py
```python
class AssetManager:
    """Centralized loader for images, JSON, and fonts."""

    def __init__(self, root_path: Path) -> None:
        """Initialize the asset manager with a root path."""

    def load_font(self, name: str, json_path: str) -> SpriteFont:
        """Load and cache a sprite font."""

    def load_fonts_from_dir(self, dir_path: str) -> None:
        """Batch load sprite fonts from a directory."""

    def setup_font_styles(self, user_fonts_config: dict) -> None:
        """Map font roles (H1, H2, Body, Small) to loaded fonts."""

    def load_sprite(self, name: str, sub_path: str) -> pygame.Surface:
        """Load and cache a sprite from the sprites directory."""

    def load_sprites_from_dir(self, dir_path: str, category: str = "") -> None:
        """Batch load sprites from a directory."""

    def get_sprite(self, name: str) -> pygame.Surface | None:
        """Return a cached sprite by name."""

    def load_image(self, name: str, full_path: str) -> pygame.Surface:
        """Load and cache an image from an absolute path."""

    def load_sound(self, name: str, sub_path: str) -> pygame.mixer.Sound:
        """Load and cache a sound asset."""

    def get_sound(self, name: str) -> pygame.mixer.Sound | None:
        """Return a cached sound by name."""

    def load_json(self, name: str, json_path: str) -> dict | None:
        """Load and cache a JSON data file."""

    def get_json(self, name: str) -> dict | None:
        """Return cached JSON by name."""

    def flush_cache(self, asset_type: str | None = None) -> None:
        """Clear cached assets by category or all."""
```

#### 7.2.5 retro_client/client/config_manager.py
```python
class ConfigManager:
    """Retro client configuration and user settings persistence."""

    DEFAULT_SETTINGS: dict

    def __init__(self, data_root: str) -> None:
        """Initialize configuration storage."""

    def get_settings_path(self) -> str:
        """Return absolute path to user_settings.json."""

    def load(self) -> bool:
        """Load user settings and merge with defaults."""

    def save(self) -> bool:
        """Persist current settings to disk."""

    def get(self, key: str, default: object | None = None) -> object | None:
        """Return a settings section by key."""
```

#### 7.2.6 retro_client/client/data_registry.py
```python
class DataRegistry:
    """Read-only registry for JSON data categories."""

    def __init__(self, data_root: str) -> None:
        """Initialize with the data root."""

    def load_category(self, category_name: str, file_name: str | None = None) -> dict | list | None:
        """Load a JSON category and build a tag index."""

    def get(self, category: str, key: str | None = None, default: object | None = None) -> object | None:
        """Get a category or item by id."""

    def find(self, category: str, **kwargs: object) -> list[dict]:
        """Return items matching all provided filters."""

    def filter_by_tag(self, category: str, tag_prefix: str) -> list[dict]:
        """Return items with at least one tag matching the prefix."""

    def all(self, category: str) -> list:
        """Return all items in a category."""
```

#### 7.2.7 retro_client/client/state_manager.py
```python
class GameStateManager:
    """Reactive data layer with world/session separation."""

    def __init__(self, save_dir: str) -> None:
        """Initialize state containers and save directory."""

    def load_world_data(self, file_name: str = "world_state.json") -> bool:
        """Load persistent world state from disk."""

    def save_world_data(self, file_name: str = "world_state.json") -> bool:
        """Persist world state to disk."""

    def get(self, key: str, default: object | None = None) -> object | None:
        """Resolve a key in session, logic, then world state."""

    def register_logic(self, key: str, manager_obj: object) -> None:
        """Bind a logic manager to the state manager."""

    def set_session(self, key: str, value: object) -> None:
        """Set a transient session value."""

    def set_world(self, key: str, value: object, autosave: bool = False) -> None:
        """Set persistent world value, optionally autosaving."""

    def update_world(self, data_dict: dict, autosave: bool = False) -> None:
        """Bulk update persistent world state."""

    def boot_game_logic(self, data_root: str) -> None:
        """Instantiate and register game logic managers."""

    def clear_session(self) -> None:
        """Clear transient session state."""
```
Note: This manager is transitional. It remains during porting, but should shrink as the facade becomes the authoritative state source.

#### 7.2.8 retro_client/client/post_processor.py
```python
class Effect:
    """Base class for screen-space effects."""
    def __init__(self) -> None:
        """Initialize effect state."""

    def apply(self, surface: pygame.Surface, scale: int) -> None:
        """Apply effect to the surface in-place."""

class CrtEffect(Effect):
    """CRT phosphor + scanline effect."""
    def __init__(self, settings: dict) -> None:
        """Initialize CRT settings and overlay cache."""

    def apply(self, screen: pygame.Surface, scale: int) -> None:
        """Apply CRT overlay if enabled."""

class BloomEffect(Effect):
    """Additive bloom/glow effect."""
    def __init__(self, settings: dict) -> None:
        """Initialize bloom settings."""

    def apply(self, screen: pygame.Surface, scale: int) -> None:
        """Apply bloom if enabled."""

class PostProcessor:
    """Manages a stack of screen-space effects."""

    def __init__(self) -> None:
        """Initialize effect list."""

    def add_effect(self, effect: Effect) -> None:
        """Register a post-processing effect."""

    def process(self, screen: pygame.Surface, scale: int) -> None:
        """Apply all enabled effects in order."""
```

#### 7.2.9 retro_client/client/renderer.py
```python
class SpriteFont:
    """Bitmap font renderer backed by sprite atlas and metadata."""

    def __init__(self, json_path: str) -> None:
        """Load font metadata and sprite atlas."""

    def draw(self, surface: pygame.Surface, text: str, x: int, y: int, color: tuple[int, int, int] | None = None) -> None:
        """Draw text aligned to a baseline."""

    def get_width(self, text: str) -> int:
        """Return rendered width for a string."""
```

#### 7.2.10 retro_client/ui/base.py
```python
class Widget:
    """Base UI widget with layout, input, and render hooks."""

    def __init__(self, rect: pygame.Rect) -> None:
        """Initialize widget geometry and state."""

    def render(self, surface: pygame.Surface) -> None:
        """Render self and children."""

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events; return True if consumed."""

    def add_child(self, child: Widget) -> None:
        """Attach a child widget."""
```

#### 7.2.11 retro_client/ui/widgets.py
```python
class Button(Widget):
    """Clickable button with text, focus, and optional shadow."""

    def __init__(self, rect: pygame.Rect, label: str, on_click: Callable[[], None],
                 has_shadow: bool = True, can_focus: bool = True) -> None:
        """Initialize button attributes."""

    def _draw_self(self, surface: pygame.Surface) -> None:
        """Render the button itself."""

class Panel(Widget):
    """Panel container with title and child widget support."""

    def __init__(self, rect: pygame.Rect, title: str) -> None:
        """Initialize panel layout and title."""

class PanelStack(Widget):
    """Single-visible panel stack."""

    def __init__(self, rect: pygame.Rect, panels: list[Panel]) -> None:
        """Initialize panel stack with a list of panels."""

    def set_active(self, index: int) -> None:
        """Activate the panel at index."""
```

#### 7.2.12 retro_client/views/base.py (target)
```python
class BaseView:
    """View contract for retro-client screens."""

    def __init__(self, engine: RetroEngine) -> None:
        """Bind the engine reference."""

    def render(self, surface: pygame.Surface) -> None:
        """Render the view."""

    def handle_action(self, action: str) -> bool:
        """Handle an engine action and return whether consumed."""

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Optional raw event handler for widget dispatch."""
```

#### 7.2.13 retro_client/views/map_view.py
```python
class MapTile:
    """Render-only tile definition for the world map."""
    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the map tile to the given rect."""

class RegionalMapTile:
    """Render-only tile definition for the regional map."""
    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the regional tile to the given rect."""

class WorldRegion:
    """Logic placeholder for regional gameplay state."""

class WorldMapWidget(Widget):
    """Widget that renders the world map inside a panel."""
    def render(self, surface: pygame.Surface) -> None:
        """Render the map using cached data."""

class RegionalMapWidget(Widget):
    """Widget that renders the regional map inside a panel."""
    def render(self, surface: pygame.Surface) -> None:
        """Render the regional map using cached data."""

class MapView(BaseView):
    """Map view with world + regional panels and navigation widgets."""

    def __init__(self, engine: RetroEngine) -> None:
        """Initialize panels, arrow buttons, and cached state."""

    def render(self, surface: pygame.Surface) -> None:
        """Render panels and map widgets."""

    def handle_action(self, action: str) -> bool:
        """Handle map actions (move, interact, enter region, back)."""

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Dispatch events to child widgets."""

    def interact(self) -> None:
        """Handle interaction on the current tile."""

    def set_panel(self, index: int) -> None:
        """Switch active panel."""
```

#### 7.2.14 retro_client/views/workshop_view.py
```python
class WorkshopView(BaseView):
    """Workshop UI for crafting and inventory operations."""

    def __init__(self, engine: RetroEngine) -> None:
        """Initialize workshop panels and widgets."""

    def render(self, surface: pygame.Surface) -> None:
        """Render workshop UI."""

    def handle_action(self, action: str) -> bool:
        """Handle workshop actions (craft, select, back)."""
```

#### 7.2.15 retro_client/views/inventory_view.py
```python
class InventoryView(BaseView):
    """Inventory UI for vault and backpack."""

    def __init__(self, engine: RetroEngine) -> None:
        """Initialize inventory widgets."""

    def render(self, surface: pygame.Surface) -> None:
        """Render inventory UI."""

    def handle_action(self, action: str) -> bool:
        """Handle inventory actions."""
```

#### 7.2.16 retro_client/views/minions_view.py
```python
class MinionsView(BaseView):
    """Minions UI and energy management."""

    def __init__(self, engine: RetroEngine) -> None:
        """Initialize minion widgets."""

    def render(self, surface: pygame.Surface) -> None:
        """Render minion UI."""

    def handle_action(self, action: str) -> bool:
        """Handle minion actions."""
```

#### 7.2.17 retro_client/views/settings_view.py
```python
class SettingsView(BaseView):
    """Settings UI for CRT/bloom and debug flags."""

    def __init__(self, engine: RetroEngine) -> None:
        """Initialize settings widgets."""

    def render(self, surface: pygame.Surface) -> None:
        """Render settings UI."""

    def handle_action(self, action: str) -> bool:
        """Handle settings actions."""
```

#### 7.2.18 retro_client/views/test_ui_view.py
```python
class TestUIView(BaseView):
    """Sandbox view for widget testing."""

    def __init__(self, engine: RetroEngine) -> None:
        """Initialize test widgets."""

    def render(self, surface: pygame.Surface) -> None:
        """Render test UI."""

    def handle_action(self, action: str) -> bool:
        """Handle test actions."""
```

Note: web-client outline will be added after retro-client review.

---

## 8) Subsystem-First Migration Plan

Phase 1 ? World/Region
- Move `world_map` + regional logic into murex-engine facade.
- Implement `move_player`, `interact`, `enter_region`, `region_move`, `harvest`, `hunt`.

Phase 2 ? Inventory/Crafting
- Facade owns inventory routing and `craft_item` / `preview_craft`.

Phase 3 ? Combat
- Facade wraps `CombatEngine` and exposes `combat_tick`, `combat_act`, `get_combat_state`.

Phase 4 ? Minions and Energy
- Minion roster/energy moves into facade; queries expose UI-ready state.

---

## 9) Non-Goals
- No multiplayer networking.
- No distributed server required for retro-client.
- HTTP adapter is optional and may stay local.
