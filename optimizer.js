/**
 * GREEN PROMPTS OPTIMIZER - Frontend JavaScript
 * Connects to Hugging Face Space API
 */

const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';
const API_ENDPOINT = `${HF_SPACE_URL}/api/predict`;

// Global stats tracking
let globalStats = {
    totalOptimizations: 0,
    totalTokensSaved: 0,
    totalEnergySaved: 0,
    totalCO2Saved: 0
};

// Load global stats from localStorage
function loadGlobalStats() {
    const stored = localStorage.getItem('greenPromptsStats');
    if (stored) {
        globalStats = JSON.parse(stored);
        updateGlobalStatsDisplay();
    }
}

// Save global stats to localStorage
function saveGlobalStats() {
    localStorage.setItem('greenPromptsStats', JSON.stringify(globalStats));
}

// Update global stats display
function updateGlobalStatsDisplay() {
    document.getElementById('global-tokens').textContent = globalStats.totalTokensSaved.toLocaleString();
    document.getElementById('global-energy').textContent = globalStats.totalEnergySaved.toFixed(6) + ' Wh';
    document.getElementById('global-co2').textContent = globalStats.totalCO2Saved.toFixed(6) + 'g';
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

// Optimize prompt function
async function optimizePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const preserveMeaning = document.getElementById('preserve-meaning').checked;
    const prompt = promptInput.value.trim();
    
    // Validation
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
        // Call Hugging Face Space API using Gradio's client API format
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: [
                    prompt,
                    preserveMeaning
                ]
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Gradio returns data in this format: {data: [output1, output2, ...]}
        if (!result.data || result.data.length < 6) {
            throw new Error('Invalid response from API');
        }
        
        // Extract results
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
        
        // Update global stats
        globalStats.totalOptimizations++;
        globalStats.totalTokensSaved += parseInt(tokensSaved) || 0;
        globalStats.totalEnergySaved += parseFloat(energySaved) || 0;
        globalStats.totalCO2Saved += parseFloat(co2Saved) || 0;
        
        saveGlobalStats();
        updateGlobalStatsDisplay();
        
        // Show results
        showElement('output-section');
        
    } catch (error) {
        console.error('Optimization error:', error);
        
        let errorMessage = 'Failed to optimize prompt. ';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Cannot connect to server. The Hugging Face Space may be sleeping - please try again in a moment.';
        } else if (error.message.includes('NetworkError')) {
            errorMessage += 'Network error. Please check your internet connection.';
        } else {
            errorMessage += error.message;
        }
        
        showError(errorMessage);
        
    } finally {
        // Hide loading
        removeClass('loading-spinner', 'active');
        document.getElementById('optimize-btn').disabled = false;
    }
}

// Copy to clipboard
async function copyToClipboard() {
    const optimizedText = document.getElementById('optimized-output').value;
    
    try {
        await navigator.clipboard.writeText(optimizedText);
        
        // Visual feedback
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

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Load saved stats
    loadGlobalStats();
    
    // Set up event listeners
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
    
    // Allow Enter key to optimize (Ctrl/Cmd + Enter)
    document.getElementById('prompt-input').addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            optimizePrompt();
        }
    });
    
    console.log('🌱 Green Prompts Optimizer initialized!');
});
