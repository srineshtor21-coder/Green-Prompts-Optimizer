/**
 * GREEN PROMPTS OPTIMIZER - GUARANTEED TO WORK
 * This connects directly to your Hugging Face Gradio Space
 */

// Your Hugging Face Space URL
const HF_SPACE_URL = 'https://huggingface.co/spaces/sirenice/GreenPromptsOptimizer';

/**
 * Main optimization function - CALL THIS FROM YOUR BUTTON
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
        // STEP 1: Call Hugging Face Gradio API
        // This is the EXACT format Gradio expects
        const response = await fetch(`${HF_SPACE_URL}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: [
                    prompt,                          // Your prompt text
                    preserveMeaning.checked          // true/false for preserve meaning
                ]
            })
        });

        // Check if request succeeded
        if (!response.ok) {
            if (response.status === 503) {
                showError('Model is starting up. Please wait 30 seconds and try again.');
            } else {
                showError(`Error: ${response.status}. Please try again.`);
            }
            hideLoading();
            return;
        }

        // STEP 2: Parse the response
        const result = await response.json();
        
        // Gradio returns: { data: [optimized, info, tokens, %, energy, co2] }
        if (!result.data || result.data.length < 6) {
            showError('Invalid response from model. Please try again.');
            hideLoading();
            return;
        }

        // STEP 3: Extract the data
        const optimizedPrompt = result.data[0];
        const tokensSaved = result.data[2];
        const reductionPercent = result.data[3];
        const energySaved = result.data[4];
        const co2Saved = result.data[5];

        // STEP 4: Display results
        document.getElementById('optimized-output').value = optimizedPrompt;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reductionPercent + '%';
        document.getElementById('energy-saved').textContent = energySaved + ' Wh';
        document.getElementById('co2-saved').textContent = co2Saved + 'g';

        // Show output section
        document.getElementById('output-section').style.display = 'block';
        document.getElementById('output-section').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });

        // Save stats (if stats tracker is loaded)
        if (typeof window.GreenPromptsStats !== 'undefined') {
            window.GreenPromptsStats.addOptimization(
                parseInt(tokensSaved) || 0,
                parseFloat(energySaved) || 0,
                parseFloat(co2Saved) || 0
            );
            // Update display immediately
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
        showError('Failed to copy');
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
    }
}

/**
 * Initialize when page loads
 */
document.addEventListener('DOMContentLoaded', () => {
    // Connect button
    const optimizeBtn = document.getElementById('optimize-btn');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizePrompt);
    }

    // Connect copy button
    const copyBtn = document.getElementById('copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyToClipboard);
    }

    // Keyboard shortcut: Ctrl+Enter
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
});
