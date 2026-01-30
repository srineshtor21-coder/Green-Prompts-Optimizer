const HF_SPACE = 'sirenice/GreenPromptsOptimizer';

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
        // Direct fetch to Gradio API
        const response = await fetch(`https://sirenice-greenpromptsoptimizer.hf.space/call/predict`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                data: [prompt, preserveMeaning.checked]
            })
        });
        
        if (!response.ok) throw new Error('API call failed');
        
        const result = await response.json();
        const eventId = result.event_id;
        
        // Poll for result using Server-Sent Events
        const eventSource = new EventSource(`https://sirenice-greenpromptsoptimizer.hf.space/call/predict/${eventId}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.msg === 'process_completed') {
                const [optimized, tokenInfo, tokensSaved, reduction, energy, co2] = data.output.data;
                
                document.getElementById('optimized-output').value = optimized;
                document.getElementById('tokens-saved').textContent = tokensSaved;
                document.getElementById('reduction-pct').textContent = reduction;
                document.getElementById('energy-saved').textContent = energy;
                document.getElementById('co2-saved').textContent = co2;
                
                showResults();
                updateGlobalStats(parseInt(tokensSaved), parseFloat(energy), parseFloat(co2));
                
                eventSource.close();
                hideLoading();
            }
        };
        
        eventSource.onerror = () => {
            eventSource.close();
            throw new Error('Connection failed');
        };
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to optimize. Please try again.');
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
