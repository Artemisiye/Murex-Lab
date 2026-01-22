# The Alchemist's Journal
## Game Design Document

### High Concept
*A word-of-mouth recipe discovery puzzle where you piece together ancient knowledge through experimentation and memory.*

### Core Fantasy
You are an apprentice alchemist in a forgotten tower. The master's journal was destroyed, leaving only scattered ingredient samples. You must **rediscover** the lost recipes through experimentation, pattern recognition, and careful note-taking.

---

## Design Pillars

### 1. Discovery Over Instruction
- No tutorial. No hints. Just ingredients and a workbench.
- Recipes unlock **organically** when you've handled all required ingredients.
- The joy is in the "Aha!" moment of connection.

### 2. Memory as Gameplay
- No recipe book. You must remember (or manually note) what you've tried.
- Failed combinations leave behind "ash" - a reminder not to repeat mistakes.
- Success creates satisfaction through mental effort, not button clicks.

### 3. Minimalist Aesthetics
- Hand-drawn ingredient icons (think: medieval manuscript illustrations).
- Parchment UI textures.
- Simple grid layout - clarity over flash.

---

## Core Loop
1. **Gather**: Start with 5 basic ingredients (Copper Ore, Ash, Water, Salt, Fire Rune).
2. **Experiment**: Drag two items together on the workbench.
3. **Discover**: If valid recipe → new item appears + "recipe learned" flash.
4. **Expand**: New items unlock more recipes (recursive discovery).
5. **Complete**: Fill the journal with all 50 recipes.

---

## Unique Mechanics

### Pattern Language
Recipes follow logical themes:
- `Metal Ore + Fire Rune = Metal Ingot`
- `Ingot + Ingot = Alloy`
- `Any Item + Ash = Destroy (chance to learn new recipe)`

### The "Almost There" System
Failed attempts that use *some* correct ingredients show a subtle visual hint (ingredients glow faintly), teaching players they're on the right track.

---

## Progression
- **Phase 1 (0-10 recipes)**: Basic elements and simple combinations.
- **Phase 2 (10-30 recipes)**: Refined materials and intermediate components.
- **Phase 3 (30-50 recipes)**: Complex assemblies requiring 3+ step chains.

---

## Success Metrics
- **Engagement**: Player takes physical notes (shows deep investment).
- **Discovery Rate**: Average time to find first 10 recipes < 5 minutes.
- **Completion**: At least 30 recipes discovered in playtest session.

---

## Out of Scope (For MVP)
- Animation/particles (keep it static).
- Sound effects (silent prototype).
- Save system (single session only).
