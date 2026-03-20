/**
 * OPTIMIZER-CORE.JS
 * Calls the HF Space proxy. Auto-retries if Space is warming up (503).
 */

const PROXY_URL = 'https://sirenice-greenpromptshelper.hf.space/optimize';

async function optimizePrompt(prompt) {
    if (!prompt || !prompt.trim()) throw new Error('Empty prompt');

    // Try up to 4 times (handles cold Space startup — usually ready in 30-60s)
    const MAX_RETRIES = 4;
    const RETRY_DELAY = 15000; // 15 seconds between retries

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        let res;
        try {
            res = await fetch(PROXY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt.trim() })
            });
        } catch (networkErr) {
            if (attempt === MAX_RETRIES) throw new Error('Network error — check your internet connection.');
            await sleep(RETRY_DELAY);
            continue;
        }

        if (res.status === 503) {
            if (attempt === MAX_RETRIES) throw new Error('Space is still starting up. Please try again in 30 seconds.');
            // Show countdown in button text via a custom event
            window.dispatchEvent(new CustomEvent('gpo-warmup', { detail: { attempt, max: MAX_RETRIES } }));
            await sleep(RETRY_DELAY);
            continue;
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
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

window.optimizePrompt = optimizePrompt;
