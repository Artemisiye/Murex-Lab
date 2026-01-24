# Summoners War ⚔️ Murex Lab: Design Integration

This document outlines the gameplay features and design philosophies from **Summoners War: Sky Arena (SW)** being integrated into **Murex Lab**. The goal is to bring the depth of SW's character progression and strategic combat to the Artificer-themed world of Murex.

---

## 1. The Minion System (Monsters)

In Murex Lab, these are the artificial lifeforms or enchanted constructs you create.

### Key Progression Mechanics:
*   **Star Ratings & Leveling**:
    | Stars | Max Level | Evolution Cost |
    | :--- | :--- | :--- |
    | 1⭐ | 15 | 1x 1⭐ |
    | 2⭐ | 20 | 2x 2⭐ |
    | 3⭐ | 25 | 3x 3⭐ |
    | 4⭐ | 30 | 4x 4⭐ |
    | 5⭐ | 35 | 5x 5⭐ |
    | 6⭐ | 40 | - |
*   **Elemental Affinity**: A triangular advantage system.
    *   **Fire** > **Earth** (Murex's replacement for Wind)
    *   **Earth** > **Water**
    *   **Water** > **Fire**
    *   *Advantage*: +15% Crit Rate, 30% chance for Crushing Hit (ignores glancing, more dmg).
    *   *Disadvantage*: 50% chance for Glancing Hit (reduced dmg, cannot crit, cannot land debuffs).

### Stat-Based Scaling (Ability Math):
Murex Lab adopts the SW methodology of diverse scaling. Skill damage isn't just `ATK * Multiplier`.
*   **Attack Scaling**: Traditional DPS (e.g., `ATK * 4.5`).
*   **Defense Scaling**: The "Paladin" build. Damage increases with DEF (e.g., `DEF * 3.2`).
*   **HP Scaling**: The "Tank" build. Damage based on MAX HP (e.g., `HP * 0.18`).
*   **Speed Scaling**: The "Assassin" build. Multiplier increases with SPD (e.g., `ATK * (SPD + 120) / 60`).

---

## 2. The Engraving System (Runes)

The most critical customization layer. Instead of "equipping gear," you "engrave" your minions with magical matrices.

### The 6-Slot Grid:
Minions have 6 engraving slots. Slots 2, 4, and 6 are percentage-based (valuable), while 1, 3, and 5 are flat-stat based (utility).

### Major Sets:
*   **Vitality (2-Set)**: +15% HP.
*   **Assault (4-Set)**: +35% Attack Power.
*   **Acceleration (4-Set)**: +25% Speed.
*   **Precision (2-Set)**: +20% Accuracy.
*   **Intangible (Abyss Exclusive)**: A "Wildcard" engraving that completes any unfinished set bonus (Limit 1 per minion).

### 2b. The Stabilizer System (Artifacts)
Additional specialized equipment (2 slots: Attribute & Type) available to 6⭐ minions.
*   **Main Stats**: Pure Flat HP, ATK, or DEF.
*   **The "True Damage" Meta**: Artifacts allow for "Additional Damage as % of SPD/ATK/HP". This is massive for multi-hit skills, as it adds fixed damage per hit, ignoring defense.
*   **Utility Substats**: "Reduced damage from [Element]", "Increased Recovery", and "Accuracy on Skill 1/2".

### Crafting & Randomization:
When you craft an Engraving in the Lab:
1.  **Grade**: Magic (1 substat), Rare (2), Hero (3), Legendary (4).
2.  **Substats**: Randomly rolled from a pool (HP%, ATK%, DEF%, SPD, Crit%, CritDmg%).
3.  **Power-up Loop**: Using Gold/Mana to upgrade. At +3, +6, +9, and +12, a random substat is increased or a new one is added.

---

## 3. Active Turn Combat (ATC)

Murex Lab uses a **Speed-based Tick System** for combat, moving away from static rounds.

### The Attack Bar (ATB) Logic:
*   Every combatant has an ATB (0 - 1000).
*   The game "ticks" at a set frequency.
*   Each tick, a unit's ATB increases by their **Speed** stat.
*   When ATB hits 1000, the unit takes its turn.
*   **Strategy**: A unit with 200 Speed will take twice as many turns as a unit with 100 Speed.

### Skills & Cooldowns:
*   Minions have 3 Skills:
    1.  **Basic**: No cooldown, simple effect.
    2.  **Special**: 2-4 turn cooldown, strong effect.
    3.  **Ultimate**: 5-7 turn cooldown, battle-changing effect.

---

---

## 4. World Navigation & Gathering

The primary way to collect raw materials. We use a **Nested Grid** system to bridge the gap between travel and labor.

### The Exploration Loop:
1.  **Global Travel**: The player moves the avatar or minions across the world map.
    *   **Resonance Cost**: 1 Energy per cell moved.
    *   **Travel Capacity**: Each minion has a daily limit to how much ground they can cover.
2.  **Regional Zoom**: When "exploring" a specific global cell, the view zooms into a high-granularity **Regional Map**.
3.  **Gathering (Labor)**: Regional cells contain specific resource nodes (e.g., Mining, Logging, Fishing).
    *   **Tools Required**: You cannot harvest without the right gear (e.g., a *Stone Pickaxe* for Ores).
    *   **By-Products**: Gathering has a small chance to yield secondary materials (Hides, Feathers, Fat).
4.  **Roaming Hazards**: Animals and enemies roam the regional map in real-time. Coming in contact triggers a **Turn-Based Encounter**.
5.  **Risk & Reward**:
    *   **The Checkpoint**: Loot gathered in the regional map is stored in a temporary "Field Bag."
    *   *Murex Rule*: If the team is defeated before returning to the "Base" or a "Safe Point," the Field Bag is lost.

---

## 5. Combat & Gear Integration

The Artificer provides the power. Minions are "shells" modified by your output.

### Gear-Based Skillsets:
*   **Weapon 1 & 2**: These determine Skills 1 and 2. 
    *   *Hammer* = High stun chance / Defense scaling.
    *   *Sword* = High Speed / Bleed effects.
*   **The 6 Engravings**: Determine raw stats (HP, SPD, ATK).
*   **The Trinket**: Determines the Passive or a utility exploration bonus (e.g., "Eagle Eye" increases hide discovery).

### Combat Execution:
*   **Player-Led Voyages**: Full **Turn-Based Combat (ATC)**. The player controls every move, skill choice, and target.
*   **Minion-Only Voyages**: Background **Simulated Combat**. Results are calculated based on Power Rating vs. Node Danger level. The player only sees the result (Success/Fail and HP lost).

## 6. By-Products & Inventory
Voyages are the source of "The Wilds" tier items (see `ITEM_LIST.md`). 
*   **Primary Drops**: Wood, Stone, Ore.
*   **By-Products**: Feathers from birds, Hides from beasts, Fat from hunts. These occur as 15-20% chance bonus drops when gathering at specific nodes.

---

## 📚 Designer Notes
The depth of Summoners War comes from the **friction** of the rune system—thousands of permutations that make every player's "Minion" unique. In Murex Lab, we replicate this by making Engraving crafting, "Auto-Farm Logic," and **Roster Breadth** (via Locking mechanics) the primary late-game loops. This allows the player to feel like an *Engineer* optimizing a large-scale war machine.
