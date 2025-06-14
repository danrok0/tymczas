-- Wyzwalacz 1: Automatyczne ustawianie daty złożenia zamówienia na aktualny czas
CREATE OR REPLACE FUNCTION set_order_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_zlozenia := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_order_date
BEFORE INSERT ON zamowienie
FOR EACH ROW
EXECUTE FUNCTION set_order_date();


-- Wyzwalacz 2: Zakaz usuwania producenta, który ma przypisane produkty
CREATE OR REPLACE FUNCTION prevent_delete_producer_with_products()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM produkt WHERE id_producenta = OLD.id_producenta
    ) THEN
        RAISE EXCEPTION 'Nie można usunąć producenta, który ma przypisane produkty!';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_delete_producer
BEFORE DELETE ON producent
FOR EACH ROW
EXECUTE FUNCTION prevent_delete_producer_with_products();


-- Wyzwalacz 3: Logowanie zmian statusu zamówienia
-- Zakładamy, że istnieje tabela "log_status_zamowienia(id SERIAL, id_zamowienia INT, stary_status INT, nowy_status INT, zmieniono TIMESTAMP)"
CREATE TABLE IF NOT EXISTS log_status_zamowienia (
    id SERIAL PRIMARY KEY,
    id_zamowienia INT,
    stary_status INT,
    nowy_status INT,
    zmieniono TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION log_order_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.id_statusu IS DISTINCT FROM NEW.id_statusu THEN
        INSERT INTO log_status_zamowienia (id_zamowienia, stary_status, nowy_status)
        VALUES (OLD.id_zamowienia, OLD.id_statusu, NEW.id_statusu);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_order_status
AFTER UPDATE ON zamowienie
FOR EACH ROW
WHEN (OLD.id_statusu IS DISTINCT FROM NEW.id_statusu)
EXECUTE FUNCTION log_order_status_change();


-- Wyzwalacz 4: Ustawianie domyślnego statusu zamówienia przy tworzeniu (np. "Nowe" = id_statusu = 1)
CREATE OR REPLACE FUNCTION set_default_order_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id_statusu IS NULL THEN
        NEW.id_statusu := 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_default_status
BEFORE INSERT ON zamowienie
FOR EACH ROW
EXECUTE FUNCTION set_default_order_status();
