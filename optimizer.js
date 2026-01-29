const HF_SPACE_URL = 'https://sirenice-greenpromptsoptimizer.hf.space';
const API_ENDPOINT = `${HF_SPACE_URL}/gradio_api/call/predict`; // CHANGED THIS LINE

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
        // Step 1: Start the job
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                data: [prompt, preserveMeaning.checked]
            })
        });
        
        const result = await response.json();
        const eventId = result.event_id;
        
        // Step 2: Get the result
        const resultResponse = await fetch(`${HF_SPACE_URL}/gradio_api/call/predict/${eventId}`);
        const finalResult = await resultResponse.json();
        
        if (finalResult.data && finalResult.data.length >= 6) {
            const [optimized, tokenInfo, tokensSaved, reduction, energy, co2] = finalResult.data;
            
            document.getElementById('optimized-output').value = optimized;
            document.getElementById('tokens-saved').textContent = tokensSaved;
            document.getElementById('reduction-pct').textContent = reduction;
            document.getElementById('energy-saved').textContent = energy;
            document.getElementById('co2-saved').textContent = co2;
            
            showResults();
        } else {
            throw new Error('Invalid response');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Optimization failed: ' + error.message);
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
