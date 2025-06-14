-- === FILE: create.sql ===
-- Create all tables based on the ERD

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    first_name TEXT,
    last_name TEXT,
    date_of_birth DATE,
    phone_number TEXT,
    avatar_url TEXT,
    time_zone TEXT,
    status TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    is_test_account BOOLEAN DEFAULT FALSE,
    account_level TEXT,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    address TEXT,
    city TEXT,
    country TEXT,
    postal_code VARCHAR(10),
    user_profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE
);

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    preferred_language TEXT,
    time_zone TEXT,
    avatar_url TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sessions (
    token TEXT PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP
);

CREATE TABLE user_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_type TEXT,
    document_number TEXT,
    document_image_front TEXT,
    document_image_back TEXT,
    selfie_image TEXT,
    review_notes TEXT,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE email_verifications (
    token TEXT PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_used BOOLEAN DEFAULT FALSE,
    expire_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_activity_log (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address TEXT,
    device_info TEXT,
    details VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE responsible_gaming_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    deposit_limit INTEGER,
    bet_limit INTEGER,
    loss_limit INTEGER,
    session_time_limit INTEGER,
    cooldown_period INTEGER,
    self_exclusion INTEGER,
    next_review_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE password_resets (
    token TEXT PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    expire_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    currency TEXT,
    balance NUMERIC,
    bonus_balance NUMERIC,
    locked_amount NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT,
    provider TEXT,
    account_number TEXT,
    expiry_date TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID REFERENCES wallets(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC,
    currency TEXT,
    description TEXT,
    reference_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE promotions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT,
    description TEXT,
    value NUMERIC,
    value_percentage NUMERIC,
    max_bonus NUMERIC,
    wagering_requirement NUMERIC,
    min_deposit NUMERIC,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE user_bonuses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    promotion_id UUID REFERENCES promotions(id) ON DELETE SET NULL,
    remaining_wagering NUMERIC,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    description TEXT,
    thumbnail_url TEXT,
    rtp NUMERIC,
    volatility TEXT,
    min_bet NUMERIC,
    max_bet NUMERIC,
    popularity NUMERIC,
    provider_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE type_game (
    id INTEGER PRIMARY KEY,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    name VARCHAR
);

CREATE TABLE provider (
    id INTEGER PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE bets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    session_id UUID,
    amount NUMERIC,
    multiplier NUMERIC,
    potential_win NUMERIC,
    outcome TEXT,
    win_amount NUMERIC,
    game_data TEXT,
    transaction_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    settled_at TIMESTAMP
);

CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    initial_balance NUMERIC,
    final_balance NUMERIC,
    total_bets NUMERIC,
    total_wins NUMERIC,
    ip_address TEXT,
    device_info TEXT
);

CREATE TABLE game_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    description TEXT,
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE game_categorization (
    id SERIAL PRIMARY KEY,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    category_id UUID REFERENCES game_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE jackpots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seed_amount NUMERIC,
    increment_rate NUMERIC,
    name TEXT,
    type TEXT,
    current_amount NUMERIC,
    last_win_amount NUMERIC,
    last_win_time TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_winner_id INTEGER
);

CREATE TABLE game_jackpots (
    id SERIAL PRIMARY KEY,
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    jackpot_id UUID REFERENCES jackpots(id) ON DELETE CASCADE,
    contribution_rate NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE allowed_games (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    informations VARCHAR
);

CREATE TABLE help_game (
    id SERIAL PRIMARY KEY,
    promotion_id UUID REFERENCES promotions(id) ON DELETE CASCADE,
    allowed_game_id INTEGER REFERENCES allowed_games(id) ON DELETE CASCADE
);

CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR,
    informations VARCHAR
);

-- Dalsze pliki: insert.sql, views.sql, functions.sql, triggers.sql, concurrency.sql – będą dodane w kolejnych częściach.
