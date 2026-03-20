/**
 * OPTIMIZER-CORE.JS
 * Calls the Hugging Face Inference API for sirenice/greenpromptsoptimizer
 * No token required — model is public. Uses x-wait-for-model to handle cold starts.
 */

const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API   = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

async function optimizePrompt(prompt) {
    if (!prompt || !prompt.trim()) throw new Error('Empty prompt');

    let res;
    try {
        res = await fetch(HF_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-wait-for-model': 'true'   // tells HF to wait for cold model instead of returning 503
            },
            body: JSON.stringify({
                inputs: `optimize: ${prompt.trim()}`,
                parameters: {
                    max_new_tokens: 150,
                    temperature: 0.3,
                    do_sample: false
                }
            })
        });
    } catch (networkErr) {
        throw new Error('Network error — check your internet connection.');
    }

    // 503 = model still loading despite x-wait-for-model (very rare)
    if (res.status === 503) {
        throw new Error('Model is warming up. Wait about 20 seconds and try again.');
    }

    // 401/403 should not happen for a public model — means HF blocked the request
    if (res.status === 401 || res.status === 403) {
        throw new Error('Access denied by Hugging Face. Make sure your model is set to Public in HF settings.');
    }

    if (!res.ok) {
        let msg = `API error ${res.status}`;
        try { const b = await res.json(); msg = b.error || msg; } catch {}
        throw new Error(msg);
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

    // Strip any echoed prefix
    optimized = optimized.replace(/^optimize:\s*/i, '').trim();

    // If model echoed the full input unchanged, do a local trim as fallback
    if (!optimized || optimized.toLowerCase() === prompt.trim().toLowerCase()) {
        optimized = prompt.trim()
            .replace(/\b(please|kindly|could you|can you|would you mind|I was wondering if|I would like you to|I need you to|like)\b/gi, '')
            .replace(/\s{2,}/g, ' ')
            .trim();
    }

    // Metrics
    const wordsOrig = prompt.trim().split(/\s+/).filter(Boolean).length;
    const wordsOpt  = optimized.split(/\s+/).filter(Boolean).length;
    const tokensSaved  = Math.max(0, Math.round((wordsOrig - wordsOpt) * 1.3));
    const reductionPct = wordsOrig > 0
        ? Math.max(0, ((wordsOrig - wordsOpt) / wordsOrig * 100)).toFixed(1)
        : '0.0';
    const energySaved = tokensSaved * 0.0003;
    const co2Saved    = energySaved * 0.385;

    return {
        optimizedPrompt: optimized,
        tokensSaved,
        reductionPct,
        energySaved,
        co2Saved
    };
}

window.optimizePrompt = optimizePrompt;
