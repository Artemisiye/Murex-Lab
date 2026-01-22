# Settler's Expedition - Godot 4 Prototype

## 🎮 How to Run

1. Open Godot 4
2. Click "Import"
3. Navigate to: `E:\Emerald Vimana\Murex-Lab\Idea-C\project.godot`
4. Click "Import & Edit"
5. Press F5 to run the game

## 🗺️ Gameplay

### Core Loop
1. **Explore**: Click on hex tiles to send idle settlers on expeditions
2. **Gather**: Settlers return with resources based on biome type
3. **Craft**: Use gathered resources to create weapons and tools
4. **Equip**: Better gear lets settlers survive higher danger zones
5. **Expand**: Push into dangerous territories for rare resources

### Map Legend
- 🟢 **Green (Camp)**: Your safe base (Danger: 0)
- 🌲 **Dark Green (Forest)**: Wood + Stone (Danger: 1 💀)
- ⛏️ **Gray (Mine)**: Copper Ore + Stone (Danger: 2 💀💀)
- ⚫ **Dark Gray (Deep Mine)**: Iron Ore + Copper (Danger: 3 💀💀💀)
- 🟣 **Purple (Ruins)**: Iron Ore + Stone (Danger: 4 💀💀💀💀)

### Settlers
- **Brave** - Initial settler
- **Scout** - Initial settler
- **Explorer** - Initial settler

Each settler can only go on one expedition at a time. They need weapons to survive dangerous zones!

### Crafting Recipes

#### Copper Ingot
- **Input**: 2x Copper Ore
- **Output**: 1x Copper Ingot
- **Station**: Smelter

#### Copper Sword (+1)
- **Input**: 2x Copper Ingot  
- **Output**: 1x Copper Sword
- **Effect**: Equips to next idle settler, allows Danger 1-2 zones
- **Station**: Forge

#### Iron Blade
- **Input**: 3x Iron Ore
- **Output**: 1x Iron Blade
- **Station**: Forge

### Strategy Tips
1. Start by exploring **Forest** tiles (low danger, easy wood)
2. Craft **Copper Swords** before attempting **Mine** tiles
3. Multiple settlers = parallel expeditions = faster resource gathering
4. Expedition time increases with danger level
5. Watch the status messages for completion notifications!

## 🎨 Features

- **Hex-based map** with procedural generation
- **Real-time expeditions** with timers
- **Dynamic difficulty** (danger-based loot multipliers)
- **Equipment system** (weapons affect survivability)
- **Resource management**
- **Auto-discovery** (fog of war reveals on visit)

## 🛠️ Technical Notes

Built with:
- Godot 4.2+
- GDScript
- Custom hex grid rendering
- Signal-based event system

All game logic is in `Scripts/`:
- `Main.gd` - Game manager
- `MapSystem.gd` - Hex map generation and rendering
- `SettlerManager.gd` - Expedition logic
- `CraftingPanel.gd` - Recipe crafting system
