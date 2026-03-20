/**
 * OPTIMIZER-CORE.JS
 * Clean Hugging Face API call
 */

const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

async function optimizePrompt(prompt) {
    if (!prompt || !prompt.trim()) {
        throw new Error("Empty prompt");
    }

    const res = await fetch(HF_API, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            inputs: `optimize: ${prompt.trim()}`,
            parameters: {
                max_new_tokens: 100,
                temperature: 0.3,
                do_sample: false
            },
            options: { wait_for_model: true }
        })
    });

    // Handle loading / errors
    if (!res.ok) {
        if (res.status === 503) {
            throw new Error("Model is loading (cold start). Try again in ~20 seconds.");
        }
        const err = await res.text();
        throw new Error(err || `API error ${res.status}`);
    }

    const data = await res.json();

    let optimized = "";

    if (Array.isArray(data) && data[0]?.generated_text) {
        optimized = data[0].generated_text;
    } else if (data.generated_text) {
        optimized = data.generated_text;
    } else {
        throw new Error("Unexpected API response");
    }

    optimized = optimized.replace(/^optimize:\s*/i, "").trim();

    // metrics
    const tokensOriginal = prompt.trim().split(/\s+/).length;
    const tokensOptimized = optimized.split(/\s+/).length;
    const tokensSaved = Math.max(0, tokensOriginal - tokensOptimized);
    const reductionPct = tokensOriginal > 0
        ? ((tokensSaved / tokensOriginal) * 100).toFixed(1)
        : "0.0";
    const energySaved = tokensSaved * 0.0001;
    const co2Saved = (energySaved / 1000) * 385;

    return {
        optimizedPrompt: optimized,
        tokensOriginal,
        tokensOptimized,
        tokensSaved,
        reductionPct,
        energySaved,
        co2Saved
    };
}

// expose globally
window.optimizePrompt = optimizePrompt;
