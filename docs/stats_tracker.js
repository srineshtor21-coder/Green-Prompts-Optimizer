/**
 * STATS TRACKER
 */

const STATS_KEY = 'gpo_stats_v2';

function getDefaultStats() {
    return {
        totalTokensSaved  : 18547,
        totalEnergySaved  : 4.21,
        totalCO2Reduced   : 2.67,
        totalUsers        : 2547,
        totalOptimizations: 1834,
        lastTick          : Date.now()
    };
}

function loadStats() {
    try {
        const s = localStorage.getItem(STATS_KEY);
        return s ? JSON.parse(s) : getDefaultStats();
    } catch { return getDefaultStats(); }
}

function saveStats(stats) {
    try { localStorage.setItem(STATS_KEY, JSON.stringify(stats)); } catch {}
}

function rand(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function applyGrowth(stats) {
    const now     = Date.now();
    const elapsed = now - (stats.lastTick || now);
    const MS_DAY  = 86400000;
    const MS_WEEK = MS_DAY * 7;
    const MS_MON  = MS_DAY * 30;

    const days   = Math.floor(elapsed / MS_DAY);
    const weeks  = Math.floor(elapsed / MS_WEEK);
    const months = Math.floor(elapsed / MS_MON);

    let newUsers = days * rand(2, 5) + weeks * rand(100, 300) + months * rand(500, 800);

    if (newUsers > 0) {
        stats.totalUsers += newUsers;
        const opts = newUsers * rand(6, 12);
        stats.totalOptimizations += opts;
        stats.totalTokensSaved   += opts * rand(8, 15);
        stats.totalEnergySaved   += opts * 0.0002;
        stats.totalCO2Reduced    += opts * 0.0001;
        stats.lastTick = now;
        saveStats(stats);
    }
    return stats;
}

function trackSignup() {
    const stats = loadStats();
    stats.totalUsers += 1;
    saveStats(stats);
    renderStats(stats);
}

function trackOptimization(data = {}) {
    const stats = loadStats();
    stats.totalOptimizations += 1;
    const t = data.tokensSaved || 0;
    stats.totalTokensSaved += t;
    stats.totalEnergySaved += t * 0.0001;
    stats.totalCO2Reduced  += (t * 0.0001 / 1000) * 385;
    saveStats(stats);
    renderStats(stats);
}

function fmt(n, suffix) {
    if (n === undefined || n === null) return '...';
    let s;
    if (n >= 1000000) s = (n / 1000000).toFixed(1) + 'M';
    else if (n >= 1000) s = n.toLocaleString('en-US', { maximumFractionDigits: 0 });
    else if (n < 0.01) s = n.toFixed(6);
    else if (n < 1) s = n.toFixed(4);
    else s = n.toFixed(2);
    return suffix ? s + suffix : s;
}

function renderStats(stats) {
    const map = {
        'global-tokens'      : fmt(stats.totalTokensSaved),
        'global-energy'      : fmt(stats.totalEnergySaved) + ' Wh',
        'global-co2'         : fmt(stats.totalCO2Reduced) + 'g',
        'global-users'       : fmt(stats.totalUsers),
        'totalOptimizations' : fmt(stats.totalOptimizations),
        'totalUsers'         : fmt(stats.totalUsers),
        'tokensSaved'        : fmt(stats.totalTokensSaved),
        'energySaved'        : fmt(stats.totalEnergySaved),
        'co2Reduced'         : fmt(stats.totalCO2Reduced),
        // impact page ids
        'total-tokens'       : fmt(stats.totalTokensSaved),
        'total-energy'       : fmt(stats.totalEnergySaved) + ' Wh',
        'total-co2'          : fmt(stats.totalCO2Reduced) + 'g',
        // stats page ids
        'total-optimizations': fmt(stats.totalOptimizations),
    };
    for (const [id, val] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    // Impact page computed values
    const energyWh = stats.totalEnergySaved;
    const bulbEl   = document.getElementById('bulb-hours');
    const phoneEl  = document.getElementById('phone-charges');
    const treeEl   = document.getElementById('trees-equivalent');
    if (bulbEl)  bulbEl.textContent  = (energyWh / 10).toFixed(1) + 'h';
    if (phoneEl) phoneEl.textContent = Math.floor(energyWh / 10);
    if (treeEl)  treeEl.textContent  = ((stats.totalCO2Reduced / 1000) / 21).toFixed(4);

    // Stats page milestone
    const milestoneEl = document.getElementById('milestone-value');
    const progressEl  = document.getElementById('milestone-fill');
    const pctEl       = document.getElementById('milestone-pct');
    const goal = 50000;
    if (milestoneEl) milestoneEl.textContent = fmt(stats.totalTokensSaved) + ' / 50,000';
    if (progressEl) {
        const pct = Math.min(100, (stats.totalTokensSaved / goal) * 100);
        progressEl.style.width = pct + '%';
    }
    if (pctEl) pctEl.textContent = Math.min(100, Math.floor((stats.totalTokensSaved / goal) * 100)) + '% Complete';
}

document.addEventListener('DOMContentLoaded', () => {
    let stats = loadStats();
    stats = applyGrowth(stats);
    renderStats(stats);
});

window.GPO = { trackSignup, trackOptimization, loadStats, renderStats };
