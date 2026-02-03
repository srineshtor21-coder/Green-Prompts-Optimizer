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
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('optimized-output').value = result.optimized;
            document.getElementById('tokens-saved').textContent = result.tokens_saved;
            document.getElementById('reduction-pct').textContent = result.reduction_percent + '%';
            document.getElementById('energy-saved').textContent = result.energy_wh + ' Wh';
            document.getElementById('co2-saved').textContent = result.co2_g + 'g';
            
            showResults();
        } else {
            throw new Error(result.error || 'Optimization failed');
        }
        
        hideLoading();
        
    } catch (error) {
        console.error('Error:', error);
        showError('Connection failed: ' + error.message + '. Make sure the Hugging Face Space is running.');
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
    document.getElementById('output-section').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
        showError('Failed to copy');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
    
    document.getElementById('prompt-input').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            optimizePrompt();
        }
    });
});
