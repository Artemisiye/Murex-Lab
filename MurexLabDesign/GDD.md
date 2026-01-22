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

## 🛠️ Technical Architecture

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
