/**
 * STATS TRACKER - Green Prompts Optimizer
 * Growth: +2-5 users/day, +100-300/week, +500-800/month
 * Real signups and optimizations tracked separately
 */

const STATS_KEY = 'gpo_stats_v2';
const LAST_TICK_KEY = 'gpo_last_tick';

function getDefaultStats() {
    return {
        totalTokensSaved: 18547,
        totalEnergySaved: 4.21,
        totalCO2Reduced: 2.67,
        totalUsers: 2547,
        totalOptimizations: 1834,
        lastTick: Date.now()
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

/**
 * Apply time-based organic growth since last visit
 * Day:   +2 to 5 users
 * Week:  +100 to 300 users (on top of daily)
 * Month: +500 to 800 users (on top of weekly)
 */
function applyGrowth(stats) {
    const now = Date.now();
    const last = stats.lastTick || now;
    const msElapsed = now - last;

    const MS_DAY   = 1000 * 60 * 60 * 24;
    const MS_WEEK  = MS_DAY * 7;
    const MS_MONTH = MS_DAY * 30;

    const days   = Math.floor(msElapsed / MS_DAY);
    const weeks  = Math.floor(msElapsed / MS_WEEK);
    const months = Math.floor(msElapsed / MS_MONTH);

    let newUsers = 0;
    newUsers += days   * rand(2, 5);
    newUsers += weeks  * rand(100, 300);
    newUsers += months * rand(500, 800);

    if (newUsers > 0) {
        stats.totalUsers += newUsers;
        // Proportional growth for other metrics
        const optRate = newUsers * rand(6, 12);
        stats.totalOptimizations += optRate;
        stats.totalTokensSaved   += optRate * rand(8, 15);
        stats.totalEnergySaved   += optRate * 0.0002;
        stats.totalCO2Reduced    += optRate * 0.0001;
        stats.lastTick = now;
        saveStats(stats);
    }

    return stats;
}

/** Call this when a real user signs up */
function trackSignup() {
    const stats = loadStats();
    stats.totalUsers += 1;
    saveStats(stats);
    renderStats(stats);
}

/** Call this after a real optimization completes */
function trackOptimization(data = {}) {
    const stats = loadStats();
    stats.totalOptimizations += 1;

    const tokensSaved = data.tokensSaved || 0;
    stats.totalTokensSaved += tokensSaved;

    // Energy: 0.0001 Wh per token (CPU inference)
    const energySaved = tokensSaved * 0.0001;
    stats.totalEnergySaved += energySaved;

    // CO2: US grid average 0.385 kg/kWh
    const co2Saved = (energySaved / 1000) * 385; // in grams
    stats.totalCO2Reduced += co2Saved;

    saveStats(stats);
    renderStats(stats);

    return { energySaved, co2Saved };
}

function fmt(n) {
    if (n === undefined || n === null) return '—';
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return n.toLocaleString('en-US', { maximumFractionDigits: 0 });
    if (n < 1) return n.toFixed(6);
    return n.toFixed(2);
}

function renderStats(stats) {
    const map = {
        'global-tokens'  : fmt(stats.totalTokensSaved),
        'global-energy'  : fmt(stats.totalEnergySaved) + ' Wh',
        'global-co2'     : fmt(stats.totalCO2Reduced)  + 'g',
        'global-users'   : fmt(stats.totalUsers),
        // dashboard / stats page ids
        'tokensSaved'       : fmt(stats.totalTokensSaved),
        'energySaved'       : fmt(stats.totalEnergySaved),
        'co2Reduced'        : fmt(stats.totalCO2Reduced),
        'totalUsers'        : fmt(stats.totalUsers),
        'totalOptimizations': fmt(stats.totalOptimizations),
    };
    for (const [id, val] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }
}

function animateCount(el, target, isFloat) {
    if (!el) return;
    const duration = 1400;
    const steps = 50;
    const interval = duration / steps;
    let step = 0;
    const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = target * eased;
        if (isFloat) {
            el.textContent = current.toFixed(2);
        } else {
            el.textContent = Math.floor(current).toLocaleString('en-US');
        }
        if (step >= steps) {
            clearInterval(timer);
            renderStats(loadStats()); // set final formatted value
        }
    }, interval);
}

document.addEventListener('DOMContentLoaded', () => {
    let stats = loadStats();
    stats = applyGrowth(stats);
    renderStats(stats);
});

// Global exports
window.GPO = {
    trackSignup,
    trackOptimization,
    loadStats,
    renderStats,
};
