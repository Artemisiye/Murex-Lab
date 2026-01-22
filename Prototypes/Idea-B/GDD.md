# The Forge Dashboard
## Game Design Document

### High Concept
*A crafting automation idle game where efficiency is art and optimization is meditation.*

### Core Fantasy
You run a fantasy forge supplying adventurers. Orders come in ("50 Bronze Swords by Day 7"). Success requires building **production pipelines** that balance speed, quality, and resource management.

---

## Design Pillars

### 1. Satisfying Optimization
- Watching resources flow through stations (Ore → Smelter → Ingot → Forge → Sword).
- Identifying bottlenecks and upgrading the right stations.
- The dopamine of "numbers going up."

### 2. Idle Elegance
- Progress continues when you step away (queued jobs finish).
- Coming back to completed orders = reward.
- But active management yields better results (quality multipliers).

### 3. Visual Precision
- Clean, modern dashboard aesthetic (think: Notion meets Factorio).
- Real-time progress bars for each station.
- Color-coded quality indicators (Gray=+0, Green=+1, Blue=+2, Purple=+3).

---

## Core Loop
1. **Order Arrives**: "Make 10 Iron Swords (Quality +1 minimum)".
2. **Plan Pipeline**: Ore → Smelter (+1 refinement) → Forge.
3. **Queue Jobs**: Assign resources to stations, watch progress bars.
4. **Deliver**: Complete order, earn gold.
5. **Upgrade**: Spend gold on faster stations or better quality caps.

---

## Unique Mechanics

### Station Levels
Each station has upgrades:
- **Speed**: Reduce crafting time (1.0x → 0.8x → 0.6x).
- **Quality**: Unlock higher refinement tiers (Smelter Lvl 1 = +1 max, Lvl 3 = +3 max).
- **Batch Size**: Process multiple items simultaneously.

### Quality vs. Quantity Trade-off
- Higher quality takes longer but pays more.
- Rush orders reward speed over quality.
- Strategic decision-making in resource allocation.

### Prestige System
- "Season" resets every 10 game-days.
- Carry over permanent bonuses (unlock new materials, recipes, station types).

---

## Progression
- **Day 1-3**: Basic metals (Copper, Tin, Bronze).
- **Day 4-7**: Iron, Steel, complex multi-component weapons.
- **Day 8-10**: Rush to maximize profit before season end.

---

## Success Metrics
- **Flow State**: Player loses track of time managing pipelines.
- **Strategic Depth**: Observable difference between optimal and suboptimal play.
- **Replayability**: "One more season" mentality.

---

## Out of Scope (For MVP)
- Worker management (stations are automated).
- Resource gathering (focus on processing, not collection).
- Combat/adventure (pure economic sim).
