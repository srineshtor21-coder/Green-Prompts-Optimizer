// Green-Prompts-Optimizer Chrome Extension - Content Script
// Integrates with popular AI platforms

// Detect AI platforms and add optimize button
const AI_PLATFORMS = {
    'chatgpt': {
        selector: 'textarea[data-id]',
        name: 'ChatGPT'
    },
    'claude': {
        selector: 'div[contenteditable="true"]',
        name: 'Claude'
    },
    'bard': {
        selector: 'textarea.ql-editor',
        name: 'Bard'
    }
};

function detectPlatform() {
    const hostname = window.location.hostname;
    
    if (hostname.includes('openai.com') || hostname.includes('chat.openai.com')) {
        return 'chatgpt';
    } else if (hostname.includes('claude.ai')) {
        return 'claude';
    } else if (hostname.includes('bard.google.com')) {
        return 'bard';
    }
    
    return null;
}

function createOptimizeButton() {
    const button = document.createElement('button');
    button.id = 'green-prompts-optimize-btn';
    button.innerHTML = '🌱 Optimize';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 24px;
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        transition: all 0.3s;
    `;
    
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 6px 16px rgba(16, 185, 129, 0.5)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.4)';
    });
    
    button.addEventListener('click', handleOptimize);
    
    document.body.appendChild(button);
}

function getPromptText(platform) {
    const config = AI_PLATFORMS[platform];
    if (!config) return null;
    
    const element = document.querySelector(config.selector);
    if (!element) return null;
    
    return element.value || element.textContent || element.innerText;
}

function setPromptText(platform, text) {
    const config = AI_PLATFORMS[platform];
    if (!config) return;
    
    const element = document.querySelector(config.selector);
    if (!element) return;
    
    if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
        element.value = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
        element.textContent = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

async function handleOptimize() {
    const platform = detectPlatform();
    if (!platform) {
        showNotification('Platform not supported', 'error');
        return;
    }
    
    const promptText = getPromptText(platform);
    if (!promptText || promptText.trim() === '') {
        showNotification('Please enter a prompt first', 'error');
        return;
    }
    
    const button = document.getElementById('green-prompts-optimize-btn');
    const originalText = button.innerHTML;
    button.innerHTML = '⏳ Optimizing...';
    button.disabled = true;
    
    try {
        const response = await fetch('http://localhost:5000/api/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: promptText })
        });
        
        if (!response.ok) {
            throw new Error('Optimization failed');
        }
        
        const data = await response.json();
        
        // Replace the prompt with optimized version
        setPromptText(platform, data.optimized_prompt);
        
        // Show success notification
        showNotification(
            `✅ Optimized! Saved ${data.tokens_saved} tokens (${data.percentage_reduction.toFixed(1)}% reduction)`,
            'success'
        );
        
        // Update extension stats
        chrome.storage.local.get(['totalPrompts', 'totalEnergy'], (result) => {
            chrome.storage.local.set({
                totalPrompts: (result.totalPrompts || 0) + 1,
                totalEnergy: (result.totalEnergy || 0) + data.energy_saved_wh
            });
        });
        
    } catch (error) {
        showNotification('Failed to optimize. Please try again.', 'error');
        console.error('Optimization error:', error);
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

function showNotification(message, type) {
    // Remove existing notification if any
    const existing = document.getElementById('green-prompts-notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.id = 'green-prompts-notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10001;
        padding: 16px 24px;
        background: ${type === 'success' ? 'rgba(16, 185, 129, 0.95)' : 'rgba(239, 68, 68, 0.95)'};
        color: white;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Initialize extension
function init() {
    const platform = detectPlatform();
    if (platform) {
        createOptimizeButton();
        console.log('Green-Prompts-Optimizer: Activated on', AI_PLATFORMS[platform].name);
    }
}

// Run initialization when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPrompt') {
        const platform = detectPlatform();
        const promptText = getPromptText(platform);
        sendResponse({ prompt: promptText });
    }
});
