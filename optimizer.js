/**
 * GREEN PROMPTS OPTIMIZER - Frontend API Client
 * Enhanced version with multiple endpoint fallback strategies
 */

// Configuration
const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';

// Try multiple possible API endpoints
const API_ENDPOINTS = [
    `${HF_SPACE_URL}/api/predict`,           // Standard Gradio API
    `${HF_SPACE_URL}/call/predict`,          // Alternative Gradio format
    `${HF_SPACE_URL}/run/predict`,           // Another alternative
];

// Energy calculation constants (fallback calculations)
const ENERGY_PER_TOKEN_WH = 0.000001;
const CO2_PER_KWH_G = 475;

/**
 * Simple token counter (fallback if API fails)
 */
function estimateTokens(text) {
    // Rough estimation: ~4 characters per token
    return Math.ceil(text.length / 4);
}

/**
 * Try calling API with different endpoint formats
 */
async function tryAPICall(prompt, preserveMeaning) {
    const errors = [];
    
    // Try each endpoint format
    for (const endpoint of API_ENDPOINTS) {
        try {
            console.log(`🔄 Trying endpoint: ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    data: [prompt, preserveMeaning]
                }),
                signal: AbortSignal.timeout(30000) // 30 second timeout
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ ${endpoint} failed:`, response.status, errorText);
                errors.push(`${endpoint}: ${response.status}`);
                continue;
            }
            
            const result = await response.json();
            console.log('✅ API response:', result);
            
            // Validate response
            if (!result.data || result.data.length < 6) {
                console.error('❌ Invalid response format:', result);
                errors.push(`${endpoint}: Invalid response format`);
                continue;
            }
            
            // Success!
            return {
                success: true,
                data: result.data,
                endpoint: endpoint
            };
            
        } catch (error) {
            console.error(`❌ ${endpoint} error:`, error);
            errors.push(`${endpoint}: ${error.message}`);
        }
    }
    
    // All endpoints failed
    return {
        success: false,
        errors: errors
    };
}

/**
 * Fallback optimization (client-side simple processing)
 */
function fallbackOptimization(prompt) {
    // Simple client-side optimization
    let optimized = prompt
        .replace(/\s+/g, ' ')  // Remove extra spaces
        .replace(/\b(please|kindly|could you|would you)\b/gi, '')  // Remove politeness
        .trim();
    
    const origTokens = estimateTokens(prompt);
    const optTokens = estimateTokens(optimized);
    const tokensSaved = Math.max(0, origTokens - optTokens);
    const reductionPct = (tokensSaved / origTokens * 100).toFixed(2);
    const energySaved = (tokensSaved * ENERGY_PER_TOKEN_WH).toFixed(6);
    const co2Saved = ((tokensSaved * ENERGY_PER_TOKEN_WH / 1000) * CO2_PER_KWH_G).toFixed(6);
    
    return [
        optimized,
        `⚠️ Fallback Mode\nOriginal: ${origTokens} tokens (estimated)\nOptimized: ${optTokens} tokens (estimated)`,
        tokensSaved.toString(),
        `${reductionPct}%`,
        energySaved,
        co2Saved
    ];
}

/**
 * Main optimize function
 */
async function optimizePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const preserveCheckbox = document.getElementById('preserve-meaning');
    const optimizeBtn = document.getElementById('optimize-btn');
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error-message');
    const outputSection = document.getElementById('output-section');
    
    const prompt = promptInput.value.trim();
    const preserveMeaning = preserveCheckbox.checked;
    
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
    loadingEl.style.display = 'block';
    optimizeBtn.disabled = true;
    outputSection.classList.remove('active');
    errorEl.classList.remove('active');
    
    try {
        console.log('🚀 Starting optimization...');
        
        // Try API call
        const result = await tryAPICall(prompt, preserveMeaning);
        
        let data;
        if (result.success) {
            console.log(`✅ Success using endpoint: ${result.endpoint}`);
            data = result.data;
        } else {
            console.warn('⚠️ All API endpoints failed, using fallback optimization');
            console.warn('Errors:', result.errors);
            data = fallbackOptimization(prompt);
        }
        
        // Extract results
        const [
            optimizedPrompt,
            tokenInfo,
            tokensSaved,
            reductionPct,
            energySaved,
            co2Saved
        ] = data;
        
        // Update UI
        document.getElementById('optimized-output').value = optimizedPrompt;
        document.getElementById('token-info').textContent = tokenInfo;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reductionPct;
        document.getElementById('energy-saved').textContent = energySaved;
        document.getElementById('co2-saved').textContent = co2Saved;
        
        // Update statistics
        updateStats(parseInt(tokensSaved), parseFloat(energySaved), parseFloat(co2Saved));
        
        // Show results
        outputSection.classList.add('active');
        
        // Auto-scroll to results
        outputSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        console.error('❌ Unexpected error:', error);
        showError('An unexpected error occurred. Please try again.');
    } finally {
        loadingEl.style.display = 'none';
        optimizeBtn.disabled = false;
    }
}

/**
 * Copy to clipboard
 */
async function copyToClipboard() {
    const optimizedText = document.getElementById('optimized-output').value;
    const copyBtn = document.getElementById('copy-btn');
    
    try {
        await navigator.clipboard.writeText(optimizedText);
        
        const originalHTML = copyBtn.innerHTML;
        copyBtn.innerHTML = '✅ Copied!';
        copyBtn.disabled = true;
        
        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Copy failed:', error);
        showError('Failed to copy to clipboard');
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    errorEl.classList.add('active');
    
    setTimeout(() => {
        errorEl.classList.remove('active');
    }, 5000);
}

/**
 * Update global statistics
 */
function updateStats(tokensSaved, energySaved, co2Saved) {
    // Get existing stats from localStorage
    let stats = JSON.parse(localStorage.getItem('greenPromptsStats') || '{}');
    
    stats.totalOptimizations = (stats.totalOptimizations || 0) + 1;
    stats.totalTokensSaved = (stats.totalTokensSaved || 0) + tokensSaved;
    stats.totalEnergySaved = (stats.totalEnergySaved || 0) + energySaved;
    stats.totalCO2Saved = (stats.totalCO2Saved || 0) + co2Saved;
    stats.lastUpdated = new Date().toISOString();
    
    // Save back to localStorage
    localStorage.setItem('greenPromptsStats', JSON.stringify(stats));
    
    console.log('📊 Stats updated:', stats);
}

/**
 * Initialize when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    const optimizeBtn = document.getElementById('optimize-btn');
    const copyBtn = document.getElementById('copy-btn');
    
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizePrompt);
    }
    
    if (copyBtn) {
        copyBtn.addEventListener('click', copyToClipboard);
    }
    
    // Allow Enter key to submit (with Shift+Enter for newlines)
    const promptInput = document.getElementById('prompt-input');
    if (promptInput) {
        promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                optimizePrompt();
            }
        });
    }
    
    console.log('🌱 Green Prompts Optimizer initialized!');
    console.log('🔍 API endpoints configured:', API_ENDPOINTS);
});
