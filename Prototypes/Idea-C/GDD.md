# Settler's Expedition
## Game Design Document

### High Concept
*Equip your settlers wisely, send them into the unknown, and craft better gear from what they bring back.*

### Core Fantasy
You manage a frontier outpost. Settlers venture into hex-tiled wilderness, facing dangers based on their equipment quality. Better crafting → braver expeditions → rarer resources → masterwork gear.

---

## Design Pillars

### 1. Preparation Tension
- The moment before sending a settler feels meaningful.
- "Is this Iron Sword good enough for the Dark Forest?"
- Crafting has stakes because gear is **consumable** (durability system).

### 2. Spatial Exploration
- Hex map reveals gradually (fog of war).
- Different biomes have thematic resources (Forest=Wood, Mountains=Ore, Ruins=Relics).
- Visual feedback of "progress outward" from safe to dangerous zones.

### 3. Asymmetric Gameplay
- **Crafting Phase**: Calm, strategic, puzzle-solving.
- **Expedition Phase**: Tense, watching health bars, hoping settler survives.

---

## Core Loop
1. **Craft Gear**: Forge a weapon/tool from available materials.
2. **Equip Settler**: Assign gear (Weapon, Armor, Tool, Backpack).
3. **Send Expedition**: Click hex tile, settler walks there (animated, 5-15 seconds).
4. **Return**: Settler brings resources (or returns injured/empty if gear was insufficient).
5. **Refine & Repeat**: Use new resources to craft better gear.

---

## Unique Mechanics

### Danger Ratings
Each hex has a **Threat Level** (1-5 skulls):
- **1 Skull**: Safe (Berry Bush, Copper Vein) - Any gear works.
- **3 Skulls**: Dangerous (Iron Mine, Wolf Den) - Need Quality +2 weapon.
- **5 Skulls**: Deadly (Ancient Tomb) - Masterwork gear required.

### Gear Durability
- Weapons/Armor degrade with use (3 expeditions per item).
- Creates demand for continuous crafting.
- Higher quality = more durability.

### Settler Traits
- Each settler has a hidden trait (revealed after 3 expeditions):
  - "Lucky" - Better loot rolls.
  - "Brave" - Can attempt +1 skull above gear level.
  - "Cautious" - Returns alive more often but with less loot.

---

## Progression
- **Early**: Explore 1-2 skull zones, gather basic materials (Wood, Copper).
- **Mid**: Craft Iron gear, push into 3-skull zones (better resources).
- **Late**: Masterwork steel weapons, unlock 5-skull Ancient Ruins (legendary items).

---

## Map Design
- **Center**: Starting outpost (safe, depleted resources).
- **Ring 1**: Low-danger zones (tutorial phase).
- **Ring 2-3**: Medium danger, diverse biomes.
- **Ring 4**: High danger, rare resources, narrative discoveries (ruins with lore).

---

## Success Metrics
- **Emotional Stakes**: Player feels loss when settler dies.
- **Strategic Depth**: Clear difference between random clicking vs. thoughtful gear matching.
- **Exploration Drive**: "What's beyond that mountain?" curiosity.

---

## Out of Scope (For MVP)
- Settler personalities/dialogue (they're functional units).
- Base building (outpost is static).
- Real-time movement (simple point-and-wait).
