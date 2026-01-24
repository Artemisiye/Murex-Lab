document.addEventListener('DOMContentLoaded', () => {
    console.log("Survival Systems Operational.");
    setupNavigation();
    setupModal();
    loadView('workshop');
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

// --- Navigation ---
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            const viewName = link.getAttribute('data-view');
            const title = document.getElementById('view-title');
            if (title) title.innerText = link.innerText;
            loadView(viewName);
        });
    });
}

async function loadView(viewName) {
    const mainArea = document.getElementById('content-area');
    if (!mainArea) return;
    mainArea.innerHTML = '<div style="padding: 50px; text-align: center; color: var(--accent); font-family: Cinzel;">Consulting Records...</div>';

    try {
        const response = await fetch(`/views/${viewName}`);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        const html = await response.text();
        mainArea.innerHTML = html;

        if (viewName === 'workshop') initWorkshopModule();
        if (viewName === 'inventory') initInventoryModule();
        if (viewName === 'map') initMapModule();
        if (viewName === 'minions') initMinionsModule();
    } catch (e) {
        console.error("Link Failure:", e);
        mainArea.innerHTML = `<div style="padding: 50px; color: #96281b; font-family: Cinzel;">Record unreadable: ${e.message}</div>`;
    }
}

// --- Workshop ---
let allSchematics = [];
let activeStationId = 'station_none';

async function initWorkshopModule() {
    try {
        const res = await fetch('/api/schematics');
        allSchematics = await res.json();
        renderSchematicList();

        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.onclick = () => {
                if (tab.classList.contains('disabled')) return;
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                activeStationId = tab.getAttribute('data-station');
                renderSchematicList();
            };
        });
    } catch (e) { console.error("Workshop Error:", e); }
}

function renderSchematicList() {
    const list = document.getElementById('schematic-list');
    if (!list) return;
    list.innerHTML = '';
    const filtered = allSchematics.filter(s => (s.station_id || 'station_none') === activeStationId);
    if (filtered.length === 0) {
        list.innerHTML = '<li class="empty-state" style="padding:30px; opacity:0.3; text-align:center;">No blueprints found.</li>';
        return;
    }
    filtered.forEach(s => {
        const li = document.createElement('li');
        li.innerHTML = `<div>${s.name}</div><small style="color: var(--text-dim);">${s.type}</small>`;
        li.onclick = () => {
            document.querySelectorAll('#schematic-list li').forEach(el => el.classList.remove('active'));
            li.classList.add('active');
            selectSchematic(s.id);
        };
        list.appendChild(li);
    });
}

async function selectSchematic(id) {
    try {
        const res = await fetch(`/api/schematic/${id}`);
        const data = await res.json();
        const canvas = document.getElementById('blueprint-slots');
        const title = document.getElementById('blueprint-title');
        if (title) title.innerText = data.name;
        if (canvas) {
            canvas.innerHTML = '';
            data.slots.forEach(slot => {
                const div = document.createElement('div');
                div.className = 'slot-node';
                div.innerHTML = `<div class="slot-label">${slot.label}</div><div class="slot-value">EMPTY</div>`;
                canvas.appendChild(div);
            });
        }
    } catch (e) { console.error("Blueprint Error:", e); }
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

                card.innerHTML = `
                    <div class="item-visual-thumbnail">
                        <div class="iv-shape"></div>
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
let mapData = null;

async function initMapModule() {
    await refreshMap();
    const exploreBtn = document.getElementById('explore-btn');
    if (exploreBtn) exploreBtn.onclick = exploreCurrentArea;
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.onclick = () => moveOnMap(btn.getAttribute('data-dir'));
    });
}

async function refreshMap() {
    try {
        const res = await fetch('/api/map/data');
        mapData = await res.json();
        renderWorldGrid();
        updateInfoPanel();
    } catch (e) { console.error("Map Load Error:", e); }
}

function updateInfoPanel() {
    const cell = mapData.cells.find(c => c.x === mapData.player_pos.x && c.y === mapData.player_pos.y);
    if (!cell) return;
    const name = document.getElementById('cell-name');
    const coords = document.getElementById('cell-coords');
    const resBox = document.getElementById('cell-resources');
    if (name) name.innerText = cell.name;
    if (coords) coords.innerText = `Region ${cell.x}, ${cell.y}`;
    if (resBox) {
        resBox.innerHTML = (cell.resources && cell.resources.length > 0)
            ? cell.resources.map(r => `<span>${r.replace('mat_', '').replace(/_/g, ' ')}</span>`).join('')
            : '<p style="opacity:0.3; font-style:italic; font-size:0.8rem;">No obvious resources.</p>';
    }
}

function renderWorldGrid() {
    const container = document.getElementById('grid-container');
    const underlay = document.getElementById('visualizer-field');
    if (!container || !underlay) return;

    const size = mapData.size;
    const cellW = 150;
    const gap = 8;

    container.style.gridTemplateColumns = `repeat(${size}, ${cellW}px)`;
    container.innerHTML = '';

    for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
            const cell = mapData.cells.find(c => c.x === x && c.y === y);
            const div = document.createElement('div');
            div.className = `grid-cell ${cell.discovered ? cell.type : 'unknown'}`;

            if (cell.discovered) {
                const sprite = document.createElement('div');
                sprite.className = `biome-marker ${cell.type}`;

                // Add internal shapes for biomes that need them
                if (cell.type === 'forest') sprite.innerHTML = '<div class="f-tree"></div><div class="f-tree"></div><div class="f-tree"></div>';
                if (cell.type === 'mountains') sprite.innerHTML = '<div class="m-peak"></div><div class="m-peak"></div>';
                if (cell.type === 'river') sprite.innerHTML = '<div class="r-path"></div>';
                if (cell.type === 'lab') sprite.innerHTML = '<div class="lab-spire"></div>';

                div.appendChild(sprite);
            } else {
                div.innerHTML = '<div class="fow-texture"></div>';
            }

            if (x === mapData.player_pos.x && y === mapData.player_pos.y) {
                const p = document.createElement('img');
                p.className = 'player-marker-sprite';
                p.src = '/static/assets/player_avatar.png';
                div.appendChild(p);
            }
            container.appendChild(div);
        }
    }

    // Dynamic Centering
    const px = mapData.player_pos.x;
    const py = mapData.player_pos.y;
    const centerX = (size - 1) / 2;
    const centerY = (size - 1) / 2;

    const offsetX = (centerX - px) * (cellW + gap);
    const offsetY = (centerY - py) * (cellW + gap);

    underlay.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
}

async function moveOnMap(direction) {
    const res = await fetch('/api/map/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction })
    });
    const data = await res.json();
    if (data.success) {
        const energyDisp = document.getElementById('energy-display');
        if (energyDisp) energyDisp.innerText = `Essence: ${data.energy}`;
        await refreshMap();
    } else {
        // Only show modal if it's NOT an ocean block (we check message from app.py)
        if (data.message && data.message !== "ocean_blocked") {
            showModal("Movement Blocked", data.message);
        }
    }
}

// --- Area Exploration ---
window.closeRegionalMap = () => {
    const overlay = document.getElementById('regional-overlay');
    if (overlay) overlay.classList.add('hidden');
};

async function exploreCurrentArea() {
    try {
        const res = await fetch('/api/map/explore', { method: 'POST' });
        const data = await res.json();
        if (data.success) renderAreaGrid(data.region_data);
    } catch (e) { console.error("Exploration Failure:", e); }
}

function renderAreaGrid(data) {
    const overlay = document.getElementById('regional-overlay');
    const grid = document.getElementById('regional-grid');
    if (!overlay || !grid) return;
    overlay.classList.remove('hidden');
    grid.innerHTML = '';

    for (let y = 0; y < 5; y++) {
        for (let x = 0; x < 5; x++) {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'reg-cell';
            const node = data.nodes.find(n => n.x === x && n.y === y);
            if (node) {
                cellDiv.classList.add('node');
                const s = document.createElement('img');
                s.className = 'reg-sprite';
                s.src = '/static/assets/item_oak_log.png'; // Using log as generic node sprite for now
                cellDiv.appendChild(s);
            }
            const entity = data.entities.find(e => e.x === x && e.y === y);
            if (entity) {
                cellDiv.classList.add('entity');
                const s = document.createElement('img');
                s.className = 'reg-sprite';
                s.src = '/static/assets/player_avatar.png'; // Placeholder for entity
                cellDiv.appendChild(s);
            }
            if (data.player_pos.x === x && data.player_pos.y === y) {
                cellDiv.classList.add('player');
                const p = document.createElement('img');
                p.className = 'reg-player-sprite';
                p.src = '/static/assets/player_avatar.png';
                cellDiv.appendChild(p);
            }
            grid.appendChild(cellDiv);
        }
    }
    renderAreaActions(data);

    if (!window.regionalHandlerAttached) {
        window.regionalHandlerAttached = true;
        window.addEventListener('keydown', async (e) => {
            const over = document.getElementById('regional-overlay');
            if (!over || over.classList.contains('hidden')) return;
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
    console.log(`Harvesting node at ${x}, ${y}...`);
    try {
        const res = await fetch('/api/map/harvest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x, y })
        });
        const data = await res.json();
        if (data.success) {
            showModal("Harvest Success", `Extracted: ${data.loot.join(', ').replace(/mat_/g, '').replace(/_/g, ' ')}`);
            renderAreaGrid(data.region_data);
        } else {
            showModal("Harvest Failed", data.message);
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
    const neighbors = [
        ...data.nodes.map(n => ({ ...n, interType: 'harvest' })),
        ...data.entities.map(e => ({ ...e, interType: e.type === 'prey' ? 'hunt' : 'combat' }))
    ].filter(obj => Math.abs(obj.x - px) <= 1 && Math.abs(obj.y - py) <= 1);

    if (neighbors.length === 0) {
        dock.innerHTML = '<p style="opacity:0.3; font-style:italic;">Move closer to interact.</p>';
        return;
    }
    neighbors.forEach(obj => {
        const btn = document.createElement('button');
        btn.className = 'context-btn';
        let label = "Interact";
        let detail = "";

        const cleanName = (obj.name || obj.id || "Target").replace(/_/g, ' ');

        if (obj.interType === 'harvest') {
            label = `Harvest ${cleanName}`;
            detail = `Needs: ${obj.tool.replace(/_/g, ' ')}`;
            btn.onclick = () => harvestNode(obj.x, obj.y);
        } else if (obj.interType === 'hunt') {
            label = `Hunt ${cleanName}`;
            btn.onclick = () => showModal("Hunting", `You are tracking the ${cleanName}...`);
        } else {
            label = `Confront ${cleanName}`;
            btn.onclick = () => showModal("Combat", `Initiating combat with ${cleanName}...`);
        }

        btn.innerHTML = `<span>${label}</span> <small>${detail}</small>`;
        dock.appendChild(btn);
    });
}

// Global Nav
window.addEventListener('keydown', (e) => {
    const title = document.getElementById('view-title');
    if (!title || !title.innerText.includes('Map')) return;
    const over = document.getElementById('regional-overlay');
    if (over && !over.classList.contains('hidden')) return;
    const moves = { 'ArrowUp': 'up', 'w': 'up', 'ArrowDown': 'down', 's': 'down', 'ArrowLeft': 'left', 'a': 'left', 'ArrowRight': 'right', 'd': 'right' };
    if (moves[e.key]) moveOnMap(moves[e.key]);
});

// --- Allies ---
async function initMinionsModule() {
    try {
        const res = await fetch('/api/minions');
        const minions = await res.json();
        const list = document.getElementById('minion-list');
        if (list) {
            list.innerHTML = minions.map(m => `
                <div class="minion-card">
                    <h3>${m.name}</h3><div class="lvl">Level ${m.level}</div>
                </div>
            `).join('');
        }
    } catch (e) { console.error("Minion Load Error:", e); }
}
// --- Developer Tools Launcher ---
window.addEventListener('keydown', (e) => {
    // Launch Tools Window: Shift + Ctrl + D
    if (e.shiftKey && e.ctrlKey && e.code === 'KeyD') {
        window.open('/debug', 'ArtificerTools', 'width=600,height=800,menubar=no,toolbar=no');
        console.log("Artificer Tools Initialized.");
    }
});
