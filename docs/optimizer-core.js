/**
 * OPTIMIZER-CORE.JS
 * Calls the Hugging Face Inference API for sirenice/greenpromptsoptimizer
 */

const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API   = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

// Optional: add HF read token for faster cold starts
// Get one free at huggingface.co > Settings > Access Tokens
const HF_TOKEN = '';

async function optimizePrompt(prompt) {
    const headers = { 'Content-Type': 'application/json' };
    if (HF_TOKEN) headers['Authorization'] = `Bearer ${HF_TOKEN}`;

    const body = JSON.stringify({
        inputs: `optimize: ${prompt.trim()}`,
        parameters: { max_new_tokens: 100, temperature: 0.3, do_sample: false },
        options: { wait_for_model: true }
    });

    const res = await fetch(HF_API, { method: 'POST', headers, body });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        if (res.status === 503) throw new Error('Model is warming up. Please wait 20 seconds and try again.');
        throw new Error(err.error || `API error ${res.status}`);
    }

    const data = await res.json();
    let optimized = '';
    if (Array.isArray(data) && data[0]?.generated_text) {
        optimized = data[0].generated_text.trim();
    } else if (data.generated_text) {
        optimized = data.generated_text.trim();
    } else {
        throw new Error('Unexpected API response. Try again.');
    }

    optimized = optimized.replace(/^optimize:\s*/i, '').trim();

    const tokensOriginal  = prompt.trim().split(/\s+/).length;
    const tokensOptimized = optimized.split(/\s+/).length;
    const tokensSaved     = Math.max(0, tokensOriginal - tokensOptimized);
    const reductionPct    = tokensOriginal > 0 ? ((tokensSaved / tokensOriginal) * 100).toFixed(1) : '0.0';
    const energySaved     = tokensSaved * 0.0001;
    const co2Saved        = (energySaved / 1000) * 385;

    return { optimizedPrompt: optimized, tokensOriginal, tokensOptimized, tokensSaved, reductionPct, energySaved, co2Saved };
}

window.optimizePrompt = optimizePrompt;
