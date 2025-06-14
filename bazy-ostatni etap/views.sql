-- Widok 1: Szczegóły zamówień z nazwą klienta i produktem
CREATE OR REPLACE VIEW v_order_details AS
SELECT 
    z.id_zamowienia,
    k.imie || ' ' || k.nazwisko AS klient,
    p.nazwa AS produkt,
    s.nazwa AS status,
    z.data_zlozenia,
    z.data_realizacji
FROM zamowienie z
JOIN klient k ON z.id_klienta = k.id_klienta
JOIN produkt p ON z.id_produktu = p.id_produktu
JOIN status s ON z.id_statusu = s.id_statusu;

-- Widok 2: Produkty z kategoriami i producentami
CREATE OR REPLACE VIEW v_product_info AS
SELECT 
    p.id_produktu,
    p.nazwa,
    p.cena,
    k.nazwa AS kategoria,
    pr.nazwa AS producent
FROM produkt p
JOIN kategoria k ON p.id_kategorii = k.id_kategorii
JOIN producent pr ON p.id_producenta = pr.id_producenta;

-- Widok 3: Liczba zamówień dla każdego klienta
CREATE OR REPLACE VIEW v_klient_zamowienia AS
SELECT 
    k.id_klienta,
    k.imie,
    k.nazwisko,
    COUNT(z.id_zamowienia) AS liczba_zamowien
FROM klient k
LEFT JOIN zamowienie z ON z.id_klienta = k.id_klienta
GROUP BY k.id_klienta, k.imie, k.nazwisko;

-- Widok 4: Historia zamówień (zrealizowane)
CREATE OR REPLACE VIEW v_historia_zamowien AS
SELECT 
    z.id_zamowienia,
    k.imie || ' ' || k.nazwisko AS klient,
    p.nazwa AS produkt,
    z.data_realizacji
FROM zamowienie z
JOIN klient k ON z.id_klienta = k.id_klienta
JOIN produkt p ON z.id_produktu = p.id_produktu
WHERE z.data_realizacji IS NOT NULL;

-- Widok 5: Średnia cena produktów w każdej kategorii
CREATE OR REPLACE VIEW v_avg_price_per_category AS
SELECT 
    k.nazwa AS kategoria,
    ROUND(AVG(p.cena), 2) AS srednia_cena
FROM produkt p
JOIN kategoria k ON p.id_kategorii = k.id_kategorii
GROUP BY k.nazwa;
