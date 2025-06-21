# System Rekomendacji Tras - Zestaw Testów

Kompletny system testów dla aplikacji rekomendacji tras turystycznych z walidacją danych, obsługą plików CSV i filtrowaniem tras według preferencji użytkownika.

## Struktura Projektu

```
testy_stepik/
├── models.py              # Modele danych (Route, UserPreference)
├── data_handling.py       # Obsługa danych CSV (FileRouteRepository, DataParsingError)
├── logic.py              # Logika rekomendacji (RouteRecommender)
├── demo.py               # Skrypt demonstracyjny
├── run_tests.py          # Skrypt uruchamiający testy
├── tests/                # Pakiet testów
│   ├── __init__.py
│   ├── test_models.py    # Testy modeli
│   ├── test_data_handling.py  # Testy obsługi danych
│   └── test_logic.py     # Testy integracyjne
└── README.md
```

## Opis Komponentów

### 1. Modele (`models.py`)

- **Route**: Klasa reprezentująca trasę turystyczną
  - `name` (str): Nazwa trasy (niepusta)
  - `distance` (float): Dystans w km (≥ 0)
  - `difficulty` (int): Trudność 1-5
  - `terrain` (str): Typ terenu (niepusty)

- **UserPreference**: Klasa preferencji użytkownika
  - `max_difficulty` (int, opcjonalne): Maksymalna trudność (1-5)
  - `terrain` (str, opcjonalne): Preferowany teren
  - `max_distance` (float, opcjonalne): Maksymalny dystans (≥ 0)

### 2. Obsługa Danych (`data_handling.py`)

- **DataParsingError**: Wyjątek dla błędów parsowania danych
- **FileRouteRepository**: Klasa do wczytywania tras z pliku CSV
  - `get_all()`: Zwraca listę wszystkich tras z pliku

### 3. Logika Rekomendacji (`logic.py`)

- **RouteRecommender**: Klasa filtrująca trasy według preferencji
  - `recommend(user_preference)`: Zwraca listę pasujących tras

## Uruchamianie Testów

### Wszystkie testy
```bash
python run_tests.py
```

### Konkretny moduł testowy
```bash
python run_tests.py test_models
python run_tests.py test_data_handling
python run_tests.py test_logic
```

### Standardowe uruchamianie unittest
```bash
python -m unittest discover tests
```

## Opis Testów

### 1. Testy Modeli (`tests/test_models.py`)

**TestRoute** - 17 testów:
- ✅ Poprawne tworzenie obiektów Route
- ✅ Walidacja nazwy (pusta, białe znaki, nieprawidłowy typ)
- ✅ Walidacja dystansu (ujemny, nieprawidłowy typ, zero)
- ✅ Walidacja trudności (poza zakresem 1-5, float)
- ✅ Walidacja terenu (pusty, białe znaki, nieprawidłowy typ)
- ✅ Porównywanie obiektów i reprezentacja tekstowa

**TestUserPreference** - 16 testów:
- ✅ Tworzenie z domyślnymi i niestandardowymi wartościami
- ✅ Walidacja max_difficulty (poza zakresem, float)
- ✅ Walidacja terrain (pusty, białe znaki, nieprawidłowy typ)
- ✅ Walidacja max_distance (ujemny, nieprawidłowy typ, zero)
- ✅ Reprezentacja tekstowa

### 2. Testy Obsługi Danych (`tests/test_data_handling.py`)

**TestFileRouteRepository** - 14 testów z zarządzaniem tymczasowymi plikami:
- ✅ **Scenariusz idealny**: Poprawne wczytywanie danych CSV
- ✅ **Błędy parsowania**: Nieprawidłowa trudność, dystans, brakujące kolumny
- ✅ **Pusty plik**: CSV tylko z nagłówkami
- ✅ **Nieistniejący plik**: Obsługa FileNotFoundError
- ✅ **Walidacja danych**: Ujemny dystans, nieprawidłowy format
- ✅ **Obsługa Unicode**: Polskie znaki w danych
- ✅ **Błędny format**: Nieprawidłowa struktura CSV

### 3. Testy Integracyjne (`tests/test_logic.py`)

**TestRouteRecommender** - 14 testów z tymczasowymi plikami CSV:
- ✅ **Filtrowanie według trudności**: Tylko trasy ≤ max_difficulty
- ✅ **Filtrowanie według terenu**: Exact match dla typu terenu
- ✅ **Filtrowanie według dystansu**: Tylko trasy ≤ max_distance
- ✅ **Kombinacja kryteriów**: Wszystkie filtry jednocześnie
- ✅ **Brak pasujących tras**: Restrykcyjne kryteria
- ✅ **Brak ograniczeń**: Zwracanie wszystkich tras
- ✅ **Wartości graniczne**: Testowanie skrajnych przypadków
- ✅ **Puste repository**: Obsługa braku danych

## Demonstracja

Uruchom skrypt demonstracyjny, aby zobaczyć system w działaniu:

```bash
python demo.py
```

Demonstracja obejmuje:
- Tworzenie i walidację modeli
- Wczytywanie danych z pliku CSV
- Różne scenariusze rekomendacji tras
- Obsługę błędów i przypadków granicznych

## Format Pliku CSV

```csv
name,distance,difficulty,terrain
Górski szlak,15.5,4,mountain
Spacer po parku,3.0,1,park
Leśna ścieżka,8.2,2,forest
```

## Kluczowe Cechy Testów

1. **Zarządzanie zasobami**: Automatyczne tworzenie i czyszczenie tymczasowych plików
2. **Kompleksowe pokrycie**: Scenariusze pozytywne, negatywne i graniczne
3. **Walidacja danych**: Szczegółowe testowanie wszystkich ograniczeń
4. **Integracja**: Testowanie współpracy między komponentami
5. **Obsługa błędów**: Sprawdzanie poprawnego rzucania wyjątków
6. **Unicode**: Obsługa polskich znaków w danych

## Instalacja i Uruchomienie

### Wymagania
- **Python 3.6+** 
- Żadnych dodatkowych bibliotek - tylko standardowe moduły

### Szybkie Uruchomienie

1. **Pobierz projekt i przejdź do katalogu**
   ```bash
   cd testy_stepik
   ```

2. **Uruchom testy (weryfikacja, że działa)**
   ```bash
   python run_tests.py
   ```

3. **Zobacz demonstrację**
   ```bash
   python demo.py
   ```

### Środowisko Wirtualne (zalecane)

```bash
# Utwórz środowisko wirtualne
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Sprawdź że działa
python run_tests.py

# Uruchom demonstrację
python demo.py
```

### Szybki Test
```bash
# Sprawdź czy wszystko działa:
python quick_test.py
```

### Przeniesienie na Inny Komputer

1. **Skopiuj cały katalog** `testy_stepik` 
2. **Na nowym komputerze:**
   ```bash
   cd testy_stepik
   
   # Utwórz środowisko wirtualne
   python -m venv venv
   venv\Scripts\activate  # Windows
   # lub: source venv/bin/activate  # Linux/macOS
   
   # Sprawdź że działa
   python quick_test.py
   ```

### Dostępne Skrypty

- `quick_test.py` - Szybka weryfikacja funkcjonalności (5 sekund)
- `run_tests.py` - Pełny zestaw 58 testów jednostkowych  
- `demo.py` - Interaktywna demonstracja systemu

## Wykorzystane Technologie

- **Python 3.6+** - Język programowania
- **unittest** - Framework testowy
- **tempfile** - Zarządzanie plikami tymczasowymi
- **csv** - Obsługa plików CSV
- **Standardowa biblioteka** - Bez zewnętrznych zależności 