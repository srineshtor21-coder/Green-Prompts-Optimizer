/**
 * OPTIMIZER-CORE.JS
 * Calls Hugging Face Inference API for sirenice/greenpromptsoptimizer
 */

const HF_TOKEN = ''; 
const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API   = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

async function optimizePrompt(prompt) {
    const trimmed = prompt.trim();
    if (!trimmed) throw new Error('Prompt is empty');

    const headers = { 'Content-Type': 'application/json' };
    if (HF_TOKEN && !HF_TOKEN.includes('REPLACE')) {
        headers['Authorization'] = `Bearer ${HF_TOKEN}`;
    }

    let res;
    try {
        res = await fetch(HF_API, {
            method: 'POST',
            headers,
            body: JSON.stringify({
                inputs: `optimize: ${trimmed}`,
                parameters: {
                    max_new_tokens: 150,
                    temperature: 0.3,
                    do_sample: false
                },
                options: {
                    wait_for_model: true,
                    use_cache: false
                }
            })
        });
    } catch (networkErr) {
        throw new Error('Network error — check your internet connection.');
    }

    // Model is loading (cold start) — HF returns 503
    if (res.status === 503) {
        const body = await res.json().catch(() => ({}));
        const wait = body.estimated_time ? Math.ceil(body.estimated_time) : 20;
        throw new Error(`Model is warming up. Please wait ${wait} seconds and try again.`);
    }

    // No token / wrong token
    if (res.status === 401 || res.status === 403) {
        throw new Error('API token missing or invalid. Add your HF read token to optimizer-core.js');
    }

    if (!res.ok) {
        let msg = `API error ${res.status}`;
        try { const b = await res.json(); msg = b.error || msg; } catch {}
        throw new Error(msg);
    }

    const data = await res.json();

    // Parse response — HF text2text-generation returns [{generated_text: "..."}]
    let optimized = '';
    if (Array.isArray(data)) {
        optimized = (data[0]?.generated_text || data[0]?.summary_text || '').trim();
    } else if (typeof data === 'object') {
        optimized = (data.generated_text || data.summary_text || '').trim();
    }

    if (!optimized) {
        throw new Error('Model returned an empty response. Try a longer prompt.');
    }

    // Strip any accidental "optimize: " prefix the model might echo
    optimized = optimized.replace(/^optimize:\s*/i, '').trim();

    // If the model echoed the full input, fall back to a local trim
    if (optimized.toLowerCase() === trimmed.toLowerCase()) {
        optimized = localFallback(trimmed);
    }

    // Metrics — word-based approximation (1 word ≈ 1.3 tokens for English)
    const wordsOrig = trimmed.split(/\s+/).filter(Boolean).length;
    const wordsOpt  = optimized.split(/\s+/).filter(Boolean).length;
    const tokensSaved  = Math.max(0, Math.round((wordsOrig - wordsOpt) * 1.3));
    const reductionPct = wordsOrig > 0
        ? Math.max(0, ((wordsOrig - wordsOpt) / wordsOrig * 100)).toFixed(1)
        : '0.0';

    // Energy: ~0.0003 Wh per token saved (conservative estimate for T5 inference)
    const energySaved = tokensSaved * 0.0003;
    // CO2: global avg grid = 0.385 kg CO2/kWh → in grams per Wh = 0.000385
    const co2Saved = energySaved * 0.385;

    return {
        optimizedPrompt: optimized,
        tokensSaved,
        reductionPct,
        energySaved,
        co2Saved
    };
}

// Local fallback: removes common filler phrases if model fails
function localFallback(text) {
    return text
        .replace(/\b(please|kindly|could you|can you|would you|I was wondering if|I would like you to|I need you to)\b/gi, '')
        .replace(/\s{2,}/g, ' ')
        .trim();
}

// Expose globally so index.html, dashboard.html, optimizer.html can all call it
window.optimizePrompt = optimizePrompt;
