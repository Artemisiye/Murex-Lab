---
project_title: Murex Lab
version: 0.1
status: Concept / Prototyping
description: A standalone 'pioneer' crafting RPG set in the Kedem universe.
---

# 🎮 Murex Lab: Overview

**Murex Lab** is a crafting-focused role-playing game where the player assumes the role of an artificer/alchemist operating a secluded workshop in the world of Kedem. While the heroes of Kedem fight great battles, you supply the war effort, research forbidden knowledge, and manage a network of expeditions to gather rare resources.

## 📖 Narrative Concept
*[Placeholder: Narrative Theme To Be Decided from NARRATIVE_POOL.md]*

The core motivation will center around the Artificer's ambition in a world dominated by warring Overlords (Zeus, Odin) and encroaching Cosmic Horrors (Cthulhu).

---

## 🔁 Core Gameplay Loop

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

## � The Artificer's Philosophy: Item & Recipe Design

The crafting system in Murex Lab avoids generic RPG tropes in favor of a "Provenance-First" approach. Our design mindset for expanding items and recipes follows five core pillars:

### 1. The Great Chain of Artificery (Civilization Stages)
Items are not just sorted by "Tier 1, Tier 2"; they are sorted by **Civilization Branches**. 
*   **The Hand**: Manual gathering and primitive assembly.
*   **The Shaper**: Masonry, pottery, and structural woodworking.
*   **The Thermal Threshold**: Mastery of heat (Kilns/Smelters) for metallurgy and glass.
*   **The High Lab**: Advanced chemistry, optics, and fog-energy imbuing.

### 2. Direct Provenance (No Forced Intermediates)
We minimize "forced" crafting steps. If a recipe requires a blade, it accepts the metal material directly (e.g., an Iron Ingot). The act of crafting the final item includes the forging/shaping of its parts. Intermediate components only exist when they serve as a shared base for *many* varied outcomes (e.g., **Cordage** for all bindings, **Timber** for all construction).

### 3. Catalysts vs. Consumption
Tools and infrastructure are **Catalysts**. 
*   An **Axe** is required to process Logs into Timber, but it is not consumed in the process.
*   A **Brick Mold** is used as a template to form Unfired Bricks.
*   Progress is measured not just by what you *have*, but by what **Stations** you have integrated into your workshop.

### 4. Logical Material Lineage
Every item must have a traceable, logical history. 
*   **Example**: `Raw Hide` -> `Drying Rack` -> `Tannery Vat (+Tree Bark)` -> `Cured Leather`. 
*   If a link is missing in the logic (e.g., how do we get water?), we create the necessary tool (**Wooden Bucket**) and the resource node (**Winding River**) to bridge the gap.

### 5. Historical & Scientific Grounding
We pull from historical technology and alchemy. We use terms like **Cinnabar**, **Tallow**, **Cured Hide**, and **Borax**. This grounds the "Magical Artificery" in a world that feels physically real and taxing to master.

---

## �🛠️ Technical Architecture

*   **Engine**: Python (Flask) + HTML/JS (Frontend).
*   **Distribution**: Single standalone `.exe` (via Murex Capsule Engine).
*   **Data Structure**:
    *   `Items`: JSON/Database definition of components.
    *   `World`: Grid-based state management.
    *   `Save`: Json serialization of player state.

---

## 📚 References
*   **Narrative Ideas**: See `NARRATIVE_POOL.md`
*   **Feature Ideas**: See `FEATURE_BACKLOG.md`
