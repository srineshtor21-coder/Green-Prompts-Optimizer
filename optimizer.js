const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';

async function optimizePrompt() {
    const promptInput = document.getElementById('prompt-input');
    const preserveMeaning = document.getElementById('preserve-meaning');
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showError('Please enter a prompt');
        return;
    }
    
    showLoading();
    
    try {
        // Use the standard Gradio API endpoint
        const response = await fetch(`${HF_SPACE_URL}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: [prompt, preserveMeaning.checked]
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Gradio returns: {data: [optimized, tokenInfo, tokensSaved, reduction, energy, co2]}
        const [optimized, tokenInfo, tokensSaved, reduction, energy, co2] = result.data;
        
        // Display results
        document.getElementById('optimized-output').value = optimized;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reduction;
        document.getElementById('energy-saved').textContent = energy + ' Wh';
        document.getElementById('co2-saved').textContent = co2 + 'g';
        
        showResults();
        hideLoading();
        
    } catch (error) {
        console.error('Error:', error);
        showError('Optimization failed: ' + error.message + '. The Hugging Face Space may be starting up (takes ~30 seconds on first load).');
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loading-spinner').classList.add('active');
    document.getElementById('optimize-btn').disabled = true;
    document.getElementById('error-message').classList.remove('active');
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.remove('active');
    document.getElementById('optimize-btn').disabled = false;
}

function showResults() {
    document.getElementById('output-section').style.display = 'block';
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = '❌ ' + message;
    errorEl.classList.add('active');
}

async function copyToClipboard() {
    const text = document.getElementById('optimized-output').value;
    
    try {
        await navigator.clipboard.writeText(text);
        
        const btn = document.getElementById('copy-btn');
        const original = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => btn.textContent = original, 2000);
    } catch (err) {
        console.error('Copy failed:', err);
        showError('Failed to copy to clipboard');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
    
    // Allow Ctrl+Enter to submit
    document.getElementById('prompt-input').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            optimizePrompt();
        }
    });
});
