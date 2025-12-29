// Green-Prompts-Optimizer Chrome Extension - Background Service Worker

// Initialize extension on install
chrome.runtime.onInstalled.addListener(() => {
    console.log('Green-Prompts-Optimizer installed!');
    
    // Initialize storage with default values
    chrome.storage.local.set({
        totalPrompts: 0,
        totalEnergy: 0,
        totalCO2: 0,
        cacheHits: 0
    });
    
    // Create context menu for right-click optimization
    chrome.contextMenus.create({
        id: 'optimize-selected-text',
        title: '🌱 Optimize with Green-Prompts',
        contexts: ['selection']
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'optimize-selected-text') {
        const selectedText = info.selectionText;
        
        // Send message to content script to optimize selected text
        chrome.tabs.sendMessage(tab.id, {
            action: 'optimizeSelection',
            text: selectedText
        });
    }
});

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'updateStats') {
        chrome.storage.local.get([
            'totalPrompts',
            'totalEnergy',
            'totalCO2',
            'cacheHits'
        ], (result) => {
            const newStats = {
                totalPrompts: (result.totalPrompts || 0) + 1,
                totalEnergy: (result.totalEnergy || 0) + (request.energySaved || 0),
                totalCO2: (result.totalCO2 || 0) + (request.co2Saved || 0),
                cacheHits: result.cacheHits || 0
            };
            
            if (request.fromCache) {
                newStats.cacheHits = newStats.cacheHits + 1;
            }
            
            chrome.storage.local.set(newStats);
            sendResponse({ success: true, stats: newStats });
        });
        return true; // Keep channel open for async response
    }
    
    if (request.action === 'getStats') {
        chrome.storage.local.get([
            'totalPrompts',
            'totalEnergy',
            'totalCO2',
            'cacheHits'
        ], (result) => {
            sendResponse({
                totalPrompts: result.totalPrompts || 0,
                totalEnergy: result.totalEnergy || 0,
                totalCO2: result.totalCO2 || 0,
                cacheHits: result.cacheHits || 0
            });
        });
        return true;
    }
});

// Badge update to show total prompts optimized
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'local' && changes.totalPrompts) {
        const count = changes.totalPrompts.newValue || 0;
        
        if (count > 0) {
            chrome.action.setBadgeText({ text: count.toString() });
            chrome.action.setBadgeBackgroundColor({ color: '#10b981' });
        }
    }
});

// Handle keyboard shortcuts (if configured in manifest)
chrome.commands.onCommand.addListener((command) => {
    if (command === 'optimize-prompt') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'triggerOptimize'
            });
        });
    }
});

// Periodic sync to update global stats from server
async function syncGlobalStats() {
    try {
        const response = await fetch('http://localhost:5000/api/stats');
        const data = await response.json();
        
        // Store global stats for display in popup
        chrome.storage.local.set({
            globalUsers: data.total_users,
            globalPrompts: data.total_prompts_optimized,
            globalEnergy: data.total_energy_saved_wh,
            globalCO2: data.total_co2_saved_g
        });
    } catch (error) {
        console.error('Failed to sync global stats:', error);
    }
}

// Sync stats every 5 minutes
chrome.alarms.create('syncStats', { periodInMinutes: 5 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'syncStats') {
        syncGlobalStats();
    }
});

// Initial sync
syncGlobalStats();
