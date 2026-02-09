const CONFIG = {
    SCREEN_W: 480,
    SCREEN_H: 270,
    SCALE: 4,
    FPS: 60,
    COLORS: {
        BG: '#0c0b09',
        FG: '#d4af37', // Gold
        FG_DIM: '#8a7d5b',
        HIGHLIGHT: '#ffffff',
        ACCENT: '#a03d21', // Red/Rust
        SHADOW: '#1a1814',
        PANEL: '#15130f',
        GRID: '#2a261f',
        METER: '#1a4e2a'
    },
    UI_FONT: 'Silkscreen',
    // Font Normalization Profiles
    // 'scale' is the multiplier needed to make the GLYPH height match the requested size.
    FONT_PROFILES: {
        'Silkscreen': { scale: 1.0 },
        'Echo Garalde TTF': { scale: 2.285 }, // 32px request -> 14px actual glyph
        'Echo Garalde OTF': { scale: 2.285 },
        'Echo Pixel Garalde': { scale: 2.22 }, // WOFF version slightly different
        'Perfect DOS VGA 437': { scale: 1.0 },
        'Fixedsys Excelsior 3.01': { scale: 1.0 },
        'Tamzen': { scale: 1.0 },
        'Minecraftia': { scale: 1.0 }
    }
};

class RetroEngine {
    constructor() {
        this.canvas = document.getElementById('virtual-console');
        this.ctx = this.canvas.getContext('2d', { alpha: false });

        this.buffer = document.createElement('canvas');
        this.bCtx = this.buffer.getContext('2d');

        this.mouse = { x: 0, y: 0, down: false, clicked: false };
        this.viewport = { x: 0, y: 0, w: 0, h: 0, scale: 1 };

        this.widgets = [];
        this.state = {
            view: 'WORKSHOP',
            inventory: [],
            blueprints: [],
            minions: [],
            map: null,
            resources: { gold: 0, essence: 100, essenceMax: 100 },
            selectedBlueprint: null,
            selectingSlot: null,
            craftingSlots: {},
            scrollOffset: 0,
            loading: true,
            settingsTab: 'FONTS',
            fontSettings: {
                family: 'Silkscreen',
                weight: 400,
                spacing: 0,
                testSize: 16
            },
            displaySettings: {
                scale: 4
            }
        };
        this.fontsReady = false;
        this.activeDropdown = null;

        // Offscreen buffer for bit-perfect text thresholding
        this.textBuffer = document.createElement('canvas');
        this.tbCtx = this.textBuffer.getContext('2d', { willReadFrequently: true });

        this.init();
    }

    async init() {
        await document.fonts.ready;
        this.fontsReady = true;

        this.resize();

        window.addEventListener('mousemove', e => this.updateMouse(e));
        window.addEventListener('mousedown', () => { this.mouse.down = true; this.mouse.clicked = true; });
        window.addEventListener('mouseup', () => { this.mouse.down = false; });
        window.addEventListener('keydown', e => this.handleKey(e));

        this.lastTime = 0;
        await this.refreshData();
        this.setView('WORKSHOP');
        requestAnimationFrame(t => this.loop(t));
    }

    async refreshData() {
        this.state.loading = true;
        try {
            const [bpRes, invRes, mapRes, minRes] = await Promise.all([
                fetch('/api/blueprints'),
                fetch('/api/inventory'),
                fetch('/api/map/data'),
                fetch('/api/minions')
            ]);
            this.state.blueprints = await bpRes.json();
            const invData = await invRes.json();
            this.state.inventory = invData.items || [];
            this.state.resources.gold = invData.gold || 0;
            this.state.map = await mapRes.json();
            this.state.minions = await minRes.json() || [];
        } catch (e) { console.error("Data refresh failed", e); }
        this.state.loading = false;
        this.buildUI();
    }

    resize() {
        const dpr = window.devicePixelRatio || 1;
        this.viewport.scale = this.state.displaySettings?.scale || CONFIG.SCALE || 4;

        // Hardcode the internal buffer to 480x270
        this.buffer.width = CONFIG.SCREEN_W;
        this.buffer.height = CONFIG.SCREEN_H;

        // The canvas is exactly the scaled native resolution
        this.canvas.width = this.buffer.width * this.viewport.scale;
        this.canvas.height = this.buffer.height * this.viewport.scale;

        // Apply physical style dimensions (accounting for DPR)
        this.canvas.style.width = `${(this.canvas.width / dpr)}px`;
        this.canvas.style.height = `${(this.canvas.height / dpr)}px`;

        this.viewport.w = this.canvas.width;
        this.viewport.h = this.canvas.height;
        this.viewport.x = 0;
        this.viewport.y = 0;

        this.buildUI();

        // Center the canvas in the window via CSS if it's smaller than the window
        this.canvas.style.position = 'absolute';
        this.canvas.style.left = '50%';
        this.canvas.style.top = '50%';
        this.canvas.style.transform = 'translate(-50%, -50%)';
    }

    updateMouse(e) {
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        const mousePhysicalX = (e.clientX - rect.left) * dpr;
        const mousePhysicalY = (e.clientY - rect.top) * dpr;

        this.mouse.x = Math.floor(mousePhysicalX / this.viewport.scale);
        this.mouse.y = Math.floor(mousePhysicalY / this.viewport.scale);
    }

    async handleKey(e) {
        if (this.state.view === 'MAP') {
            const keys = { 'w': 'north', 's': 'south', 'a': 'west', 'd': 'east', 'arrowup': 'north', 'arrowdown': 'south', 'arrowleft': 'west', 'arrowright': 'east' };
            const action = keys[e.key.toLowerCase()];
            if (action) {
                await fetch('/api/map/move', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ direction: action }) });
                await this.refreshData();
            }
        }
    }

    setView(viewName) {
        this.state.view = viewName;
        this.state.selectedBlueprint = null;
        this.state.selectingSlot = null;
        this.state.craftingSlots = {};
        this.state.scrollOffset = 0;
        this.buildUI();
    }

    buildUI() {
        this.widgets = [];
        const sidebarW = 78;
        const padding = 2;
        const bW = this.buffer.width;
        const bH = this.buffer.height;

        // --- SIDEBAR ---
        this.widgets.push(new Rect(0, 0, sidebarW, bH, CONFIG.COLORS.PANEL, true));
        this.widgets.push(new Rect(sidebarW, 0, 1, bH, CONFIG.COLORS.FG_DIM, true));

        this.widgets.push(new Label(padding + 4, padding + 6, "MUREX LAB", CONFIG.COLORS.HIGHLIGHT, 12));
        this.widgets.push(new Rect(padding + 4, padding + 20, sidebarW - 12, 1, CONFIG.COLORS.FG_DIM, true));

        const navItems = [
            { id: 'WORKSHOP', label: 'Workshop' },
            { id: 'VAULT', label: 'Inventory' },
            { id: 'MAP', label: 'Map' },
            { id: 'TEAM', label: 'Minions' },
            { id: 'SETTINGS', label: 'Settings' }
        ];
        navItems.forEach((btn, i) => {
            const active = this.state.view === btn.id;
            this.widgets.push(new NavButton(0, 48 + (i * 24), sidebarW, 20, btn.label, () => this.setView(btn.id), active));
        });

        const footerY = bH - 45;
        this.widgets.push(new Button(padding + 4, footerY - 22, sidebarW - 10, 16, "[ RETRO ]", () => { }, true, true));
        this.widgets.push(new Button(padding + 4, footerY - 40, sidebarW - 10, 16, "[ MODERN ]", () => window.location.href = "/", false, true));

        this.widgets.push(new Label(padding + 4, footerY, "ESSENCE", CONFIG.COLORS.FG_DIM, 8));
        this.widgets.push(new Meter(padding + 4, footerY + 10, sidebarW - 10, 4, this.state.resources.essence, 100, CONFIG.COLORS.METER));
        this.widgets.push(new Label(padding + 4, footerY + 18, `GOLD: ${this.state.resources.gold}`, CONFIG.COLORS.FG, 8));
        this.widgets.push(new Label(padding + 4, footerY + 28, "DAY 1", CONFIG.COLORS.FG_DIM, 8));

        // --- MAIN CONTENT AREA ---
        const mainX = sidebarW + 15;
        const mainW = bW - mainX - 10;

        const viewTitles = {
            WORKSHOP: 'ARTIFICER WORKSHOP',
            VAULT: 'STORAGE VAULT',
            MAP: 'WORLD EXPLORATION',
            TEAM: 'MINION COMMAND',
            SETTINGS: 'SYSTEM SETTINGS'
        };
        this.widgets.push(new Label(mainX, 10, viewTitles[this.state.view] || this.state.view, CONFIG.COLORS.HIGHLIGHT, 12));

        const contentY = 32;
        const contentH = bH - 42;
        this.widgets.push(new Rect(mainX, contentY, mainW, contentH, CONFIG.COLORS.PANEL, true));
        this.widgets.push(new Rect(mainX, contentY, mainW, contentH, CONFIG.COLORS.FG_DIM, false));

        if (this.state.view === 'WORKSHOP') this.buildWorkshopView(mainX, contentY + 5, mainW, contentH - 10);
        else if (this.state.view === 'VAULT') this.buildVaultView(mainX, contentY + 5, mainW, contentH - 10);
        else if (this.state.view === 'MAP') this.buildMapView(mainX + 5, contentY + 5, mainW - 10, contentH - 10);
        else if (this.state.view === 'TEAM') this.buildTeamView(mainX, contentY + 5, mainW, contentH - 10);
        else if (this.state.view === 'SETTINGS') this.buildSettingsView(mainX, contentY + 5, mainW, contentH - 10);
    }

    buildSettingsView(x, y, w, h) {
        const tabs = ['FONTS', 'AUDIO', 'DISPLAY', 'DEBUG'];
        const tabW = Math.floor(w / tabs.length);
        tabs.forEach((tab, i) => {
            const active = this.state.settingsTab === tab;
            this.widgets.push(new TabButton(x + (i * tabW), y, tabW, 20, tab, () => {
                this.state.settingsTab = tab;
                this.buildUI();
            }, active));
        });

        const panelY = y + 25;
        const panelH = h - 25;

        if (this.state.settingsTab === 'FONTS') {
            this.buildFontSettings(x + 10, panelY, w - 20, panelH);
        } else if (this.state.settingsTab === 'DISPLAY') {
            this.buildDisplaySettings(x + 10, panelY, w - 20, panelH);
        } else if (this.state.settingsTab === 'DEBUG') {
            this.buildDebugView(x + 10, panelY, w - 20, panelH);
        } else {
            this.widgets.push(new Label(x + w / 2, panelY + panelH / 2, "MODULE OFFLINE", CONFIG.COLORS.FG_DIM, 8, 'center'));
        }
    }

    buildDebugView(x, y, w, h) {
        const s = this.state.fontSettings;
        let curY = y + 10;
        this.widgets.push(new Label(x, curY, "FONT PIXEL ANALYZER", CONFIG.COLORS.FG_DIM, 8));
        curY += 15;

        // Test Size Slider
        this.widgets.push(new Slider(x, curY, 150, 14, "Test Size", s.testSize, 8, 48, 1, (v) => {
            s.testSize = v;
            this.buildUI();
        }));
        curY += 20;

        this.widgets.push(new Label(x, curY, `Measuring: ${s.family} @ ${s.testSize}px`, CONFIG.COLORS.HIGHLIGHT, 8));
        curY += 20;

        const testChars = ['M', 'Q', 'j', 'H', 'x', '0'];
        this.widgets.push(new Label(x, curY, "CHAR", CONFIG.COLORS.FG_DIM, 8));
        this.widgets.push(new Label(x + 50, curY, "WIDTH", CONFIG.COLORS.FG_DIM, 8));
        this.widgets.push(new Label(x + 100, curY, "HEIGHT", CONFIG.COLORS.FG_DIM, 8));
        this.widgets.push(new Label(x + 160, curY, "BOUNDS(Y)", CONFIG.COLORS.FG_DIM, 8));
        curY += 12;

        testChars.forEach(char => {
            const m = this.measureGlyph(s.family, s.testSize, char);
            // Render the character at the ACTUAL requested size so the user can see blur/sharpness
            this.widgets.push(new Label(x, curY, char, CONFIG.COLORS.HIGHLIGHT, s.testSize, 'left', s.family));

            this.widgets.push(new Label(x + 50, curY + 2, `${m.w}px`, CONFIG.COLORS.FG, 8));
            this.widgets.push(new Label(x + 100, curY + 2, `${m.h}px`, CONFIG.COLORS.FG, 8));
            this.widgets.push(new Label(x + 160, curY + 2, `${m.top}-${m.bottom}px`, CONFIG.COLORS.FG_DIM, 8));

            // Increment Y based on the larger of the font size or measured height
            curY += Math.max(s.testSize, m.h) + 4;
        });

        const infoY = y + h - 40;
        this.widgets.push(new Label(x, infoY, "NOTE: If HEIGHT is unexpectedly large, the font has internal leading.", CONFIG.COLORS.ACCENT, 8));
        this.widgets.push(new Label(x, infoY + 10, "Standard pixel fonts should match size or be slightly smaller.", CONFIG.COLORS.FG_DIM, 8));
    }

    measureGlyph(family, size, char) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 100;
        canvas.height = 100;
        ctx.font = `400 ${size}px "${family}"`;
        ctx.fillStyle = '#FFFFFF';
        ctx.textBaseline = 'top';
        ctx.fillText(char, 20, 20);

        const imgData = ctx.getImageData(0, 0, 100, 100).data;
        let top = 100, bottom = 0, left = 100, right = 0;

        for (let y = 0; y < 100; y++) {
            for (let x = 0; x < 100; x++) {
                const alpha = imgData[(y * 100 + x) * 4 + 3];
                if (alpha > 0) {
                    if (x < left) left = x;
                    if (x > right) right = x;
                    if (y < top) top = y;
                    if (y > bottom) bottom = y;
                }
            }
        }

        return {
            w: right - left + 1,
            h: bottom - top + 1,
            top: top,
            bottom: bottom,
            left: left,
            right: right
        };
    }

    buildDisplaySettings(x, y, w, h) {
        const s = this.state.displaySettings;
        let curY = y + 10;
        this.widgets.push(new Label(x, curY, "DISPLAY CONFIGURATION", CONFIG.COLORS.FG_DIM, 8));
        curY += 20;

        this.widgets.push(new Label(x, curY, "Resolution:", CONFIG.COLORS.FG, 8));
        this.widgets.push(new Label(x + 80, curY, `${CONFIG.SCREEN_W}x${CONFIG.SCREEN_H} (Native)`, CONFIG.COLORS.HIGHLIGHT, 8));
        curY += 18;

        this.widgets.push(new Slider(x, curY, w / 2, 14, "Integer Scale", s.scale, 1, 6, 1, (v) => {
            s.scale = v;
            this.resize();
            // Sync OS window size if running in native app mode
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.resize(CONFIG.SCREEN_W * v, CONFIG.SCREEN_H * v);
            }
        }));
    }

    buildFontSettings(x, y, w, h) {
        const s = this.state.fontSettings;
        const colW = Math.floor(w / 2) - 10;

        // Column 1: Typography
        let curY = y + 10;
        this.widgets.push(new Label(x, curY, "TYPOGRAPHY", CONFIG.COLORS.FG_DIM, 8));
        curY += 15;

        // Family Dropdown
        this.widgets.push(new Label(x, curY, "Family", CONFIG.COLORS.FG, 8));
        const families = [
            'Silkscreen', 'Echo Pixel Garalde', 'Echo Garalde TTF', 'Echo Garalde OTF', 'Valmeria', 'Oldbitz', 'Ithaca', 'Perfect DOS VGA 437', 'Fixedsys Excelsior 3.01', 'Tamzen', 'Minecraftia',
            'Press Start 2P', 'VT323', 'DotGothic16', 'Share Tech Mono', 'Roboto Mono', 'Cinzel', 'Inter'
        ];
        this.widgets.push(new Dropdown(x + 60, curY - 2, colW - 60, 14, families, s.family, (v) => {
            s.family = v;
            this.buildUI();
        }));
        curY += 18;

        // Column 2: Effects
        curY = y + 10;
        const col2X = x + colW + 20;
        curY += 30;

        // Preview Area
        this.widgets.push(new Label(col2X, curY, "PREVIEW", CONFIG.COLORS.FG_DIM, 8));
        curY += 15;
        this.widgets.push(new Rect(col2X, curY, colW, 50, CONFIG.COLORS.SHADOW, true));
        this.widgets.push(new Label(col2X + colW / 2, curY + 15, "ABCDEFGHIJKL", CONFIG.COLORS.HIGHLIGHT, 12, 'center', s.family));
        this.widgets.push(new Label(col2X + colW / 2, curY + 30, "0123456789!?", CONFIG.COLORS.FG, 12, 'center', s.family));
    }

    buildWorkshopView(x, y, w, h) {
        const colW = Math.floor(w / 3);
        const dividerCol = CONFIG.COLORS.SHADOW;

        this.widgets.push(new Label(x + 5, y, "BLUEPRINTS", CONFIG.COLORS.FG_DIM, 8));
        this.state.blueprints.forEach((bp, i) => {
            const active = this.state.selectedBlueprint && this.state.selectedBlueprint.id === bp.id;
            this.widgets.push(new ListButton(x + 5, y + 16 + (i * 20), colW - 10, 18, bp.name, bp.station || "FORGE", () => {
                this.state.selectedBlueprint = bp;
                this.state.craftingSlots = {};
                this.state.selectingSlot = null;
                this.buildUI();
            }, active));
        });

        this.widgets.push(new Rect(x + colW, y, 1, h, dividerCol, true));

        if (this.state.selectedBlueprint) {
            this.buildSelectedBlueprintSlots(x + colW + 5, y, colW - 10, h);
        } else {
            this.widgets.push(new Label(x + colW + 10, y + 20, "SELECT BLUEPRINT", CONFIG.COLORS.FG_DIM, 8));
        }

        this.widgets.push(new Rect(x + (colW * 2), y, 1, h, dividerCol, true));

        if (this.state.selectingSlot) {
            this.buildComponentSelector(x + (colW * 2) + 5, y, colW - 10, h);
        } else {
            this.widgets.push(new Label(x + (colW * 2) + 10, y + 20, "SELECT SLOT", CONFIG.COLORS.FG_DIM, 8));
        }
    }

    async buildSelectedBlueprintSlots(x, y, w, h) {
        const bp = this.state.selectedBlueprint;
        this.widgets.push(new Label(x, y, bp.name.toUpperCase(), CONFIG.COLORS.HIGHLIGHT, 8));

        if (!bp.slots) {
            const res = await fetch(`/api/blueprint/${bp.id}`);
            this.state.selectedBlueprint = await res.json();
            this.buildUI(); return;
        }

        let slotY = y + 20;
        bp.slots.forEach(slot => {
            const selItem = this.state.craftingSlots[slot.id];
            const label = selItem ? selItem.name : `[ EMPTY ${slot.label} ]`;
            const active = this.state.selectingSlot && this.state.selectingSlot.id === slot.id;
            this.widgets.push(new ListButton(x, slotY, w, 18, label, (slot.type || "ITEM").toUpperCase(), () => {
                this.state.selectingSlot = slot; this.buildUI();
            }, active));
            slotY += 21;
        });

        if (bp.slots.length > 0) {
            this.widgets.push(new Button(x, y + h - 22, w, 20, "CRAFT ITEM", () => this.handleCraft()));
        }
    }

    async buildComponentSelector(x, y, w, h) {
        const slot = this.state.selectingSlot;
        this.widgets.push(new Label(x, y, `FIT: ${slot.label.toUpperCase()}`, CONFIG.COLORS.FG, 8));

        const res = await fetch(`/api/components/${this.state.selectedBlueprint.id}/${slot.id}`);
        const components = await res.json();

        if (components.length === 0) {
            this.widgets.push(new Label(x, y + 20, "NO VALID COMPONENTS", CONFIG.COLORS.FG_DIM, 8));
        }

        components.forEach((comp, i) => {
            this.widgets.push(new ListButton(x, y + 20 + (i * 20), w, 18, comp.name, `QTY:${comp.quantity}`, () => {
                this.state.craftingSlots[slot.id] = comp;
                this.buildUI();
            }));
        });
    }

    async handleCraft() {
        const components = {};
        for (let slotId in this.state.craftingSlots) components[slotId] = this.state.craftingSlots[slotId].id;
        try {
            const res = await fetch('/api/craft_item', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ blueprint_id: this.state.selectedBlueprint.id, components: components })
            });
            const result = await res.json();
            if (result.success) {
                await this.refreshData();
                this.setView('VAULT');
            } else {
                console.warn("Crafting failed:", result.error || "Unknown error");
                await this.refreshData();
            }
        } catch (e) { console.error("Communication error during crafting:", e); }
    }

    buildVaultView(x, y, w, h) {
        const items = this.state.inventory || [];
        items.forEach((item, i) => {
            if (item) this.widgets.push(new ListButton(x + 5, y + 10 + (i * 20), w - 10, 18, item.name, `x${item.quantity}`, () => { }));
        });
    }

    buildTeamView(x, y, w, h) {
        const minions = this.state.minions || [];
        minions.forEach((m, i) => {
            if (m) this.widgets.push(new ListButton(x + 5, y + 10 + (i * 20), w - 10, 18, m.name, `L${m.level}`, () => { }));
        });
    }

    buildMapView(x, y, w, h) {
        if (!this.state.map) return;
        this.widgets.push(new MapWidget(x, y, w, h, this.state.map));
    }

    loop(timestamp) {
        const dt = timestamp - this.lastTime; this.lastTime = timestamp;
        this.update(dt); this.draw();
        this.mouse.clicked = false;
        requestAnimationFrame(t => this.loop(t));
    }

    update(dt) {
        this.widgets.forEach(w => w.update(this.mouse, this));
        if (this.mouse.clicked && this.activeDropdown && !this.activeDropdown.hover) {
            this.activeDropdown.open = false;
            this.activeDropdown = null;
        }
    }

    draw() {
        if (!this.fontsReady) return;
        const b = this.bCtx;
        b.imageSmoothingEnabled = false;
        b.fillStyle = CONFIG.COLORS.BG; b.fillRect(0, 0, this.buffer.width, this.buffer.height);

        // Base widgets
        this.widgets.forEach(w => w.draw(b, this));

        // Top-level widgets (like open dropdowns)
        if (this.activeDropdown) {
            this.activeDropdown.drawList(b, this);
        }

        const ctx = this.ctx;
        ctx.fillStyle = '#000000'; ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(this.buffer, 0, 0, this.viewport.w, this.viewport.h);
    }
}

// --- WIDGETS ---
class Widget { constructor(x, y) { this.x = Math.floor(x); this.y = Math.floor(y); } update(mouse) { } draw(ctx, engine) { } }

class Rect extends Widget {
    constructor(x, y, w, h, color, fill = true) { super(x, y); this.w = Math.floor(w); this.h = Math.floor(h); this.color = color; this.fill = fill; }
    draw(ctx) {
        if (this.fill) { ctx.fillStyle = this.color; ctx.fillRect(this.x, this.y, this.w, this.h); }
        else { ctx.strokeStyle = this.color; ctx.lineWidth = 1; ctx.strokeRect(this.x + 0.5, this.y + 0.5, this.w, this.h); }
    }
}

class Meter extends Widget {
    constructor(x, y, w, h, val, max, color) { super(x, y); this.w = Math.floor(w); this.h = Math.floor(h); this.val = val; this.max = max; this.color = color; }
    draw(ctx) {
        ctx.fillStyle = CONFIG.COLORS.SHADOW; ctx.fillRect(this.x, this.y, this.w, this.h);
        const p = Math.min(1, this.val / (this.max || 1));
        ctx.fillStyle = this.color; ctx.fillRect(this.x, this.y, Math.floor(this.w * p), this.h);
    }
}

class Label extends Widget {
    constructor(x, y, text, color, size, align = 'left', family = null) {
        super(x, y); this.text = text; this.color = color; this.size = size; this.align = align; this.family = family;
    }
    draw(ctx, engine) {
        this.drawText(ctx, engine, this.text, this.x, this.y, this.size, this.color, this.align);
    }

    drawText(ctx, engine, text, x, y, size, color, align) {
        if (!text) return;
        const s = engine.state.fontSettings;
        const family = this.family || CONFIG.UI_FONT;

        // Resolve Normalized Size
        const profile = CONFIG.FONT_PROFILES[family] || { scale: 1.0 };
        const requestSize = Math.round(size * profile.scale);

        // --- PIXEL PERFECT NATIVE RENDER (NO THRESHOLD) ---
        ctx.save();
        ctx.font = `${s.weight} ${requestSize}px "${family}"`;
        ctx.fillStyle = color;
        ctx.textAlign = align;
        ctx.textBaseline = 'top';

        // Snap to the 480x270 native grid
        const snapX = Math.floor(x);
        const snapY = Math.floor(y);

        if (s.spacing !== 0) ctx.letterSpacing = `${s.spacing}px`;
        ctx.fillText(text, snapX, snapY);
        ctx.restore();
    }
}

class Button extends Widget {
    constructor(x, y, w, h, label, callback, active = false, outlineOnly = false) {
        super(x, y); this.w = Math.floor(w); this.h = Math.floor(h);
        this.label = label; this.callback = callback; this.hover = false; this.active = active; this.outlineOnly = outlineOnly;
    }
    update(mouse) { this.hover = (mouse.x >= this.x && mouse.x <= this.x + this.w && mouse.y >= this.y && mouse.y <= this.y + this.h); if (this.hover && mouse.clicked) this.callback(); }
    draw(ctx, engine) {
        const drawX = Math.floor(this.x);
        const drawY = Math.floor(this.y);
        if (!this.outlineOnly) {
            ctx.fillStyle = this.active ? CONFIG.COLORS.FG_DIM : (this.hover ? CONFIG.COLORS.FG : CONFIG.COLORS.BG);
            ctx.fillRect(drawX, drawY, this.w, this.h);
            ctx.strokeStyle = this.hover || this.active ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.SHADOW;
            ctx.strokeRect(drawX + 0.5, drawY + 0.5, this.w - 1, this.h - 1);
        } else {
            ctx.strokeStyle = this.hover ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG_DIM;
            ctx.strokeRect(drawX + 0.5, drawY + 0.5, this.w - 1, this.h - 1);
            if (this.hover) { ctx.fillStyle = "rgba(255,255,255,0.05)"; ctx.fillRect(drawX, drawY, this.w, this.h); }
        }

        const labelColor = (this.hover && !this.outlineOnly) ? CONFIG.COLORS.BG : (this.active ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG);
        const lbl = new Label(drawX + this.w / 2, drawY + this.h / 2 - 4, this.label, labelColor, 8, 'center');
        lbl.draw(ctx, engine);
    }
}

class NavButton extends Button {
    draw(ctx, engine) {
        if (this.active) { ctx.fillStyle = "rgba(212, 175, 55, 0.1)"; ctx.fillRect(this.x, this.y, this.w, this.h); }
        if (this.hover) { ctx.fillStyle = "rgba(255, 255, 255, 0.05)"; ctx.fillRect(this.x, this.y, this.w, this.h); }
        const labelColor = this.active ? CONFIG.COLORS.HIGHLIGHT : (this.hover ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG_DIM);
        const lbl = new Label(this.x + 8, this.y + this.h / 2 - 4, this.label.toUpperCase(), labelColor, 8, 'left');
        lbl.draw(ctx, engine);
        if (this.active) { ctx.fillStyle = CONFIG.COLORS.FG; ctx.fillRect(this.x, this.y, 2, this.h); }
    }
}

class TabButton extends Button {
    draw(ctx, engine) {
        ctx.fillStyle = this.active ? CONFIG.COLORS.PANEL : CONFIG.COLORS.BG;
        ctx.fillRect(this.x, this.y, this.w, this.h);
        ctx.strokeStyle = this.active ? CONFIG.COLORS.FG : CONFIG.COLORS.SHADOW;
        ctx.strokeRect(this.x + 0.5, this.y + 0.5, this.w - 1, this.h - 1);
        const labelColor = this.active ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG_DIM;
        const lbl = new Label(this.x + this.w / 2, this.y + this.h / 2 - 4, this.label, labelColor, 8, 'center');
        lbl.draw(ctx, engine);
    }
}

class ListButton extends Button {
    constructor(x, y, w, h, label, subtext, callback, active = false) { super(x, y, w, h, label, callback, active); this.subtext = subtext; }
    draw(ctx, engine) {
        if (this.active) { ctx.fillStyle = "rgba(212, 175, 55, 0.15)"; ctx.fillRect(this.x, this.y, this.w, this.h); }
        else if (this.hover) { ctx.fillStyle = "rgba(255,255,255,0.05)"; ctx.fillRect(this.x, this.y, this.w, this.h); }

        const mainColor = (this.hover || this.active) ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG;
        const subColor = CONFIG.COLORS.FG_DIM;

        const lblMain = new Label(this.x + 4, this.y + this.h / 2 - 4, this.label, mainColor, 8, 'left');
        const lblSub = new Label(this.x + this.w - 4, this.y + this.h / 2 - 4, this.subtext, subColor, 8, 'right');

        lblMain.draw(ctx, engine);
        lblSub.draw(ctx, engine);

        ctx.strokeStyle = "rgba(255,255,255,0.05)"; ctx.beginPath(); ctx.moveTo(this.x, this.y + this.h); ctx.lineTo(this.x + this.w, this.y + this.h); ctx.stroke();
        if (this.active) { ctx.fillStyle = CONFIG.COLORS.FG; ctx.fillRect(this.x, this.y, 1, this.h); }
    }
}

class Slider extends Widget {
    constructor(x, y, w, h, label, value, min, max, step, callback) {
        super(x, y); this.w = w; this.h = h; this.label = label; this.value = value; this.min = min; this.max = max; this.step = step; this.callback = callback;
        this.dragging = false;
    }
    update(mouse) {
        const handleX = this.x + 60 + ((this.value - this.min) / (this.max - this.min)) * (this.w - 85);
        const hover = (mouse.x >= this.x + 55 && mouse.x <= this.x + this.w && mouse.y >= this.y && mouse.y <= this.y + this.h);
        if (hover && mouse.clicked) this.dragging = true;
        if (!mouse.down) this.dragging = false;

        if (this.dragging) {
            let p = (mouse.x - (this.x + 60)) / (this.w - 85);
            p = Math.max(0, Math.min(1, p));
            let val = this.min + p * (this.max - this.min);
            val = Math.round(val / this.step) * this.step;
            if (val !== this.value) {
                this.value = val;
                this.callback(val);
            }
        }
    }
    draw(ctx, engine) {
        new Label(this.x, this.y + 2, this.label, CONFIG.COLORS.FG, 8).draw(ctx, engine);
        const barX = this.x + 60;
        const barW = this.w - 85;
        ctx.fillStyle = CONFIG.COLORS.SHADOW;
        ctx.fillRect(barX, this.y + 6, barW, 2);

        const handlePos = ((this.value - this.min) / (this.max - this.min)) * barW;
        ctx.fillStyle = CONFIG.COLORS.FG;
        ctx.fillRect(barX + handlePos - 2, this.y + 3, 4, 8);

        new Label(this.x + this.w, this.y + 2, String(this.value.toFixed(this.step < 1 ? 1 : 0)), CONFIG.COLORS.HIGHLIGHT, 8, 'right').draw(ctx, engine);
    }
}

class Toggle extends Widget {
    constructor(x, y, w, h, label, value, callback) {
        super(x, y); this.w = w; this.h = h; this.label = label; this.value = value; this.callback = callback;
    }
    update(mouse) {
        const hover = (mouse.x >= this.x && mouse.x <= this.x + this.w && mouse.y >= this.y && mouse.y <= this.y + this.h);
        if (hover && mouse.clicked) {
            this.value = !this.value;
            this.callback(this.value);
        }
    }
    draw(ctx, engine) {
        new Label(this.x, this.y + 2, this.label, CONFIG.COLORS.FG, 8).draw(ctx, engine);
        const btnX = this.x + 60;
        ctx.fillStyle = this.value ? CONFIG.COLORS.METER : CONFIG.COLORS.ACCENT;
        ctx.fillRect(btnX, this.y + 2, 30, 10);
        new Label(btnX + 15, this.y + 3, this.value ? "ON" : "OFF", CONFIG.COLORS.HIGHLIGHT, 8, 'center').draw(ctx, engine);
    }
}

class Dropdown extends Widget {
    constructor(x, y, w, h, options, selected, callback) {
        super(x, y); this.w = w; this.h = h; this.options = options; this.selected = selected; this.callback = callback;
        this.open = false; this.hover = false;
    }
    update(mouse, engine) {
        this.hover = (mouse.x >= this.x && mouse.x <= this.x + this.w && mouse.y >= this.y && mouse.y <= this.y + this.h);

        if (this.open) {
            const itemH = 14;
            const listY = this.y + this.h;
            this.options.forEach((opt, i) => {
                const optY = listY + (i * itemH);
                if (mouse.x >= this.x && mouse.x <= this.x + this.w && mouse.y >= optY && mouse.y <= optY + itemH) {
                    if (mouse.clicked) {
                        this.callback(opt);
                        this.open = false;
                        engine.activeDropdown = null;
                        return;
                    }
                }
            });
        }

        if (this.hover && mouse.clicked) {
            this.open = !this.open;
            if (this.open) engine.activeDropdown = this;
            else engine.activeDropdown = null;
        }
    }
    draw(ctx, engine) {
        ctx.fillStyle = CONFIG.COLORS.SHADOW;
        ctx.fillRect(this.x, this.y, this.w, this.h);
        ctx.strokeStyle = (this.hover || this.open) ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG_DIM;
        ctx.strokeRect(this.x + 0.5, this.y + 0.5, this.w - 1, this.h - 1);

        new Label(this.x + 5, this.y + 3, this.selected, CONFIG.COLORS.HIGHLIGHT, 8).draw(ctx, engine);
        new Label(this.x + this.w - 8, this.y + 3, this.open ? "^" : "v", CONFIG.COLORS.FG_DIM, 8).draw(ctx, engine);
    }
    drawList(ctx, engine) {
        const itemH = 14;
        const totalH = this.options.length * itemH;
        let listY = this.y + this.h;

        // Background
        ctx.fillStyle = CONFIG.COLORS.PANEL;
        ctx.fillRect(this.x, listY, this.w, totalH);
        ctx.strokeStyle = CONFIG.COLORS.HIGHLIGHT;
        ctx.strokeRect(this.x + 0.5, listY + 0.5, this.w - 1, totalH - 1);

        this.options.forEach((opt, i) => {
            const optY = listY + (i * itemH);
            const optHover = (engine.mouse.x >= this.x && engine.mouse.x <= this.x + this.w && engine.mouse.y >= optY && engine.mouse.y <= optY + itemH);

            if (optHover) {
                ctx.fillStyle = "rgba(255,255,255,0.1)";
                ctx.fillRect(this.x + 1, optY + 1, this.w - 2, itemH - 2);
            }

            const color = (opt === this.selected) ? CONFIG.COLORS.HIGHLIGHT : (optHover ? CONFIG.COLORS.HIGHLIGHT : CONFIG.COLORS.FG_DIM);
            new Label(this.x + 5, optY + 3, opt, color, 8).draw(ctx, engine);
        });
    }
}

class MapWidget extends Widget {
    constructor(x, y, w, h, data) { super(x, y); this.w = Math.floor(w); this.h = Math.floor(h); this.data = data; }
    draw(ctx) {
        const grid = this.data.grid; const player = this.data.player_pos;
        const cellSize = Math.floor(Math.min(this.w / this.data.width, this.h / this.data.height));
        for (let r = 0; r < this.data.height; r++) {
            for (let c = 0; c < this.data.width; c++) {
                const cx = this.x + c * cellSize; const cy = this.y + r * cellSize;
                const cell = grid[r][c];
                ctx.fillStyle = cell && cell.discovered ? "#2d2a24" : "#1a1814";
                ctx.fillRect(cx, cy, cellSize - 1, cellSize - 1);
                if (r === player[0] && c === player[1]) {
                    ctx.fillStyle = CONFIG.COLORS.ACCENT; ctx.fillRect(cx + 2, cy + 2, cellSize - 5, cellSize - 5);
                }
            }
        }
    }
}

window.onload = () => { window.Game = new RetroEngine(); };
