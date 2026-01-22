document.addEventListener('DOMContentLoaded', () => {
    console.log("Murex Lab Systems Initialized.");
    setupNavigation();
    setupModal();

    // Auto-load Workshop on start for dev speed
    loadView('workshop');
});

// --- Modal System ---
let modalCallback = null;

function setupModal() {
    const overlay = document.getElementById('modal-overlay');
    const closeBtn = document.getElementById('modal-close');

    closeBtn.onclick = () => {
        overlay.classList.add('hidden');
        if (modalCallback) {
            modalCallback();
            modalCallback = null;
        }
    };
}

function showModal(title, body, callback = null) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-body').innerHTML = body;
    document.getElementById('modal-overlay').classList.remove('hidden');
    modalCallback = callback;
}

// --- Navigation ---
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links li');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // UI Toggle
            document.querySelectorAll('.nav-links li').forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // View Load
            const viewName = link.getAttribute('data-view');
            const title = link.innerText;
            document.getElementById('view-title').innerText = title;
            loadView(viewName);
        });
    });
}

async function loadView(viewName) {
    const main = document.getElementById('content-area');
    main.innerHTML = '<div class="placeholder-message">Loading Module...</div>';

    try {
        const response = await fetch(`/views/${viewName}`);
        const html = await response.text();
        main.innerHTML = html;

        // Initialize Module specific logic
        if (viewName === 'workshop') initWorkshopModule();
        if (viewName === 'inventory') initInventoryModule();
        if (viewName === 'map') initMapModule();

    } catch (e) {
        console.error(e);
        main.innerHTML = `<div class="placeholder-message" style="color:red">Module Failure: ${e}</div>`;
    }
}

// --- Workshop Module Logic ---
let currentSchematicId = null;
let currentSlotsConfig = []; // Stores slot definitions
let selectedComponents = {}; // Map slot_id -> component_id
let allSchematics = [];
let activeStationId = 'station_none';

async function initWorkshopModule() {
    console.log("Workshop Init. Active Station:", activeStationId);
    const list = document.getElementById('schematic-list');
    const tabs = document.querySelectorAll('.tab-btn');

    // 1. Fetch Schematics
    try {
        const res = await fetch('/api/schematics');
        allSchematics = await res.json();

        // 2. Setup Tab Listeners and initial highlight
        tabs.forEach(tab => {
            const tabStation = tab.getAttribute('data-station');

            // Highlight active station tab
            if (tabStation === activeStationId) {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
            }

            tab.onclick = () => {
                if (tab.classList.contains('disabled')) return;
                console.log("Switching to station:", tabStation);
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                activeStationId = tabStation;
                currentSchematicId = null; // Reset selection
                selectedComponents = {};
                renderSchematicList();
                const blueprint = document.getElementById('blueprint-slots');
                if (blueprint) blueprint.innerHTML = '<div class="empty-state">Select a schematic to begin crafting</div>';
                updatePreview();
            };
        });

        renderSchematicList();
    } catch (e) {
        list.innerText = "Connection Failed.";
    }
}

function renderSchematicList() {
    const list = document.getElementById('schematic-list');
    list.innerHTML = '';

    // Filter by station
    const filtered = allSchematics.filter(s => (s.station_id || 'station_none') === activeStationId);

    if (filtered.length === 0) {
        list.innerHTML = '<li class="dim">No schematics for this station</li>';
        return;
    }

    filtered.forEach(s => {
        const li = document.createElement('li');
        li.innerHTML = `<div>${s.name}</div><small style='color:#666'>${s.type}</small>`;
        li.onclick = () => selectSchematic(s.id, li);
        if (s.id === currentSchematicId) li.classList.add('active');
        list.appendChild(li);
    });
}

async function selectSchematic(id, el) {
    console.log("Selecting Schematic:", id);
    // UI Highlight
    document.querySelectorAll('#schematic-list li').forEach(l => l.classList.remove('active'));
    el.classList.add('active');

    currentSchematicId = id;
    selectedComponents = {}; // Reset selection

    // Fetch Details
    const res = await fetch(`/api/schematic/${id}`);
    const data = await res.json();
    currentSlotsConfig = data.slots;

    // Render Blueprint
    document.getElementById('blueprint-title').innerText = data.name;
    const canvas = document.getElementById('blueprint-slots');
    canvas.innerHTML = ''; // Clear

    data.slots.forEach(slot => {
        const slotDiv = document.createElement('div');
        slotDiv.className = 'slot-node';
        slotDiv.id = `ui-slot-${slot.id}`;
        slotDiv.innerHTML = `
            <div class="slot-label">${slot.label} ${slot.required ? '*' : ''}</div>
            <div class="slot-value">Empty</div>
        `;
        slotDiv.onclick = () => openComponentPicker(slot.id, slot.label);
        canvas.appendChild(slotDiv);
    });

    updatePreview();
}

async function openComponentPicker(slotId, slotLabel) {
    const picker = document.getElementById('component-picker');
    const list = document.getElementById('component-list');

    // Show Picker
    picker.classList.remove('hidden');
    list.innerHTML = '<li>Loading parts...</li>';

    // Fetch Valid Components
    const res = await fetch(`/api/components/${currentSchematicId}/${slotId}`);
    const components = await res.json();

    list.innerHTML = '';

    // Add "None" option if optional? (Not implemented for MVP)

    if (components.length === 0) {
        list.innerHTML = '<li style="padding:10px">No compatible components found in inventory.</li>';
    }

    components.forEach(comp => {
        const li = document.createElement('li');
        li.className = 'comp-item';
        li.innerHTML = `
            <div style="display:flex; justify-content:space-between">
                <div class="comp-name">${comp.name}</div>
                <div style="color:var(--accent)">x${comp.quantity}</div>
            </div>
            <div class="comp-mat">${comp.material || 'Generic'} | Stats: ${JSON.stringify(comp.stats)}</div>
        `;
        li.onclick = () => selectComponent(slotId, comp);
        list.appendChild(li);
    });
}

function selectComponent(slotId, component) {
    // Save Selection (Using the inventory key)
    selectedComponents[slotId] = component.inv_key;

    // Update Slot UI
    const slotDiv = document.getElementById(`ui-slot-${slotId}`);
    slotDiv.classList.add('filled');
    slotDiv.querySelector('.slot-value').innerText = component.name;

    // Hide Picker
    document.getElementById('component-picker').classList.add('hidden');

    updatePreview();
}

async function updatePreview() {
    const statsBox = document.getElementById('preview-stats');
    const craftBtn = document.getElementById('craft-btn');

    if (currentSlotsConfig.length === 0) {
        statsBox.innerHTML = '<p class="dim">Select a blueprint</p>';
        craftBtn.disabled = true;
        return;
    }

    // Call Preview API
    try {
        const res = await fetch('/api/preview_craft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ schematic_id: currentSchematicId, components: selectedComponents })
        });

        if (!res.ok) throw new Error(`Server Error: ${res.status}`);

        const result = await res.json();
        console.log("Preview Result:", result);

        if (result.error) {
            statsBox.innerHTML = `<p style="color:#e74c3c">${result.error}</p>`;
            craftBtn.disabled = true;
        } else {
            // Render Stats
            let html = '<h3>Predicted Stats</h3><ul style="list-style:none; padding:0; margin-top:10px">';
            for (const [key, val] of Object.entries(result.stats)) {
                html += `<li style="display:flex; justify-content:space-between; border-bottom:1px solid #333; padding:5px">
                <span>${key}</span> <span style="color:#f1c40f">${val}</span>
            </li>`;
            }
            html += '</ul>';
            statsBox.innerHTML = html;

            craftBtn.disabled = false;
            craftBtn.onclick = () => performCraft();
        }
    } catch (e) {
        console.error("Preview error:", e);
        statsBox.innerHTML = `<p style="color:#e74c3c">Forge connection failed.</p>`;
        craftBtn.disabled = true;
    }
}

async function performCraft() {
    const res = await fetch('/api/craft_item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schematic_id: currentSchematicId, components: selectedComponents })
    });

    const result = await res.json();
    if (result.success) {
        showModal("Success", result.message, () => {
            const activeLi = document.querySelector('#schematic-list li.active');
            if (activeLi) activeLi.click();
        });
    } else {
        showModal("Error", "Crafting Failed: " + (result.error || "Unknown error"));
    }
}

// --- Inventory Module Logic ---
let fullInventory = [];

async function initInventoryModule() {
    console.log("Inventory Init");
    const display = document.getElementById('inventory-display');

    // 1. Fetch Inventory
    const res = await fetch('/api/inventory');
    fullInventory = await res.json();

    renderInventory('all');

    // 2. Setup Filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderInventory(btn.getAttribute('data-filter'));
        });
    });
}

function renderInventory(filter) {
    const display = document.getElementById('inventory-display');
    if (!display) return;
    display.innerHTML = '';

    const filtered = filter === 'all'
        ? fullInventory
        : fullInventory.filter(item => item.type === filter);

    if (filtered.length === 0) {
        display.innerHTML = '<div class="empty-state">No items found in this category.</div>';
        return;
    }

    filtered.forEach(item => {
        const card = document.createElement('div');
        card.className = `inventory-card type-${item.type}`;

        let detailsHtml = '';
        if (item.type === 'product' && item.data && item.data.stats) {
            detailsHtml = '<div class="item-details">';
            for (const [s, v] of Object.entries(item.data.stats)) {
                detailsHtml += `<span>${s}: ${v} </span> `;
            }
            detailsHtml += '</div>';
        }

        card.innerHTML = `
            <span class="item-type-tag">${item.type}</span>
            <div class="item-name">${item.data?.name || item.name}</div>
            <div class="item-qty">x${item.quantity}</div>
            ${detailsHtml}
        `;
        display.appendChild(card);
    });
}

// --- Map Module Logic (Grid Redesign) ---
let mapData = null;

async function initMapModule() {
    console.log("Map Grid Init");
    await refreshMap();

    // Setup Nav Buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.onclick = () => movePlayer(btn.getAttribute('data-dir'));
    });

    document.getElementById('scavenge-btn').onclick = scavengeCurrentCell;
}

async function refreshMap() {
    const res = await fetch('/api/map/data');
    mapData = await res.json();
    renderGrid();
    updateSidebar(findCell(mapData.player_pos.x, mapData.player_pos.y));
}

function renderGrid() {
    const container = document.getElementById('grid-container');
    if (!container) return;

    container.style.gridTemplateColumns = `repeat(${mapData.size}, 60px)`;
    container.innerHTML = '';

    for (let y = 0; y < mapData.size; y++) {
        for (let x = 0; x < mapData.size; x++) {
            const cell = findCell(x, y);
            const div = document.createElement('div');
            div.className = `grid-cell ${cell.discovered ? cell.type : 'unknown'}`;
            div.id = `cell-${x}-${y}`;

            let icon = '';
            if (cell.discovered) {
                if (cell.type === 'forest') icon = '🌲';
                if (cell.type === 'mountains') icon = '⛰️';
                if (cell.type === 'lab') icon = '🏠';
                if (cell.type === 'river') icon = '🌊';
            }
            div.innerText = icon;

            if (x === mapData.player_pos.x && y === mapData.player_pos.y) {
                const p = document.createElement('div');
                p.className = 'player-marker';
                p.innerText = '👤';
                div.appendChild(p);
            }
            container.appendChild(div);
        }
    }
}

function findCell(x, y) {
    return mapData.cells.find(c => c.x === x && c.y === y);
}

function updateSidebar(cell) {
    document.getElementById('cell-name').innerText = cell.name;
    document.getElementById('cell-coords').innerText = `Coordinates: [${cell.x}, ${cell.y}]`;

    const resDiv = document.getElementById('cell-resources');
    if (cell.resources.length > 0) {
        resDiv.innerHTML = '<strong>Resources:</strong><br>' +
            cell.resources.map(r => `<span>${r.replace('mat_', '')}</span>`).join('');
    } else {
        resDiv.innerHTML = '<p class="dim">No natural resources here.</p>';
    }

    const sBtn = document.getElementById('scavenge-btn');
    sBtn.disabled = (cell.type === 'lab');
}

async function movePlayer(direction) {
    const res = await fetch('/api/map/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction })
    });

    const data = await res.json();
    if (data.success) {
        // Full refresh to update Fog of War for all cells
        await refreshMap();
    }
}

async function scavengeCurrentCell() {
    const res = await fetch('/api/map/scavenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });

    const result = await res.json();
    if (result.success) {
        showLootReport(result.loot);
    }
}

function showLootReport(loot) {
    const report = document.getElementById('loot-report');
    const list = document.getElementById('loot-list');

    report.classList.remove('hidden');
    list.innerHTML = '';

    if (loot.length === 0) {
        list.innerHTML = '<p>Nothing found this time.</p>';
        return;
    }

    loot.forEach(item => {
        const div = document.createElement('div');
        div.className = 'loot-item';
        div.innerHTML = `<span>${item.id}</span> <span>x${item.quantity}</span>`;
        list.appendChild(div);
    });
}
