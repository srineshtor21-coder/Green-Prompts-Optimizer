const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Pool } = require('pg');
const WebSocket = require('ws');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middleware
app.use(cors());
app.use(express.json());

// Database connection
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'green_prompts',
  password: process.env.DB_PASSWORD || 'your_password',
  port: process.env.DB_PORT || 5432,
});

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-this';

// Initialize database tables
async function initializeDatabase() {
  const client = await pool.connect();
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        username VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS optimizations (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        original_prompt TEXT NOT NULL,
        optimized_prompt TEXT NOT NULL,
        tokens_saved INTEGER NOT NULL,
        energy_saved DECIMAL(10, 4) NOT NULL,
        co2_saved DECIMAL(10, 4) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS global_stats (
        id INTEGER PRIMARY KEY DEFAULT 1,
        total_prompts INTEGER DEFAULT 0,
        total_tokens_saved INTEGER DEFAULT 0,
        total_energy_saved DECIMAL(12, 4) DEFAULT 0,
        total_co2_saved DECIMAL(12, 4) DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT single_row CHECK (id = 1)
      );

      INSERT INTO global_stats (id) VALUES (1) ON CONFLICT DO NOTHING;
    `);
    console.log('Database initialized successfully');
  } finally {
    client.release();
  }
}

initializeDatabase();

// Authentication Middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
}

// ============ AUTH ROUTES ============

// Register
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password, username } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    // Check if user exists
    const userExists = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );

    if (userExists.rows.length > 0) {
      return res.status(400).json({ error: 'Email already registered' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const result = await pool.query(
      'INSERT INTO users (email, password, username) VALUES ($1, $2, $3) RETURNING id, email, username',
      [email, hashedPassword, username || email.split('@')[0]]
    );

    const user = result.rows[0];
    const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '30d' });

    res.status(201).json({
      token,
      user: { id: user.id, email: user.email, username: user.username }
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

// Login
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = result.rows[0];
    const validPassword = await bcrypt.compare(password, user.password);

    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '30d' });

    res.json({
      token,
      user: { id: user.id, email: user.email, username: user.username }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// ============ OPTIMIZATION ROUTES ============

// Optimize prompt
app.post('/api/optimize', authenticateToken, async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt required' });
    }

    // Call your AI optimization logic here
    const optimizedPrompt = await optimizePromptWithAI(prompt);
    
    // Calculate savings
    const originalTokens = estimateTokens(prompt);
    const optimizedTokens = estimateTokens(optimizedPrompt);
    const tokensSaved = Math.max(0, originalTokens - optimizedTokens);
    
    const energySaved = tokensSaved * 0.00015; // Wh per token
    const co2Saved = energySaved * 0.7; // grams CO2

    // Save optimization to database
    await pool.query(
      `INSERT INTO optimizations 
       (user_id, original_prompt, optimized_prompt, tokens_saved, energy_saved, co2_saved) 
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [req.user.id, prompt, optimizedPrompt, tokensSaved, energySaved, co2Saved]
    );

    // Update global stats
    await pool.query(
      `UPDATE global_stats SET 
       total_prompts = total_prompts + 1,
       total_tokens_saved = total_tokens_saved + $1,
       total_energy_saved = total_energy_saved + $2,
       total_co2_saved = total_co2_saved + $3,
       last_updated = CURRENT_TIMESTAMP
       WHERE id = 1`,
      [tokensSaved, energySaved, co2Saved]
    );

    // Broadcast updated stats to all connected WebSocket clients
    broadcastStats();

    res.json({
      original: prompt,
      optimized: optimizedPrompt,
      savings: {
        tokens: tokensSaved,
        energy: energySaved.toFixed(4),
        co2: co2Saved.toFixed(4)
      }
    });
  } catch (error) {
    console.error('Optimization error:', error);
    res.status(500).json({ error: 'Optimization failed' });
  }
});

// Get user's optimization history
app.get('/api/optimizations', authenticateToken, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, original_prompt, optimized_prompt, tokens_saved, 
              energy_saved, co2_saved, created_at 
       FROM optimizations 
       WHERE user_id = $1 
       ORDER BY created_at DESC 
       LIMIT 50`,
      [req.user.id]
    );

    res.json(result.rows);
  } catch (error) {
    console.error('Fetch optimizations error:', error);
    res.status(500).json({ error: 'Failed to fetch optimizations' });
  }
});

// Get user stats
app.get('/api/user/stats', authenticateToken, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT 
        COUNT(*) as total_optimizations,
        COALESCE(SUM(tokens_saved), 0) as total_tokens_saved,
        COALESCE(SUM(energy_saved), 0) as total_energy_saved,
        COALESCE(SUM(co2_saved), 0) as total_co2_saved
       FROM optimizations 
       WHERE user_id = $1`,
      [req.user.id]
    );

    res.json(result.rows[0]);
  } catch (error) {
    console.error('User stats error:', error);
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});

// ============ GLOBAL STATS ROUTES ============

// Get global stats (public)
app.get('/api/stats/global', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM global_stats WHERE id = 1');
    
    if (result.rows.length === 0) {
      return res.json({
        total_prompts: 0,
        total_tokens_saved: 0,
        total_energy_saved: 0,
        total_co2_saved: 0
      });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Global stats error:', error);
    res.status(500).json({ error: 'Failed to fetch global stats' });
  }
});

// ============ WEBSOCKET FOR REAL-TIME STATS ============

async function broadcastStats() {
  try {
    const result = await pool.query('SELECT * FROM global_stats WHERE id = 1');
    const stats = result.rows[0];

    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({
          type: 'stats_update',
          data: stats
        }));
      }
    });
  } catch (error) {
    console.error('Broadcast error:', error);
  }
}

wss.on('connection', (ws) => {
  console.log('New WebSocket connection');
  
  // Send current stats immediately
  pool.query('SELECT * FROM global_stats WHERE id = 1')
    .then(result => {
      ws.send(JSON.stringify({
        type: 'stats_update',
        data: result.rows[0]
      }));
    });

  ws.on('close', () => {
    console.log('WebSocket connection closed');
  });
});

// ============ HELPER FUNCTIONS ============

// Simple token estimation (roughly 4 chars = 1 token)
function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

// Placeholder for AI optimization - integrate your actual AI model here
async function optimizePromptWithAI(prompt) {
  // TODO: Replace with actual AI call to your trained model
  // For now, returning a simplified version
  
  // Example: Remove extra whitespace, redundant words, etc.
  let optimized = prompt
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/please /gi, '')
    .replace(/kindly /gi, '')
    .replace(/could you /gi, '');

  // If you have a model endpoint:
  // const response = await fetch('YOUR_MODEL_ENDPOINT', {
  //   method: 'POST',
  //   body: JSON.stringify({ prompt })
  // });
  // optimized = await response.json();

  return optimized;
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket server ready for real-time stats`);
});
