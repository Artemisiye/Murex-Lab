# **Technical Specification Document: Murex Lab**

## **Overview**
A high-level summary of the engine architecture, the core technological stack (Python/Flask, Vanilla JS, CSS3), and the primary engineering goal: a high-performance, low-asset survival fantasy simulation.

### **Directory Structure**
- `apps/murex_lab/app.py`: Main Flask entry point and API route definitions.
- `apps/murex_lab/modules/`: Backend logic for Map, Inventory, Crafting, and Minions.
- `apps/murex_lab/data/`: JSON storage for player state, world generation, and blueprints.
- `apps/murex_lab/static/`: CSS styling (style.css), JS logic (main.js), and CSS-based assets.
- `apps/murex_lab/templates/`: HTML structures and view partials (Inventory, Workshop, Map).
- `_engine/`: Shared game client launcher.



## **System Architecture**
### 1 **Backend Structure**
*   **State Management** - Mechanism for handling session data and persistence.
*   **Module Registry** - How independent systems (Inventory, Map, Crafting) interface with the core Flask app.
*   **Data Models** - JSON-based storage strategy for player progress, blueprints, and world state.

### 2 **Frontend Architecture**


## **Core Modules**
The game takes place on a grid based procedurally generated world map, with biomes, resources, and encounters. At the center of the map is the player's home lab, which is the starting point for the game, serving as a base of operations for the player. The player can explore the world. When standing in the lab tile, the player can access the workshop, where they can forge items, manage their inventory, and instruct their minions. Across the world, the player can also find shops and merchants, where they can purchase or sellf items and materials. 

### 1 **World Map**
- **Dynamic Centering** - The view should always be centered on the player, as if a camera is following the player.
- **Tile Size** - The tile size should be 150x150px.
- **Map Size** - The map should be 100x100 tiles.
- **Ocean Padding** - The "continent" should be padded by 2 tiles of sea, and 3 tiles of ocean. 
    - Player can step onto sea tiles for fishing, but cannot step onto ocean tiles.
    - Attempting to move into the ocean would not result in movement (`return False, "ocean_blocked"`).
- **Movement** - Player movement is free, but movement of the minions requires energy. 
    - **Animation** - When the player moves, the player avatar should animate to the new position. Since we are using absolute positioning, animate a transition of the grid position to the new grid position.
- **Fog of War** - The map has fog of war applied to it, where the player can only see the tiles they have already explored. The player can see a 1 tile radius around them, and can explore the map by moving their avatar.
    - **reveal_surroundings** - functions adds the tiles around the player to the discovered cells set.
- **Map Generation** - TBD, likely will use a perlin noise-based generation system rasterization on a grid, with transition rules for biomes. (grassland -> shrubland -> forest -> mountain etc)
- **Biomes** - 
- **DO NOT** - Enable regional exploration while in the workshop or at a shop.

### 2 **Regional Map**
When standing on a world map tile, the player can explore the regional map of the tile, where they can harvest resources, and engage in combat (encounters or hunts). The regional map is a map at higher granularity than the world map, displaying indvidual resource nodes such as trees, ores, and other resources. Animals and creatures roam the regional map. Some are hostile and will seek to attack the player - upon reaching the player (1 tile away), combat is automatically triggered. 



### 3 **Forging & Workshop**
* **Crafting System** - Any item in the game can be either harvested (raw material) or crafted through forging (blueprints) or refining (refinement station). To access the crafting interface, the player must be in the workshop, located at the center of the map. 
* **Blueprints** - Each crafting recipe is a blueprint, in the sense that some materials are interexchangeable, but require certain properties (such as Material.Metal tag, or Property.Flamable tag), thus the recipe relies on tags rather on secific item IDs. Each blueprint will specify the required components, the required crafting station, tools, and the result.
* **Tools** - Tools are items that are used to perform crafting or harvesting actions but are not consumed in the process. 
* **Stations** - Stations are structures that enable certain recipes. Stations will be accesible in the workshop upon construction.
    * **Crafting Stations** - Crafting stations are stations that usually combine multiple items to create a new item. 
    * **Refinement Stations** - Refinement stations are stations that usually transform a single item (raw material) into a refined item (crafting material). 

### 4 **The Vault (Inventory)**
* **Access** - The vault is accessible in the workshop, where the player can access their inventory and manage their items. All items in the vault are accessible for crafting and refining. Upon returning the the workshop, all newly acquired (non-equipped) items are added to the vault.
* **Tag System** - Items are categorized using tags, which are used to determine the type of item and its properties. 
* **Item Types** - 
    * **Raw Materials** - Items that are harvested from the world. 
    * **Refined Materials** - Items that are refined from raw materials.
    * **Equipment** - Items that are worn by the player.
    * **Weapons** - Weapons are items that are used to attack enemies.
    * **Consumables** - Items that are used to restore health or mana.
    * **Tools** - Tools are items that are used to perform crafting or harvesting actions but are not consumed in the process.


* **Asset Mapping** - Dictionary structure connecting item IDs to visual markers.
* **Backpack** - When the player is out in the wild, collecting resources, new items are added to the backpack. The backpack will be replace the inventory view when the player is out in the wild. In the map view, a widget in the bottom-right corner will display the number of items in the backpack.
* **Starting Equipment** - The player will start with:
    * 15 Gold
    * Leather pouch
    * Staff
    * Dagger
    * Simple shirt
    * Simple pants
    * Simple shoes
* **Filters** - The inventory will have filters for categorizing items.
    * Raw Materials
    * Refined Materials
    * Equipment
    * Weapons
    * Consumables
* **Sorting** - The inventory will have sorting functionality for organizing items.
    * Alphabetic
    * Amount
    * Value


## **Interaction Logic**
### 1 **Harvesting Pipeline**
* **Proximity Detection** - Server-side validation of harvest ranges.
* **Node Depletion** - The lifecycle of a resource node from detection to extraction.

### 2 **Automated Encounters**
* **Auto-Trigger Logic** - Coordinate-collision detection for hostile entities.
* **Engagement States** - Transitioning from Map navigation to the Encounter focused state.

## **Visual Language & Aesthetics**
### 1 **Typography**
* **Fonts** - Murex Lab will use Cinzel for titles, Simonetta for headings, and Ysabeau Office for body text.
* **Genesis Script** - If at any point of development, the concept of runes or ancient writings will be required, Murex Lab will use Kedem's concept of Genesis Script, using the Phoenician script.

### 2 **Assets**
* **Tile Rendering** - Pure CSS thumbnails will be used as placeholders for world map tiles (Triangles for peaks, paths for rivers), until a proper tileset is available. Tileset texture is to be flat and rather unicolor per biome.
* **Player Avatar** - Player avatar will be a simple CSS thumbnail, until a proper avatar is available. Avatar will be rendered on top of the tile background. Avatar will be centered on the tile. 
* **DONT DO** - Do not use emojis. Do not apply glow effects. Do not apply hover/scaling effects to the map tiles.

## **Performance & Optimization**
- **Consistent and Pooling Viewport** - Use a single absolutely-positioned “map layer” and render only a fixed 9×9 window around the player; reuse DOM nodes (tile pool) instead of creating/destroying nodes per move.
- **Positioned Tile Layer** - Use Positioned tile layer instead of CSS Grid, to only update tile content, not layout.
- **Hash Table** - Use a hash table to store the world map tiles, where the key is the coordinate string (x,y) and the value is the tile object.
- **CSS Hardware Acceleration** - Using `transform` vs `top/left` for movement.
- **requestAnimationFrame** - Use requestAnimationFrame for map updates and batch DOM writes.
- **Caching** - Precompute static biome sprite HTML for each biome and cache it (string templates or DOM clones).
- **Networking** - Stop fetching full map after every move. Instead, return only deltas: new player position + newly revealed tiles + changed resources.
- **Lazy Load Reguinal Map** - The regional map will be generated on the fly when the player enters a new cell.
- **Fog of War Bitmask** - Use a lightweight bitmask to store the fog of war state instead of strings.
- **DO BOT** - Dont use `box-shadow` on tiles.

## **Roadmap & Integration Stages**
* **Stage 1**: Foundation & Primitive Extraction (Completed)
* **Stage 2**: Advanced Forging & Tool Requirements
* **Stage 3**: Combat & Minion Stat Progression
* **Stage 4**: Research & Blueprint Discovery

## **Debugging & Tools**
* **Debugging** - The game will be debugged using the browser's developer tools. 
* **Tools** - Game tools will be implemented and launched through a seperate window (Tools Window).
* **Cheats** - Debugging cheats will be implemented to allow for easy testing of the game. Cheats menu will appear in the Tools Window.
    * **Cheat List**
        * Clear Inventory - rests the inventory to the starting equipment.
        * Clear Backpack - empties the backpacl.
        * Add Item - adds a specific item to the inventory, specified by item ID.
* **Recipe Manager** - A tool to easilty create new recipes, picking from a list of items and stations.
    * 

