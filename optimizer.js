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
        // Use the working endpoint
        const response = await fetch(`${HF_SPACE_URL}/gradio_api/call/predict`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                data: [prompt, preserveMeaning.checked]
            })
        });
        
        const result = await response.json();
        
        if (!result.event_id) {
            throw new Error('No event ID received');
        }
        
        // Poll for result
        let attempts = 0;
        while (attempts < 30) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const statusResponse = await fetch(`${HF_SPACE_URL}/gradio_api/call/predict/${result.event_id}`);
            const statusData = await statusResponse.json();
            
            if (statusData.status === 'complete' && statusData.data) {
                const [optimized, tokenInfo, tokensSaved, reduction, energy, co2] = statusData.data;
                
                document.getElementById('optimized-output').value = optimized;
                document.getElementById('tokens-saved').textContent = tokensSaved;
                document.getElementById('reduction-pct').textContent = reduction;
                document.getElementById('energy-saved').textContent = energy;
                document.getElementById('co2-saved').textContent = co2;
                
                showResults();
                return;
            }
            
            attempts++;
        }
        
        throw new Error('Timeout waiting for result');
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('optimize-btn').disabled = true;
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('optimize-btn').disabled = false;
}

function showResults() {
    document.getElementById('output-section').classList.add('active');
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    errorEl.classList.add('active');
    setTimeout(() => errorEl.classList.remove('active'), 5000);
}

async function copyToClipboard() {
    const text = document.getElementById('optimized-output').value;
    await navigator.clipboard.writeText(text);
    
    const btn = document.getElementById('copy-btn');
    const original = btn.textContent;
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = original, 2000);
}

// CONNECT THE BUTTON - ADD THIS AT THE END
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('optimize-btn').addEventListener('click', optimizePrompt);
    document.getElementById('copy-btn').addEventListener('click', copyToClipboard);
});
