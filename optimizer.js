const HF_SPACE = 'sirenice/GreenPromptsOptimizer';

// Import Gradio client from CDN
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js';
document.head.appendChild(script);

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
        // Wait for Gradio client to load
        await new Promise(resolve => {
            if (window.gradio) resolve();
            else script.onload = resolve;
        });
        
        const app = await window.gradio.client(HF_SPACE);
        const result = await app.predict("/predict", [prompt, preserveMeaning.checked]);
        
        const [optimized, tokenInfo, tokensSaved, reduction, energy, co2] = result.data;
        
        document.getElementById('optimized-output').value = optimized;
        document.getElementById('tokens-saved').textContent = tokensSaved;
        document.getElementById('reduction-pct').textContent = reduction;
        document.getElementById('energy-saved').textContent = energy;
        document.getElementById('co2-saved').textContent = co2;
        
        showResults();
        updateGlobalStats(parseInt(tokensSaved), parseFloat(energy), parseFloat(co2));
        
    } catch (error) {
        console.error('Error:', error);
        showError('Optimization failed. The Space might be starting up. Try again in 30 seconds.');
    } finally {
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
    errorEl.textContent = message;
    errorEl.classList.add('active');
}

async function copyToClipboard() {
    const text = document.getElementById('optimized-output').value;
    await navigator.clipboard.writeText(text);
    
    const btn = document.getElementById('copy-btn');
    const original = btn.textContent;
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = original, 2000);
}

function updateGlobalStats(tokens, energy, co2) {
    const stats = JSON.parse(localStorage.getItem('greenPromptsStats') || '{"tokens":0,"energy":0,"co2":0}');
    stats.tokens += tokens;
    stats.energy += energy;
    stats.co2 += co2;
    localStorage.setItem('greenPromptsStats', JSON.stringify(stats));
    
    document.getElementById('global-tokens').textContent = stats.tokens;
    document.getElementById('global-energy').textContent = stats.energy.toFixed(6) + ' Wh';
    document.getElementById('global-co2').textContent = stats.co2.toFixed(6) + 'g';
}

function loadGlobalStats() {
    const stats = JSON.parse(localStorage.getItem('greenPromptsStats') || '{"tokens":0,"energy":0,"co2":0}');
    document.getElementById('global-tokens').textContent = stats.tokens;
    document.getElementById('global-energy').textContent = stats.energy.toFixed(6) + ' Wh';
    document.getElementById('global-co2').textContent = stats.co2.toFixed(6) + 'g';
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
    loadGlobalStats();
});
