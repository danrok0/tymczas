# System Zarządzania Biblioteką Domową

Aplikacja konsolowa do zarządzania domową biblioteką, umożliwiająca katalogowanie książek i autorów.

## Funkcjonalności

### Zarządzanie autorami
- Dodawanie nowych autorów
- Wyświetlanie listy autorów
- Wyszukiwanie autorów
- Edycja danych autorów
- Usuwanie autorów (tylko jeśli nie mają przypisanych książek)

### Zarządzanie książkami
- Dodawanie nowych książek
- Wyświetlanie wszystkich książek
- Wyszukiwanie książek po tytule, autorze lub roku wydania
- Edycja informacji o książkach
- Usuwanie książek
- Wyświetlanie książek konkretnego autora

### Raporty i statystyki
- Liczba książek w bibliotece
- Liczba autorów
- Najstarsze i najnowsze książki
- Autorzy z największą liczbą książek

## Wymagania

- Python 3.7 lub nowszy
- SQLAlchemy 2.0.27

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```

## Uruchomienie

Aby uruchomić aplikację, wykonaj:
```
python main.py
```

## Struktura projektu

```
biblioteka/
├── src/
│   ├── database_manager.py    # Zarządzanie połączeniem i operacjami na bazie
│   ├── models.py              # Definicje klas Author i Book
│   ├── repositories.py        # Repozytoria dla autorów i książek
│   └── ui.py                  # Interfejs użytkownika (menu konsolowe)
├── data/
│   └── library.db            # Plik bazy danych SQLite
├── requirements.txt          # Zależności projektu
└── main.py                   # Główny plik aplikacji
```

## Przykładowe dane

Po pierwszym uruchomieniu aplikacja automatycznie dodaje przykładowe dane:
- Autorzy: Adam Mickiewicz, Henryk Sienkiewicz, Czesław Miłosz
- Książki: "Pan Tadeusz", "Quo Vadis", "Dolina Issy" 