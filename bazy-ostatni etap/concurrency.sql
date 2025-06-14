-- Przykład 1: Zakup losu (roulette spin), wykorzystujemy transakcję i SELECT FOR UPDATE
BEGIN;

-- rezerwujemy środki z portfela
SELECT balance, locked_amount
  INTO v_balance, v_locked
FROM wallets
WHERE id = '00000000-0000-0000-0000-000000000001'
FOR UPDATE;

IF v_balance - 10 < 0 THEN
    ROLLBACK;
    RAISE 'Brak środków';
END IF;

UPDATE wallets
SET balance = v_balance - 10,
    locked_amount = v_locked + 10
WHERE id = '00000000-0000-0000-0000-000000000001';

-- wstawiamy zakład
INSERT INTO bets (id, user_id, game_id, amount, currency, created_at)
VALUES (
    gen_random_uuid(),
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    10, 'EUR', NOW()
);

COMMIT;


-- Przykład 2: Transakcja o wysokim poziomie izolacji SERIALIZABLE
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

BEGIN;
-- odczyt salda
SELECT balance, bonus_balance
  INTO v_balance, v_bonus
FROM wallets
WHERE id = '00000000-0000-0000-0000-000000000001';

-- obliczenia na podstawie salda
-- ...

-- aktualizacja
UPDATE wallets
SET bonus_balance = v_bonus + 5
WHERE id = '00000000-0000-0000-0000-000000000001';

COMMIT;


-- Przykład 3: Unikanie "lost update" przez row‑level locking
BEGIN;

SELECT * FROM promotions
WHERE id = '00000000-0000-0000-0000-000000000001'
FOR UPDATE;

UPDATE promotions
SET value = value - 1
WHERE id = '00000000-0000-0000-000-000000000001';

COMMIT;
