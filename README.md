# 🧪 Murex Lab

**Murex Lab** is a crafting-RPG set in the **Kedem** universe. You play as an artificer mastering the balance between science, magic, and logistics to supply the war of the gods.

This repository contains the main game development, the capsule engine, and the research prototypes.

## 📂 Repository Structure

- **`apps/`**: The active game development folders.
    - **`murex_lab/`**: The main game (In Development).
    - **`hello_world/`**: A capsule engine test case.
- **`_engine/`**: The **Murex Capsule Engine**. Tools to wrap Flask apps into native standalone executables.
- **`MurexLabDesign/`**: Living design documents.
    - `GDD.md`: The Master Game Design Document.
    - `NARRATIVE_POOL.md`: Collection of narrative themes and lore.
    - `FEATURE_BACKLOG.md`: Pool of 50+ mechanics to implement.
- **`Prototypes/`**: Archived research prototypes (Ideas A-E) used to validate mechanics.

## 🚀 How to Run the Main Game (Murex Lab)

*Currently in initial setup phase.*

1.  Navigate to `apps/murex_lab` (Coming Soon)
2.  Run `python app.py`

## 🛠️ The Prototypes (Research)

These were built to test specific loops. They are now archived in `Prototypes/`.

*   **Idea-A (The Alchemist)**: Economy & Exploration Loop.
*   **Idea-B (The Forge)**: UI & Clicker Mechanics.
*   **Idea-C (The Settler)**: Godot Hex-Map Exploration.
*   **Idea-D (The Crucible)**: Roguelike Combat.
*   **Idea-E (The Codex)**: Deep Stats & Constraint Solving.

## 📦 Building a Standalone EXE

We use the internal **Capsule Engine** to freeze the Python game into a distributable `.exe`.

```powershell
# Example Build Command
python _engine/builder.py apps/hello_world app.py "MurexHelloWorld"
```
