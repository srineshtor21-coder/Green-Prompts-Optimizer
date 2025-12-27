from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import torch
import os
from transformers import T5Tokenizer, T5ForConditionalGeneration
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
CORS(app)  # Enable CORS for external connections
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


class PromptOptimizer:
    def __init__(self, model_path="optimizer_model"):
        self.model_path = model_path
        self.device = self._setup_device()
        self.tokenizer = None
        self.model = None
        self._load_model()
       
    def _setup_device(self):
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU device")
        return device
   
    def _load_model(self):
        try:
            logger.info(f"Loading model from {self.model_path}")
           
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model directory not found: {self.model_path}")
           
            self.tokenizer = T5Tokenizer.from_pretrained(
                self.model_path,
                local_files_only=True
            )
           
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_path,
                local_files_only=True
            )
           
            self.model.to(self.device)
            self.model.eval()
           
            logger.info("Model loaded successfully")
           
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
   
    def optimize(self, prompt, max_length=64, num_beams=5, temperature=0.7):
        """Optimize a verbose prompt to be more concise"""
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Empty prompt provided")
       
        # Add the task prefix that the model was trained with
        input_text = f"optimize: {prompt}"
       
        # Tokenize input
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding=True
        )
       
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
       
        # Generate optimized prompt
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                no_repeat_ngram_size=2,
                do_sample=False,
                length_penalty=0.6  # Encourage shorter outputs
            )
       
        # Decode the optimized text
        optimized_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
       
        # If the model didn't optimize well, apply fallback rules
        if len(optimized_text) >= len(prompt) * 0.9:
            optimized_text = self._fallback_optimization(prompt)
       
        return optimized_text.strip()
   
    def _fallback_optimization(self, prompt):
        """Simple rule-based optimization as fallback"""
        # Remove filler words
        filler_words = [
            "please", "can you", "could you", "i need", "i want to",
            "help me", "tell me", "explain to me", "for me", "to me"
        ]
       
        optimized = prompt.lower()
        for filler in filler_words:
            optimized = optimized.replace(filler, "")
       
        # Clean up extra spaces
        optimized = " ".join(optimized.split())
       
        # Capitalize first letter
        optimized = optimized[0].upper() + optimized[1:] if optimized else ""
       
        return optimized
   
    def calculate_metrics(self, original, optimized):
        """Calculate token savings and energy metrics"""
        # Count tokens
        original_tokens = len(self.tokenizer.encode(original, add_special_tokens=False))
        optimized_tokens = len(self.tokenizer.encode(optimized, add_special_tokens=False))
       
        tokens_saved = original_tokens - optimized_tokens
       
        # Calculate percentage savings
        if original_tokens > 0:
            savings_percent = (tokens_saved / original_tokens) * 100
        else:
            savings_percent = 0
       
        # Energy calculation based on research
        # GPT-3 uses approximately 0.0004 kWh per 1000 tokens
        # Source: Patterson et al. "Carbon Emissions and Large Neural Network Training"
        kwh_per_1000_tokens = 0.0004
       
        # Calculate energy saved in Watt-hours (Wh)
        energy_saved_kwh = (tokens_saved / 1000) * kwh_per_1000_tokens
        energy_saved_wh = energy_saved_kwh * 1000
       
        # CO2 calculation: Average grid ~0.5 kg CO2 per kWh
        co2_per_kwh = 0.5
        co2_saved_kg = energy_saved_kwh * co2_per_kwh
        co2_saved_grams = co2_saved_kg * 1000
       
        return {
            'original_tokens': original_tokens,
            'optimized_tokens': optimized_tokens,
            'tokens_saved': tokens_saved,
            'savings_percent': round(savings_percent, 1),
            'compression_ratio': round(optimized_tokens / original_tokens, 2) if original_tokens > 0 else 1.0,
            'energy_saved_wh': round(energy_saved_wh, 6),
            'co2_saved_grams': round(co2_saved_grams, 4)
        }


# Initialize optimizer
optimizer = PromptOptimizer()


# Example prompts
EXAMPLE_PROMPTS = [
    {
        "verbose": "Can you please explain to me what black holes are and how they work in space?",
        "optimized": "Explain black holes and their mechanics"
    },
    {
        "verbose": "I need help writing a Python program that can sort a list of numbers using bubble sort",
        "optimized": "Write Python bubble sort program"
    },
    {
        "verbose": "Could you help me understand how photosynthesis works in plants?",
        "optimized": "Explain photosynthesis process"
    },
    {
        "verbose": "I want to learn about the difference between machine learning and deep learning",
        "optimized": "Machine learning vs deep learning"
    },
    {
        "verbose": "Please tell me how I can improve the performance of my React application",
        "optimized": "Optimize React app performance"
    }
]


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GreenPrompts - AI Prompt Optimizer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 20px;
        }
        .logo {
            font-size: 48px;
            margin-bottom: 10px;
        }
        h1 {
            font-size: 36px;
            background: linear-gradient(135deg, #10b981, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .subtitle {
            color: rgba(16, 185, 129, 0.7);
        }
        .card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            min-height: 120px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 15px;
            color: white;
            font-size: 14px;
            resize: vertical;
            margin-bottom: 15px;
        }
        textarea::placeholder {
            color: rgba(16, 185, 129, 0.3);
        }
        textarea:focus {
            outline: none;
            border-color: #10b981;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #10b981, #059669);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        }
        button:disabled {
            background: rgba(100, 116, 139, 0.5);
            cursor: not-allowed;
            transform: none;
        }
        .examples {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .example-btn {
            padding: 8px 16px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            color: #10b981;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            width: auto;
        }
        .example-btn:hover {
            background: rgba(16, 185, 129, 0.2);
            transform: none;
        }
        .result {
            display: none;
            margin-top: 20px;
        }
        .result.show {
            display: block;
        }
        .result-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .result-box {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 15px;
        }
        .result-box h3 {
            font-size: 14px;
            color: #10b981;
            margin-bottom: 10px;
        }
        .result-box p {
            font-size: 14px;
            line-height: 1.6;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .metric {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .metric-label {
            font-size: 12px;
            color: rgba(16, 185, 129, 0.7);
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #10b981;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🌱</div>
            <h1>GreenPrompts</h1>
            <p class="subtitle">AI-Powered Prompt Optimizer - Reduce Tokens & Save Energy</p>
        </div>


        <div class="card">
            <div class="examples">
                <button class="example-btn" onclick="setExample(0)">Example 1</button>
                <button class="example-btn" onclick="setExample(1)">Example 2</button>
                <button class="example-btn" onclick="setExample(2)">Example 3</button>
                <button class="example-btn" onclick="setExample(3)">Example 4</button>
            </div>


            <textarea
                id="prompt"
                placeholder="Enter your verbose prompt here, e.g., 'Can you please explain to me what black holes are and how they work in space?'"
            ></textarea>


            <button onclick="optimize()" id="optimizeBtn">
                ⚡ Optimize Prompt
            </button>


            <div id="result" class="result">
                <div class="result-grid">
                    <div class="result-box">
                        <h3>📝 Original Prompt</h3>
                        <p id="originalText"></p>
                        <small id="originalTokens" style="color: rgba(16, 185, 129, 0.7);"></small>
                    </div>
                    <div class="result-box">
                        <h3>✨ Optimized Prompt</h3>
                        <p id="optimizedText" style="font-weight: 600; color: #10b981;"></p>
                        <small id="optimizedTokens" style="color: rgba(16, 185, 129, 0.7);"></small>
                    </div>
                </div>


                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Tokens Saved</div>
                        <div class="metric-value" id="tokensSaved">0</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Savings %</div>
                        <div class="metric-value" id="savingsPercent">0%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Energy Saved</div>
                        <div class="metric-value" id="energySaved">0 Wh</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">CO₂ Saved</div>
                        <div class="metric-value" id="co2Saved">0 g</div>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <script>
        const examples = [
            "Can you please explain to me what black holes are and how they work in space?",
            "I need help writing a Python program that can sort a list of numbers using bubble sort",
            "Could you help me understand how photosynthesis works in plants?",
            "Please tell me how I can improve the performance of my React application"
        ];


        function setExample(index) {
            document.getElementById('prompt').value = examples[index];
        }


        async function optimize() {
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) {
                alert('Please enter a prompt');
                return;
            }


            const btn = document.getElementById('optimizeBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Optimizing...';


            try {
                const response = await fetch('/optimize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt })
                });


                const data = await response.json();


                if (data.status === 'success') {
                    document.getElementById('originalText').textContent = data.original;
                    document.getElementById('originalTokens').textContent = data.original_tokens + ' tokens';
                    document.getElementById('optimizedText').textContent = data.optimized;
                    document.getElementById('optimizedTokens').textContent = data.optimized_tokens + ' tokens';
                    document.getElementById('tokensSaved').textContent = data.tokens_saved;
                    document.getElementById('savingsPercent').textContent = data.savings_percent + '%';
                    document.getElementById('energySaved').textContent = data.energy_saved_wh.toFixed(6) + ' Wh';
                    document.getElementById('co2Saved').textContent = data.co2_saved_grams.toFixed(4) + ' g';
                    document.getElementById('result').classList.add('show');
                } else {
                    alert('Optimization failed: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                btn.disabled = false;
                btn.innerHTML = '⚡ Optimize Prompt';
            }
        }


        // Allow Enter key to submit (with Shift+Enter for newline)
        document.getElementById('prompt').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                optimize();
            }
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "model_loaded": optimizer.model is not None,
        "device": str(optimizer.device)
    })


@app.route("/optimize", methods=["POST"])
def optimize_endpoint():
    try:
        data = request.get_json()
       
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
       
        prompt = data.get("prompt", "").strip()
       
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400
       
        if len(prompt) > 500:
            return jsonify({
                "error": "Prompt exceeds maximum length of 500 characters"
            }), 400
       
        # Optimize the prompt
        optimized_prompt = optimizer.optimize(prompt)
       
        # Calculate metrics
        metrics = optimizer.calculate_metrics(prompt, optimized_prompt)
       
        response_data = {
            "original": prompt,
            "optimized": optimized_prompt,
            "original_tokens": metrics['original_tokens'],
            "optimized_tokens": metrics['optimized_tokens'],
            "tokens_saved": metrics['tokens_saved'],
            "savings_percent": metrics['savings_percent'],
            "compression_ratio": metrics['compression_ratio'],
            "energy_saved_wh": metrics['energy_saved_wh'],
            "co2_saved_grams": metrics['co2_saved_grams'],
            "status": "success"
        }
       
        logger.info(f"✅ Optimized: '{prompt[:50]}...' → '{optimized_prompt}' | Saved {metrics['tokens_saved']} tokens ({metrics['savings_percent']}%) | Energy: {metrics['energy_saved_wh']:.6f} Wh")
       
        return jsonify(response_data), 200
       
    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve), "status": "error"}), 400
       
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return jsonify({
            "error": "An error occurred during optimization",
            "details": str(e),
            "status": "error"
        }), 500


@app.route("/batch-optimize", methods=["POST"])
def batch_optimize():
    try:
        data = request.get_json()
       
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
       
        prompts = data.get("prompts", [])
       
        if not isinstance(prompts, list):
            return jsonify({"error": "Prompts must be a list"}), 400
       
        if len(prompts) == 0:
            return jsonify({"error": "No prompts provided"}), 400
       
        if len(prompts) > 50:
            return jsonify({"error": "Maximum 50 prompts per batch"}), 400
       
        results = []
        total_tokens_saved = 0
        total_energy_saved = 0
       
        for idx, prompt in enumerate(prompts):
            prompt = prompt.strip()
           
            if not prompt:
                results.append({
                    "index": idx,
                    "error": "Empty prompt",
                    "status": "skipped"
                })
                continue
           
            if len(prompt) > 500:
                results.append({
                    "index": idx,
                    "error": "Prompt too long",
                    "status": "skipped"
                })
                continue
           
            try:
                optimized = optimizer.optimize(prompt)
                metrics = optimizer.calculate_metrics(prompt, optimized)
               
                total_tokens_saved += metrics['tokens_saved']
                total_energy_saved += metrics['energy_saved_wh']
               
                results.append({
                    "index": idx,
                    "original": prompt,
                    "optimized": optimized,
                    "tokens_saved": metrics['tokens_saved'],
                    "savings_percent": metrics['savings_percent'],
                    "energy_saved_wh": metrics['energy_saved_wh'],
                    "status": "success"
                })
               
            except Exception as e:
                results.append({
                    "index": idx,
                    "error": str(e),
                    "status": "failed"
                })
       
        return jsonify({
            "results": results,
            "total_prompts": len(prompts),
            "successful": sum(1 for r in results if r.get('status') == 'success'),
            "total_tokens_saved": total_tokens_saved,
            "total_energy_saved_wh": total_energy_saved,
            "status": "complete"
        }), 200
       
    except Exception as e:
        logger.error(f"Batch optimization error: {str(e)}")
        return jsonify({
            "error": "Batch optimization failed",
            "status": "error"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    import os
    
    # Use PORT from environment (for Render deployment)
    port = int(os.environ.get("PORT", 5000))
    
    print("\n" + "="*60)
    print("🌱 GreenPrompts - AI Prompt Optimizer")
    print("="*60)
    print(f"✅ Model loaded: {optimizer.model is not None}")
    print(f"💻 Device: {optimizer.device}")
    print(f"🌐 Server starting on port {port}")
    print("="*60 + "\n")
   
    # Use debug=False for production
    app.run(host="0.0.0.0", port=port, debug=False)

