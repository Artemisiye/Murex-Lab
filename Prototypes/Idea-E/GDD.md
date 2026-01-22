# The Artificer's Codex
## Game Design Document

### High Concept
*A theorycrafting encyclopedia disguised as a game. Deep dive into component stats, build optimization, and "what-if" scenario testing.*

### Core Fantasy
You are the kingdom's master artificer, consulted by heroes before quests. Your job: **design the perfect weapon** for each scenario using a deep understanding of component properties and stat interactions.

---

## Design Pillars

### 1. Information is Content
- Every item has 10+ stats (Weight, Balance, Sharpness, Durability, Comfort, Reach, etc.).
- Tooltips explain formulas (e.g., "Attack Speed = 100 / (Weight * 0.8 + 20)").
- The game is a **calculator with narrative flavor**.

### 2. Build Comparison
- Save multiple weapon builds.
- Side-by-side comparison tables.
- Export builds to share (JSON format).

### 3. Database Exploration
- **Codex** houses all discovered items/recipes.
- Filtering/sorting by any stat.
- "Show me all handles with Comfort > 8 and Weight < 2."

---

## Core Loop
1. **Request**: Receive hero's quest ("I need a sword for underwater combat").
2. **Research**: Explore codex for water-resistant materials.
3. **Assemble**: Select Handle, Blade, Guard from dropdowns.
4. **Inspect**: View detailed stat table with explanations.
5. **Save Build**: Archive to database with notes ("Poseidon Build v2").
6. **Compare**: Test against previous builds, refine.

---

## Unique Mechanics

### Quest Constraints
Each request has **requirements**:
- "Weight < 3kg" (for agile fighter).
- "Fire Resist > 50" (for dragon hunt).
- "Durability > 100" (for long campaign).

Builds are **scored** based on meeting requirements (0-100%).

### Stat Synergies
Components interact:
- `Heavy Blade + Light Handle = Poor Balance (-20% Attack Speed)`.
- `Matching Set Bonus (All Iron) = +10% Durability`.
- Creates puzzle-like optimization challenges.

### Material Encyclopedia
- Each material has lore, properties, acquisition notes.
- "Ironwood: Harvested from ancient forests. Combines wood's lightness with metal's strength."
- Encourages exploration of the database as gameplay.

---

## UI Design
### Main Screen: Workbench
- **3 Dropdowns**: Handle / Blade / Guard.
- **Live Stats Panel**: Updates immediately on selection change.
- **Comparison Toggle**: Show previous build side-by-side.

### Secondary Screen: Codex
- **Searchable Table**: All items with sortable columns.
- **Filters**: Material type, tier, stat thresholds.
- **Detail View**: Full lore + acquisition + related recipes.

---

## Progression
- **Phase 1**: Simple requests (5 constraints).
- **Phase 2**: Complex multi-stat optimization.
- **Phase 3**: "Free Mode" - no requests, just experiment and build your dream arsenal.

---

## Success Metrics
- **Depth of Use**: Player uses filters and sorting (shows engagement with data).
- **Build Variety**: Multiple saved builds with distinct strategies.
- **Learning Curve**: Understanding of stat formulas improves over time.

---

## Out of Scope (For MVP)
- Hero feedback/satisfaction (no visual hero characters).
- Animated stat changes (tables update instantly, no transitions).
- Import feature (export only for MVP).
