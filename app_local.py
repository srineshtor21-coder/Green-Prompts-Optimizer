"""
Green-Prompts-Optimizer: Energy-Efficient AI Prompt Optimization System
Author: Srinesh Toranala
ISM Original Work - Energy Saver AI

RENDER DEPLOYMENT VERSION - Uses YOUR trained model!
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import sqlite3
from datetime import datetime
import hashlib
import os
from pathlib import Path
import time

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'green-prompts-secret-key-2024-ism')
CORS(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'model_path': 'models/prompt_optimizer',  # YOUR trained model!
    'max_input_length': 256,
    'max_output_length': 128,
    'cache_size': 1000,
    'energy_per_token_wh': 0.000001,  # 1 microwatt-hour per token
    'co2_per_kwh_g': 475  # grams CO2 per kWh (US average)
}

# Get PORT from environment (Render sets this automatically)
PORT = int(os.environ.get('PORT', 5000))

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db():
    """Initialize SQLite databases"""
    # Users database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_optimizations INTEGER DEFAULT 0,
            total_energy_saved_wh REAL DEFAULT 0.0,
            total_co2_saved_g REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()
    
    # Cache database
    conn = sqlite3.connect('cache.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS optimization_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_hash TEXT UNIQUE NOT NULL,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            original_tokens INTEGER,
            optimized_tokens INTEGER,
            energy_saved_wh REAL,
            co2_saved_g REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hit_count INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()
    
    print("✓ Databases initialized")

# ============================================================================
# AI MODEL LOADING
# ============================================================================

class PromptOptimizer:
    """AI-powered prompt optimizer using YOUR trained T5 model"""
    
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading YOUR trained model from {model_path}...")
        print(f"Using device: {self.device}")
        
        try:
            # Load YOUR trained model
            self.tokenizer = T5Tokenizer.from_pretrained(model_path)
            self.model = T5ForConditionalGeneration.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            print("✓ YOUR TRAINED MODEL loaded successfully!")
        except Exception as e:
            print(f"⚠️  Error loading trained model: {e}")
            print("Falling back to rule-based optimization...")
            self.model = None
            self.tokenizer = None
        
        # In-memory cache
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def preprocess_prompt(self, prompt):
        """Smart preprocessing to reduce tokens"""
        # Remove redundant words
        redundant_words = [
            'please', 'kindly', 'could you', 'can you', 'would you',
            'I would like', 'I want to', 'help me', 'assist me',
            'I need to', 'I\'m trying to', 'basically', 'actually',
            'just', 'really', 'very', 'quite'
        ]
        
        result = prompt
        for word in redundant_words:
            result = result.replace(word, '')
        
        # Clean up extra spaces
        result = ' '.join(result.split())
        
        return result
    
    def count_tokens(self, text):
        """Count tokens using your model's tokenizer or approximation"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Approximation: ~4 chars per token
            return len(text) // 4
    
    def optimize(self, prompt):
        """Optimize prompt using YOUR trained AI model + preprocessing"""
        start_time = time.time()
        
        # Check cache first
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Memory cache
        if prompt_hash in self.cache:
            self.cache_hits += 1
            cached = self.cache[prompt_hash]
            return {
                **cached,
                'cached': True,
                'processing_time': time.time() - start_time
            }
        
        # Database cache
        cached_result = self.get_from_db_cache(prompt_hash)
        if cached_result:
            self.cache_hits += 1
            self.cache[prompt_hash] = cached_result
            self.update_cache_hit_count(prompt_hash)
            return {
                **cached_result,
                'cached': True,
                'processing_time': time.time() - start_time
            }
        
        self.cache_misses += 1
        
        # Preprocess first
        preprocessed = self.preprocess_prompt(prompt)
        
        # Use YOUR trained model if available
        if self.model and self.tokenizer:
            try:
                input_text = f"optimize: {preprocessed}"
                input_ids = self.tokenizer.encode(input_text, return_tensors='pt').to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        input_ids,
                        max_length=128,
                        num_beams=3,  # Reduced for speed
                        early_stopping=True,
                        no_repeat_ngram_size=2
                    )
                
                optimized = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception as e:
                print(f"Model inference error: {e}")
                optimized = preprocessed
        else:
            # Fallback: just use preprocessing
            optimized = preprocessed
        
        # Calculate savings
        original_tokens = self.count_tokens(prompt)
        optimized_tokens = self.count_tokens(optimized)
        tokens_saved = max(0, original_tokens - optimized_tokens)
        
        energy_saved_wh = tokens_saved * CONFIG['energy_per_token_wh']
        co2_saved_g = (energy_saved_wh / 1000) * CONFIG['co2_per_kwh_g']
        
        result = {
            'original': prompt,
            'optimized': optimized,
            'original_tokens': original_tokens,
            'optimized_tokens': optimized_tokens,
            'tokens_saved': tokens_saved,
            'reduction_percentage': round((tokens_saved / original_tokens * 100), 2) if original_tokens > 0 else 0,
            'energy_saved_wh': energy_saved_wh,
            'co2_saved_g': co2_saved_g,
            'cached': False,
            'processing_time': time.time() - start_time
        }
        
        # Save to cache
        self.cache[prompt_hash] = result
        self.save_to_db_cache(prompt_hash, result)
        
        # Limit memory cache size
        if len(self.cache) > CONFIG['cache_size']:
            # Remove oldest entry
            self.cache.pop(next(iter(self.cache)))
        
        return result
    
    def get_from_db_cache(self, prompt_hash):
        """Retrieve from database cache"""
        try:
            conn = sqlite3.connect('cache.db')
            c = conn.cursor()
            c.execute('SELECT * FROM optimization_cache WHERE prompt_hash = ?', (prompt_hash,))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'original': row[2],
                    'optimized': row[3],
                    'original_tokens': row[4],
                    'optimized_tokens': row[5],
                    'tokens_saved': row[4] - row[5],
                    'reduction_percentage': round(((row[4] - row[5]) / row[4] * 100), 2) if row[4] > 0 else 0,
                    'energy_saved_wh': row[6],
                    'co2_saved_g': row[7]
                }
        except Exception as e:
            print(f"Cache read error: {e}")
        return None
    
    def save_to_db_cache(self, prompt_hash, result):
        """Save to database cache"""
        try:
            conn = sqlite3.connect('cache.db')
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO optimization_cache 
                (prompt_hash, original_prompt, optimized_prompt, original_tokens, 
                 optimized_tokens, energy_saved_wh, co2_saved_g)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                prompt_hash,
                result['original'],
                result['optimized'],
                result['original_tokens'],
                result['optimized_tokens'],
                result['energy_saved_wh'],
                result['co2_saved_g']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def update_cache_hit_count(self, prompt_hash):
        """Increment cache hit counter"""
        try:
            conn = sqlite3.connect('cache.db')
            c = conn.cursor()
            c.execute('UPDATE optimization_cache SET hit_count = hit_count + 1 WHERE prompt_hash = ?', 
                     (prompt_hash,))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_stats(self):
        """Get optimizer statistics"""
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'model_loaded': self.model is not None
        }

# Initialize optimizer
optimizer = None

# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/api/signup', methods=['POST'])
@limiter.limit("5 per hour")
def signup():
    """User signup"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                 (username, email, password_hash))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'username': username
        })
    
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or email already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """User login"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'username': user[1]
            })
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/user', methods=['GET'])
def get_user():
    """Get current user info"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username')
        })
    return jsonify({'logged_in': False})

# ============================================================================
# ROUTES - OPTIMIZATION
# ============================================================================

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/optimize', methods=['POST'])
@limiter.limit("30 per minute")
def optimize_prompt():
    """Optimize a prompt using YOUR trained AI model"""
    data = request.json
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    if len(prompt) > 2000:
        return jsonify({'error': 'Prompt too long (max 2000 characters)'}), 400
    
    try:
        # Optimize using YOUR trained model
        result = optimizer.optimize(prompt)
        
        # Update user stats if logged in
        if 'user_id' in session:
            update_user_stats(
                session['user_id'],
                result['energy_saved_wh'],
                result['co2_saved_g']
            )
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Optimization error: {e}")
        return jsonify({'error': 'Optimization failed'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get global statistics"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT SUM(total_optimizations), SUM(total_energy_saved_wh), SUM(total_co2_saved_g) FROM users')
        stats = c.fetchone()
        conn.close()
        
        optimizer_stats = optimizer.get_stats()
        
        return jsonify({
            'total_optimizations': stats[0] or 0,
            'total_energy_saved_wh': round(stats[1] or 0, 6),
            'total_co2_saved_g': round(stats[2] or 0, 6),
            'total_users': get_user_count(),
            **optimizer_stats
        })
    
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def update_user_stats(user_id, energy_saved, co2_saved):
    """Update user optimization statistics"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            UPDATE users 
            SET total_optimizations = total_optimizations + 1,
                total_energy_saved_wh = total_energy_saved_wh + ?,
                total_co2_saved_g = total_co2_saved_g + ?
            WHERE id = ?
        ''', (energy_saved, co2_saved, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating user stats: {e}")

def get_user_count():
    """Get total number of users"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        count = c.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌱 GREEN-PROMPTS-OPTIMIZER - ISM PROJECT")
    print("="*70)
    print("Author: Srinesh Toranala")
    print("Using YOUR trained AI model!")
    print("="*70 + "\n")
    
    # Initialize databases
    init_db()
    
    # Load YOUR trained model
    optimizer = PromptOptimizer(CONFIG['model_path'])
    
    # Start server
    print(f"\n✓ Server starting on port {PORT}...")
    print(f"✓ Access at: http://localhost:{PORT}")
    print(f"✓ Using YOUR trained model: {CONFIG['model_path']}")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
