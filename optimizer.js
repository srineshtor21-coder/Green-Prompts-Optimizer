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
        // FIXED: Changed backticks to parentheses
        const response = await fetch(`${HF_SPACE_URL}/call/predict`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                data: [prompt, preserveMeaning.checked]
            })
        });
        
        const result = await response.json();
        const eventId = result.event_id;
        
        // Poll for results
        let attempts = 0;
        const maxAttempts = 60;
        
        while (attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // FIXED: Changed backticks to parentheses
            const statusResponse = await fetch(`${HF_SPACE_URL}/call/predict/${eventId}`);
            const statusText = await statusResponse.text();
            
            const lines = statusText.split('\n').filter(line => line.startsWith('data:'));
            
            for (const line of lines) {
                const data = JSON.parse(line.substring(5));
                
                if (data.msg === 'process_completed') {
                    const [optimized, tokenInfo, tokensSaved, reduction, energy, co2] = data.output.data;
                    
                    document.getElementById('optimized-output').value = optimized;
                    document.getElementById('tokens-saved').textContent = tokensSaved;
                    document.getElementById('reduction-pct').textContent = reduction;
                    document.getElementById('energy-saved').textContent = energy;
                    document.getElementById('co2-saved').textContent = co2;
                    
                    showResults();
                    hideLoading();
                    return;
                }
            }
            
            attempts++;
        }
        
        throw new Error('Timeout waiting for result');
        
    } catch (error) {
        console.error('Error:', error);
        showError('Optimization failed. Please try again. ' + error.message);
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

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
});
