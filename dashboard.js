/**
 * GREEN PROMPTS OPTIMIZER - Dashboard
 * Personal dashboard with optimization history and stats
 */

const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';
const API_ENDPOINT = `${HF_SPACE_URL}/api/predict`;

let currentUser = null;

// Check authentication
function checkAuth() {
    const session = localStorage.getItem('greenPromptsSession');
    if (!session) {
        window.location.href = 'login.html';
        return null;
    }
    
    const { email, loginTime } = JSON.parse(session);
    const dayInMs = 24 * 60 * 60 * 1000;
    
    // Session expires after 7 days
    if (Date.now() - loginTime > 7 * dayInMs) {
        localStorage.removeItem('greenPromptsSession');
        window.location.href = 'login.html';
        return null;
    }
    
    return JSON.parse(session);
}

// Get current user data
function getCurrentUser() {
    const session = checkAuth();
    if (!session) return null;
    
    const users = JSON.parse(localStorage.getItem('greenPromptsUsers') || '{}');
    return users[session.email];
}

// Save user data
function saveUserData(user) {
    const users = JSON.parse(localStorage.getItem('greenPromptsUsers') || '{}');
    users[user.email] = user;
    localStorage.setItem('greenPromptsUsers', JSON.stringify(users));
}

// Load user info and stats
function loadUserInfo() {
    currentUser = getCurrentUser();
    if (!currentUser) return;
    
    // Update UI with user info
    document.getElementById('user-name').textContent = currentUser.name;
    document.getElementById('welcome-name').textContent = currentUser.name;
    
    // Update stats
    const stats = currentUser.stats || {
        totalOptimizations: 0,
        totalTokensSaved: 0,
        totalEnergySaved: 0,
        totalCO2Saved: 0
    };
    
    document.getElementById('total-optimizations').textContent = stats.totalOptimizations;
    document.getElementById('total-tokens').textContent = stats.totalTokensSaved.toLocaleString();
    document.getElementById('total-energy').textContent = stats.totalEnergySaved.toFixed(6) + ' Wh';
    document.getElementById('total-co2').textContent = stats.totalCO2Saved.toFixed(6) + 'g';
    
    // Load history
    loadHistory();
}

// Load optimization history
function loadHistory() {
    if (!currentUser || !currentUser.history || currentUser.history.length === 0) {
        return;
    }
    
    const container = document.getElementById('history-container');
    container.innerHTML = '';
    
    // Sort by most recent first
    const sortedHistory = [...currentUser.history].reverse().slice(0, 10);
    
    sortedHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const date = new Date(item.timestamp);
        const timeStr = date.toLocaleString();
        
        historyItem.innerHTML = `
            <div class="history-header">
                <div class="history-time">${timeStr}</div>
                <div class="history-stats">
                    <span>${item.tokensSaved}</span> tokens saved
                    <span>${item.reductionPct}</span> reduction
                </div>
            </div>
            <div class="history-content">
                <div class="history-prompt">
                    <div class="prompt-label">Original:</div>
                    ${item.original}
                </div>
                <div class="history-prompt">
                    <div class="prompt-label">Optimized:</div>
                    ${item.optimized}
                </div>
            </div>
        `;
        
        container.appendChild(historyItem);
    });
}

// Show/hide elements
function showElement(id) {
    document.getElementById(id).style.display = 'block';
}

function hideElement(id) {
    document.getElementById(id).style.display = 'none';
}

function addClass(id, className) {
    document.getElementById(id).classList.add(className);
}

function removeClass(id, className) {
    document.getElementById(id).classList.remove(className);
}

// Show error message
function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    addClass('error-message', 'active');
    setTimeout(() => {
        removeClass('error-message', 'active');
    }, 5000);
}

// Optimize prompt
async function optimizePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const preserveMeaning = document.getElementById('preserve-meaning').checked;
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showError('Please enter a prompt to optimize');
        return;
    }
    
    if (prompt.length > 2000) {
        showError('Prompt is too long (max 2000 characters)');
        return;
    }
    
    // Show loading
    addClass('loading-spinner', 'active');
    document.getElementById('optimize-btn').disabled = true;
    hideElement('output-section');
    removeClass('error-message', 'active');
    
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: [prompt, preserveMeaning]
            })
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!result.data || result.data.length < 6) {
            throw new Error('Invalid response from API');
        }
        
        const [
            optimizedPrompt,
            tokenInfo,
            tokensSaved,
            reductionPct,
            energySaved,
            co2Saved
        ] = result.data;
        
        // Update display
        document.getElementById('optimized-output').value = optimizedPrompt;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reductionPct;
        document.getElementById('energy-saved').textContent = energySaved + ' Wh';
        document.getElementById('co2-saved').textContent = co2Saved + 'g';
        
        // Update user stats
        currentUser.stats = currentUser.stats || {
            totalOptimizations: 0,
            totalTokensSaved: 0,
            totalEnergySaved: 0,
            totalCO2Saved: 0
        };
        
        currentUser.stats.totalOptimizations++;
        currentUser.stats.totalTokensSaved += parseInt(tokensSaved) || 0;
        currentUser.stats.totalEnergySaved += parseFloat(energySaved) || 0;
        currentUser.stats.totalCO2Saved += parseFloat(co2Saved) || 0;
        
        // Add to history
        currentUser.history = currentUser.history || [];
        currentUser.history.push({
            timestamp: Date.now(),
            original: prompt,
            optimized: optimizedPrompt,
            tokensSaved: parseInt(tokensSaved),
            reductionPct: reductionPct,
            energySaved: parseFloat(energySaved),
            co2Saved: parseFloat(co2Saved)
        });
        
        // Save user data
        saveUserData(currentUser);
        
        // Refresh UI
        loadUserInfo();
        
        // Show results
        showElement('output-section');
        
    } catch (error) {
        console.error('Optimization error:', error);
        
        let errorMessage = 'Failed to optimize prompt. ';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Cannot connect to server. The Hugging Face Space may be sleeping - please try again in a moment.';
        } else {
            errorMessage += error.message;
        }
        
        showError(errorMessage);
        
    } finally {
        removeClass('loading-spinner', 'active');
        document.getElementById('optimize-btn').disabled = false;
    }
}

// Copy to clipboard
async function copyToClipboard() {
    const optimizedText = document.getElementById('optimized-output').value;
    
    try {
        await navigator.clipboard.writeText(optimizedText);
        
        const copyBtn = document.getElementById('copy-btn');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ Copied!';
        copyBtn.style.background = 'rgba(16, 185, 129, 0.4)';
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '';
        }, 2000);
        
    } catch (error) {
        console.error('Copy failed:', error);
        showError('Failed to copy to clipboard');
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('greenPromptsSession');
        window.location.href = 'index.html';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadUserInfo();
    
    // Event listeners
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Allow Ctrl/Cmd + Enter to optimize
    document.getElementById('prompt-input').addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            optimizePrompt();
        }
    });
    
    console.log('🌱 Dashboard initialized!');
});
