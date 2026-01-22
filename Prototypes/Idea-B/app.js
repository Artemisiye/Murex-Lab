// The Forge Dashboard - Game Logic

// Game State
const gameState = {
    resources: {
        copper_ore: 5,
        tin_ore: 5,
        iron_ore: 2,
        coal: 10,
    },
    gold: 50,
    day: 1,
    totalCrafted: 0,
    miningEnergy: 100,
    maxMiningEnergy: 100,
    orders: [],
    completedOrders: 0,
};

// Recipes Database
const recipes = {
    smelter: [
        {
            id: 'copper_ingot',
            name: 'Copper Ingot',
            inputs: { copper_ore: 1, coal: 1 },
            output: 'copper_ingot',
            time: 3000,
            quality: 1,
            value: 10
        },
        {
            id: 'tin_ingot',
            name: 'Tin Ingot',
            inputs: { tin_ore: 1, coal: 1 },
            output: 'tin_ingot',
            time: 3000,
            quality: 1,
            value: 10
        },
        {
            id: 'iron_ingot',
            name: 'Iron Ingot',
            inputs: { iron_ore: 1, coal: 2 },
            output: 'iron_ingot',
            time: 4000,
            quality: 1,
            value: 20
        },
        {
            id: 'bronze_alloy',
            name: 'Bronze Alloy',
            inputs: { copper_ingot: 1, tin_ingot: 1 },
            output: 'bronze_ingot',
            time: 5000,
            quality: 2,
            value: 35
        },
    ],
    forge: [
        {
            id: 'copper_sword',
            name: 'Copper Sword',
            inputs: { copper_ingot: 2 },
            output: 'copper_sword',
            time: 4000,
            quality: 1,
            value: 30
        },
        {
            id: 'bronze_sword',
            name: 'Bronze Sword',
            inputs: { bronze_ingot: 2 },
            output: 'bronze_sword',
            time: 6000,
            quality: 2,
            value: 80
        },
        {
            id: 'iron_sword',
            name: 'Iron Sword',
            inputs: { iron_ingot: 3 },
            output: 'iron_sword',
            time: 7000,
            quality: 2,
            value: 100
        },
    ]
};

// Station States
const stations = {
    smelter: {
        name: '🔥 Smelter',
        level: 1,
        currentJob: null,
        progress: 0,
        queue: []
    },
    forge: {
        name: '⚒️ Forge',
        level: 1,
        currentJob: null,
        progress: 0,
        queue: []
    }
};

// Initialize UI
function init() {
    updateResourceDisplay();
    updateStatsDisplay();
    renderStations();
    startGameLoop();
}

function updateResourceDisplay() {
    const resourcesDiv = document.getElementById('resources');
    resourcesDiv.innerHTML = '';

    for (const [resource, count] of Object.entries(gameState.resources)) {
        const resourceDiv = document.createElement('div');
        resourceDiv.className = 'resource-item';
        resourceDiv.innerHTML = `
            <span class="resource-name">${formatResourceName(resource)}</span>
            <span class="resource-count">${count}</span>
        `;
        resourcesDiv.appendChild(resourceDiv);
    }
}

function updateStatsDisplay() {
    document.getElementById('gold').textContent = gameState.gold;
    document.getElementById('day').textContent = gameState.day;
    document.getElementById('totalCrafted').textContent = gameState.totalCrafted;

    const energyEl = document.getElementById('energy');
    if (energyEl) {
        energyEl.textContent = `${gameState.miningEnergy}/${gameState.maxMiningEnergy}`;
    }

    const ordersEl = document.getElementById('ordersCount');
    if (ordersEl) {
        ordersEl.textContent = gameState.completedOrders;
    }
}

function formatResourceName(resource) {
    return resource.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

function renderStations() {
    const stationsDiv = document.getElementById('stations');
    stationsDiv.innerHTML = '';

    for (const [stationId, station] of Object.entries(stations)) {
        const stationDiv = document.createElement('div');
        stationDiv.className = 'station-card';

        const recipesOptions = recipes[stationId].map(recipe => {
            const canCraft = canCraftRecipe(recipe);
            const disabled = !canCraft ? 'disabled' : '';
            return `<option value="${recipe.id}" ${disabled}>${recipe.name} (+${recipe.quality}) - ${recipe.time / 1000}s</option>`;
        }).join('');

        stationDiv.innerHTML = `
            <div class="station-header">
                <span class="station-name">${station.name}</span>
                <span class="station-level">Level ${station.level}</span>
            </div>
            
            <select class="recipe-select" id="recipe-${stationId}">
                <option value="">Select Recipe...</option>
                ${recipesOptions}
            </select>
            
            <button class="craft-btn" onclick="queueCraft('${stationId}')">
                Add to Queue
            </button>
            
            ${station.currentJob ? `
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-${stationId}" style="width: ${station.progress}%">
                        ${Math.round(station.progress)}%
                    </div>
                </div>
                <div style="margin-top: 10px; text-align: center;">
                    Crafting: ${station.currentJob.name}
                    <span class="quality-badge q${station.currentJob.quality}">+${station.currentJob.quality}</span>
                </div>
            ` : ''}
            
            ${station.queue.length > 0 ? `
                <div class="queue">
                    <strong>Queue (${station.queue.length}):</strong>
                    ${station.queue.slice(0, 3).map(job => `
                        <div class="queue-item">
                            ${job.name} 
                            <span class="quality-badge q${job.quality}">+${job.quality}</span>
                        </div>
                    `).join('')}
                    ${station.queue.length > 3 ? `<div class="queue-item">...and ${station.queue.length - 3} more</div>` : ''}
                </div>
            ` : ''}
        `;

        stationsDiv.appendChild(stationDiv);
    }
}

function canCraftRecipe(recipe) {
    for (const [resource, needed] of Object.entries(recipe.inputs)) {
        if ((gameState.resources[resource] || 0) < needed) {
            return false;
        }
    }
    return true;
}

function queueCraft(stationId) {
    const selectElement = document.getElementById(`recipe-${stationId}`);
    const recipeId = selectElement.value;

    if (!recipeId) return;

    const recipe = recipes[stationId].find(r => r.id === recipeId);
    if (!recipe || !canCraftRecipe(recipe)) {
        showMessage('Not enough resources!', 'error');
        return;
    }

    // Consume resources
    for (const [resource, amount] of Object.entries(recipe.inputs)) {
        gameState.resources[resource] -= amount;
    }

    // Add to queue or start immediately
    const station = stations[stationId];
    if (!station.currentJob) {
        startCrafting(stationId, recipe);
    } else {
        station.queue.push({ ...recipe, startTime: null });
    }

    updateResourceDisplay();
    renderStations();
    showMessage(`Queued: ${recipe.name}`);
}

function startCrafting(stationId, recipe) {
    const station = stations[stationId];
    station.currentJob = {
        ...recipe,
        startTime: Date.now()
    };
    station.progress = 0;
}

function updateStations(deltaTime) {
    for (const [stationId, station] of Object.entries(stations)) {
        if (station.currentJob) {
            const elapsed = Date.now() - station.currentJob.startTime;
            station.progress = Math.min(100, (elapsed / station.currentJob.time) * 100);

            // Update progress bar
            const progressBar = document.getElementById(`progress-${stationId}`);
            if (progressBar) {
                progressBar.style.width = station.progress + '%';
                progressBar.textContent = Math.round(station.progress) + '%';
            }

            // Complete crafting
            if (station.progress >= 100) {
                completeCrafting(stationId);
            }
        }
    }
}

function completeCrafting(stationId) {
    const station = stations[stationId];
    const job = station.currentJob;

    // Add output to resources
    if (!gameState.resources[job.output]) {
        gameState.resources[job.output] = 0;
    }
    gameState.resources[job.output]++;

    // Add gold
    gameState.gold += job.value;
    gameState.totalCrafted++;

    showMessage(`✓ Crafted: ${job.name} (+${job.value} gold)`);

    // Start next in queue
    if (station.queue.length > 0) {
        const nextJob = station.queue.shift();
        startCrafting(stationId, nextJob);
    } else {
        station.currentJob = null;
        station.progress = 0;
    }

    updateResourceDisplay();
    updateStatsDisplay();
    renderStations();
}

// Mining minigame
let miningActive = false;
let miningTimer = 0;
let targetZone = 0.5;

function startMining() {
    if (gameState.miningEnergy < 10) {
        showMessage('Not enough energy! Wait for recharge.', 'error');
        return;
    }

    miningActive = true;
    miningTimer = 0;
    targetZone = 0.3 + Math.random() * 0.4; // Random target between 0.3-0.7

    showMiningUI();
}

function showMiningUI() {
    const existingUI = document.getElementById('mining-ui');
    if (existingUI) existingUI.remove();

    const miningDiv = document.createElement('div');
    miningDiv.id = 'mining-ui';
    miningDiv.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);padding:30px;border-radius:10px;z-index:1000;';

    miningDiv.innerHTML = `
        <h2 style="color:#f39c12;text-align:center;">⛏️ MINE ORE</h2>
        <p style="color:#eee;text-align:center;">Click when the bar is in the TARGET zone!</p>
        <div style="width:400px;height:30px;background:#333;position:relative;margin:20px 0;border-radius:5px;overflow:hidden;">
            <div id="mining-bar" style="width:0%;height:100%;background:linear-gradient(90deg,#3498db,#2ecc71);transition:width 0.05s;"></div>
            <div style="position:absolute;left:${targetZone * 100}%;width:15%;height:100%;background:rgba(46,204,113,0.3);border:2px solid #2ecc71;"></div>
        </div>
        <button onclick="attemptMine()" style="width:100%;padding:15px;background:#3498db;border:none;color:white;font-size:18px;border-radius:5px;cursor:pointer;">MINE!</button>
        <button onclick="closeMining()" style="width:100%;padding:10px;background:#e74c3c;border:none;color:white;margin-top:10px;border-radius:5px;cursor:pointer;">Cancel</button>
    `;

    document.body.appendChild(miningDiv);
    updateMiningBar();
}

function updateMiningBar() {
    if (!miningActive) return;

    miningTimer += 0.02;
    const progress = (Math.sin(miningTimer * 3) + 1) / 2; // Oscillate 0-1

    const bar = document.getElementById('mining-bar');
    if (bar) {
        bar.style.width = (progress * 100) + '%';
    }

    setTimeout(updateMiningBar, 50);
}

function attemptMine() {
    const progress = (Math.sin(miningTimer * 3) + 1) / 2;
    const success = Math.abs(progress - targetZone) < 0.075; // Hit zone

    gameState.miningEnergy -= 10;

    if (success) {
        // Big reward
        const oreTypes = ['copper_ore', 'tin_ore', 'iron_ore'];
        const ore = oreTypes[Math.floor(Math.random() * oreTypes.length)];
        gameState.resources[ore] = (gameState.resources[ore] || 0) + 8;
        gameState.resources.coal = (gameState.resources.coal || 0) + 4;
        showMessage('⭐ PERFECT! +8 Ore, +4 Coal', 'success');
    } else {
        // Small reward
        gameState.resources.copper_ore = (gameState.resources.copper_ore || 0) + 2;
        gameState.resources.coal = (gameState.resources.coal || 0) + 1;
        showMessage('Missed target. +2 Copper, +1 Coal', 'error');
    }

    updateResourceDisplay();
    updateStatsDisplay();
    closeMining();
}

function closeMining() {
    miningActive = false;
    const ui = document.getElementById('mining-ui');
    if (ui) ui.remove();
}

// Energy regeneration
setInterval(() => {
    if (gameState.miningEnergy < gameState.maxMiningEnergy) {
        gameState.miningEnergy = Math.min(gameState.maxMiningEnergy, gameState.miningEnergy + 1);
        updateStatsDisplay();
    }
}, 1000);

// Order system
function generateOrder() {
    const orderTypes = [
        { item: 'copper_sword', name: 'Copper Sword', count: 3, reward: 150, deadline: 60 },
        { item: 'bronze_sword', name: 'Bronze Sword', count: 2, reward: 300, deadline: 90 },
        { item: 'iron_sword', name: 'Iron Sword', count: 1, reward: 200, deadline: 50 },
    ];

    const order = { ...orderTypes[Math.floor(Math.random() * orderTypes.length)] };
    order.id = Date.now();
    order.timeLeft = order.deadline;
    order.progress = 0;

    gameState.orders.push(order);
    renderOrders();
    showMessage(`📜 New Order: ${order.count}x ${order.name} in ${order.deadline}s for ${order.reward} gold!`);
}

function updateOrders() {
    for (let i = gameState.orders.length - 1; i >= 0; i--) {
        const order = gameState.orders[i];
        order.timeLeft -= 0.1;

        // Check progress
        const currentCount = gameState.resources[order.item] || 0;
        order.progress = Math.min(currentCount, order.count);

        // Complete
        if (order.progress >= order.count) {
            gameState.resources[order.item] -= order.count;
            gameState.gold += order.reward;
            gameState.completedOrders++;
            showMessage(`✅ Order Complete! +${order.reward} gold`);
            gameState.orders.splice(i, 1);
        }
        // Failed
        else if (order.timeLeft <= 0) {
            showMessage(`❌ Order Failed: ${order.name}`, 'error');
            gameState.orders.splice(i, 1);
        }
    }
    renderOrders();
}

function renderOrders() {
    let ordersDiv = document.getElementById('orders-panel');
    if (!ordersDiv) return;

    if (gameState.orders.length === 0) {
        ordersDiv.innerHTML = '<div style="text-align:center;opacity:0.6;padding:20px;">No active orders</div>';
        return;
    }

    ordersDiv.innerHTML = gameState.orders.map(order => `
        <div style="background:rgba(255,255,255,0.05);padding:10px;margin-bottom:10px;border-radius:5px;border-left:3px solid #f39c12;">
            <div style="font-weight:bold;">${order.count}x ${order.name}</div>
            <div style="font-size:0.9em;margin-top:5px;">
                Progress: ${order.progress}/${order.count} | 
                Time: ${Math.ceil(order.timeLeft)}s | 
                Reward: ${order.reward}g
            </div>
            <div style="width:100%;height:5px;background:#333;margin-top:5px;border-radius:3px;overflow:hidden;">
                <div style="width:${(order.progress / order.count) * 100}%;height:100%;background:#2ecc71;"></div>
            </div>
        </div>
    `).join('');
}

// Generate orders periodically
setInterval(generateOrder, 45000); // Every 45 seconds
setTimeout(generateOrder, 5000); // First order after 5s

function showMessage(text, type = 'success') {
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.textContent = text;
    if (type === 'error') {
        messageDiv.style.background = 'rgba(231, 76, 60, 0.9)';
    }

    document.body.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Game Loop
function startGameLoop() {
    setInterval(() => {
        updateStations();
        updateOrders();
    }, 100);
}

// Initialize on load
window.addEventListener('DOMContentLoaded', init);
