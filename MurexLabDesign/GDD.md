---
project_title: Murex Lab
version: 0.1
status: Concept / Prototyping
description: A standalone 'pioneer' crafting RPG set in the Kedem universe.
---

# Murex Lab: Overview

**Murex Lab** is a crafting-focused role-playing game where the player assumes the role of an artificer/alchemist operating a secluded workshop in the world of Kedem. While the heroes of Kedem fight great battles, you supply the war effort, research forbidden knowledge, and manage a network of expeditions to gather rare resources.

## Narrative Concept
*[Placeholder: Narrative Theme To Be Decided from NARRATIVE_POOL.md]*

The core motivation will center around the Artificer's ambition in a world dominated by warring Overlords (Zeus, Odin) and encroaching Cosmic Horrors (Cthulhu).

---

## Core Gameplay Loop

The game revolves around three distinct phases that feed into each other:

### 1. The Lab (Home Base)
*   **The Hub**: The player stays mostly in their laboratory/workshop.
*   **Crafting**: Combining resources to create equipment (Weapons, Armor, Tools, Potions).
*   **Management**: Upgrading stations, managing storage, and researching new blueprints.

### 2. The Map (Logistics & Exploration)
*   **Grid System**: A hex or grid-based map representing the continent.
*   **Resource Nodes**: Specific tiles contain specific resources (Forest = Wood, Mountain = Iron).
*   **Expeditions**: The player delegates resource acquisition to **Companions/Minions**.
*   **Equipping Minions**: Minions are not just stats; they must be equipped with the gear YOU craft to survive higher-danger biomes.

### 3. The Economy (Trade & Combat)
*   **Trade**: Selling crafted goods to vendors or fulfilling specific client orders to earn Gold.
*   **Procurement**: Buying rare materials that cannot be easily found.
*   **Combat (Turn-Based)**: 
    *   Occurs when expeditions encounter danger or the Lab is attacked.
    *   Combat is **Turn-Based**.
    *   Can be **Simulated** (Auto-battler based on stats) or **Player Controlled**.

---

## Item & Recipe Design

### Direct Provenance
We minimize "forced" crafting steps. If a recipe requires a blade, it accepts the metal material directly (e.g., an Iron Ingot). The act of crafting the final item includes the forging/shaping of its parts. Intermediate components only exist when they serve as a shared base for *many* varied outcomes (e.g., **Cordage** for all bindings, **Timber** for all construction), and require a meaningful action from the player (e.g. requires a new tool or station; explore new biome).

### Tools and Requirements
Tools and infrastructure are enables for crafting. E.g.:
*   An **Axe** is required to harvest wood.
*   A **Kiln** is required transform raw clay into bricks, and wood into charcoal.
*   A **Smelter** is required to transform ores into ingots.

### Blueprints
Blueprints are crafting recipes. They are not physical items, but are knowledge discovered by discovering all the components of a recipe (e.g. acquiring a copper ingot and a tin ingot will unlock the blueprint for a bronze ingot).

### Logical Material Lineage
Every item must have a traceable, logical history. 
*   **Example**: `Raw Hide` -> `Drying Rack` -> `Tannery Vat (+Tree Bark)` -> `Cured Leather`. 
*   If a link is missing in the logic (e.g., how do we get water?), we create the necessary tool (**Wooden Bucket**) and the resource node (**Winding River**) to bridge the gap.

### Historical & Scientific Grounding
We pull from historical technology and alchemy. We use terms like **Cinnabar**, **Tallow**, **Cured Hide**, and **Borax**. This grounds the "Magical Artificery" in a world that feels physically real and taxing to master.

---

## Technical Architecture

*   **Engine**: Python (Flask) + HTML/JS (Frontend).
*   **Distribution**: Single standalone `.exe` (via Murex Capsule Engine).
*   **Data Structure**:
    *   `Items`: JSON/Database definition of components.
    *   `World`: Grid-based state management.
    *   `Save`: Json serialization of player state.

---

## References
*   **Narrative Ideas**: See `NARRATIVE_POOL.md`
*   **Feature Ideas**: See `FEATURE_BACKLOG.md`
