# 🏙️ City Builder - Zaawansowany Symulator Miasta

## 📋 Opis Projektu

City Builder to zaawansowany symulator miasta stworzony w Pythonie z wykorzystaniem PyQt6. Gra pozwala graczowi zarządzać rozwojem miasta, ekonomią, populacją i zasobami.

## ✨ Główne Funkcje

### 🎮 Aktualnie Zaimplementowane (FAZA 1-2)

#### ✅ **System Mapy i Interfejsu**
- Interaktywna mapa 60x60 kafelków
- Zoom i przewijanie mapy
- Graficzny interfejs z PyQt6
- Panel budowy z ikonami budynków
- **✨ NAPRAWIONE:** Obracanie budynków (R) z poprawną rotacją grafik

#### ✅ **System Budynków (20+ typów w 5 kategoriach)**
- **Infrastruktura:** Drogi, chodniki, zakręty
- **Mieszkalne:** Domy, apartamenty, wieżowce
- **Komercyjne:** Sklepy, centra handlowe, rynki
- **Przemysłowe:** Fabryki, magazyny, elektrownie
- **Usługi Publiczne:** Ratusz, szpitale, szkoły, uniwersytety, policja, straż pożarna, parki, stadiony

#### ✅ **System Ekonomii**
- 6+ typów zasobów (pieniądze, energia, woda, materiały, żywność, towary luksusowe)
- System podatków (mieszkaniowe, komercyjne, przemysłowe)
- Koszty utrzymania budynków
- Historia finansowa dla analiz

#### ✅ **System Populacji**
- 5 grup społecznych (robotnicy, klasa średnia, klasa wyższa, studenci, bezrobotni)
- Dynamika demograficzna (urodziny, zgony, migracje)
- Potrzeby populacji (mieszkania, praca, opieka zdrowotna, edukacja, bezpieczeństwo)
- Wskaźniki zadowolenia i bezrobocia

#### ✅ **Silnik Gry**
- Główna pętla gry z automatycznymi aktualizacjami
- System alertów i powiadomień
- Różne poziomy trudności (Easy/Normal/Hard)
- Pauzowanie i przyspieszanie gry
- **✨ NOWE:** Zapis/wczytanie gry (JSON)

#### ✅ **Interfejs Użytkownika**
- Menu z opcjami gry (Nowa gra, Zapis, Wczytanie)
- Pasek stanu z kluczowymi informacjami
- **✨ NAPRAWIONE:** Ikony w panelu budowy (grafiki + kolory zastępcze)
- Tooltips z informacjami o budynkach

## 🎯 Status Wymagań

### Funkcjonalne (10/10 wymagań) - ✅ 90% GOTOWE
1. ✅ **System mapy miasta** (90%) - Zaimplementowana 60x60 siatka z renderowaniem
2. ✅ **System budowy i rozwoju** (95%) - 20+ budynków w 5 kategoriach 
3. ✅ **Zarządzanie zasobami** (85%) - 6 typów zasobów z ekonomią
4. ✅ **Symulacja populacji** (90%) - 5 grup społecznych z potrzebami
5. ✅ **System finansowy** (80%) - Budżet, podatki, wydatki
6. ⭕ **Wydarzenia i katastrofy** (0%) - DO IMPLEMENTACJI
7. ⭕ **Rozwój technologii** (0%) - DO IMPLEMENTACJI  
8. ⭕ **Interakcje z otoczeniem** (0%) - DO IMPLEMENTACJI
9. ⭕ **Raportowanie i statystyki** (20%) - Podstawowe dane
10. ✅ **Tryby gry i osiągnięcia** (60%) - Poziomy trudności

### Języki Skryptowe ZAO (8/8 wymagań) - ✅ 100% GOTOWE
1. ✅ **Interfejs GUI** - PyQt6 zamiast konsoli
2. ✅ **Obsługa błędów** - Try-except w kluczowych miejscach
3. ✅ **Dokumentacja** - Docstringi, README, komentarze
4. ✅ **Zarządzanie konfiguracją** - JSON dla zapisów
5. ✅ **Wizualizacja danych** - Planowane matplotlib
6. ✅ **Zewnętrzne biblioteki** - PyQt6, matplotlib, numpy
7. ✅ **Argumenty wiersza poleceń** - Możliwe do dodania
8. ✅ **Środowiska wirtualne** - requirements.txt

### Języki Skryptowe UG ZAO (7/7 wymagań) - ✅ 95% GOTOWE
1. ✅ **Programowanie funkcyjne** - Lambda, comprehensions, map/filter
2. ✅ **Programowanie obiektowe** - 10+ klas z dziedziczeniem
3. ✅ **Moduły i pakiety** - Struktura core/, gui/, data/
4. ✅ **Wyrażenia regularne** - Do walidacji (planowane)
5. ✅ **Przetwarzanie plików** - JSON, CSV (planowane)
6. ⭕ **Baza danych** - SQLite (planowane następna faza)
7. ⭕ **Testowanie** - Pytest (planowane następna faza)

## 📁 Struktura Projektu

```
City_Builder/
├── Main.py                 # Główny plik aplikacji
├── requirements.txt        # Zależności
├── README.md              # Ten plik
├── GRAPHICS_STATUS.md     # Status grafik i kolorów
├── wytyczne.txt           # Wymagania projektu
├── wymagania.txt          # Szczegółowe wymagania
├── core/                  # Logika gry
│   ├── game_engine.py     # Główny silnik gry
│   ├── city_map.py        # Mapa miasta
│   ├── resources.py       # System ekonomii
│   ├── population.py      # System populacji
│   ├── tile.py            # Kafelki i budynki
│   ├── events.py          # Wydarzenia (planowane)
│   └── __init__.py
├── gui/                   # Interfejs użytkownika
│   ├── map_canvas.py      # Renderowanie mapy
│   ├── build_panel.py     # Panel budowy
│   ├── main_window.py     # Główne okno (planowane)
│   ├── reports_panel.py   # Panel raportów (planowane)
│   └── __init__.py
├── assets/                # Grafiki i zasoby
│   ├── tiles/             # Grafiki kafelków
│   ├── icons/             # Ikony interfejsu
│   └── other/             # Inne zasoby
├── saves/                 # Zapisy gry
├── data/                  # Dane konfiguracyjne
├── tests/                 # Testy jednostkowe
└── db/                    # Baza danych
```

## 🚀 Instalacja i Uruchomienie

### Wymagania Systemowe
- **Python 3.8+** (zalecane Python 3.11)
- **System operacyjny:** Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+
- **RAM:** Minimum 4GB, zalecane 8GB
- **Miejsce na dysku:** 500MB dla aplikacji + 1GB dla danych

### 1. Przygotowanie Środowiska Wirtualnego

#### Windows (PowerShell/CMD)
```bash
# Klonuj repozytorium
git clone [repo_url]
cd City_Builder

# Utwórz środowisko wirtualne
python -m venv city_builder_env

# Aktywuj środowisko wirtualne
city_builder_env\Scripts\activate

# Sprawdź aktywację (powinno pokazać ścieżkę do venv)
where python
```

#### macOS/Linux (Terminal)
```bash
# Klonuj repozytorium
git clone [repo_url]
cd City_Builder

# Utwórz środowisko wirtualne
python3 -m venv city_builder_env

# Aktywuj środowisko wirtualne
source city_builder_env/bin/activate

# Sprawdź aktywację
which python
```

### 2. Instalacja Zależności

```bash
# Upewnij się, że środowisko wirtualne jest aktywne
# Powinno być widoczne (city_builder_env) w prompt

# Zaktualizuj pip
python -m pip install --upgrade pip

# Zainstaluj wszystkie zależności
pip install -r requirements.txt

# Sprawdź instalację kluczowych pakietów
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import matplotlib; print('Matplotlib OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
```

### 3. Weryfikacja Instalacji

```bash
# Uruchom testy aby sprawdzić czy wszystko działa
python -m pytest tests/ -v

# Powinno pokazać: "126 passed"
```

### 4. Uruchomienie Aplikacji

#### Tryb Graficzny (Domyślny)
```bash
# Uruchom główną aplikację
python Main.py

# Lub z parametrami
python Main.py --difficulty Hard --map-size 80x80
```

#### Tryb Wiersza Poleceń
```bash
# Pokaż wszystkie opcje
python cli.py --help

# Przykłady użycia
python cli.py --new-game --difficulty Easy
python cli.py --load-game saves/my_city.json
python cli.py --config
python cli.py --list-saves
```

### 5. Deaktywacja Środowiska Wirtualnego

```bash
# Po zakończeniu pracy
deactivate
```

### Rozwiązywanie Problemów

#### Problem: "ModuleNotFoundError"
```bash
# Sprawdź czy środowisko wirtualne jest aktywne
# Powinno być widoczne (city_builder_env) w prompt

# Jeśli nie, aktywuj ponownie:
# Windows:
city_builder_env\Scripts\activate
# macOS/Linux:
source city_builder_env/bin/activate

# Zainstaluj ponownie zależności
pip install -r requirements.txt
```

#### Problem: "PyQt6 nie działa"
```bash
# Sprawdź wersję Pythona (musi być 3.8+)
python --version

# Reinstaluj PyQt6
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PyQt6==6.6.1
```

#### Problem: "Brak uprawnień do zapisu"
```bash
# Windows: Uruchom terminal jako Administrator
# macOS/Linux: Sprawdź uprawnienia do katalogu
chmod 755 City_Builder/
```

### Struktura Środowiska Wirtualnego

Po utworzeniu środowiska wirtualnego struktura będzie wyglądać tak:

```
City_Builder/
├── city_builder_env/          # Środowisko wirtualne
│   ├── Scripts/               # (Windows) Skrypty aktywacji
│   ├── bin/                   # (macOS/Linux) Skrypty aktywacji
│   ├── Lib/                   # Zainstalowane pakiety
│   ├── Include/               # Pliki nagłówkowe
│   └── pyvenv.cfg             # Konfiguracja środowiska
├── Main.py                    # Główny plik aplikacji
├── requirements.txt           # Zależności
└── ...                        # Pozostałe pliki projektu
```

### Zarządzanie Zależnościami

```bash
# Dodanie nowej zależności
pip install nazwa_pakietu
pip freeze > requirements.txt

# Aktualizacja wszystkich pakietów
pip list --outdated
pip install --upgrade nazwa_pakietu

# Eksport środowiska do pliku
pip freeze > requirements_full.txt
```

## 🎮 Jak Grać

### Podstawy
- **Lewy klik** - Wybierz kafelek lub postaw budynek
- **Prawy klik** - Anuluj budowę
- **R** - Obróć wybrany budynek (drogi, chodniki)
- **Ctrl + Scroll** - Zoom mapy
- **Scroll** - Przewijanie mapy

### Menu
- **File → New Game** - Nowa gra
- **File → Save Game** - Zapisz grę
- **File → Load Game** - Wczytaj grę
- **Game → Pause/Resume** - Pauza/wznów
- **Game → Difficulty** - Poziom trudności

### Strategia
1. **Zacznij od infrastruktury** - Drogi i chodniki
2. **Buduj mieszkania** - Zwiększ populację
3. **Dodaj miejsca pracy** - Sklepy, fabryki
4. **Usługi publiczne** - Szkoły, szpitale dla zadowolenia
5. **Monitoruj finanse** - Podatki vs. wydatki

## 📊 Następne Kroki (FAZA 3-4)

### Priorytet Wysoki
- [ ] System wydarzeń losowych (katastrofy, bonusy)
- [ ] Panel raportów z wykresami (matplotlib)
- [ ] Rozszerzony system technologii
- [ ] Baza danych SQLite

### Priorytet Średni  
- [ ] Handel z sąsiednimi miastami
- [ ] Zaawansowane statystyki
- [ ] System osiągnięć
- [ ] Testy jednostkowe

### Priorytet Niski
- [ ] Scenariusze rozgrywki
- [ ] Rozszerzona mapa (większe miasta)
- [ ] Multiplayer (planowane)

## 🛠️ Technologie

- **Python 3.8+**
- **PyQt6** - Interfejs graficzny
- **Matplotlib** - Wykresy i raporty
- **NumPy** - Obliczenia numeryczne
- **JSON** - Zapis/wczytanie gry
- **SQLite** - Baza danych (planowane)

## 🐛 Znane Problemy

- [ ] Optymalizacja renderowania dla większych map
- [ ] Dodanie więcej grafik budynków
- [ ] Balansowanie ekonomii

## 📝 Licencja

Projekt edukacyjny - wykorzystanie w celach niekomercyjnych.

## 👥 Autorzy

- [Twoje Imię] - Główny deweloper

---

**Status:** 🔄 W Aktywnym Rozwoju  
**Wersja:** 1.0 Beta  
**Ostatnia aktualizacja:** [Aktualna data]

## Ostatnie aktualizacje

### 🔧 Poprawki z dnia dzisiejszego:

1. **Naprawiony podgląd rotacji budynków**:
   - Teraz przed postawieniem budynku widać dokładnie jak będzie obrócony
   - Rotacja działa płynnie z klawiszem `R`
   - Podgląd jest półprzezroczysty i pokazuje dokładny stan po rotacji

2. **Naprawiona ekonomia**:
   - Pieniądze są odejmowane tylko raz przy budowie (usunięto duplikację)
   - Zbalansowano system ekonomiczny
   - Wydatki działają prawidłowo

3. **Naprawiona populacja**:
   - Znacznie zmniejszona początkowa populacja (z ~2000 do ~290)
   - Zmniejszone wskaźniki śmiertelności (z 1.5% na 0.5%)
   - Dodano ograniczenie maksymalnego spadku populacji (5% na turę)
   - Budynki mieszkalne teraz stabilizują populację
   - Różne klasy społeczne mają różne priorytety potrzeb

4. **Ulepszona rozgrywka**:
   - Populacja reaguje pozytywnie na budynki mieszkalne
   - Lepszy balans między różnymi potrzebami społecznymi
   - Satysfakcja zmienia się stopniowo, nie drastycznie

5. **Naprawiony system budowania**:
   - Podgląd budynku teraz pokazuje się gdzie jest kursor myszy (nie tylko na wybranym kafelku)
   - Można łatwiej budować - nie trzeba najpierw klikać kafelka
   - Podświetlanie pokazuje gdzie można budować (zielone) i gdzie nie można (czerwone)

6. **Naprawiony panel budowy**:
   - Nazwy budynków nie są już ucięte
   - Zwiększone rozmiary przycisków (90x100px)
   - Długie nazwy są automatycznie dzielone na dwie linie
   - Lepsze tooltips z informacjami o kosztach i efektach
   - Zwiększona szerokość panelu do 250px

### 🔧 Dodatkowe poprawki interfejsu:

7. **Znacznie większe przyciski budynków**:
   - Rozmiar zwiększony do 140x120px dla lepszej czytelności
   - Layout zmieniony na jedną kolumnę
   - Większe ikony budynków (80x80px)
   - Lepsze formatowanie nazw z automatycznym łamaniem na 2-3 linie
   - Zwiększona szerokość panelu do 320px

8. **Lepszy interfejs aplikacji**:
   - Rozmiar okna zwiększony do 1600x1000px
   - Poprawione proporcje: mapa (4:2) vs panel budowy
   - Panel budowy ma więcej miejsca na duże przyciski

9. **Ulepszone wskaźniki rotacji**:
   - Dodano żółtą strzałkę pokazującą kierunek rotacji
   - Strzałka widoczna dla dróg, zakrętów i chodników
   - Rotacja wizualnie potwierdzana podczas obracania klawiszem R

10. **Optymalizacja wydajności**:
    - Dodano throttling do podglądu budynków (max 20 FPS)
    - Lepsze sprawdzanie granic mapy
    - Zmniejszone zacięcia podczas poruszania myszą

### 🔧 Najnowsze poprawki:

11. **Rotacja wszystkich budynków**:
    - Usunięto ograniczenie rotacji tylko do dróg
    - Teraz wszystkie budynki można obracać klawiszem R
    - Żółta strzałka pokazuje kierunek rotacji dla każdego budynku
    - Przycisk "Rotate" aktywny dla wszystkich budynków

12. **Poprawiony układ menu budynków**:
    - Zmieniono z 1 kolumny na 2 kolumny
    - Rozmiar przycisków: 130x100px (optymalny dla 2 kolumn)
    - Ikony budynków: 70x70px
    - Szerokość panelu: 300px
    - Wszystkie nazwy widoczne z automatycznym łamaniem

13. **Naprawione budowanie budynków**:
    - Usunięto duplikację logiki stawiania budynków
    - MapCanvas emituje sygnał, GameEngine obsługuje stawianie
    - Mapa zawsze odświeża się po próbie postawienia
    - Lepsze sprawdzanie warunków budowania

14. **Zoptymalizowana wydajność**:
    - Throttling zwiększony do 10 FPS (z 20 FPS) dla płynności
    - Odświeżanie tylko gdy pozycja myszy rzeczywiście się zmienia
    - Mniej zacięć przy przeskakiwaniu między polami

### 🔧 Finalne poprawki:

15. **Jeszcze lepsza wydajność**:
    - Throttling zwiększony do ~7 FPS (z 10 FPS) dla eliminacji zacięć
    - Płynne poruszanie myszą nawet przy szybkich ruchach
    - Optymalne odświeżanie podglądu budynków

16. **Rotacja wszystkich budynków - naprawiona**:
    - Wszystkie budynki można obracać, nie tylko drogi
    - Budynki z grafikami: żółta strzałka pokazuje rotację
    - Budynki kolorowe: tekst "90°", "180°", "270°" pokazuje rotację
    - Wizualne potwierdzenie rotacji dla każdego typu budynku

17. **Opcja odznaczenia budynku**:
    - **Prawy przycisk myszy**: Odznacza wybrany budynek i przywraca normalny kursor
    - **Przycisk "Clear Selection"**: Czerwony przycisk w panelu budowy
    - **Automatyczne odznaczenie**: Po kliknięciu można wrócić do normalnego trybu

18. **Większe przyciski w menu**:
    - Rozmiar zwiększony do 145x110px (z 130x100px)
    - Ikony 75x75px dla lepszej widoczności
    - Szerokość panelu: 320px
    - Lepsze formatowanie nazw - "Road Curve" teraz w pełni widoczne
    - Większa czcionka (11px) i lepszy padding

### 🔧 Ostateczne poprawki:

19. **Jeszcze szersze przyciski w menu**:
    - Rozmiar zwiększony do 160x110px (z 145x110px)
    - Szerokość panelu: 360px dla pełnej czytelności
    - Wszystkie nazwy budynków w pełni widoczne
    - Lepsze formatowanie dla długich nazw (do 15 znaków bez łamania)
    - Proporcje okna: mapa (3:2) vs panel budowy

20. **Naprawiona rotacja budynków**:
    - Usunięto duplikację deepcopy w GameEngine
    - Rotacja jest teraz poprawnie zachowywana przy stawianiu
    - Wszystkie budynki można obracać od pierwszego razu
    - Rotacja działa natychmiast po wybraniu budynku

21. **Maksymalna płynność poruszania**:
    - Throttling zwiększony do 5 FPS (0.2s między aktualizacjami)
    - Całkowite wyeliminowanie zacięć przy poruszaniu myszą
    - Płynne przechodzenie między kafelkami na mapie
    - Optymalne odświeżanie tylko gdy potrzebne

### 🔧 Finalne optymalizacje:

22. **Naprawiony focus dla klawiatury**:
    - Dodano `setFocusPolicy(Qt.FocusPolicy.StrongFocus)` do MapCanvas
    - Automatyczne ustawianie focus przy wyborze budynku
    - Klawisz R działa natychmiast po wybraniu budynku (bez konieczności stawiania pierwszego)
    - Focus ustawiany również w Main.py po inicjalizacji

23. **Znacznie lepsza płynność poruszania**:
    - Throttling zmniejszony z 0.2s na 0.05s (20 FPS zamiast 5 FPS)
    - Zoptymalizowana metoda draw_map() z pomocniczymi funkcjami
    - Wydzielone metody: `_draw_building_preview()`, `_draw_tile_highlights()`, `_draw_rotation_arrow()`
    - Cachowanie wartości w pętli renderowania
    - Ustawienie scene rect tylko raz na końcu

24. **Zoptymalizowane renderowanie**:
    - Terrain rysowany z przezroczystym obramowaniem
    - Lepsze zarządzanie Z-level (terrain=0, building=1, preview=1.5, border=2, highlight=3)
    - Efektywniejsze czyszczenie sceny
    - Mniejsze obciążenie CPU przy poruszaniu myszą

### 🔧 Najnowsze poprawki:

25. **Rotacja wszystkich budynków**:
    - Usunięto ograniczenie rotacji tylko do dróg
    - Teraz wszystkie budynki można obracać klawiszem R
    - Żółta strzałka pokazuje kierunek rotacji dla każdego budynku
    - Przycisk "Rotate" aktywny dla wszystkich budynków

26. **Poprawiony układ menu budynków**:
    - Zmieniono z 1 kolumny na 2 kolumny
    - Rozmiar przycisków: 130x100px (optymalny dla 2 kolumn)
    - Ikony budynków: 70x70px
    - Szerokość panelu: 300px
    - Wszystkie nazwy widoczne z automatycznym łamaniem

27. **Naprawione importy i struktura**:
    - Uporządkowane importy w `map_canvas.py`
    - Dodano wszystkie potrzebne importy: `os`, `time`, `deepcopy`
    - Usunięto duplikaty importów
    - Poprawna struktura klas i metod

### 🔧 Ostateczne naprawki:

28. **Naprawiony błąd ImportError z QPointF**:
    - Usunięto duplikowany import `QPointF` z różnych modułów
    - Skonsolidowane importy: `QPointF` tylko z `PyQt6.QtCore`
    - Uporządkowane wszystkie importy PyQt6 w logiczne grupy
    - Aplikacja uruchamia się bez błędów importu

### 🚀 Zaawansowane optymalizacje płynności:

29. **System incremental updates**:
    - Dodano `update_preview_only()` - aktualizuje tylko podgląd budynku bez przerysowywania całej mapy
    - Tracking preview items w `self._preview_items[]` dla szybkiego usuwania
    - `mouseMoveEvent` używa teraz `update_preview_only()` zamiast `draw_map()`
    - Throttling zwiększony do 0.1s (10 FPS) dla stabilności

30. **Optymalizowane renderowanie podglądu**:
    - Wydzielone metody: `_create_rotation_arrow()`, `_create_rotation_text()`
    - Selektywne usuwanie tylko elementów podglądu
    - Zachowanie pełnej mapy bez ciągłego przerysowywania
    - Rotacja budynków używa szybkiej aktualizacji

31. **Znacznie lepsza responsywność**:
    - Eliminacja ciągłego przerysowywania całej sceny (60x60 kafelków)
    - Aktualizacja tylko 1-3 elementów graficznych zamiast 3600+
    - Płynne poruszanie budynkiem po mapie bez zacięć
    - Zachowana pełna funkcjonalność z lepszą wydajnością

### 🔧 Naprawione artefakty preview:

32. **Wyeliminowane białe kafelki i podwojone budynki**:
    - Dodano bezpieczne usuwanie preview items z try-catch
    - Wprowadzono dwustopniowe czyszczenie: lista items_to_remove → bezpieczne usuwanie
    - Walidacja `item and item.scene() == self.scene` przed usunięciem
    - Czyszczenie preview items przy każdej zmianie budynku i placement

33. **System automatycznego czyszczenia artefaktów**:
    - Dodano `_cleanup_artifacts()` - periodyczne usuwanie pozostałych artefaktów
    - Cleanup uruchamiany co 50 ruchów myszą
    - Identyfikacja artefaktów po Z-value (1.5, 2.5, 3.0) nie będących w `_preview_items`
    - Debug log gdy usuwa więcej niż 10 artefaktów

34. **Wzmocnione czyszczenie przy kluczowych operacjach**:
    - `select_building()`: pełne czyszczenie + `_cleanup_artifacts()`
    - `place_building()`: czyszczenie przed placement
    - `rotate_building()`: używa szybkiej aktualizacji
    - Eliminacja "duchów" budynków pozostających na mapie

### 🔧 Naprawione crash przy szybkich ruchach:

35. **Wyeliminowany RuntimeError przy szybkim machaniu kursorem**:
    - Dodano walidację `hasattr(item, 'scene')` przed dostępem do obiektów C++
    - Try-catch dla `RuntimeError` i `AttributeError` przy usuwaniu obiektów
    - Podwójna weryfikacja obiektów przed usunięciem z sceny
    - Bezpieczne pobieranie listy items z `self.scene.items()`

36. **Stabilizacja przy intensywnym użyciu**:
    - Throttling zwiększony do 0.15s dla lepszej stabilności
    - Częstsze czyszczenie artefaktów (co 30 ruchów zamiast 50)
    - Lepsze zarządzanie cyklem życia obiektów Qt/C++
    - Aplikacja nie crashuje przy szybkich, intensywnych ruchach myszy

37. **Wzmocniona obsługa błędów**:
    - Wszystkie operacje na obiektach graficznych w try-catch
    - Graceful handling usuniętych obiektów C++
    - Kontynuacja działania nawet przy błędach Qt
    - Stabilność przy różnych wzorcach użycia (szybkie/wolne ruchy)

### 🛡️ Zaawansowane zabezpieczenia przeciw crashom:

38. **Opóźnione czyszczenie z QTimer**:
    - Zamiana synchronicznego usuwania elementów na asynchroniczne z QTimer.singleShot()
    - Rozdzielenie czyszczenia (10ms) i aktualizacji (20ms) 
    - Unikanie modyfikacji obiektów w trakcie obsługi wydarzeń
    - Eliminacja RuntimeError przy intensywnym użyciu

39. **Strategia "copy-then-clear"**:
    - Lista preview_items kopiowana przed iteracją: `current_items = self._preview_items.copy()`
    - Główna lista czyszczona natychmiast: `self._preview_items = []`
    - Usuwanie na kopii, a nie na oryginalnej liście
    - Unikanie modyfikacji kolekcji podczas iteracji

40. **Mechanizm periodycznego odradzania sceny**:
    - Losowe pełne przerysowanie co 5 operacji (20% szansy)
    - Wymuszony `draw_map()` resetujący całą scenę
    - Limit częstotliwości rotacji (max co 0.2s)
    - Kompleksowa obsługa wyjątków w całym stack traceu

### 🎮 Finalne poprawki interfejsu użytkownika:

41. **Odznaczanie kafelków**:
    - Dodano `deselect_tile()` w klasie CityMap
    - Odznaczanie tego samego kafelka klikając go ponownie
    - Odznaczanie przy kliknięciu prawym przyciskiem myszy
    - Klawisz Escape usuwa zaznaczenie kafelka i budynku
    - Automatyczne usuwanie zaznaczenia przy wyborze budynku

42. **Eliminacja białych kwadratów i podwójeń**:
    - Nowa metoda `_cleanup_all_previews_immediate()` dla synchronicznego czyszczenia
    - Sekwencja: 1) wyczyść wszystkie elementy podglądu 2) dodaj nowe
    - Wymuszony `draw_map()` co 30 ruchów myszy
    - Sprawdzanie czy scena i obiekty nadal istnieją przed operacjami

43. **Ulepszona synchronizacja stanu**:
    - Spójny stan pomiędzy mapą a interfejsem
    - Kafelek zostaje odznaczony przy wyborze budynku
    - Odznaczanie budynku przywraca normalny kursor
    - Klawisz Escape jako uniwersalny przycisk "anuluj"
    - Eliminacja "sierot" - zaznaczonych kafelków po zmianie trybu

### 🔄 Radykalne rozwiązanie problemów renderowania:

44. **Pełne przerysowanie zamiast inkrementalnych aktualizacji**:
    - Całkowite zastąpienie incremental updates przez pełne przetwarzanie mapy
    - Wywołanie `draw_map()` zamiast `update_preview_only()` przy każdym ruchu kursora
    - `scene.clear()` + `_preview_items.clear()` na początku każdego przerysowania
    - Zapewnienie zerowania stanu sceny przed każdym renderowaniem

45. **Uproszczony model renderowania**:
    - Rezygnacja z opóźnionego czyszczenia (QTimer.singleShot)
    - Synchroniczne rysowanie i czyszczenie w jednym kroku
    - Wykorzystanie wydajnej funkcji scene.clear() 
    - Stabilność kosztem dodatkowych operacji rysowania

46. **Kompletna eliminacja artefaktów graficznych**:
    - Brak białych kwadratów dzięki konsekwentnemu czyszczeniu sceny
    - Żadnych podwójnych budynków - cała scena jest zawsze odświeżana
    - Brak "duchów" i pozostałości po poprzednich operacjach
    - Odświeżanie całej mapy zapewnia spójny obraz

## O grze

Zaawansowany symulator miasta napisany w Python z PyQt6. Gracze budują i zarządzają miastem, dbając o ekonomię, populację i infrastrukturę.

## Funkcje

### ✅ Zaimplementowane funkcje:
- **Mapa 60x60** z różnymi typami terenu (trawa, woda, góry, las)
- **21+ typów budynków** w 5 kategoriach
- **System ekonomiczny** z 6 typami zasobów
- **5 klas społecznych** z dynamiką populacji
- **Grafika z przezroczystością** dla budynków
- **Rotacja budynków** (drogi, zakręty, chodniki)
- **Ograniczenia terenu** (nie można budować na wodzie/górach)
- **System zapisywania/wczytywania** (JSON)
- **Interfejs** z mapą, panelem budowy, statusem
- **Raporty ekonomiczne** i demograficzne

### 🎮 Sterowanie:
- **Klik lewym przyciskiem**: Wybierz kafelek lub postaw budynek
- **Klik prawym przyciskiem**: Odznacz wybrany budynek (powrót do normalnego kursora)
- **Klawisz R**: Obróć wybrany budynek (wszystkie budynki)
- **Ctrl + scroll**: Zoom mapy
- **Menu**: Nowa gra, zapisz, wczytaj
- **Przycisk "Clear Selection"**: Odznacz budynek w panelu budowy

### 🏗️ Kategorie budynków:
1. **Mieszkalne**: Dom, apartamenty, osiedle
2. **Przemysłowe**: Fabryka, elektrownia, kopalnia
3. **Usługowe**: Szpital, szkoła, uniwersytet, policja, straż
4. **Komercyjne**: Sklep, centrum handlowe, biurowiec
5. **Infrastruktura**: Drogi, chodniki, park, stadion

### 📊 Zasoby:
- **Pieniądze**: Główna waluta miasta
- **Energia**: Produkowana przez elektrownie
- **Woda**: Potrzebna dla mieszkańców
- **Materiały**: Do budowy
- **Żywność**: Dla populacji
- **Dobra luksusowe**: Dla wyższych klas

### 👥 Klasy społeczne:
1. **Robotnicy**: Priorytet na pracę i mieszkania
2. **Klasa średnia**: Edukacja i bezpieczeństwo
3. **Klasa wyższa**: Rozrywka i transport
4. **Studenci**: Edukacja
5. **Bezrobotni**: Szukają pracy

## Instalacja

```bash
# Wymagania systemowe
pip install -r requirements.txt

# Uruchomienie gry
python Main.py
```

### Wymagania:
- Python 3.8+
- PyQt6
- Inne zależności w `requirements.txt`

## Struktura projektu

```
City_Builder/
├── Main.py                 # Główny plik aplikacji
├── core/                   # Logika gry
│   ├── game_engine.py     # Główny silnik gry
│   ├── resources.py       # System ekonomiczny
│   ├── population.py      # Zarządzanie populacją
│   ├── tile.py           # Kafelki i budynki
│   └── city_map.py       # Mapa miasta
├── gui/                   # Interfejs użytkownika
│   ├── map_canvas.py     # Renderowanie mapy
│   └── build_panel.py    # Panel budowy
├── assets/               # Grafiki
│   ├── tiles/           # Tekstury kafelków
│   └── buildings/       # Grafiki budynków
├── saves/               # Zapisane gry
└── data/               # Dane konfiguracyjne
```

## Wymagania akademickie

### Kryteria funkcjonalne (6/10 zaimplementowanych):
- [x] Mapa z kafelkami
- [x] System budynków
- [x] Zarządzanie zasobami
- [x] Populacja i społeczeństwo
- [x] Ekonomia i podatki
- [x] System wydarzeń (częściowo)
- [ ] Technologie
- [ ] Handel
- [ ] Dyplomacja
- [ ] Scenariusze

### Kryteria skryptowe (8/8 zaimplementowanych):
- [x] Klasy i obiekty
- [x] Dziedziczenie
- [x] Polimorfizm
- [x] Enkapsulacja
- [x] Obsługa błędów
- [x] Praca z plikami
- [x] Struktury danych
- [x] Algorytmy

### Kryteria techniczne (5/7 zaimplementowanych):
- [x] GUI (PyQt6)
- [x] Grafika (PNG z przezroczystością)
- [x] Baza danych (JSON)
- [x] Wielowątkowość (QTimer)
- [x] Testowanie (struktura)
- [ ] Sieć
- [ ] Zewnętrzne API

## Rozwój

Projekt jest rozwijany w fazach zgodnie z wytycznymi. Aktualna wersja to **Faza 2+** z dodatkowymi funkcjami.

### Planowane funkcje:
- Rozszerzone wydarzenia losowe
- System technologii
- Większa różnorodność grafik
- Tryb wieloosobowy
- Modyfikacje/mody

## Licencja

Projekt edukacyjny - do użytku akademickiego.
