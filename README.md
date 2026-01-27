# Murex Lab

**Murex Lab** is a crafting-RPG set in the **Kedem** universe. You play as an artificer mastering the balance between science, magic, and logistics to supply the war of the gods.

This repository contains the main game development, the capsule engine, and the research prototypes.

## Repository Structure

> [!IMPORTANT]
> **AI Agents/Developers:** Please refer to [AGENT_CONTEXT.md](./AGENT_CONTEXT.md) for a comprehensive overview of the architecture, tech stack, and implementation guidelines.


- **`apps/`**: The active game development folders.
    - **`murex_lab/`**: The main game (In Development).
    - **`hello_world/`**: A capsule engine test case.
- **`_engine/`**: The **Murex Capsule Engine**. Tools to wrap Flask apps into native standalone executables.
- **`MurexLabDesign/`**: Living design documents.
    - `GDD.md`: The Master Game Design Document.
    - `NARRATIVE_POOL.md`: Collection of narrative themes and lore.
    - `FEATURE_BACKLOG.md`: Pool of 50+ mechanics to implement.
    - `TECHNICAL_SPECS.md`: Technical specifications for the game.
    - `BIOMES.md`: Free form list of biomes to be implemented in the game.
    - `ITEMS_List.md`: Free form list of items to be implemented in the game.
    - `SCHEMATICS.md`: Free form list of schematics to be implemented in the game.
    - `CRAFTING_STATIONS.md`: Free form list of crafting stations to be implemented in the game.
    - `SW_DESIGN.md`: Study of gameplay features that can borrowed from **Summoner's War: Sky Arena**.

## How to Run the Main Game (Murex Lab)

*Currently in initial setup phase.*

1.  Navigate to `apps/murex_lab` (Coming Soon)
2.  Run `python app.py`

## Building a Standalone EXE

We use the internal **Capsule Engine** to freeze the Python game into a distributable `.exe`.

```powershell
# Example Build Command
python _engine/builder.py apps/hello_world app.py "MurexHelloWorld"
```
