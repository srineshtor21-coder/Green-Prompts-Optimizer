/**
 * GREEN PROMPTS OPTIMIZER - Frontend API Client
 * For GitHub Pages → Hugging Face Space API
 * FIXED VERSION - Handles CORS, timeouts, and errors properly
 */

// ============================================================
// CONFIGURATION
// ============================================================

const API_CONFIG = {
    BASE_URL: 'https://huggingface.co/spaces/sirenice/GreenPromptsOptimizer',
    
    // Endpoints
    ENDPOINTS: {
        optimize: '/api/optimize',
        stats: '/api/stats',
        health: '/health'
    },
    
    // Timeouts
    TIMEOUT_MS: 30000, // 30 seconds (HF Spaces can be slow on free tier)
    
    // Retry settings
    MAX_RETRIES: 2,
    RETRY_DELAY_MS: 2000
};

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Make API request with timeout and retry logic
 */
async function makeAPIRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    
    const fetchWithTimeout = async (url, options, timeout) => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    ...options.headers
                }
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    };
    
    let lastError;
    
    // Try with retries
    for (let attempt = 0; attempt <= API_CONFIG.MAX_RETRIES; attempt++) {
        try {
            console.log(`🔄 API Request attempt ${attempt + 1}/${API_CONFIG.MAX_RETRIES + 1}: ${endpoint}`);
            
            const response = await fetchWithTimeout(url, options, API_CONFIG.TIMEOUT_MS);
            
            // Check if response is ok
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `API Error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ API Response received:', data);
            return data;
            
        } catch (error) {
            lastError = error;
            console.warn(`❌ Attempt ${attempt + 1} failed:`, error.message);
            
            // Don't retry on certain errors
            if (error.message.includes('Failed to fetch') || 
                error.message.includes('CORS') ||
                error.message.includes('NetworkError')) {
                console.error('🚫 CORS or Network error - not retrying');
                break;
            }
            
            // Wait before retry
            if (attempt < API_CONFIG.MAX_RETRIES) {
                console.log(`⏳ Waiting ${API_CONFIG.RETRY_DELAY_MS}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY_MS));
            }
        }
    }
    
    // All attempts failed
    throw lastError;
}

// ============================================================
// API FUNCTIONS
// ============================================================

/**
 * Check if API is available
 */
async function checkAPIHealth() {
    try {
        const data = await makeAPIRequest(API_CONFIG.ENDPOINTS.health, {
            method: 'GET'
        });
        
        console.log('✅ API is healthy:', data);
        return {
            success: true,
            status: data.status,
            modelType: data.model_type || 'unknown'
        };
    } catch (error) {
        console.error('❌ API health check failed:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Optimize a prompt
 */
async function optimizePrompt(prompt, preserveMeaning = true) {
    // Validation
    if (!prompt || prompt.trim().length === 0) {
        return {
            success: false,
            error: 'Please enter a prompt to optimize'
        };
    }
    
    if (prompt.length > 2000) {
        return {
            success: false,
            error: 'Prompt is too long (max 2000 characters)'
        };
    }
    
    try {
        const data = await makeAPIRequest(API_CONFIG.ENDPOINTS.optimize, {
            method: 'POST',
            body: JSON.stringify({
                prompt: prompt.trim(),
                preserve_meaning: preserveMeaning
            })
        });
        
        return {
            success: true,
            ...data
        };
        
    } catch (error) {
        console.error('❌ Optimization failed:', error);
        
        // Return user-friendly error messages
        let errorMessage = 'Optimization failed. Please try again.';
        
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('NetworkError')) {
            errorMessage = 'Cannot connect to server. Please check your internet connection.';
        } else if (error.message.includes('CORS')) {
            errorMessage = 'Server configuration error (CORS). Please contact support.';
        } else if (error.name === 'AbortError' || error.message.includes('timeout')) {
            errorMessage = 'Request timed out. The server may be waking up - please try again in a few seconds.';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        return {
            success: false,
            error: errorMessage
        };
    }
}

/**
 * Get global statistics
 */
async function getGlobalStats() {
    try {
        const data = await makeAPIRequest(API_CONFIG.ENDPOINTS.stats, {
            method: 'GET'
        });
        
        return {
            success: true,
            ...data
        };
        
    } catch (error) {
        console.error('❌ Failed to fetch stats:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// ============================================================
// UI HELPER FUNCTIONS
// ============================================================

/**
 * Display optimization result in UI
 */
function displayOptimizationResult(result) {
    const resultContainer = document.getElementById('optimization-result');
    const errorContainer = document.getElementById('error-message');
    
    if (!result.success) {
        // Show error
        if (errorContainer) {
            errorContainer.textContent = result.error;
            errorContainer.style.display = 'block';
        }
        if (resultContainer) {
            resultContainer.style.display = 'none';
        }
        return;
    }
    
    // Hide error, show result
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
    
    // Update optimized prompt
    const optimizedPromptEl = document.getElementById('optimized-prompt');
    if (optimizedPromptEl) {
        optimizedPromptEl.value = result.optimized;
    }
    
    // Update metrics
    updateMetric('original-tokens', result.original_tokens);
    updateMetric('optimized-tokens', result.optimized_tokens);
    updateMetric('tokens-saved', result.tokens_saved);
    updateMetric('reduction-percentage', result.reduction_percentage + '%');
    updateMetric('energy-saved', result.energy_saved_wh.toFixed(8) + ' Wh');
    updateMetric('co2-saved', result.co2_saved_g.toFixed(6) + ' g');
    
    // Show result container
    if (resultContainer) {
        resultContainer.style.display = 'block';
    }
}

/**
 * Update a metric element
 */
function updateMetric(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Show loading state
 */
function setLoadingState(isLoading) {
    const button = document.getElementById('optimize-button');
    const spinner = document.getElementById('loading-spinner');
    
    if (button) {
        button.disabled = isLoading;
        button.textContent = isLoading ? 'Optimizing...' : 'Optimize Prompt';
    }
    
    if (spinner) {
        spinner.style.display = isLoading ? 'block' : 'none';
    }
}

// ============================================================
// MAIN INITIALIZATION
// ============================================================

/**
 * Initialize the optimizer when page loads
 */
async function initializeOptimizer() {
    console.log('🌿 Green Prompts Optimizer - Initializing...');
    
    // Check if API URL is configured
    if (API_CONFIG.BASE_URL.includes('YOUR-USERNAME')) {
        console.error('❌ API URL not configured! Please update API_CONFIG.BASE_URL');
        const errorContainer = document.getElementById('error-message');
        if (errorContainer) {
            errorContainer.textContent = 'Configuration error: API URL not set. Please update the code.';
            errorContainer.style.display = 'block';
        }
        return;
    }
    
    // Check API health
    console.log('🏥 Checking API health...');
    const health = await checkAPIHealth();
    
    if (health.success) {
        console.log(`✅ API is ready! Model type: ${health.modelType}`);
    } else {
        console.warn(`⚠️ API health check failed: ${health.error}`);
        console.log('💡 This is normal if the Hugging Face Space is sleeping. It will wake up on first request.');
    }
    
    // Load global stats
    const stats = await getGlobalStats();
    if (stats.success) {
        updateMetric('total-optimizations', stats.total_optimizations || 0);
        updateMetric('total-tokens-saved', stats.total_tokens_saved || 0);
        updateMetric('total-energy-saved', (stats.total_energy_saved_wh || 0).toFixed(6) + ' Wh');
        updateMetric('total-co2-saved', (stats.total_co2_saved_g || 0).toFixed(4) + ' g');
    }
    
    // Set up event listeners
    const optimizeButton = document.getElementById('optimize-button');
    if (optimizeButton) {
        optimizeButton.addEventListener('click', handleOptimizeClick);
    }
    
    console.log('✅ Optimizer initialized successfully!');
}

/**
 * Handle optimize button click
 */
async function handleOptimizeClick() {
    const promptInput = document.getElementById('prompt-input');
    const preserveMeaningCheckbox = document.getElementById('preserve-meaning');
    
    if (!promptInput) {
        console.error('❌ Prompt input not found');
        return;
    }
    
    const prompt = promptInput.value;
    const preserveMeaning = preserveMeaningCheckbox ? preserveMeaningCheckbox.checked : true;
    
    // Show loading state
    setLoadingState(true);
    
    // Optimize
    const result = await optimizePrompt(prompt, preserveMeaning);
    
    // Hide loading state
    setLoadingState(false);
    
    // Display result
    displayOptimizationResult(result);
}

// ============================================================
// AUTO-INITIALIZE ON PAGE LOAD
// ============================================================

// Wait for DOM to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeOptimizer);
} else {
    initializeOptimizer();
}

// Export for use in other scripts
window.GreenPromptsAPI = {
    optimizePrompt,
    getGlobalStats,
    checkAPIHealth,
    displayOptimizationResult
};
