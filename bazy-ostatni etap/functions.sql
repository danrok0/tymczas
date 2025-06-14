-- Funkcja 1: Zwraca pełne dane klienta po ID
CREATE OR REPLACE FUNCTION get_client_details(p_id INT)
RETURNS TABLE(imie TEXT, nazwisko TEXT, email TEXT, telefon TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT k.imie, k.nazwisko, k.email, k.telefon
    FROM klient k
    WHERE k.id_klienta = p_id;
END;
$$ LANGUAGE plpgsql;

-- Funkcja 2: Zwraca liczbę zamówień danego klienta
CREATE OR REPLACE FUNCTION count_client_orders(p_id INT)
RETURNS INT AS $$
DECLARE
    liczba INT;
BEGIN
    SELECT COUNT(*) INTO liczba FROM zamowienie WHERE id_klienta = p_id;
    RETURN liczba;
END;
$$ LANGUAGE plpgsql;

-- Funkcja 3: Dodaje nowy produkt (jeśli nie istnieje taki sam nazwa + producent)
CREATE OR REPLACE FUNCTION add_product(p_nazwa TEXT, p_cena NUMERIC, p_id_kategorii INT, p_id_producenta INT)
RETURNS TEXT AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM produkt
        WHERE nazwa = p_nazwa AND id_producenta = p_id_producenta
    ) THEN
        RETURN 'Produkt już istnieje';
    ELSE
        INSERT INTO produkt (nazwa, cena, id_kategorii, id_producenta)
        VALUES (p_nazwa, p_cena, p_id_kategorii, p_id_producenta);
        RETURN 'Produkt dodany';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Funkcja 4: Zmienia status zamówienia
CREATE OR REPLACE FUNCTION update_order_status(p_id_zamowienia INT, p_id_statusu INT)
RETURNS VOID AS $$
BEGIN
    UPDATE zamowienie
    SET id_statusu = p_id_statusu
    WHERE id_zamowienia = p_id_zamowienia;
END;
$$ LANGUAGE plpgsql;

-- Funkcja 5: Zwraca średnią cenę wszystkich produktów danej kategorii
CREATE OR REPLACE FUNCTION get_avg_price_by_category(p_id_kategorii INT)
RETURNS NUMERIC AS $$
DECLARE
    srednia NUMERIC;
BEGIN
    SELECT AVG(cena) INTO srednia
    FROM produkt
    WHERE id_kategorii = p_id_kategorii;
    RETURN COALESCE(srednia, 0);
END;
$$ LANGUAGE plpgsql;
