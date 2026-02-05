/**
 * GREEN PROMPTS OPTIMIZER - FIXED VERSION
 * Connects to your Flask app on Hugging Face Space
 */

// CORRECT Hugging Face Space URL (not the /spaces/ URL!)
const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';

/**
 * Main optimization function
 */
async function optimizePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const preserveMeaning = document.getElementById('preserve-meaning');
    const prompt = promptInput.value.trim();

    // Validate
    if (!prompt) {
        showError('Please enter a prompt to optimize');
        return;
    }

    // Show loading
    showLoading();

    try {
        // Call YOUR Flask /optimize endpoint (not /api/predict!)
        const response = await fetch(`${HF_SPACE_URL}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                preserve_meaning: preserveMeaning.checked
            })
        });

        // Check response
        if (!response.ok) {
            if (response.status === 503) {
                showError('Model is starting up. Please wait 30-60 seconds and try again.');
            } else {
                const errorData = await response.json().catch(() => ({}));
                showError(errorData.error || `Error ${response.status}. Please try again.`);
            }
            hideLoading();
            return;
        }

        // Parse result from YOUR Flask format
        const result = await response.json();
        
        if (!result.success) {
            showError(result.error || 'Optimization failed');
            hideLoading();
            return;
        }

        // Extract data from YOUR Flask response format
        const optimizedPrompt = result.optimized;
        const tokensSaved = result.tokens_saved;
        const reductionPercent = result.reduction_percent;
        const energySaved = result.energy_wh;
        const co2Saved = result.co2_g;

        // Display results
        document.getElementById('optimized-output').value = optimizedPrompt;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reductionPercent + '%';
        document.getElementById('energy-saved').textContent = energySaved + ' Wh';
        document.getElementById('co2-saved').textContent = co2Saved + 'g';

        // Show output section
        const outputSection = document.getElementById('output-section');
        if (outputSection) {
            outputSection.style.display = 'block';
            outputSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }

        // Update stats if stats tracker is loaded
        if (typeof window.GreenPromptsStats !== 'undefined') {
            window.GreenPromptsStats.addOptimization(
                parseInt(tokensSaved) || 0,
                parseFloat(energySaved) || 0,
                parseFloat(co2Saved) || 0
            );
            window.GreenPromptsStats.updateStatsDisplay();
        }

        hideLoading();

    } catch (error) {
        console.error('Error:', error);
        showError('Connection failed. Is the Hugging Face Space running?');
        hideLoading();
    }
}

/**
 * Copy to clipboard
 */
async function copyToClipboard() {
    const text = document.getElementById('optimized-output').value;
    
    try {
        await navigator.clipboard.writeText(text);
        const btn = document.getElementById('copy-btn');
        const original = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => btn.textContent = original, 2000);
    } catch (err) {
        showError('Failed to copy to clipboard');
    }
}

/**
 * UI Helper Functions
 */
function showLoading() {
    const spinner = document.getElementById('loading-spinner');
    const button = document.getElementById('optimize-btn');
    
    if (spinner) spinner.classList.add('active');
    if (button) button.disabled = true;
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    const button = document.getElementById('optimize-btn');
    
    if (spinner) spinner.classList.remove('active');
    if (button) button.disabled = false;
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.textContent = '❌ ' + message;
        errorEl.classList.add('active');
        errorEl.style.display = 'block';
        
        setTimeout(() => {
            errorEl.classList.remove('active');
            errorEl.style.display = 'none';
        }, 5000);
    } else {
        // Fallback if error element doesn't exist
        alert(message);
    }
}

/**
 * Initialize when page loads
 */
document.addEventListener('DOMContentLoaded', () => {
    // Connect optimize button
    const optimizeBtn = document.getElementById('optimize-btn');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizePrompt);
    }

    // Connect copy button
    const copyBtn = document.getElementById('copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyToClipboard);
    }

    // Keyboard shortcut: Ctrl+Enter to optimize
    const promptInput = document.getElementById('prompt-input');
    if (promptInput) {
        promptInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                optimizePrompt();
            }
        });
    }

    console.log('🌱 Green Prompts Optimizer ready!');
    console.log('📡 Connected to:', HF_SPACE_URL);
});
