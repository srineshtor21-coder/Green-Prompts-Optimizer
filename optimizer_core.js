/**
 * OPTIMIZER-CORE.JS
 * Calls the Hugging Face Inference API for sirenice/greenpromptsoptimizer
 * Drop this on any page that needs the optimize function.
 */

const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API   = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

// Optional: set your HF read token here for faster cold starts (safe for read-only public models)
// Leave as empty string to call without auth (works for public models, may be slower)
const HF_TOKEN = '';

/**
 * Optimize a prompt via the HF Inference API
 * @param {string} prompt - raw user prompt
 * @returns {Promise<{optimizedPrompt, tokensOriginal, tokensOptimized, tokensSaved, reductionPct, energySaved, co2Saved}>}
 */
async function optimizePrompt(prompt) {
    const input = `optimize: ${prompt.trim()}`;

    const headers = { 'Content-Type': 'application/json' };
    if (HF_TOKEN) headers['Authorization'] = `Bearer ${HF_TOKEN}`;

    const body = JSON.stringify({
        inputs: input,
        parameters: {
            max_new_tokens: 100,
            temperature: 0.3,
            do_sample: false,
        },
        options: { wait_for_model: true }
    });

    const res = await fetch(HF_API, { method: 'POST', headers, body });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        // Model loading (503) - tell user to wait
        if (res.status === 503) throw new Error('Model is warming up — please try again in 20 seconds.');
        throw new Error(err.error || `API error ${res.status}`);
    }

    const data = await res.json();
    // HF text2text returns [{generated_text: "..."}]
    let optimized = '';
    if (Array.isArray(data) && data[0]?.generated_text) {
        optimized = data[0].generated_text.trim();
    } else if (data.generated_text) {
        optimized = data.generated_text.trim();
    } else {
        throw new Error('Unexpected API response format.');
    }

    // Remove "optimize: " prefix if model echoed it
    optimized = optimized.replace(/^optimize:\s*/i, '').trim();

    // Token counts (rough: split on whitespace)
    const tokensOriginal  = prompt.trim().split(/\s+/).length;
    const tokensOptimized = optimized.split(/\s+/).length;
    const tokensSaved     = Math.max(0, tokensOriginal - tokensOptimized);
    const reductionPct    = tokensOriginal > 0 ? ((tokensSaved / tokensOriginal) * 100).toFixed(1) : '0.0';

    // Energy: 0.0001 Wh per token (CPU)
    const energySaved = tokensSaved * 0.0001;
    // CO2: 0.385 kg CO2 per kWh → grams
    const co2Saved = (energySaved / 1000) * 385;

    return {
        optimizedPrompt: optimized,
        tokensOriginal,
        tokensOptimized,
        tokensSaved,
        reductionPct,
        energySaved,
        co2Saved,
    };
}

window.optimizePrompt = optimizePrompt;
