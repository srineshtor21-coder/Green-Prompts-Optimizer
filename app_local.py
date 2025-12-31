"""
Green-Prompts-Optimizer: Complete Working System
Author: Srinesh Toranala - ALL BUGS FIXED
"""
from flask import Flask, render_template, request, jsonify, session, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os
from pathlib import Path
import time
import re
from functools import wraps
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'green-prompts-secret-key-2024')
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

CORS(app, supports_credentials=True, origins=['*'], 
     allow_headers=['Content-Type', 'Authorization'], methods=['GET', 'POST', 'OPTIONS'])

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["1000/day", "200/hour"])

# Initialize database when app starts (for gunicorn workers)
@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

CONFIG = {
    'model_path': 'models/prompt_optimizer',
    'fallback_model': 't5-small',
    'max_input_length': 256,
    'max_output_length': 128,
    'cache_size': 1000,
    'energy_per_token_wh': 0.000001,
    'co2_per_kwh_g': 475
}

PORT = int(os.environ.get('PORT', 5000))
optimizer = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_db(db_name):
    try:
        conn = sqlite3.connect(db_name, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def init_db():
    print("📊 Initializing databases...")
    
    # Users DB
    conn = get_db(os.path.join(DATA_DIR, 'users.db'))
    if conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_optimizations INTEGER DEFAULT 0,
                total_energy_saved_wh REAL DEFAULT 0.0,
                total_co2_saved_g REAL DEFAULT 0.0,
                total_tokens_saved INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                original_prompt TEXT NOT NULL,
                optimized_prompt TEXT NOT NULL,
                tokens_saved INTEGER,
                energy_saved_wh REAL,
                co2_saved_g REAL,
                reduction_percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE INDEX IF NOT EXISTS idx_user_history ON user_history(user_id);
        ''')
        conn.close()
        print("✅ Users DB ready")
    
    # Cache DB
    conn = get_db(os.path.join(DATA_DIR, 'cache.db'))
    if conn:
        conn.executescript('''
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
            );
            CREATE INDEX IF NOT EXISTS idx_cache_hash ON optimization_cache(prompt_hash);
        ''')
        conn.close()
        print("✅ Cache DB ready")

class PromptOptimizer:
    def __init__(self, model_path, fallback_model=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.model_type = "none"
        self.cache = {}
        self.total_optimizations = 0
        
        print(f"🤖 Initializing on {self.device}")
        
        # SKIP MODEL LOADING ON RENDER (free tier can't handle it)
        if os.environ.get('RENDER') or os.environ.get('PORT') == '10000':
            print("⚠️ Running on Render - Rule-based optimization only (model in repo)")
            self.model_type = "rule_based"
            return
        
        # Try trained model (only loads locally)
        try:
            if Path(model_path).exists():
                print(f"Loading YOUR model from {model_path}...")
                self.tokenizer = T5Tokenizer.from_pretrained(model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(model_path)
                self.model.to(self.device)
                self.model.eval()
                self.model_loaded = True
                self.model_type = "custom_trained"
                print("✅ YOUR MODEL loaded!")
                return
        except Exception as e:
            print(f"Custom model failed: {e}")
        
        # Fallback
        if fallback_model:
            try:
                print(f"Loading fallback: {fallback_model}")
                self.tokenizer = T5Tokenizer.from_pretrained(fallback_model)
                self.model = T5ForConditionalGeneration.from_pretrained(fallback_model)
                self.model.to(self.device)
                self.model.eval()
                self.model_loaded = True
                self.model_type = "fallback"
                print("✅ Fallback loaded")
                return
            except Exception as e:
                print(f"Fallback failed: {e}")
        
        print("⚠️ Rule-based mode only")
        self.model_type = "rule_based"
    
    def preprocess(self, prompt):
        patterns = [
            (r'\bplease\b', ''), (r'\bkindly\b', ''), (r'\bcould you\b', ''),
            (r'\bcan you\b', ''), (r'\bwould you\b', ''), (r'\bI would like\b', ''),
            (r'\bhelp me\b', ''), (r'\bI need to\b', ''), (r'\bjust\b', ''),
            (r'\breally\b', ''), (r'\bvery\b', ''), (r'\bquite\b', ''),
        ]
        result = prompt
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        result = re.sub(r'\s+', ' ', result).strip()
        return result
    
    def count_tokens(self, text):
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except:
                pass
        return max(1, len(text) // 4)
    
    def optimize_with_model(self, prompt):
        try:
            input_text = f"optimize: {prompt}"
            input_ids = self.tokenizer.encode(
                input_text, return_tensors='pt', 
                max_length=CONFIG['max_input_length'], truncation=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids, max_length=CONFIG['max_output_length'],
                    num_beams=4, early_stopping=True, no_repeat_ngram_size=2
                )
            
            optimized = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return optimized if len(optimized) < len(prompt) else None
        except Exception as e:
            print(f"Model error: {e}")
            return None
    
    def optimize(self, prompt):
        start_time = time.time()
        self.total_optimizations += 1
        
        if not prompt or len(prompt.strip()) == 0:
            return {'error': 'Empty prompt', 'success': False}
        
        prompt = prompt.strip()
        if len(prompt) > 2000:
            return {'error': 'Prompt too long', 'success': False}
        
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        # Check cache
        if prompt_hash in self.cache:
            result = self.cache[prompt_hash].copy()
            result['cached'] = True
            result['processing_time'] = time.time() - start_time
            return result
        
        # Check DB cache
        cached = self._get_from_db_cache(prompt_hash)
        if cached:
            self.cache[prompt_hash] = cached
            cached['cached'] = True
            cached['processing_time'] = time.time() - start_time
            return cached
        
        # Preprocess
        preprocessed = self.preprocess(prompt)
        
        # Try model
        optimized = None
        method = "rule_based"
        
        if self.model_loaded:
            optimized = self.optimize_with_model(preprocessed)
            if optimized:
                method = self.model_type
        
        if not optimized or len(optimized) >= len(prompt):
            optimized = preprocessed
        
        # Calculate metrics
        orig_tokens = self.count_tokens(prompt)
        opt_tokens = self.count_tokens(optimized)
        tokens_saved = max(1, orig_tokens - opt_tokens)
        
        reduction_pct = (tokens_saved / orig_tokens * 100) if orig_tokens > 0 else 0
        energy_saved = tokens_saved * CONFIG['energy_per_token_wh']
        co2_saved = (energy_saved / 1000) * CONFIG['co2_per_kwh_g']
        
        result = {
            'success': True,
            'original': prompt,
            'optimized': optimized,
            'original_tokens': orig_tokens,
            'optimized_tokens': opt_tokens,
            'tokens_saved': tokens_saved,
            'reduction_percentage': round(reduction_pct, 2),
            'energy_saved_wh': round(energy_saved, 8),
            'co2_saved_g': round(co2_saved, 6),
            'cached': False,
            'processing_time': round(time.time() - start_time, 4),
            'optimization_method': method,
            'model_type': self.model_type
        }
        
        # Save to cache
        self.cache[prompt_hash] = result.copy()
        self._save_to_db_cache(prompt_hash, result)
        
        if len(self.cache) > CONFIG['cache_size']:
            self.cache.pop(next(iter(self.cache)))
        
        return result
    
    def _get_from_db_cache(self, prompt_hash):
        try:
            conn = get_db('cache.db')
            if conn:
                c = conn.cursor()
                c.execute('SELECT * FROM optimization_cache WHERE prompt_hash = ?', (prompt_hash,))
                row = c.fetchone()
                conn.close()
                
                if row:
                    tokens_saved = row['original_tokens'] - row['optimized_tokens']
                    return {
                        'success': True,
                        'original': row['original_prompt'],
                        'optimized': row['optimized_prompt'],
                        'original_tokens': row['original_tokens'],
                        'optimized_tokens': row['optimized_tokens'],
                        'tokens_saved': tokens_saved,
                        'reduction_percentage': round((tokens_saved/row['original_tokens']*100), 2),
                        'energy_saved_wh': row['energy_saved_wh'],
                        'co2_saved_g': row['co2_saved_g']
                    }
        except:
            pass
        return None
    
    def _save_to_db_cache(self, prompt_hash, result):
        try:
            conn = get_db('cache.db')
            if conn:
                c = conn.cursor()
                c.execute('''INSERT OR REPLACE INTO optimization_cache 
                    (prompt_hash, original_prompt, optimized_prompt, original_tokens, 
                     optimized_tokens, energy_saved_wh, co2_saved_g)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (prompt_hash, result['original'], result['optimized'],
                     result['original_tokens'], result['optimized_tokens'],
                     result['energy_saved_wh'], result['co2_saved_g']))
                conn.commit()
                conn.close()
        except:
            pass
# ============================================================
# GLOBAL STARTUP INITIALIZATION (Gunicorn-safe)
# ============================================================

print("=" * 80)
print("🌿 GREEN PROMPTS OPTIMIZER - Startup Initialization")
print("=" * 80)

# Initialize databases at import time (Render-safe)
try:
    init_db()
except Exception as e:
    print(f"❌ Database initialization failed: {e}")

# Initialize optimizer at import time (Gunicorn-safe)
try:
    print("🤖 Initializing optimizer at startup...")
    optimizer = PromptOptimizer(CONFIG['model_path'], CONFIG['fallback_model'])
    print(f"✅ Optimizer ready | Mode: {optimizer.model_type}")
except Exception as e:
    optimizer = None
    print("❌ Optimizer failed to initialize")
    traceback.print_exc()

print("=" * 80)

# AUTH ROUTES
@app.route('/api/signup', methods=['POST', 'OPTIONS'])
@limiter.limit("10/hour")
def signup():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'error': 'Missing fields', 'success': False}), 400
        
        if len(username) < 3 or len(password) < 6:
            return jsonify({'error': 'Username/password too short', 'success': False}), 400
        
        conn = get_db('users.db')
        if not conn:
            return jsonify({'error': 'DB error', 'success': False}), 500
        
        try:
            c = conn.cursor()
            password_hash = generate_password_hash(password)
            c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                     (username, email, password_hash))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            
            session.permanent = True
            session['user_id'] = user_id
            session['username'] = username
            
            print(f"✅ New user: {username}")
            return jsonify({'success': True, 'message': 'Account created!', 
                          'username': username, 'user_id': user_id}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Username/email exists', 'success': False}), 400
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
@limiter.limit("20/hour")
def login():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials', 'success': False}), 400
        
        conn = get_db('users.db')
        if not conn:
            return jsonify({'error': 'DB error', 'success': False}), 500
        
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            print(f"✅ Login: {username}")
            return jsonify({'success': True, 'message': 'Logged in!', 
                          'username': user['username'], 'user_id': user['id']}), 200
        
        return jsonify({'error': 'Invalid credentials', 'success': False}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user_id' in session:
        try:
            conn = get_db('users.db')
            if conn:
                c = conn.cursor()
                c.execute('''SELECT username, email, total_optimizations, 
                           total_energy_saved_wh, total_co2_saved_g, total_tokens_saved 
                           FROM users WHERE id = ?''', (session['user_id'],))
                user = c.fetchone()
                conn.close()
                
                if user:
                    return jsonify({
                        'logged_in': True,
                        'username': user['username'],
                        'email': user['email'],
                        'total_optimizations': user['total_optimizations'],
                        'total_energy_saved_wh': round(user['total_energy_saved_wh'], 6),
                        'total_co2_saved_g': round(user['total_co2_saved_g'], 6),
                        'total_tokens_saved': user['total_tokens_saved']
                    })
        except:
            pass
    return jsonify({'logged_in': False}), 200

# OPTIMIZATION ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/optimize', methods=['POST', 'OPTIONS'])
@limiter.limit("100/minute")
def optimize_prompt():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'No prompt', 'success': False}), 400
        
        if optimizer is None:
            return jsonify({
                'success': False,
                'error': 'Optimizer not available',
                'model_status': 'offline'
                }), 503

        result = optimizer.optimize(prompt)

        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Update user stats
        if 'user_id' in session:
            conn = get_db('users.db')
            if conn:
                c = conn.cursor()
                c.execute('''UPDATE users SET 
                    total_optimizations = total_optimizations + 1,
                    total_energy_saved_wh = total_energy_saved_wh + ?,
                    total_co2_saved_g = total_co2_saved_g + ?,
                    total_tokens_saved = total_tokens_saved + ?
                    WHERE id = ?''',
                    (result['energy_saved_wh'], result['co2_saved_g'], 
                     result['tokens_saved'], session['user_id']))
                
                c.execute('''INSERT INTO user_history 
                    (user_id, original_prompt, optimized_prompt, tokens_saved, 
                     energy_saved_wh, co2_saved_g, reduction_percentage)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (session['user_id'], result['original'], result['optimized'],
                     result['tokens_saved'], result['energy_saved_wh'], 
                     result['co2_saved_g'], result['reduction_percentage']))
                conn.commit()
                conn.close()
        
        print(f"✅ Optimized: {result['reduction_percentage']}% reduction")
        return jsonify(result), 200
    except Exception as e:
        print(f"Optimize error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db('users.db')
        if conn:
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) as users, 
                       SUM(total_optimizations) as opts,
                       SUM(total_energy_saved_wh) as energy,
                       SUM(total_co2_saved_g) as co2,
                       SUM(total_tokens_saved) as tokens
                       FROM users''')
            row = c.fetchone()
            conn.close()
            
            return jsonify({
                'total_users': row['users'] or 0,
                'total_optimizations': row['opts'] or 0,
                'total_energy_saved_wh': round(row['energy'] or 0, 6),
                'total_co2_saved_g': round(row['co2'] or 0, 4),
                'total_tokens_saved': row['tokens'] or 0,
                'model_status': optimizer.model_type if optimizer else 'offline',
                'cache_size': len(optimizer.cache) if optimizer else 0
            })
    except Exception as e:
        print(f"Stats error: {e}")
    
    return jsonify({'total_users': 0, 'total_optimizations': 0}), 200

@app.route('/api/history', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Login required', 'success': False}), 401
    
    try:
        conn = get_db('users.db')
        if conn:
            c = conn.cursor()
            c.execute('''SELECT original_prompt, optimized_prompt, tokens_saved,
                       energy_saved_wh, co2_saved_g, reduction_percentage, created_at
                       FROM user_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 50''',
                     (session['user_id'],))
            rows = c.fetchall()
            conn.close()
            
            history = [{
                'original': row['original_prompt'],
                'optimized': row['optimized_prompt'],
                'tokens_saved': row['tokens_saved'],
                'energy_saved_wh': round(row['energy_saved_wh'], 8),
                'co2_saved_g': round(row['co2_saved_g'], 6),
                'reduction_percentage': round(row['reduction_percentage'], 2),
                'created_at': row['created_at']
            } for row in rows]
            
            return jsonify({'success': True, 'history': history})
    except Exception as e:
        print(f"History error: {e}")
    
    return jsonify({'error': 'Failed to fetch history', 'success': False}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': optimizer.model_loaded if optimizer else False,
        'model_type': optimizer.model_type if optimizer else 'none',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🌿 GREEN PROMPTS OPTIMIZER - Starting...")
    print("=" * 80)
    
    # Initialize database FIRST
    init_db()
    
    # Initialize optimizer
    print("\n🤖 Loading AI model...")
    optimizer = PromptOptimizer(CONFIG['model_path'], CONFIG['fallback_model'])
    
    print("\n" + "=" * 80)
    print(f"✅ Server ready on port {PORT}")
    print(f"🔗 Visit: http://localhost:{PORT}")
    print(f"🤖 Model: {optimizer.model_type}")
    print("=" * 80 + "\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
