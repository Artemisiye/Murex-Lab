# AGENT_CONTEXT.md

## Project Overview
**Murex Lab** is a high-performance, low-asset crafting-RPG set in the **Kedem** universe. The game focuses on science, magic, and logistics, where players act as artificers supplying a divine war.

## Tech Stack
- **Backend:** Python 3 + Flask (API-driven).
- **Frontend:** Vanilla JavaScript (ES6+), HTML5, CSS3 (No frameworks like React/Tailwind).
- **Deployment:** **Murex Capsule Engine** (`_engine/`) wraps the Flask app into a standalone native executable using a webview/launcher.

## Key Directory Map
- `/apps/murex_lab/`: Main application directory.
    - `app.py`: Flask entry point & API routes.
    - `modules/`: Core backend logic (Map, Inventory, Crafting, Tag System).
    - `data/`: JSON-based state and static definitions (Schematics, Materials).
    - `static/`: Frontend assets (`main.js`, `style.css`).
    - `templates/`: HTML structures and UI partials.
- `/_engine/`: Builder tools to package the app into an `.exe`.
- `/MurexLabDesign/`: Living design documentation (GDD, Tech Specs, Item Lists).

## Core Systems & Logic
- **Tag-Based Crafting:** `modules/tag_system.py` enables recipes (Schematics) to require properties (e.g., `Material.Metal`, `Property.Flammable`) instead of specific item IDs.
- **Dual-Layer Movement:**
    - **World Map:** 100x100 grid of tiles.
    - **Regional Map:** Granular exploration within a single tile for harvesting/combat.
- **Inventory Management:**
    - **The Vault:** Global storage accessible at the home lab.
    - **Backpack:** Limited mobile storage for field gathering.
- **Visual Style:** Pure CSS aesthetics. No emojis, no external icons. Use CSS-based shapes and gradients.

## Guidelines for Agents
1.  **Read Specs First:** Always consult `MurexLabDesign/TECHNICAL_SPECS.md` before implementing new features.
2.  **Stateless API:** Keep Flask routes clean; delegate complex logic to files in `/modules/`.
3.  **Data Driven:** New items, biomes, or recipes should be added to the JSON files in `/data/` first.
4.  **UI Consistency:** Match the typography and glassmorphic/dark-mode aesthetic defined in `style.css`. Use `Cinzel` for titles and `Simonetta` for headings.
5.  **Performance:** Optimize for localized state updates on the frontend to avoid full page reloads.

## Quick Start for Agents
- To start the dev server: `python apps/murex_lab/app.py`
- To check data definitions: `apps/murex_lab/data/schematics.json`
- To modify UI: `apps/murex_lab/static/js/main.js` and `apps/murex_lab/static/css/style.css`
