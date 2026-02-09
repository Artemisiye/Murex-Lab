# Item & Acquisition Chain Assessment

This document maps the lifecycle of items from their raw source on the World Map to their final forged state in the Workshop.

## 1. Raw Materials (Harvesting)

| Raw Material | Source Node | Biome | Tool Required |
| :--- | :--- | :--- | :--- |
| **Oak Log** | Oak Tree | Forest, River | Axe |
| **Rough Stone** | Rock Outcrop, Loose Stone | Mountains, Plains, Forest | Pickaxe (for Outcrop) |
| **Plant Fibers** | Wild Shrub, Tall Grass, River Reeds | Forest, Plains, River | None |
| **Raw Clay** | Clay Deposit | River | Shovel |
| **Flint Shard** | Rock Outcrop | Mountains | Pickaxe |
| **Iron Ore** | Iron Vein | Mountains | Pickaxe |
| **Native Copper** | Copper Vein (TBD) | Mountains | Pickaxe |
| **Tiny/Cinnabar Ore**| Ore Veins (TBD) | Mountains | Pickaxe |
| **Wild Seeds** | Seed Pods, Wild Herbs | Plains, Forest | None |
| **Bitter Herbs** | Wild Herbs | Forest | None |
| **River Water** | River / Lake | River, Lake | Bucket |
| **Raw Hide** | Animal Loot (Boar/Deer) | Forest, Plains | Hunting/Combat |
| **Animal Fat** | Animal Loot (Boar) | Forest | Hunting/Combat |

## 2. Refinement & Components (Crafting)

| Refined Item | Inputs | Station | Notes |
| :--- | :--- | :--- | :--- |
| **Cordage** | Plant Fibers | Manual / Workshop | Essential binding agent. |
| **Timber** | Oak Log + Axe | Wood Block | Basic building component. |
| **Clay Paste** | Raw Clay + Water | Manual | Prepared for molding. |
| **Unfired Brick** | Clay Paste + Brick Mold | Manual | Requires drying/firing next. |
| **Charcoal** | Oak Log | Fire Pit | High-temp fuel for smelting. |
| **Animal Tallow** | Animal Fat | Fire Pit | Low-temp fuel / Alchemy base. |
| **Iron Ingot** | Iron Ore + Charcoal | Forge (TBD) | Requires high temperature. |

## 3. Final Products (Tools & Gear)

| Item | Components | Station | Function |
| :--- | :--- | :--- | :--- |
| **Stone Axe** | Stone + Wood + Cordage | Workshop | Harvest Wood, Combat (Axe) |
| **Stone Pickaxe** | Stone + Wood + Cordage | Workshop | Harvest Stone/Ore |
| **Wooden Bucket** | Wood + Cordage | Workshop | Collect Liquids |
| **Brick Mold** | Timber | Workshop | Tool for making bricks. |
| **Small Pouch** | Raw Hide + Cordage | Workshop | Basic storage. |
| **Staff** | Wood + Cordage | Workshop | Basic weapon. |

## 4. Gap Analysis & Next Steps

### Recently Implemented
- **Shovel & Sand**: `Stone Shovel` added. `Beach` biomes now spawn with `Drift Sand` nodes requiring a shovel.
- **Copper & Tin**: Native Copper and Tin Ore veins added to Mountains. Smelting blueprints added for all base metals.
- **Bronze Age**: `Bronze Ingot` blueprint added (Alloy Copper + Tin).
- **Sea Harvesting**: `Sea` tiles are now explorable and contain `Salt Crust` nodes for `Sea Salt`.
- **Hunting**: `Hunt` action implemented. Animals (Boar) now drop `Raw Hide` and `Animal Fat`.
- **Smelting Station**: Smelting blueprints added using the `station_forge` requirement.

### Remaining Gaps
- **Tool Durability**: Defined in `TECHNICAL_SPECS.md` but not yet enforced in the harvest/hunt logic.
- **Cinnabar Use Cases**: Ore spawns, but no specific Alchemical blueprints use it yet.
- **Combat System**: Hunting is currently a simple click-to-loot; full turn-based combat is pending.

### Design Observations
- **Cordage** is the universal bottleneck for early game tools.
- **Wood** is abundant, but **Refined Timber** requires an Axe, creating a "First Axe" progression gate.
- **Fire Pit** is currently the only non-manual station with blueprint support.
