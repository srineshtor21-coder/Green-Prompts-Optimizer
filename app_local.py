"""
Green-Prompts-Optimizer: Energy-Efficient AI Prompt Optimization System
Author: Srinesh Toranala
ISM Original Work - Energy Saver AI

This application optimizes AI prompts to reduce computational load and energy consumption
while maintaining semantic meaning and effectiveness.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForSeq2SeqLM
import json
import time
import datetime
import hashlib
import secrets
import os
from pathlib import Path
import sqlite3
from functools import wraps
import re
import numpy as np
from collections import defaultdict
import pickle

# ============================================================================
# CONFIGURATION AND INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Rate limiting to prevent abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Directory setup
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

for directory in [DATA_DIR, MODELS_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# Database setup
DB_PATH = DATA_DIR / "users.db"
CACHE_DB_PATH = DATA_DIR / "prompt_cache.db"

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_database():
    """Initialize SQLite databases for users and prompt caching"""
    # Users database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_prompts INTEGER DEFAULT 0,
            total_energy_saved REAL DEFAULT 0.0,
            total_co2_saved REAL DEFAULT 0.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            energy_saved REAL,
            co2_saved REAL,
            tokens_saved INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Prompt cache database
    cache_conn = sqlite3.connect(CACHE_DB_PATH)
    cache_cursor = cache_conn.cursor()
    
    cache_cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompt_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_hash TEXT UNIQUE NOT NULL,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            token_count_original INTEGER,
            token_count_optimized INTEGER,
            energy_saved REAL,
            usage_count INTEGER DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cache_conn.commit()
    cache_conn.close()

init_database()

# ============================================================================
# ENERGY CALCULATION MODELS
# ============================================================================

class EnergyCalculator:
    """
    Calculate energy consumption and CO2 emissions for AI model inference
    Based on research from Zeus library and GPU power consumption data
    """
    
    def __init__(self):
        # Average power consumption per token (in Watt-hours)
        # Based on T5-small model running on CPU
        self.power_per_token_cpu = 0.0001  # Wh per token
        self.power_per_token_gpu = 0.0003  # Wh per token (if GPU available)
        
        # CO2 emissions factor (kg CO2 per kWh) - US average
        self.co2_factor = 0.385
        
        # Device detection
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.power_per_token = self.power_per_token_gpu if self.device == "cuda" else self.power_per_token_cpu
    
    def calculate_energy(self, token_count, inference_time=None):
        """
        Calculate energy consumption for processing tokens
        
        Args:
            token_count: Number of tokens processed
            inference_time: Actual inference time (optional)
        
        Returns:
            dict with energy metrics
        """
        # Base calculation on token count
        energy_wh = token_count * self.power_per_token
        
        # If we have actual inference time, adjust calculation
        if inference_time:
            # Assume model uses about 15W on CPU during inference
            model_power = 15 if self.device == "cpu" else 75  # watts
            time_based_energy = (model_power * inference_time) / 3600  # convert to Wh
            energy_wh = max(energy_wh, time_based_energy)
        
        # Convert to kWh
        energy_kwh = energy_wh / 1000
        
        # Calculate CO2 emissions
        co2_kg = energy_kwh * self.co2_factor
        co2_g = co2_kg * 1000
        
        return {
            'energy_wh': round(energy_wh, 6),
            'energy_kwh': round(energy_kwh, 8),
            'co2_kg': round(co2_kg, 8),
            'co2_g': round(co2_g, 6),
            'device': self.device
        }
    
    def calculate_savings(self, original_tokens, optimized_tokens, original_time=None, optimized_time=None):
        """Calculate energy and CO2 savings from optimization"""
        original_metrics = self.calculate_energy(original_tokens, original_time)
        optimized_metrics = self.calculate_energy(optimized_tokens, optimized_time)
        
        savings = {
            'original': original_metrics,
            'optimized': optimized_metrics,
            'saved_energy_wh': round(original_metrics['energy_wh'] - optimized_metrics['energy_wh'], 6),
            'saved_co2_g': round(original_metrics['co2_g'] - optimized_metrics['co2_g'], 6),
            'tokens_original': original_tokens,
            'tokens_optimized': optimized_tokens,
            'tokens_saved': original_tokens - optimized_tokens,
            'percentage_reduction': round(((original_tokens - optimized_tokens) / original_tokens * 100), 2) if original_tokens > 0 else 0
        }
        
        return savings

# ============================================================================
# PROMPT CACHE SYSTEM
# ============================================================================

class PromptCache:
    """
    Intelligent caching system to store and reuse optimized prompts
    Reduces redundant model inference, saving energy
    """
    
    def __init__(self, db_path=CACHE_DB_PATH):
        self.db_path = db_path
        self.memory_cache = {}  # In-memory cache for faster access
        self.max_memory_cache = 1000
        self.load_frequent_prompts()
    
    def generate_hash(self, prompt):
        """Generate a hash for the prompt"""
        return hashlib.sha256(prompt.lower().strip().encode()).hexdigest()
    
    def load_frequent_prompts(self):
        """Load frequently used prompts into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prompt_hash, original_prompt, optimized_prompt, 
                   token_count_original, token_count_optimized, energy_saved
            FROM prompt_cache
            ORDER BY usage_count DESC
            LIMIT ?
        ''', (self.max_memory_cache,))
        
        for row in cursor.fetchall():
            self.memory_cache[row[0]] = {
                'original': row[1],
                'optimized': row[2],
                'tokens_original': row[3],
                'tokens_optimized': row[4],
                'energy_saved': row[5]
            }
        
        conn.close()
    
    def get(self, prompt):
        """Retrieve cached optimized prompt if exists"""
        prompt_hash = self.generate_hash(prompt)
        
        # Check memory cache first
        if prompt_hash in self.memory_cache:
            self.increment_usage(prompt_hash)
            return self.memory_cache[prompt_hash]
        
        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_prompt, optimized_prompt, token_count_original, 
                   token_count_optimized, energy_saved
            FROM prompt_cache
            WHERE prompt_hash = ?
        ''', (prompt_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            cached_data = {
                'original': row[0],
                'optimized': row[1],
                'tokens_original': row[2],
                'tokens_optimized': row[3],
                'energy_saved': row[4]
            }
            
            # Add to memory cache
            self.memory_cache[prompt_hash] = cached_data
            self.increment_usage(prompt_hash)
            
            return cached_data
        
        return None
    
    def set(self, prompt, optimized, tokens_original, tokens_optimized, energy_saved):
        """Store optimized prompt in cache"""
        prompt_hash = self.generate_hash(prompt)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO prompt_cache 
                (prompt_hash, original_prompt, optimized_prompt, token_count_original, 
                 token_count_optimized, energy_saved)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (prompt_hash, prompt, optimized, tokens_original, tokens_optimized, energy_saved))
            
            conn.commit()
            
            # Add to memory cache
            self.memory_cache[prompt_hash] = {
                'original': prompt,
                'optimized': optimized,
                'tokens_original': tokens_original,
                'tokens_optimized': tokens_optimized,
                'energy_saved': energy_saved
            }
        except sqlite3.IntegrityError:
            # Prompt already exists, update it
            cursor.execute('''
                UPDATE prompt_cache 
                SET optimized_prompt = ?, token_count_optimized = ?, 
                    energy_saved = ?, usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE prompt_hash = ?
            ''', (optimized, tokens_optimized, energy_saved, prompt_hash))
            conn.commit()
        
        conn.close()
    
    def increment_usage(self, prompt_hash):
        """Increment usage counter for cached prompt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE prompt_cache 
            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
            WHERE prompt_hash = ?
        ''', (prompt_hash,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), SUM(usage_count), SUM(energy_saved) FROM prompt_cache')
        total_cached, total_uses, total_energy_saved = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_cached_prompts': total_cached or 0,
            'total_cache_hits': total_uses or 0,
            'total_energy_saved_from_cache': round(total_energy_saved or 0, 4)
        }

# ============================================================================
# AI MODEL LOADER AND OPTIMIZER
# ============================================================================

class PromptOptimizer:
    """
    Main AI model for prompt optimization
    Uses T5 transformer for sequence-to-sequence optimization
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.energy_calc = EnergyCalculator()
        self.cache = PromptCache()
        self.load_model()
    
    def load_model(self):
        """Load the T5 model for prompt optimization"""
        try:
            model_path = MODELS_DIR / "prompt_optimizer"
            
            if model_path.exists():
                print(f"Loading fine-tuned model from {model_path}")
                self.tokenizer = T5Tokenizer.from_pretrained(model_path)
                self.model = T5ForConditionalGeneration.from_pretrained(model_path)
            else:
                print("Loading base T5-small model")
                self.tokenizer = T5Tokenizer.from_pretrained("t5-small")
                self.model = T5ForConditionalGeneration.from_pretrained("t5-small")
            
            self.model.to(self.device)
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def preprocess_prompt(self, prompt):
        """Clean and prepare prompt for optimization"""
        # Remove excessive whitespace
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        # Remove redundant phrases
        redundant_phrases = [
            'please help me',
            'can you please',
            'i need help with',
            'could you',
            'would you mind'
        ]
        
        prompt_lower = prompt.lower()
        for phrase in redundant_phrases:
            prompt_lower = prompt_lower.replace(phrase, '')
        prompt_lower = re.sub(r'\s+', ' ', prompt_lower).strip()

        # Reconstruct with proper capitalization
        if len(prompt_lower) > 0:
            prompt = prompt_lower[0].upper() + prompt_lower[1:]
        
        return prompt.strip()
    
    def optimize_prompt(self, prompt, use_cache=True):
        """
        Optimize a prompt to reduce tokens while preserving meaning
        
        Args:
            prompt: Original user prompt
            use_cache: Whether to use cached results
        
        Returns:
            dict with optimization results
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cached = self.cache.get(prompt)
            if cached:
                inference_time = time.time() - start_time
                return {
                    'original_prompt': prompt,
                    'optimized_prompt': cached['optimized'],
                    'tokens_original': cached['tokens_original'],
                    'tokens_optimized': cached['tokens_optimized'],
                    'energy_saved_wh': cached['energy_saved'],
                    'inference_time': inference_time,
                    'from_cache': True
                }
        
        # Preprocess
        preprocessed = self.preprocess_prompt(prompt)
        
        # Tokenize original
        original_tokens = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        original_token_count = original_tokens.input_ids.size(1)

        
        # Prepare input for model
        input_text = f"optimize: {preprocessed}"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        input_ids = input_ids.to(self.device)
        
        # Generate optimized prompt
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_length=128,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2,
                temperature=0.7
            )
        
        optimized_prompt = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Tokenize optimized
        optimized_tokens = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        optimized_token_count = riginal_tokens.input_ids.size(1)
        
        inference_time = time.time() - start_time
        
        # Calculate energy savings
        savings = self.energy_calc.calculate_savings(
            original_token_count,
            optimized_token_count,
            inference_time,
            inference_time * 0.6  # Optimized prompt typically processes faster
        )
        
        # Cache the result
        if use_cache:
            self.cache.set(
                prompt,
                optimized_prompt,
                original_token_count,
                optimized_token_count,
                savings['saved_energy_wh']
            )
        
        return {
            'original_prompt': prompt,
            'optimized_prompt': optimized_prompt,
            'tokens_original': original_token_count,
            'tokens_optimized': optimized_token_count,
            'tokens_saved': savings['tokens_saved'],
            'percentage_reduction': savings['percentage_reduction'],
            'energy_original_wh': savings['original']['energy_wh'],
            'energy_optimized_wh': savings['optimized']['energy_wh'],
            'energy_saved_wh': savings['saved_energy_wh'],
            'co2_saved_g': savings['saved_co2_g'],
            'inference_time': inference_time,
            'from_cache': False,
            'device': self.device.type
        }
    
    def batch_optimize(self, prompts):
        """Optimize multiple prompts at once"""
        results = []
        for prompt in prompts:
            result = self.optimize_prompt(prompt)
            results.append(result)
        return results

# Initialize the optimizer
optimizer = PromptOptimizer()

# ============================================================================
# USER AUTHENTICATION SYSTEM
# ============================================================================

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def create_user(username, email, password):
    """Create a new user account"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {'success': True, 'user_id': user_id}
    
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': 'Username or email already exists'}

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    cursor.execute('''
        SELECT id, username, email FROM users
        WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'success': True,
            'user_id': user[0],
            'username': user[1],
            'email': user[2]
        }
    
    return {'success': False, 'error': 'Invalid credentials'}

def save_user_history(user_id, original, optimized, energy_saved, co2_saved, tokens_saved):
    """Save optimization to user history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_history 
        (user_id, original_prompt, optimized_prompt, energy_saved, co2_saved, tokens_saved)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, original, optimized, energy_saved, co2_saved, tokens_saved))
    
    cursor.execute('''
        UPDATE users
        SET total_prompts = total_prompts + 1,
            total_energy_saved = total_energy_saved + ?,
            total_co2_saved = total_co2_saved + ?
        WHERE id = ?
    ''', (energy_saved, co2_saved, user_id))
    
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Get user statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT total_prompts, total_energy_saved, total_co2_saved
        FROM users WHERE id = ?
    ''', (user_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    if stats:
        return {
            'total_prompts': stats[0],
            'total_energy_saved': round(stats[1], 4),
            'total_co2_saved': round(stats[2], 4)
        }
    
    return None

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
@limiter.limit("5 per hour")
def signup():
    """User registration endpoint"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validation
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    if '@' not in email:
        return jsonify({'error': 'Invalid email address'}), 400
    
    result = create_user(username, email, password)
    
    if result['success']:
        session['user_id'] = result['user_id']
        session['username'] = username
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'username': username
        })
    
    return jsonify(result), 400

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """User login endpoint"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    result = authenticate_user(username, password)
    
    if result['success']:
        session['user_id'] = result['user_id']
        session['username'] = result['username']
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': result['username']
        })
    
    return jsonify(result), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/optimize', methods=['POST'])
@limiter.limit("30 per minute")
def optimize():
    """Main optimization endpoint"""
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'Prompt cannot be empty'}), 400
    
    if len(prompt) > 2000:
        return jsonify({'error': 'Prompt too long (max 2000 characters)'}), 400
    
    try:
        result = optimizer.optimize_prompt(prompt)
        
        # Save to user history if logged in
        if 'user_id' in session:
            save_user_history(
                session['user_id'],
                result['original_prompt'],
                result['optimized_prompt'],
                result['energy_saved_wh'],
                result['co2_saved_g'],
                result['tokens_saved']
            )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    cache_stats = optimizer.cache.get_stats()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*), SUM(total_prompts), SUM(total_energy_saved), SUM(total_co2_saved) FROM users')
    total_users, total_prompts, total_energy, total_co2 = cursor.fetchone()
    
    conn.close()
    
    stats = {
        'total_users': total_users or 0,
        'total_prompts_optimized': total_prompts or 0,
        'total_energy_saved_wh': round(total_energy or 0, 4),
        'total_co2_saved_g': round(total_co2 or 0, 4),
        'cache_stats': cache_stats
    }
    
    # Add user-specific stats if logged in
    if 'user_id' in session:
        user_stats = get_user_stats(session['user_id'])
        stats['user_stats'] = user_stats
    
    return jsonify(stats)

@app.route('/api/user/history', methods=['GET'])
@login_required
def user_history():
    """Get user's optimization history"""
    user_id = session['user_id']
    limit = request.args.get('limit', 50, type=int)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT original_prompt, optimized_prompt, energy_saved, co2_saved, 
               tokens_saved, timestamp
        FROM user_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            'original': row[0],
            'optimized': row[1],
            'energy_saved': round(row[2], 6),
            'co2_saved': round(row[3], 6),
            'tokens_saved': row[4],
            'timestamp': row[5]
        })
    
    conn.close()
    
    return jsonify({'history': history})

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500
    
@app.errorhandler(Exception)
def handle_all_errors(e):
    return jsonify({'error': str(e)}), 500
# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Green-Prompts-Optimizer: Energy Saver AI")
    print("=" * 70)
    print(f"Device: {optimizer.device}")
    print(f"Cache loaded: {len(optimizer.cache.memory_cache)} prompts")
    print("Starting Flask server...")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
