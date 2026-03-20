/**
 * OPTIMIZER-CORE.JS
 * Calls the Hugging Face Inference API for sirenice/greenpromptsoptimizer
 */

const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_MODEL = 'sirenice/greenpromptsoptimizer';
const HF_API = `https://api-inference.huggingface.co/models/${HF_MODEL}`;

async function optimizePrompt(prompt) {
    const res = await fetch(HF_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

    const data = await res.json();

    let optimized = data?.[0]?.generated_text || data.generated_text || "";
    optimized = optimized.replace(/^optimize:\s*/i, '').trim();

    return { optimizedPrompt: optimized };
}

window.optimizePrompt = optimizePrompt;

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
