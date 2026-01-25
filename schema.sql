-- Green Prompts Optimizer Database Schema

-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  username VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP,
  is_active BOOLEAN DEFAULT true
);

-- Optimizations table (stores each prompt optimization)
CREATE TABLE optimizations (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  original_prompt TEXT NOT NULL,
  optimized_prompt TEXT NOT NULL,
  tokens_saved INTEGER NOT NULL,
  energy_saved DECIMAL(10, 4) NOT NULL,
  co2_saved DECIMAL(10, 4) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  model_used VARCHAR(50) DEFAULT 'green-prompt-v1'
);

-- Global statistics table (single row with aggregate data)
CREATE TABLE global_stats (
  id INTEGER PRIMARY KEY DEFAULT 1,
  total_prompts INTEGER DEFAULT 0,
  total_tokens_saved INTEGER DEFAULT 0,
  total_energy_saved DECIMAL(12, 4) DEFAULT 0,
  total_co2_saved DECIMAL(12, 4) DEFAULT 0,
  total_users INTEGER DEFAULT 0,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT single_row CHECK (id = 1)
);

-- Insert initial stats row
INSERT INTO global_stats (id) VALUES (1) ON CONFLICT DO NOTHING;

-- Indexes for performance
CREATE INDEX idx_optimizations_user_id ON optimizations(user_id);
CREATE INDEX idx_optimizations_created_at ON optimizations(created_at DESC);
CREATE INDEX idx_users_email ON users(email);

-- Function to update global stats automatically
CREATE OR REPLACE FUNCTION update_global_stats()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE global_stats SET
    total_prompts = total_prompts + 1,
    total_tokens_saved = total_tokens_saved + NEW.tokens_saved,
    total_energy_saved = total_energy_saved + NEW.energy_saved,
    total_co2_saved = total_co2_saved + NEW.co2_saved,
    last_updated = CURRENT_TIMESTAMP
  WHERE id = 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update stats
CREATE TRIGGER trigger_update_stats
AFTER INSERT ON optimizations
FOR EACH ROW
EXECUTE FUNCTION update_global_stats();

-- Function to update total users count
CREATE OR REPLACE FUNCTION update_user_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE global_stats SET
    total_users = (SELECT COUNT(*) FROM users WHERE is_active = true),
    last_updated = CURRENT_TIMESTAMP
  WHERE id = 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update user count
CREATE TRIGGER trigger_update_user_count
AFTER INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_user_count();
