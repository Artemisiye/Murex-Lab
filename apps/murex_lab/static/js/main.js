let activeView = 'map';
let isMoving = false;

document.addEventListener('DOMContentLoaded', () => {
    console.log("Survival Systems Operational.");
    setupNavigation();
    setupModal();
    loadView('map');
});

// --- Modals ---
let modalCallback = null;
function setupModal() {
    const overlay = document.getElementById('modal-overlay');
    const closeBtn = document.getElementById('modal-close');
    if (closeBtn) {
        closeBtn.onclick = () => {
            overlay.classList.add('hidden');
            if (modalCallback) { modalCallback(); modalCallback = null; }
        };
    }
}
function showModal(title, body, callback = null) {
    const t = document.getElementById('modal-title');
    const b = document.getElementById('modal-body');
    const o = document.getElementById('modal-overlay');
    if (t) t.innerText = title;
    if (b) b.innerHTML = body;
    if (o) o.classList.remove('hidden');
    modalCallback = callback;
}

// --- Toasts ---
function showToast(message, type = 'info', duration = 2500) {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

// --- Navigation ---
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const viewName = link.getAttribute('data-view');
            loadView(viewName);
        });
    });
}

const TITLE_MAP = {
    'workshop': 'Artificer Workshop',
    'inventory': 'The Vault',
    'map': 'World Map',
    'exploration': 'Area Exploration',
    'minions': 'Allies'
};

async function loadView(viewName) {
    const mainArea = document.getElementById('content-area');
    if (!mainArea) return;
    mainArea.innerHTML = '<div style="padding: 50px; text-align: center; color: var(--accent); font-family: Cinzel;">Consulting Records...</div>';

    try {
        const response = await fetch(`/views/${viewName}`);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        const html = await response.text();
        mainArea.innerHTML = html;
        activeView = viewName;

        const title = document.getElementById('view-title');
        if (title) title.innerText = TITLE_MAP[viewName] || 'Murex Lab';

        // Update Sidebar Active State
        document.querySelectorAll('.nav-links li').forEach(link => {
            if (link.getAttribute('data-view') === viewName) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        if (viewName === 'workshop') initWorkshopModule();
        if (viewName === 'inventory') initInventoryModule();
        if (viewName === 'map') initMapModule();
        if (viewName === 'minions') initMinionsModule();
        if (viewName === 'exploration') initExplorationModule();
    } catch (e) {
        console.error("Link Failure:", e);
        mainArea.innerHTML = `<div style="padding: 50px; color: #96281b; font-family: Cinzel;">Record unreadable: ${e.message}</div>`;
    }
}

// --- Workshop ---
// --- Workshop State ---
let allBlueprints = [];
let activeStationId = 'station_none';
let activeBlueprint = null;
let selectedSlot = null;
let selections = {}; // { slot_id: inv_key }

async function initWorkshopModule() {
    try {
        const res = await fetch('/api/blueprints');
        allBlueprints = await res.json();
        renderBlueprintList();

        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.onclick = () => {
                if (tab.classList.contains('disabled')) return;
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                activeStationId = tab.getAttribute('data-station');
                renderBlueprintList();
            };
        });

        const craftBtn = document.getElementById('craft-btn');
        if (craftBtn) craftBtn.onclick = executeCraft;
    } catch (e) { console.error("Workshop Error:", e); }
}

function renderBlueprintList() {
    const list = document.getElementById('blueprint-list');
    if (!list) return;
    list.innerHTML = '';
    const filtered = allBlueprints.filter(s => (s.station_id || 'station_none') === activeStationId);
    if (filtered.length === 0) {
        list.innerHTML = '<li class="empty-state" style="padding:30px; opacity:0.3; text-align:center;">No blueprints found.</li>';
        return;
    }
    filtered.forEach(s => {
        const li = document.createElement('li');
        li.innerHTML = `<div>${s.name}</div><small style="color: var(--text-dim);">${s.type}</small>`;
        li.onclick = () => {
            document.querySelectorAll('#blueprint-list li').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            selectBlueprint(s.id);
        };
        list.appendChild(li);
    });
}

async function selectBlueprint(id) {
    try {
        const res = await fetch(`/api/blueprint/${id}`);
        activeBlueprint = await res.json();
        selections = {};

        const canvas = document.getElementById('blueprint-slots');
        const title = document.getElementById('blueprint-title');
        if (title) title.innerText = activeBlueprint.name;

        if (canvas) {
            canvas.innerHTML = '';
            activeBlueprint.slots.forEach(slot => {
                const div = document.createElement('div');
                div.className = 'slot-node';
                div.id = `slot-${slot.id}`;
                div.innerHTML = `<div class="slot-label">${slot.label}</div><div class="slot-value">EMPTY</div>`;
                div.onclick = () => openComponentPicker(slot);
                canvas.appendChild(div);
            });
        }
        updateCraftPreview();
    } catch (e) { console.error("Blueprint Error:", e); }
}

async function openComponentPicker(slot) {
    selectedSlot = slot;
    const picker = document.getElementById('component-picker');
    const list = document.getElementById('component-list');
    if (!picker || !list) return;

    picker.classList.remove('hidden');
    list.innerHTML = '<li style="padding:20px; opacity:0.5;">Searching Vault...</li>';

    try {
        const res = await fetch(`/api/components/${activeBlueprint.id}/${slot.id}`);
        const items = await res.json();

        list.innerHTML = '';
        if (items.length === 0) {
            list.innerHTML = '<li style="padding:20px; opacity:0.5; font-style:italic;">No valid items found in vault.</li>';
        }

        items.forEach(item => {
            const li = document.createElement('li');
            li.className = 'comp-item';
            li.innerHTML = `
                <div style="display:flex; justify-content:space-between;">
                    <strong>${item.name}</strong>
                    <span>x${item.quantity}</span>
                </div>
            `;
            li.onclick = () => selectComponent(item);
            list.appendChild(li);
        });
    } catch (e) { console.error("Picker Error:", e); }
}

function selectComponent(item) {
    selections[selectedSlot.id] = item.inv_key;

    // Update UI
    const node = document.getElementById(`slot-${selectedSlot.id}`);
    if (node) {
        node.classList.add('filled');
        node.querySelector('.slot-value').innerText = item.name;
    }

    document.getElementById('component-picker').classList.add('hidden');
    updateCraftPreview();
}

async function updateCraftPreview() {
    const btn = document.getElementById('craft-btn');
    const statsBox = document.getElementById('preview-stats');
    if (!btn || !statsBox) return;

    // Check if all required slots filled
    const allFilled = activeBlueprint.slots.every(s => s.optional || selections[s.id]);
    btn.disabled = !allFilled;

    if (!allFilled) {
        statsBox.innerHTML = '<p class="dim">Assemble all components to analyze outcome.</p>';
        return;
    }

    try {
        const res = await fetch('/api/preview_craft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ blueprint_id: activeBlueprint.id, components: selections })
        });
        const data = await res.json();

        if (data.success) {
            let statsHtml = `
                <div class="result-preview" style="text-align:center; padding:20px; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:20px;">
                    <div style="font-size:0.7rem; color:var(--text-dim); text-transform:uppercase; margin-bottom:10px;">Forged Outcome</div>
                    <img src="/assets/${ITEM_IMAGE_MAP[data.output_id] || ('item_sprites/' + data.output_id + '.png')}" 
                         onerror="this.src='/assets/item-sprites/logs.png'" 
                         style="width:80px; height:80px; object-fit:contain; margin-bottom:15px; image-rendering: pixelated;">
                    <div style="font-family:'Cinzel'; font-size:1.1rem; color:#fff;">${data.output_name}</div>
                </div>
            `;

            statsHtml += '<strong>Predicted Attributes:</strong><ul style="list-style:none; padding:10px; margin:0;">';
            for (const [stat, val] of Object.entries(data.stats)) {
                statsHtml += `<li>${stat.replace(/_/g, ' ')}: ${val.toFixed(1)}</li>`;
            }
            statsHtml += '</ul>';
            statsBox.innerHTML = statsHtml;
        } else {
            statsBox.innerHTML = `<p style="color:#e74c3c;">Analysis failed: ${data.error}</p>`;
            btn.disabled = true;
        }
    } catch (e) { console.error("Preview Error:", e); }
}

async function executeCraft() {
    const btn = document.getElementById('craft-btn');
    btn.disabled = true;
    btn.innerText = "Executing Forge...";

    try {
        const res = await fetch('/api/craft_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ blueprint_id: activeBlueprint.id, components: selections })
        });
        const data = await res.json();

        if (data.success) {
            showModal("Crafting Success", `You have created: ${data.item_name}`);
            // Clear current selection
            selectBlueprint(activeBlueprint.id);
        } else {
            showModal("Crafting Failed", data.error);
        }
    } catch (e) { console.error("Craft Error:", e); }

    btn.innerText = "Craft Item";
}

// --- Inventory ---
async function initInventoryModule() {
    const display = document.getElementById('inventory-display');
    if (!display) return;
    try {
        const res = await fetch('/api/inventory');
        const data = await res.json();
        const items = data.items;

        // Update global gold display
        const goldDisplay = document.querySelector('.gold');
        if (goldDisplay) goldDisplay.innerText = `Gold: ${data.gold}`;

        const header = document.querySelector('.panel-header');
        if (header) {
            header.innerText = data.is_backpack ? "Field Backpack" : "The Artificer's Vault";
            header.style.color = data.is_backpack ? "#a89f8c" : "var(--accent)";
        }

        let currentFilter = 'all';
        let currentSort = 'name';

        const render = () => {
            display.innerHTML = '';

            // 1. Filter
            let filtered = currentFilter === 'all' ? items : items.filter(i => i.type === currentFilter);

            // 2. Sort
            filtered.sort((a, b) => {
                if (currentSort === 'name') return a.name.localeCompare(b.name);
                if (currentSort === 'amount') return b.quantity - a.quantity;
                return 0;
            });

            if (filtered.length === 0) {
                display.innerHTML = '<div class="loading-state">No items found in this category.</div>';
                return;
            }

            filtered.forEach(item => {
                const card = document.createElement('div');
                card.className = `inventory-card type-${item.type} ${item.item_id}`;

                const imgSrc = ITEM_IMAGE_MAP[item.item_id] || `item_${item.item_id}.png`;

                card.innerHTML = `
                    <div class="item-visual-thumbnail">
                        <img src="/assets/${imgSrc}" onerror="this.style.display='none'; this.nextElementSibling.style.display='block'" class="pixel-art">
                        <div class="iv-shape" style="display:none"></div>
                    </div>
                    <div class="item-details">
                        <div class="item-name">${item.name}</div>
                        <div class="item-qty">${item.quantity}</div>
                    </div>
                `;
                display.appendChild(card);
            });
        };

        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.onclick = () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.getAttribute('data-filter');
                render();
            };
        });

        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.onchange = (e) => {
                currentSort = e.target.value;
                render();
            };
        }
        render();
    } catch (e) {
        console.error("Storage Error:", e);
        display.innerHTML = `<div style="color:#96281b; padding:40px; font-family: Cinzel;">UNABLE TO ACCESS STORAGE: ${e.message}</div>`;
    }
}

// --- Map & Navigation ---
// --- Map & Navigation ---
let mapCache = new Map(); // "x,y" => cellData
let playerPos = { x: 50, y: 50 };
let mapSize = 100;
let pooledTiles = [];
const VIEW_RADIUS = 6; // 13x13 window (2 tile buffer for smoother animation)
const TILE_SIZE = 150;
// isMoving is declared at top

// Precomputed Biome Sprites
const ITEM_IMAGE_MAP = {
    'iron_dagger': 'item-sprites/dagger.png',
    'simple_shirt': 'item-sprites/shirt.png',
    'simple_pants': 'item-sprites/pants.png',
    'staff': 'item-sprites/staff.png',
    'pouch': 'item-sprites/pouch.png',
    'mat_oak_log': 'item-sprites/logs.png',
    'oak_log': 'item-sprites/logs.png'
};

// Precomputed Biome Sprites
const BIOME_TEMPLATES = {
    'forest': '<div class="biome-marker forest"><img src="/assets/tiles/woodland.png"></div>',
    'mountains': '<div class="biome-marker mountains"><div class="m-peak"></div><div class="m-peak"></div></div>',
    'river': '<div class="biome-marker river"><div class="r-path"></div></div>',
    'lab': '<div class="biome-marker lab"><div class="lab-spire"></div></div>',
    'plains': '<div class="biome-marker plains"><img src="/assets/tiles/grassland.png"></div>',
    'unknown': '<div class="fow-texture"></div>'
};

async function initMapModule() {
    setupTilePool();
    await loadInitialMap();

    const exploreBtn = document.getElementById('explore-btn');
    if (exploreBtn) exploreBtn.onclick = exploreCurrentArea;

    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.onclick = () => moveOnMap(btn.getAttribute('data-dir'));
    });
}

function setupTilePool() {
    const container = document.getElementById('grid-container');
    const viewport = document.querySelector('.map-viewport');
    if (!container || !viewport) return;

    container.innerHTML = '';
    pooledTiles = [];

    const count = (VIEW_RADIUS * 2 + 1) ** 2;
    for (let i = 0; i < count; i++) {
        const div = document.createElement('div');
        div.className = 'grid-cell';
        container.appendChild(div);
        pooledTiles.push(div);
    }

    // Detaching avatar from grid: adding to viewport root for steady camera feel
    const p = document.createElement('img');
    p.id = 'active-player-marker';
    p.className = 'player-marker-sprite';
    p.src = '/assets/player_avatar.png';
    viewport.appendChild(p);
}

async function loadInitialMap() {
    try {
        const res = await fetch('/api/map/data');
        const data = await res.json();
        playerPos = data.player_pos;
        mapSize = data.size;

        mapCache.clear();
        data.cells.forEach(c => {
            mapCache.set(`${c.x},${c.y}`, c);
        });

        requestAnimationFrame(renderWorldGrid);
        updateInfoPanel();
    } catch (e) { console.error("Initial Map Load Error:", e); }
}

function updateInfoPanel() {
    const cell = mapCache.get(`${playerPos.x},${playerPos.y}`);
    if (!cell) return;
    const name = document.getElementById('cell-name');
    const coords = document.getElementById('cell-coords');
    const resBox = document.getElementById('cell-resources');
    if (name) name.innerText = cell.name;
    if (coords) coords.innerText = `Region ${cell.x}, ${cell.y}`;
    if (resBox) {
        resBox.innerHTML = (cell.resources && cell.resources.length > 0)
            ? cell.resources.map(r => `<span>${r.replace(/_/g, ' ')}</span>`).join('')
            : '<p style="opacity:0.3; font-style:italic; font-size:0.8rem;">No obvious resources.</p>';
    }
}

function renderWorldGrid() {
    if (pooledTiles.length === 0) return;

    let tileIdx = 0;
    const centerTileX = playerPos.x;
    const centerTileY = playerPos.y;

    console.log(`[MAP RENDER] Logical Center: ${centerTileX}, ${centerTileY} | Radius: ${VIEW_RADIUS}`);

    // Symmetrical loop around player center
    for (let dy = -VIEW_RADIUS; dy <= VIEW_RADIUS; dy++) {
        for (let dx = -VIEW_RADIUS; dx <= VIEW_RADIUS; dx++) {
            const worldX = centerTileX + dx;
            const worldY = centerTileY + dy;
            const tile = pooledTiles[tileIdx++];
            if (!tile) continue;

            // Positioning within the 13x13 container (1950px wide)
            tile.style.left = `${(dx + VIEW_RADIUS) * TILE_SIZE}px`;
            tile.style.top = `${(dy + VIEW_RADIUS) * TILE_SIZE}px`;

            // Bound check for map edges
            if (worldX < 0 || worldX >= mapSize || worldY < 0 || worldY >= mapSize) {
                tile.style.opacity = '0';
                continue;
            }
            tile.style.opacity = '1';

            const cell = mapCache.get(`${worldX},${worldY}`);
            const isDiscovered = cell && cell.discovered;

            if (!cell || !isDiscovered) {
                tile.className = 'grid-cell unknown';
                tile.innerHTML = BIOME_TEMPLATES['unknown'];
            } else {
                tile.className = `grid-cell ${cell.type}`;
                tile.innerHTML = BIOME_TEMPLATES[cell.type] || '';
                if (cell.type === 'lab') tile.classList.add('lab');
            }

            // Instrumentation: Coordinates Label
            let debugLabel = tile.querySelector('.debug-coord');
            if (!debugLabel) {
                debugLabel = document.createElement('div');
                debugLabel.className = 'debug-coord';
                debugLabel.style.cssText = 'position:absolute; bottom:5px; right:5px; font-size:10px; pointer-events:none; z-index:50;';
                tile.appendChild(debugLabel);
            }
            debugLabel.innerText = `${worldX},${worldY}`;
            debugLabel.style.color = isDiscovered ? 'rgba(255,255,255,0.4)' : 'rgba(255,0,0,0.8)';

            // Visual Debug: Outline the logical center tile
            if (dx === 0 && dy === 0) {
                tile.style.outline = '2px solid rgba(255, 255, 0, 0.5)';
                tile.style.outlineOffset = '-2px';
                tile.style.zIndex = '5';
            } else {
                tile.style.outline = 'none';
                tile.style.zIndex = '1';
            }
        }
    }
}

async function moveOnMap(direction) {
    if (isMoving) return;

    try {
        const res = await fetch('/api/map/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        });
        const data = await res.json();
        if (data.success) {
            isMoving = true;
            const container = document.getElementById('grid-container');
            const player = document.getElementById('active-player-marker');

            // 1. Update cache with new cells immediately (even if in buffer)
            if (data.new_cells) {
                data.new_cells.forEach(c => {
                    mapCache.set(`${c.x},${c.y}`, c);
                });
            }

            // 2. Animate the shift
            if (player) player.classList.add('walking');
            const moves = { 'up': [0, 1], 'down': [0, -1], 'left': [1, 0], 'right': [-1, 0] };
            const [mx, my] = moves[direction];

            if (container) {
                container.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                container.style.transform = `translate(${mx * TILE_SIZE}px, ${my * TILE_SIZE}px)`;
            }

            // 3. After animation, SNAP back and update logically
            setTimeout(() => {
                if (container) {
                    container.style.transition = 'none';
                    container.style.transform = 'translate(0, 0)';
                }
                if (player) player.classList.remove('walking');

                playerPos = data.player_pos;
                renderWorldGrid();
                updateInfoPanel();

                if (data.backpack_unloaded > 0) {
                    showToast(`Vault Secured: ${data.backpack_unloaded} items stored`, 'success');
                }

                const energyDisp = document.getElementById('energy-display');
                if (energyDisp) energyDisp.innerText = `Energy: ${data.energy}`;

                isMoving = false;
            }, 300);

        } else {
            if (data.message && data.message !== "ocean_blocked") {
                showModal("Movement Blocked", data.message);
            }
        }
    } catch (e) {
        console.error("Movement Error:", e);
        isMoving = false;
    }
}

// --- Area Exploration ---
window.closeRegionalMap = () => {
    loadView('map');
};

async function exploreCurrentArea() {
    loadView('exploration');
}

async function initExplorationModule() {
    try {
        const res = await fetch('/api/map/explore', { method: 'POST' });
        const data = await res.json();

        if (data.redirect) {
            loadView(data.redirect);
            return;
        }

        if (data.success) {
            renderAreaGrid(data.region_data);

            // Re-bind nav buttons in the new view
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.onclick = async () => {
                    const resMove = await fetch('/api/map/region_move', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ direction: btn.getAttribute('data-dir') })
                    });
                    const resData = await resMove.json();
                    if (resData.success) {
                        renderAreaGrid(resData.region_data);
                        checkAutoTriggers(resData.region_data);
                    }
                };
            });
        } else {
            showModal("Exploration Blocked", data.message);
            loadView('map');
        }
    } catch (e) {
        console.error("Exploration Failure:", e);
        loadView('map');
    }
}

function renderAreaGrid(data) {
    const grid = document.getElementById('regional-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const ASSET_MAP = {
        'node_oak': 'item-sprites/logs.png',
        'node_herbs': 'item-sprites/item_bitter_herbs.png',
        'node_shrub': 'item-sprites/item_plant_fibers.png',
        'node_grass': 'item-sprites/item_plant_fibers.png',
        'node_seeds': 'item-sprites/item_wild_seeds.png',
        'node_bush': 'item-sprites/item_wild_seeds.png',
        'node_loose_stone': 'item-sprites/item_rough_stone.png',
        'node_iron': 'item-sprites/item_iron_ore.png',
        'node_stone': 'item-sprites/item_rough_stone.png',
        'node_clay': 'item-sprites/item_raw_clay.png',
        'node_fish': 'item-sprites/item_fish.png',
        'node_reeds': 'item-sprites/item_plant_fibers.png',
        'node_fallen_branches': 'item_oak_log.png',
        'node_driftwood': 'item_oak_log.png'
    };

    for (let y = 0; y < 10; y++) {
        for (let x = 0; x < 10; x++) {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'reg-cell';

            const node = data.nodes.find(n => n.x === x && n.y === y);
            const entity = data.entities.find(e => e.x === x && e.y === y);
            const isPlayer = data.player_pos.x === x && data.player_pos.y === y;

            if (node) {
                cellDiv.classList.add('node');

                const lbl = document.createElement('div');
                lbl.className = 'reg-label';
                lbl.style.cssText = 'font-size: 0.9vmin; color: var(--text-dim); text-transform: uppercase; font-family: Cinzel; pointer-events: none;';
                lbl.innerText = node.name;
                cellDiv.appendChild(lbl);

                const asset = ASSET_MAP[node.id];
                if (asset) {
                    const s = document.createElement('img');
                    s.className = 'reg-sprite';
                    s.src = `/assets/${asset}`;
                    s.style.display = 'none';
                    s.onload = () => { s.style.display = 'block'; lbl.style.display = 'none'; };
                    s.onerror = () => { s.remove(); lbl.style.display = 'block'; };
                    cellDiv.appendChild(s);
                }
            }

            if (entity) {
                cellDiv.classList.add('entity');
                const s = document.createElement('img');
                s.className = 'reg-sprite';
                s.src = '/assets/player_avatar.png'; // Placeholder for mob
                s.style.opacity = '0.4';
                cellDiv.appendChild(s);
            }

            if (isPlayer) {
                cellDiv.classList.add('player');
                const p = document.createElement('img');
                p.className = 'reg-player-sprite';
                p.src = '/assets/player_avatar.png';
                cellDiv.appendChild(p);
            }

            grid.appendChild(cellDiv);
        }
    }
    renderAreaActions(data);

    if (!window.regionalHandlerAttached) {
        window.regionalHandlerAttached = true;
        window.addEventListener('keydown', async (e) => {
            if (activeView !== 'exploration') return;
            const moves = { 'ArrowUp': 'up', 'w': 'up', 'ArrowDown': 'down', 's': 'down', 'ArrowLeft': 'left', 'a': 'left', 'ArrowRight': 'right', 'd': 'right' };

            if (moves[e.key]) {
                e.preventDefault();
                const res = await fetch('/api/map/region_move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ direction: moves[e.key] })
                });
                const resData = await res.json();
                if (resData.success) {
                    renderAreaGrid(resData.region_data);
                    checkAutoTriggers(resData.region_data);
                }
            } else if (e.key === ' ') {
                e.preventDefault();
                // Harvest current pos
                const gridData = await fetch('/api/map/explore', { method: 'POST' }).then(r => r.json());
                if (gridData.success) {
                    harvestNode(gridData.region_data.player_pos.x, gridData.region_data.player_pos.y);
                }
            } else if (e.key === 'Backspace') {
                e.preventDefault();
                closeRegionalMap();
            }
        });
    }
}

function checkAutoTriggers(data) {
    const px = data.player_pos.x;
    const py = data.player_pos.y;
    // If we land exactly on an entity, or if one is right next to us?
    // User said "hostile mob - should auto trigger encounter".
    const hostiles = data.entities.filter(e => e.type === 'hostile' || e.hostile);
    const at = hostiles.find(h => h.x === px && h.y === py);
    if (at) {
        showModal("Ambushed!", `A hostile ${at.id.replace(/_/g, ' ')} attacks! (Combat system pending)`);
    }
}

async function harvestNode(x, y) {
    const dock = document.getElementById('context-actions');

    try {
        const res = await fetch('/api/map/harvest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x, y })
        });
        const data = await res.json();

        if (data.success) {
            // Toast Notification
            showToast(`+ ${data.loot.join(', ').replace(/_/g, ' ')}`, 'success');
            renderAreaGrid(data.region_data);
        } else {
            // Silent if nothing here
            if (data.message === "No resource here.") return;

            // Shake UI if failed (e.g. no tool)
            if (dock) {
                dock.classList.add('shake');
                setTimeout(() => dock.classList.remove('shake'), 400);
            }
        }
    } catch (e) {
        console.error("Harvest Error:", e);
    }
}

function renderAreaActions(data) {
    const dock = document.getElementById('context-actions');
    if (!dock) return;
    dock.innerHTML = '';
    const px = data.player_pos.x;
    const py = data.player_pos.y;

    // Only actions on the CURRENT TILE
    const currentObjects = [
        ...data.nodes.map(n => ({ ...n, interType: 'harvest' })),
        ...data.entities.map(e => ({ ...e, interType: e.type === 'prey' ? 'hunt' : 'combat' }))
    ].filter(obj => obj.x === px && obj.y === py);

    if (currentObjects.length === 0) {
        dock.innerHTML = '<p style="opacity:0.3; font-style:italic;">Nothing to interact with here.</p>';
        return;
    }

    currentObjects.forEach(obj => {
        const btn = document.createElement('button');
        btn.className = 'context-btn';
        let label = "Interact";
        let detail = "";

        const cleanName = (obj.name || obj.id || "Target").replace(/_/g, ' ');

        if (obj.interType === 'harvest') {
            label = `Harvest ${cleanName}`;
            if (obj.tool) {
                const toolName = obj.tool.split('.').pop();
                detail = `Tool: ${toolName}`;
            } else {
                detail = "Manual";
            }
            btn.onclick = () => harvestNode(obj.x, obj.y);
        } else if (obj.interType === 'hunt') {
            label = `Hunt ${cleanName}`;
            btn.onclick = async () => {
                const res = await fetch('/api/map/hunt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ x: n.x, y: n.y })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Killed ${cleanName}: ${data.loot.join(', ').replace(/_/g, ' ')}`, 'success');
                    renderAreaGrid(data.region_data);
                } else {
                    showToast(data.message, 'info');
                }
            };
        } else {
            label = `Confront ${cleanName}`;
            btn.onclick = async () => {
                const res = await fetch('/api/map/hunt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ x: obj.x, y: obj.y })
                });
                const data = await res.json();
                if (data.success && data.combat_started) {
                    initCombatView();
                } else if (data.message) {
                    showToast(data.message, 'info');
                }
            };
        }

        btn.innerHTML = `
            <span class="label">${label}</span>
            <span class="detail">${detail}</span>
        `;
        dock.appendChild(btn);
    });
}

// Global Nav Shortcuts
window.addEventListener('keydown', (e) => {
    // Shared Backspace behavior for sub-views
    if (e.key === 'Backspace') {
        if (activeView === 'workshop' || activeView === 'exploration' || activeView === 'inventory' || activeView === 'minions') {
            // Prevent backspace from navigating browser back
            // Only if not in an input field (safety check)
            if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                e.preventDefault();
                loadView('map');
            }
        }
    }

    if (activeView !== 'map') return;
    const moves = { 'ArrowUp': 'up', 'w': 'up', 'ArrowDown': 'down', 's': 'down', 'ArrowLeft': 'left', 'a': 'left', 'ArrowRight': 'right', 'd': 'right' };
    if (moves[e.key]) moveOnMap(moves[e.key]);
    if (e.key === ' ') {
        e.preventDefault();
        exploreCurrentArea();
    }
});

// --- Allies ---
// --- Allies ---
let selectedMinionId = null;
let cachedMinions = [];

async function initMinionsModule() {
    try {
        const res = await fetch('/api/minions');
        cachedMinions = await res.json();
        renderMinionsView();
    } catch (e) { console.error("Minion Load Error:", e); }
}

function renderMinionsView() {
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div class="minion-layout">
            <div class="minion-list-panel">
                <h3>Roster</h3>
                <div id="minion-list" class="minion-list">
                    ${cachedMinions.map(m => `
                        <div class="minion-card-summary ${selectedMinionId === m.id ? 'active' : ''}" 
                             id="minion-card-${m.id}"
                             onclick="selectMinion('${m.id}')">
                            <div class="m-name">${m.name}</div>
                            <div class="m-role">Artificer</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="minion-detail-panel" id="minion-detail">
                <div class="empty-state">Select a unit to inspect details.</div>
            </div>
        </div>
    `;

    // Initial Selection Logic (Only if needed)
    if (cachedMinions.length > 0 && !selectedMinionId) {
        selectedMinionId = cachedMinions[0].id;
    }

    if (selectedMinionId) {
        renderMinionDetails();
    }
}

function selectMinion(id) {
    selectedMinionId = id;

    // Update List UI without full re-render
    document.querySelectorAll('.minion-card-summary').forEach(el => el.classList.remove('active'));
    const activeCard = document.getElementById(`minion-card-${id}`);
    if (activeCard) activeCard.classList.add('active');

    renderMinionDetails();
}

function renderMinionDetails() {
    const m = cachedMinions.find(x => x.id === selectedMinionId);
    if (!m) return;

    const detail = document.getElementById('minion-detail');
    if (!detail) return;

    detail.innerHTML = `
        <div class="detail-header">
            <h2>${m.name}</h2>
            <div class="subtitle">Artificer Construct</div>
        </div>
        
        <div class="detail-grid">
            <div class="stat-block">
                <h4>Base Stats</h4>
                <div class="stat-row"><span>HP</span> <span>${m.stats.hp}</span></div>
                <div class="stat-row"><span>ATK</span> <span>${m.stats.atk}</span></div>
                <div class="stat-row"><span>DEF</span> <span>${m.stats.def}</span></div>
                <div class="stat-row"><span>SPD</span> <span>${m.stats.spd}</span></div>
                <div class="stat-row"><span>CRit R</span> <span>${Math.round(m.stats.crit_rate * 100)}%</span></div>
                <div class="stat-row"><span>Crit D</span> <span>${Math.round(m.stats.crit_dmg * 100)}%</span></div>
            </div>
            
            <div class="gear-block">
                <h4>Equipment</h4>
                <div class="gear-slot">
                    <div class="slot-label">Weapon</div>
                    <div class="slot-item">${m.gear?.weapon?.name || 'Empty'}</div>
                </div>
                <div class="gear-slot">
                    <div class="slot-label">Armor</div>
                    <div class="slot-item">${m.gear?.armor?.name || 'Empty'}</div>
                </div>
                 <div class="gear-slot">
                    <div class="slot-label">Accessory</div>
                    <div class="slot-item">${m.gear?.accessory?.name || 'Empty'}</div>
                </div>
            </div>
        </div>
    `;
}
// --- Developer Tools Launcher ---
window.addEventListener('keydown', (e) => {
    // Launch Tools Window: Shift + Ctrl + D
    if (e.shiftKey && e.ctrlKey && e.code === 'KeyD') {
        window.open('/debug', 'ArtificerTools', 'width=600,height=800,menubar=no,toolbar=no');
        console.log("Artificer Tools Initialized.");
    }
});

// --- Combat Module ---
let combatManager = null;

async function initCombatView() {
    const container = document.getElementById('combat-container');
    const res = await fetch('/api/combat/status');
    const data = await res.json();

    if (data.success) {
        // Switch Viewport
        document.getElementById('main-view').classList.add('hidden');
        document.querySelector('.sidebar').classList.add('hidden');
        container.classList.remove('hidden');

        // Render Viewport Template
        container.innerHTML = `
            <div class="combat-view">
                <div class="combat-header">
                    <h2>Engaging Hostiles</h2>
                    <div id="combat-turn-info">Initializing...</div>
                </div>
                <div class="combat-arena">
                    <div class="combat-side enemy-side" id="enemy-team"></div>
                    <div class="combat-center"><div id="combat-fx-layer"></div></div>
                    <div class="combat-side player-side" id="player-team"></div>
                </div>
                <div class="combat-controls">
                    <div class="skill-dock" id="skill-dock"></div>
                    <div class="combat-status-panel">
                        <div class="combat-log" id="combat-log"></div>
                        <button class="flee-btn" onclick="fleeCombat()">[ FORFEIT ]</button>
                    </div>
                </div>
                <div class="combat-result-overlay hidden" id="combat-result">
                    <h1 id="result-title">VICTORY</h1>
                    <div class="rewards-list" id="rewards-list"></div>
                    <button class="primary-btn" onclick="returnFromCombat()">Continue</button>
                </div>
            </div>
        `;

        combatManager = new CombatManager(data.state);
        combatManager.startTickLoop();
    }
}

class CombatManager {
    constructor(state) {
        this.state = state;
        this.isTicking = false;
        this.selectedSkill = null;
        this.updateUI();
    }

    async startTickLoop() {
        if (this.isTicking || this.state.is_finished) return;
        this.isTicking = true;

        while (this.isTicking && !this.state.is_finished) {
            const res = await fetch('/api/combat/tick', { method: 'POST' });
            const data = await res.json();
            this.state = data.state;
            this.updateUI();

            if (data.ready_unit) {
                this.isTicking = false;
                this.handleTurn(data.ready_unit);
                break;
            }
            // Wait for 1 tick interval
            await new Promise(r => setTimeout(r, 100));
        }
    }

    updateUI() {
        const pTeam = document.getElementById('player-team');
        const eTeam = document.getElementById('enemy-team');
        const log = document.getElementById('combat-log');

        if (!pTeam || !eTeam || !log) return;

        // Render Log
        log.innerHTML = this.state.log.map(msg => `<div>${msg}</div>`).join('');
        log.scrollTop = log.scrollHeight;

        // Render Entities (Simple 2D Thumbnails)
        const renderEntity = (e) => `
            <div class="combatant-card ${e.id === this.state.active_unit_id ? 'active' : ''} ${e.is_dead ? 'dead' : ''}" 
                 id="entity-${e.id}" onclick="combatManager.selectTarget('${e.id}')">
                <div class="unit-thumbnail ${e.side}">
                    <div class="unit-icon">${e.name.charAt(0)}</div>
                </div>
                <div class="bar-container"><div class="hp-bar" style="width: ${(e.hp / e.max_hp) * 100}%"></div></div>
                <div class="bar-container"><div class="atb-bar" style="width: ${Math.min(100, e.atb / 10)}%"></div></div>
                <div class="combatant-name">${e.name}</div>
                ${e.is_dead ? '<div class="death-tag">DEFEATED</div>' : ''}
            </div>
        `;

        pTeam.innerHTML = this.state.entities.filter(e => e.side === 'player').map(renderEntity).join('');
        eTeam.innerHTML = this.state.entities.filter(e => e.side === 'enemy').map(renderEntity).join('');

        // Turn Info
        const active = this.state.entities.find(e => e.id === this.state.active_unit_id);
        const turnInfo = document.getElementById('combat-turn-info');
        if (turnInfo) turnInfo.innerText = active ? `Turn: ${active.name}` : "Advancing Time...";

        if (this.state.is_finished) {
            this.showResult();
        }
    }

    handleTurn(unitId) {
        const unit = this.state.entities.find(e => e.id === unitId);
        if (unit.side === 'enemy') {
            setTimeout(() => this.autoEnemyTurn(unit), 1000);
        } else {
            this.renderSkills(unit);
        }
    }

    renderSkills(unit) {
        const dock = document.getElementById('skill-dock');
        if (!dock) return;
        // For now, hardcoded skills for Lead Artificer. Future: Fetch from unit.skills
        const skills = ['skill_basic_strike', 'skill_quick_slash', 'skill_arcane_bolt'];

        dock.innerHTML = skills.map(sid => `
            <button class="skill-btn" id="btn-${sid}" onclick="combatManager.selectSkill('${sid}')">
                ${sid.replace('skill_', '').replace('_', ' ')}
            </button>
        `).join('');
    }

    selectSkill(sid) {
        this.selectedSkill = sid;
        document.querySelectorAll('.skill-btn').forEach(b => b.classList.remove('active'));
        const btn = document.getElementById(`btn-${sid}`);
        if (btn) btn.classList.add('active');
        showToast("Select a target", "info");
    }

    async selectTarget(tid) {
        if (!this.selectedSkill) return;

        const res = await fetch('/api/combat/act', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill_id: this.selectedSkill, target_id: tid })
        });
        const data = await res.json();

        if (data.success) {
            this.state = data.state;
            this.selectedSkill = null;
            const dock = document.getElementById('skill-dock');
            if (dock) dock.innerHTML = '';
            this.updateUI();
            this.startTickLoop();
        }
    }

    async autoEnemyTurn(unit) {
        // AI: Target lowest HP player
        const players = this.state.entities.filter(e => e.side === 'player' && !e.is_dead);
        if (players.length === 0) return;
        players.sort((a, b) => a.hp - b.hp);
        const target = players[0];

        const res = await fetch('/api/combat/act', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skill_id: 'skill_basic_strike', target_id: target.id })
        });
        const data = await res.json();
        this.state = data.state;
        this.updateUI();
        this.startTickLoop();
    }

    showResult() {
        const overlay = document.getElementById('combat-result');
        if (!overlay) return;
        overlay.classList.remove('hidden');
        const title = document.getElementById('result-title');
        if (title) title.innerText = this.state.winner === 'player' ? "VICTORY" : "DEFEAT";
    }
}

function returnFromCombat() {
    document.getElementById('combat-container').classList.add('hidden');
    document.getElementById('main-view').classList.remove('hidden');
    document.querySelector('.sidebar').classList.remove('hidden');
    combatManager = null;
    // Refresh map state
    exploreCurrentArea();
}

function fleeCombat() {
    if (confirm("Forfeiting will result in losing all unsaved loot. Proceed?")) {
        returnFromCombat();
    }
}
