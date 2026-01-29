/**
 * GREEN PROMPTS OPTIMIZER - Chrome Extension
 * Popup script for extension functionality
 */

const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';
const API_ENDPOINT = `${HF_SPACE_URL}/api/predict`;

// Show/hide elements
function show(id) {
    document.getElementById(id).style.display = 'block';
}

function hide(id) {
    document.getElementById(id).style.display = 'none';
}

function addClass(id, className) {
    document.getElementById(id).classList.add(className);
}

function removeClass(id, className) {
    document.getElementById(id).classList.remove(className);
}

// Show error
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
    show('loading');
    document.getElementById('optimize-btn').disabled = true;
    removeClass('output-section', 'active');
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
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
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
        
        // Save stats to extension storage
        chrome.storage.local.get(['totalOptimizations', 'totalTokensSaved', 'totalEnergySaved', 'totalCO2Saved'], (data) => {
            chrome.storage.local.set({
                totalOptimizations: (data.totalOptimizations || 0) + 1,
                totalTokensSaved: (data.totalTokensSaved || 0) + parseInt(tokensSaved),
                totalEnergySaved: (data.totalEnergySaved || 0) + parseFloat(energySaved),
                totalCO2Saved: (data.totalCO2Saved || 0) + parseFloat(co2Saved)
            });
        });
        
        // Show results
        addClass('output-section', 'active');
        
    } catch (error) {
        console.error('Optimization error:', error);
        
        let errorMessage = 'Failed to optimize. ';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Cannot connect to server. The Hugging Face Space may be sleeping.';
        } else {
            errorMessage += error.message;
        }
        
        showError(errorMessage);
        
    } finally {
        hide('loading');
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
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
        
    } catch (error) {
        console.error('Copy failed:', error);
        showError('Failed to copy to clipboard');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
    
    // Try to get selected text from active tab
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, {action: 'getSelectedText'}, (response) => {
            if (response && response.text) {
                document.getElementById('prompt-input').value = response.text;
            }
        });
    });
    
    console.log('🌱 Green Prompts Extension initialized!');
});
