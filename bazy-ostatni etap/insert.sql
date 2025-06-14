-- Przykładowe dane do tabel

-- Tabela: users
INSERT INTO users (id, email, password_hash, username, fast_name, last_name, date_of_birth, phone_number, is_verified, account_locked, email_verified, last_login_at)
VALUES 
  ('00000000-0000-0000-0000-000000000001', 'john.doe@example.com', 'hashed_pass_123', 'johndoe', 'John', 'Doe', '1990-01-01', '+48123456789', true, false, true, NOW());

-- Tabela: user_profiles
INSERT INTO user_profiles (id, user_id, preferred_language, time_zone, avatar_url)
VALUES 
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'en', 'UTC+1', 'http://avatar.example.com/john.png');

-- Tabela: wallets
INSERT INTO wallets (id, user_id, currency, balance, bonus_balance, locked_amount)
VALUES 
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'EUR', 1000.00, 100.00, 0.00);

-- Tabela: games
INSERT INTO games (id, name, description, rtp, volatility, min_bet, max_bet, popularity)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'Super Slots', 'Popular slot machine game.', 96.5, 'high', 0.1, 100, 90);

-- Tabela: transactions
INSERT INTO transactions (id, wallet_id, user_id, amount, currency, description)
VALUES
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 200.00, 'EUR', 'Initial deposit');

-- Tabela: promotions
INSERT INTO promotions (id, code, description, value, value_type, max_bonus, wagering_requirement, min_deposit)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'WELCOME100', '100% bonus up to 200 EUR', 100, 'percentage', 200, 30, 10);

-- Tabela: user_bonuses
INSERT INTO user_bonuses (user_id, promotion_id, value, remaining_wagering, is_active)
VALUES
  (1, 1, 200, 6000, true);

-- Tabela: jackpots
INSERT INTO jackpots (id, name, type, seed_amount, current_amount, is_active)
VALUES
  (1, 'Mega Jackpot', 'progressive', 10000, 10500, true);

-- Tabela: game_jackpots
INSERT INTO game_jackpots (game_id, jackpot_id, contribution_rate)
VALUES
  ('00000000-0000-0000-0000-000000000001', 1, 0.05);

-- Tabela: bets
INSERT INTO bets (id, game_id, user_id, amount, currency, potential_win)
VALUES
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 10.00, 'EUR', 100.00);

-- Tabela: game_sessions
INSERT INTO game_sessions (id, game_id, user_id, initial_balance, final_balance, total_bets, total_wins)
VALUES
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 1000, 1090, 10, 100);

-- Tabela: game_categories
INSERT INTO game_categories (id, name, description)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'Slots', 'Slot machine games.');

-- Tabela: game_categorization
INSERT INTO game_categorization (game_id, category_id)
VALUES
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001');
