/**
 * OPTIMIZER.JS
 * Used by optimizer.html - calls Hugging Face Inference API directly
 */

const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API   = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

async function optimizePrompt(prompt) {
    if (!prompt || !prompt.trim()) throw new Error('Empty prompt');

    const res = await fetch(HF_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputs: `optimize: ${prompt.trim()}`,
            parameters: { max_new_tokens: 100, temperature: 0.3, do_sample: false },
            options: { wait_for_model: true, use_cache: false }
        })
    });

    if (!res.ok) {
        if (res.status === 503) throw new Error('Model is warming up. Wait ~20 seconds and try again.');
        if (res.status === 401 || res.status === 403) throw new Error('API auth error.');
        const err = await res.text();
        throw new Error(err || `API error ${res.status}`);
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

    if (!optimized) throw new Error('Model returned empty response.');

    const tokensOriginal  = prompt.trim().split(/\s+/).length;
    const tokensOptimized = optimized.split(/\s+/).length;
    const tokensSaved     = Math.max(0, tokensOriginal - tokensOptimized);
    const reductionPct    = tokensOriginal > 0
        ? ((tokensSaved / tokensOriginal) * 100).toFixed(1)
        : '0.0';
    const energySaved = tokensSaved * 0.0001;
    const co2Saved    = (energySaved / 1000) * 385;

    return { optimizedPrompt: optimized, tokensOriginal, tokensOptimized, tokensSaved, reductionPct, energySaved, co2Saved };
}

window.optimizePrompt = optimizePrompt;
