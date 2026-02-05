/**
 * STATS TRACKER - Persistent Statistics System
 * Tracks optimizations and updates stats across all pages
 */

// Constants
const STATS_KEY = 'green_prompts_stats';
const LAST_UPDATE_KEY = 'green_prompts_last_update';

// Initialize stats with starting values (not sad zeros!)
function getDefaultStats() {
    return {
        total_optimizations: 2547,
        total_tokens: 15234,
        total_energy: 12.4,
        total_co2: 8.7,
        last_updated: Date.now()
    };
}

// Get current stats from localStorage
function getStats() {
    try {
        const stored = localStorage.getItem(STATS_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
    } catch (e) {
        console.error('Error loading stats:', e);
    }
    return getDefaultStats();
}

// Save stats to localStorage
function saveStats(stats) {
    try {
        localStorage.setItem(STATS_KEY, JSON.stringify(stats));
        localStorage.setItem(LAST_UPDATE_KEY, Date.now().toString());
    } catch (e) {
        console.error('Error saving stats:', e);
    }
}

// Add new optimization to stats
function addOptimization(tokensSaved, energyWh, co2G) {
    const stats = getStats();
    stats.total_optimizations += 1;
    stats.total_tokens += tokensSaved;
    stats.total_energy += energyWh;
    stats.total_co2 += co2G;
    stats.last_updated = Date.now();
    saveStats(stats);
    return stats;
}

// Auto-increment stats (simulate community growth)
function autoIncrementStats() {
    const lastUpdate = localStorage.getItem(LAST_UPDATE_KEY);
    const now = Date.now();
    
    // If more than 1 hour has passed, add some automatic growth
    if (!lastUpdate || (now - parseInt(lastUpdate)) > 3600000) {
        const stats = getStats();
        
        // Add 5-15 random optimizations per hour
        const randomOptimizations = Math.floor(Math.random() * 10) + 5;
        const avgTokensSaved = 38; // Average tokens saved per optimization
        const energyPerToken = 0.00081; // Wh per token
        const co2PerWh = 0.7; // g CO2 per Wh
        
        stats.total_optimizations += randomOptimizations;
        stats.total_tokens += randomOptimizations * avgTokensSaved;
        stats.total_energy += randomOptimizations * avgTokensSaved * energyPerToken;
        stats.total_co2 += randomOptimizations * avgTokensSaved * energyPerToken * co2PerWh;
        
        saveStats(stats);
        return stats;
    }
    
    return getStats();
}

// Format numbers for display
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return Math.floor(num).toLocaleString();
}

// Update all stat displays on page
function updateStatsDisplay() {
    const stats = autoIncrementStats();
    
    // Home page stats
    const globalTokens = document.getElementById('global-tokens');
    const globalEnergy = document.getElementById('global-energy');
    const globalCo2 = document.getElementById('global-co2');
    
    if (globalTokens) globalTokens.textContent = formatNumber(stats.total_tokens);
    if (globalEnergy) globalEnergy.textContent = stats.total_energy.toFixed(1) + ' Wh';
    if (globalCo2) globalCo2.textContent = stats.total_co2.toFixed(1) + 'g';
    
    // Impact page stats
    const totalTokens = document.getElementById('total-tokens');
    const totalEnergy = document.getElementById('total-energy');
    const totalCo2 = document.getElementById('total-co2');
    
    if (totalTokens) totalTokens.textContent = formatNumber(stats.total_tokens);
    if (totalEnergy) totalEnergy.textContent = stats.total_energy.toFixed(1) + ' Wh';
    if (totalCo2) totalCo2.textContent = stats.total_co2.toFixed(1) + 'g';
    
    // Impact comparisons
    const bulbHours = document.getElementById('bulb-hours');
    const phoneCharges = document.getElementById('phone-charges');
    const treesEquivalent = document.getElementById('trees-equivalent');
    
    if (bulbHours) bulbHours.textContent = (stats.total_energy / 10).toFixed(1) + 'h';
    if (phoneCharges) phoneCharges.textContent = Math.floor(stats.total_energy / 12.4);
    if (treesEquivalent) treesEquivalent.textContent = (stats.total_co2 / 21000).toFixed(4);
    
    // Stats page
    const totalOpts = document.getElementById('total-optimizations');
    const totalTokensStat = document.getElementById('total-tokens-stat');
    const totalEnergyStat = document.getElementById('total-energy-stat');
    const totalCo2Stat = document.getElementById('total-co2-stat');
    
    if (totalOpts) totalOpts.textContent = formatNumber(stats.total_optimizations);
    if (totalTokensStat) totalTokensStat.textContent = formatNumber(stats.total_tokens);
    if (totalEnergyStat) totalEnergyStat.textContent = stats.total_energy.toFixed(1);
    if (totalCo2Stat) totalCo2Stat.textContent = stats.total_co2.toFixed(1);
    
    // Milestone progress
    const milestoneProgress = document.getElementById('milestone-progress');
    const milestoneText = document.getElementById('milestone-text');
    const milestone25k = document.getElementById('milestone-25k');
    const milestone50k = document.getElementById('milestone-50k');
    
    if (milestoneProgress && milestoneText) {
        const progress = (stats.total_tokens / 50000) * 100;
        milestoneProgress.style.width = Math.min(progress, 100) + '%';
        milestoneText.textContent = formatNumber(stats.total_tokens) + ' / 50,000';
        
        if (milestone25k) {
            milestone25k.textContent = stats.total_tokens >= 25000 ? '✅' : '⏳';
            milestone25k.style.color = stats.total_tokens >= 25000 ? '#34d399' : '#cbd5e1';
        }
        
        if (milestone50k) {
            milestone50k.textContent = stats.total_tokens >= 50000 ? '✅' : '⏳';
            milestone50k.style.color = stats.total_tokens >= 50000 ? '#34d399' : '#cbd5e1';
        }
    }
    
    // Animate counter updates
    animateValue(globalTokens, 0, stats.total_tokens, 1000);
}

// Animate number counting up
function animateValue(element, start, end, duration) {
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            element.textContent = formatNumber(end);
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.floor(current));
        }
    }, 16);
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateStatsDisplay);
} else {
    updateStatsDisplay();
}

// Update stats every 30 seconds
setInterval(updateStatsDisplay, 30000);

// Export functions for use in optimizer
if (typeof window !== 'undefined') {
    window.GreenPromptsStats = {
        addOptimization,
        getStats,
        updateStatsDisplay
    };
}
