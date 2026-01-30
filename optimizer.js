async function optimizePrompt() {
    const prompt = document.getElementById('prompt-input').value.trim();
    const preserve = document.getElementById('preserve-meaning').checked;
    
    if (!prompt) {
        showError('Please enter a prompt');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('https://sirenice-greenpromptsoptimizer.hf.space/api/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({data: [prompt, preserve]})
        });
        
        const result = await response.json();
        const [optimized, info, saved, reduction, energy, co2] = result.data;
        
        document.getElementById('optimized-output').value = optimized;
        document.getElementById('tokens-saved').textContent = saved;
        document.getElementById('reduction-pct').textContent = reduction;
        document.getElementById('energy-saved').textContent = energy;
        document.getElementById('co2-saved').textContent = co2;
        
        showResults();
        
    } catch (error) {
        showError('Failed to optimize. Please try again.');
    } finally {
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loading-spinner').classList.add('active');
    document.getElementById('optimize-btn').disabled = true;
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.remove('active');
    document.getElementById('optimize-btn').disabled = false;
}

function showResults() {
    document.getElementById('output-section').style.display = 'block';
}

function showError(msg) {
    const el = document.getElementById('error-message');
    el.textContent = msg;
    el.classList.add('active');
}

async function copyToClipboard() {
    await navigator.clipboard.writeText(document.getElementById('optimized-output').value);
    const btn = document.getElementById('copy-btn');
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = '📋 Copy to Clipboard', 2000);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
});
