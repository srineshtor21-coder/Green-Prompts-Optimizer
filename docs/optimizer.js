const HF_SPACE = "https://sirenice-greenpromptsoptimizer.hf.space";
const API_URL = HF_SPACE + "/run/predict";

async function optimizePrompt() {
  const prompt = document.getElementById("prompt-input").value.trim();
  const preserve = document.getElementById("preserve-meaning").checked;

  if (!prompt) return alert("Enter prompt");

  showLoading();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ data: [prompt, preserve] })
    });

    if (!res.ok) throw new Error(res.status);

    const json = await res.json();

    // Fix Gradio nested output
    let d = json.data;
    if (Array.isArray(d[0])) d = d[0];

    const [optimized, info, tokens, reduction, energy, co2] = d;

    document.getElementById("optimized-output").value = optimized;
    document.getElementById("tokens-saved").innerText = tokens;
    document.getElementById("reduction-pct").innerText = reduction;
    document.getElementById("energy-saved").innerText = energy;
    document.getElementById("co2-saved").innerText = co2;

  } catch (e) {
    console.error(e);
    alert("HF Space sleeping or CORS blocked");
  }

  hideLoading();
}
