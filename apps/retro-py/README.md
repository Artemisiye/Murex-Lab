Retro-Py: Murex Lab UI Runtime
=============================

Retro-Py is the dedicated retro-styled UI runtime for the Murex Lab game logic.
It is intentionally split from the gameplay layer so rendering/UI can evolve
independently of domain rules and data.

Goals
-----
- Provide a lightweight UI engine with strict separation of concerns.
- Render and navigate views while delegating gameplay rules to murex_lab.
- Keep assets, configs, and input mappings centralized and predictable.

High-Level Architecture
-----------------------
Gameplay (murex_lab) and UI (retro-py) are intentionally decoupled.

    +------------------+        +---------------------------+
    |  murex_lab       |<------>|  retro-py (UI runtime)     |
    |  Game Logic      |        |  MurexEngine + Views       |
    +------------------+        +---------------------------+

Within retro-py:

    main.py
      -> MurexEngine
           - ConfigManager      (user settings)
           - AssetManager       (fonts/sprites/data)
           - DataRegistry       (static data)
           - GameStateManager   (logic + state)
           - InputManager       (logical actions)
           - PostProcessor      (CRT/Bloom)
      -> Views (Map/Workshop/etc.)
           - Render UI via ui/ widgets
           - Use engine reference for state access

Core Components
---------------
- engine/core.py: MurexEngine game loop, rendering pipeline, input dispatch.
- engine/state_manager.py: Initializes and exposes game logic managers from murex_lab.
- engine/asset_manager.py: Loads fonts, sprites, sounds, and JSON data assets.
- engine/input_manager.py: Maps raw input to logical actions by mode.
- ui/: Widget library for panels, buttons, sliders, etc.
- views/: Screen-level views (Map, Workshop, Inventory, etc).

Entry Point
-----------
- apps/retro-py/main.py is the current entrypoint.
- Legacy main.py was retired; _main.py was renamed to main.py.

Input Flow
----------
- InputManager translates Pygame events into logical actions.
- MurexEngine selects the input mode by active tab.
- Views consume actions via handle_action(action, engine).

Rendering Flow
--------------
1) Engine clears the virtual buffer.
2) Active view renders via ui widgets.
3) Global header/tabs rendered by engine.
4) Overlays (dropdowns/tooltips) drawn.
5) Screen upscaled, debug overlay drawn (optional).
6) Post-processing (CRT/Bloom) applied.

Assets & Data
-------------
- assets/sprite-fonts: SpriteFont JSON + PNGs.
- assets/ui: UI sprite icons (e.g., D-pad arrows).
- assets/tiles/retro_map_tiles.json: Map tile palette and regional colors.

Hot Reload
----------
Press F2 to re-instantiate views during development.

Notes
-----
- Window resizing is intentionally disabled to preserve pixel aspect.
- The UI layer should not embed gameplay rules; those belong to murex_lab.
