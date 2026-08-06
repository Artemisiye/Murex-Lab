# CLAUDE.md

## Project Overview
**Murex Lab** is a high-performance, low-asset crafting-RPG set in the **Kedem** universe. The game focuses on science, magic, and logistics, where players act as artificers supplying a divine war.

## Tech Stack
- **Backend/gameplay logic:** Python 3.
- **Two parallel UI clients**, both currently reading/writing the same gameplay logic independently (see "Architecture reality" below):
    - `apps/murex_lab/` — Flask (API-driven) + vanilla JS/HTML/CSS frontend. No frameworks (no React/Tailwind).
    - `apps/retro-py/` — pygame retro/CRT-styled client, mid-refactor.
- **Deployment:** `apps/flask_packager/` wraps a Flask app into a standalone native `.exe` via a pywebview launcher.

## Architecture reality vs. intent
- `apps/murex_lab/modules/` is the **only** place gameplay logic actually lives right now (crafting, inventory, combat, minions, world/regional maps).
- `apps/retro-py/` does not go through Flask/HTTP — instead `apps/retro-py/main.py` appends `apps/murex_lab/` to `sys.path` and `engine/state_manager.py` does `from modules.crafting import CraftingManager` etc. directly. So both clients run the *same* gameplay code, but as two separate in-process instances with no shared facade or session — each boots its own manager objects and can drift out of sync with the other's runtime state.
- `MurexLabDesign/Specs/ARCHITECTURE_SPECS.md` defines the target fix: a `murex-engine` facade (`apps/murex-engine/`) that owns all gameplay state, with both `retro-client` and `web-client` as thin renderers over it, plus a shared `src/murex_common/` DTO package.
  **This port has not started.** `apps/murex-engine/`, `apps/retro-client/`, `apps/web-client/`, and `src/murex_common/` are empty placeholder folders reserved by the spec — do not assume any code exists there yet. Until the port happens, treat `apps/murex_lab/modules/` as ground truth for gameplay rules and `apps/retro-py/` as a UI-only concern.

## Key Directory Map
- `apps/murex_lab/`: Main Flask app (gameplay logic authority, In Development).
    - `app.py`: Flask entry point & API routes.
    - `modules/`: Core backend logic (Map, Inventory, Crafting, Tag System, Combat, Minions).
    - `data/`: JSON-based state and static definitions (Schematics, Materials).
    - `static/` / `templates/`: Frontend assets and HTML partials.
- `apps/retro-py/`: pygame retro-UI client. `engine/` (managers: config, asset, data, state, input, post-processor), `ui/` (widget toolkit), `views/` (map, inventory, minions, settings, workshop). See `apps/retro-py/docs/ENGINE_MODULATION_SPECS.md` for its own in-progress refactor.
- `apps/flask_packager/`: Build tooling only — wraps a Flask app into a native `.exe`. Not a gameplay engine.
- `apps/hello_world/`: Minimal Flask app used as a `flask_packager` smoke test.
- `apps/murex-engine/`, `apps/retro-client/`, `apps/web-client/`, `src/murex_common/`: empty target-architecture stubs — see "Architecture reality" above.
- `MurexLabDesign/`: Living design documentation (GDD, biomes, items, schematics).
    - `MurexLabDesign/Specs/`: `ARCHITECTURE_SPECS.md` (refactor blueprint) and `TECHNICAL_SPECS.md`.
- `assets/`: Shared sprites, fonts, tiles — used by both clients.
- `tools/`: Standalone dev/debug scripts (not part of either app).

## Core Systems & Logic
- **Tag-Based Crafting:** `modules/tag_system.py` enables recipes (Schematics) to require properties (e.g., `Material.Metal`, `Property.Flammable`) instead of specific item IDs.
- **Dual-Layer Movement:**
    - **World Map:** 100x100 grid of tiles.
    - **Regional Map:** Granular exploration within a single tile for harvesting/combat.
- **Inventory Management:**
    - **The Vault:** Global storage accessible at the home lab.
    - **Backpack:** Limited mobile storage for field gathering.
- **Visual Style:** Pure CSS aesthetics in the web client (no emojis, no external icons — CSS-based shapes/gradients). The retro-py client uses its own bitmap sprite-font/CRT-shader pipeline instead.

## Guidelines for Agents
1.  **Read specs first:** Consult `MurexLabDesign/Specs/TECHNICAL_SPECS.md` (current systems) and `MurexLabDesign/Specs/ARCHITECTURE_SPECS.md` (target architecture, not yet implemented) before implementing new features.
2.  **Stateless API:** Keep Flask routes clean; delegate complex logic to files in `apps/murex_lab/modules/`.
3.  **Data driven:** New items, biomes, or recipes go into the JSON files in `apps/murex_lab/data/` first.
4.  **UI consistency:** Web client — match the typography and glassmorphic/dark-mode aesthetic in `style.css` (`Cinzel` for titles, `Simonetta` for headings). Retro client — match the existing pixel/CRT aesthetic in `apps/retro-py/ui/style.py`.
5.  **Performance:** Optimize for localized state updates on the frontend to avoid full page reloads.
6.  **Design patterns:** `.claude/skills/python-design-patterns` covers SRP/composition/DI/layering — relevant when working on the murex-engine decoupling.

## Quick Start for Agents
- Web client dev server: `python apps/murex_lab/app.py`
- Retro client: `python apps/retro-py/main.py`
- Data definitions: `apps/murex_lab/data/schematics.json`
- Web UI: `apps/murex_lab/static/js/main.js` and `apps/murex_lab/static/css/style.css`
