/**
 * GREEN PROMPTS OPTIMIZER - GRADIO VERSION
 * Connects to your Gradio app on Hugging Face Space
 */

// Your Hugging Face Space URL
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
        // Call Gradio's /api/predict endpoint
        // Gradio format: { data: [input1, input2, ...] }
        const response = await fetch(`${HF_SPACE_URL}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: [
                    prompt,                          // First input: prompt text
                    preserveMeaning.checked          // Second input: preserve meaning checkbox
                ]
            })
        });

        // Check response
        if (!response.ok) {
            if (response.status === 503) {
                showError('Model is starting up. Please wait 30-60 seconds and try again.');
            } else {
                showError(`Error ${response.status}. Please try again.`);
            }
            hideLoading();
            return;
        }

        // Parse Gradio response
        const result = await response.json();
        
        // Gradio returns: { data: [output1, output2, output3, ...] }
        // Our function returns: [optimized, info, tokens_saved, reduction_pct, energy_wh, co2_g]
        if (!result.data || result.data.length < 6) {
            showError('Invalid response from model. Please try again.');
            hideLoading();
            return;
        }

        // Extract results
        const optimizedPrompt = result.data[0];  // Optimized text
        const info = result.data[1];              // Token info
        const tokensSaved = result.data[2];       // Tokens saved (number)
        const reductionPercent = result.data[3];  // Reduction percentage (string with %)
        const energySaved = result.data[4];       // Energy in Wh (string with unit)
        const co2Saved = result.data[5];          // CO2 in g (string with unit)

        // Display results
        document.getElementById('optimized-output').value = optimizedPrompt;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reductionPercent;
        document.getElementById('energy-saved').textContent = energySaved;
        document.getElementById('co2-saved').textContent = co2Saved;

        // Show output section
        const outputSection = document.getElementById('output-section');
        if (outputSection) {
            outputSection.classList.add('active');
            outputSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }

        // Update global stats if stats tracker is loaded
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
        showError('Connection failed. Make sure the Hugging Face Space is running.');
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
        
        setTimeout(() => {
            errorEl.classList.remove('active');
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
