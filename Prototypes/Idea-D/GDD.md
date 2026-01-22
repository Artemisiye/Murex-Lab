# The Crucible
## Game Design Document

### High Concept
*Roguelike survival where crafting IS combat preparation. Every run is a race to forge the gear that keeps you alive.*

### Core Fantasy
You're a lone blacksmith in a demon-infested forge. Each night, waves of enemies attack. You must **craft weapons between waves**, using scavenged materials from defeated foes. Better crafting = longer survival. Death = start over.

---

## Design Pillars

### 1. Pressure Crafting
- Limited time between waves (30 seconds).
- Crafting requires precise decision-making under stress.
- "Do I risk the complex recipe or settle for safe choice?"

### 2. Permadeath Investment
- Every run is fresh, but knowledge persists (recipe book unlocks).
- Emotional attachment to gear you crafted.
- "That Bronze Sword kept me alive until Wave 7!"

### 3. Component Composition
- Weapons are assembled from parts (Blade + Handle + Guard).
- Each component affects stats (Weight, Damage, Speed).
- Lightweight sword = fast swings but low damage.
- Heavy hammer = slow but crushes armor.

---

## Core Loop
1. **Night Phase**: Survive wave, collect enemy drops (Bone, Leather, Ore).
2. **Day Phase (30s)**: Craft/upgrade weapon at forge.
3. **Next Wave**: Test new gear, survive longer.
4. **Death**: Record best wave reached, unlock new recipes.
5. **Retry**: Apply learned strategies with new build.

---

## Unique Mechanics

### Adaptive Difficulty
- Waves scale with your gear quality.
- Powerful sword = stronger enemies spawn.
- Creates strategic tension: "Should I craft Tier +3 weapon or stay safe?"

### Component Scavenging
- Enemies drop **specific parts**:
  - Skeletons → Bone Blades (light, fast).
  - Golems → Stone Hammers (heavy, slow).
  - Demons → Cursed Grips (damage boost, drain health).
- Encourages experimentation with hybrid builds.

### The Final Forge
- Wave 10 is a boss.
- Dropped material lets you craft "Legendary" item (permanent unlock for future runs).
- Creates long-term goal beyond "survive longer."

---

## Combat (Minimal Implementation)
- Simple 2D arena, enemies walk toward player.
- Player has **one attack button** (weapon determines speed/damage).
- Health bar, dodge roll (i-frames).
- Goal: Make crafting the *interesting* part, combat the *test*.

---

## Progression
- **Meta**: Unlock recipes (persistent across runs).
- **Per-Run**: Start with bare fists, build up to masterwork gear.
- **Skill**: Learn enemy patterns, optimal crafting routes.

---

## Success Metrics
- **"One More Run"**: Player immediately retries after death.
- **Build Diversity**: Multiple viable weapon strategies (speed, tank, hybrid).
- **Difficulty Curve**: New players reach Wave 3-5, skilled players reach Wave 10+.

---

## Out of Scope (For MVP)
- Complex animations (simple attack swings).
- Enemy variety (3 types max).
- Crafting station variety (single forge only).
- Visual polish (placeholder sprites acceptable).
