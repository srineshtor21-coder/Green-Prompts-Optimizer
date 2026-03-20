/**
 * OPTIMIZER-CORE.JS
 * Calls your HF Space proxy which forwards to the model server-side.
 * This avoids the CORS block that happens with direct browser → HF API calls.
 */

const PROXY_URL = 'https://sirenice-greenpromptshelper.hf.space/optimize';

async function optimizePrompt(prompt) {
    if (!prompt || !prompt.trim()) throw new Error('Empty prompt');

    let res;
    try {
        res = await fetch(PROXY_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt.trim() })
        });
    } catch (networkErr) {
        throw new Error('Network error — check your internet connection.');
    }

    if (res.status === 503) {
        throw new Error('Model is warming up. Wait about 20 seconds and try again.');
    }

    if (!res.ok) {
        let msg = `API error ${res.status}`;
        try { const b = await res.json(); msg = b.error || msg; } catch {}
        throw new Error(msg);
    }

    const data = await res.json();
    let optimized = data.optimized || '';

    if (!optimized) throw new Error('Model returned empty response. Try again.');

    // Fallback if model echoed input unchanged
    if (optimized.toLowerCase() === prompt.trim().toLowerCase()) {
        optimized = prompt.trim()
            .replace(/\b(please|kindly|could you|can you|would you|like|I was wondering|I would like you to|I need you to)\b/gi, '')
            .replace(/\s{2,}/g, ' ').trim();
    }

    // Metrics
    const wordsOrig   = prompt.trim().split(/\s+/).filter(Boolean).length;
    const wordsOpt    = optimized.split(/\s+/).filter(Boolean).length;
    const tokensSaved = Math.max(0, Math.round((wordsOrig - wordsOpt) * 1.3));
    const reductionPct = wordsOrig > 0
        ? Math.max(0, ((wordsOrig - wordsOpt) / wordsOrig * 100)).toFixed(1) : '0.0';
    const energySaved = tokensSaved * 0.0003;
    const co2Saved    = energySaved * 0.385;

    return { optimizedPrompt: optimized, tokensSaved, reductionPct, energySaved, co2Saved };
}

window.optimizePrompt = optimizePrompt;
