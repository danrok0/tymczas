# System Rekomendacji Szlaków Turystycznych - Dokumentacja

## 1. Główne Komponenty Systemu

### 1.1 Obliczanie Komfortu Wędrówki
System wykorzystuje złożony algorytm do obliczania indeksu komfortu (0-100) dla każdej trasy:

1. Kalkulacja temperatury (40% wagi końcowej):
   - Temperatura idealna: 15-18°C = 100 punktów
   - Poniżej 15°C: -15 punktów za każdy stopień
   - Powyżej 18°C: -18 punktów za każdy stopień
   - Przykład: 20°C = 100 - (20-18)*18 = 64 punktów

2. Kalkulacja opadów (35% wagi końcowej):
   - Brak opadów = 100 punktów
   - Każdy mm opadów = -40 punktów
   - Przykład: 2mm opadów = 100 - (2*40) = 20 punktów

3. Kalkulacja zachmurzenia (25% wagi końcowej):
   - 20-40% zachmurzenia = 100 punktów
   - 0-20% = 80 punktów (możliwe za duże nasłonecznienie)
   - 40-60% = 60 punktów
   - >60% = liniowy spadek (2 punkty za każdy % powyżej 60)

Finalna wartość to średnia ważona powyższych komponentów.
Lokalizacja kodu: `utils/weather_utils.py -> WeatherUtils.calculate_hiking_comfort()`

### 1.2 System Oceny i Wagi
- Temperatura (40% wagi)
  - Optymalna temperatura: 15-18°C
  - Punktacja maleje przy odchyleniach od zakresu optymalnego
  
- Opady (35% wagi)
  - Im niższe opady, tym wyższa ocena
  - Uwzględniane są zarówno opady aktualne jak i prognozowane
  
- Zachmurzenie (25% wagi)
  - Optymalne zachmurzenie: 20-40%
  - Zapewnia balans między ochroną przed słońcem a dobrą widocznością

### 1.2 Modyfikatory Terenowe
Indeks jest modyfikowany w zależności od typu terenu:
- Teren górski: 
  - Temperatura obniżana o 0.6°C na każde 100m wysokości
  - Opady zwiększane o 20%
  
## 9. System Wag i Obliczanie Wyników (ZAKTUALIZOWANY)

### 9.1 Domyślne Wagi Kryteriów i Ich Działanie
System wykorzystuje następujący rozkład wag przy ocenie tras:

1. **Długość trasy (25% wagi końcowej)** - ZAKTUALIZOWANE:
   - Bazowa waga: 0.25 (zmieniono z 0.30)
   - Sposób obliczania:
     * Dla każdej trasy obliczana jest odległość od optymalnego zakresu (5-15 km)
     * Jeśli trasa mieści się w zakresie: 100 punktów
     * Za każdy km poniżej 5km: -5 punktów
     * Za każdy km powyżej 15km: -5 punktów
     * Przykład: trasa 18km = 100 - (18-15)*5 = 85 punktów
   - Lokalizacja: `utils/weight_calculator.py -> calculate_length_score()`

2. **Trudność (25% wagi końcowej)**:
   - Bazowa waga: 0.25
   - Sposób obliczania:
     * Poziom 1 (łatwy) = 100 punktów
     * Poziom 2 (średni) = 66.66 punktów
     * Poziom 3 (trudny) = 33.33 punktów
     * Dodatkowe modyfikatory:
       - Przewyższenie > 500m: -10 punktów
       - Przewyższenie > 1000m: -20 punktów
   - Lokalizacja: `utils/weight_calculator.py -> calculate_difficulty_score()`

3. **Warunki pogodowe (25% wagi końcowej)**:
   - Bazowa waga: 0.25
   - Wykorzystuje indeks komfortu (0-100)
   - Dodatkowe modyfikatory:
     * Deszczowy dzień: -30 punktów
     * Silny wiatr (>20 km/h): -20 punktów
   - Lokalizacja: `utils/weather_utils.py -> calculate_hiking_comfort()`

4. **Typ terenu (25% wagi końcowej)** - ZAKTUALIZOWANE:
   - Bazowa waga: 0.25 (zmieniono z 0.20)
   - Punktacja bazowa:
     * Górski: 90 punktów
     * Leśny: 85 punktów
     * Mieszany: 80 punktów
     * Nadrzeczny: 75 punktów
     * Miejski: 70 punktów
   - Modyfikatory:
     * Punkty widokowe: +10 punktów
     * Atrakcje turystyczne: +5 punktów każda
   - Lokalizacja: `utils/weight_calculator.py -> calculate_terrain_score()`

### 9.2 🆕 NOWY System Ustawiania Wag
**WAŻNE**: System wag został całkowicie przeprojektowany!

**Stary problem**: System pytał o wagi dla każdego miasta osobno
**Nowe rozwiązanie**: Wagi ustawiane JEDEN RAZ na początku

**Nowe funkcje**:
- Obsługa pustych wartości (ENTER = domyślne)
- Możliwość częściowego wypełnienia
- Automatyczna normalizacja do sumy 100%
- Walidacja poprawności danych
- Lepsze komunikaty użytkownika

### 2.2 Składowe Oceny Ważonej
1. Długość (normalizowana do 0-100)
   - Optymalna długość: 5-15 km (100 punktów)
   - Punktacja maleje o 5 punktów na każdy kilometr odchylenia

2. Trudność (skala 0-100)
   - Poziom 1: 100 punktów
   - Poziom 2: 66.66 punktów
   - Poziom 3: 33.33 punktów

3. Warunki pogodowe
   - Wykorzystuje indeks komfortu (0-100)

4. Typ terenu (ocena bazowa)
   - Górski: 90 punktów
   - Leśny: 85 punktów
   - Mieszany: 80 punktów
   - Nadrzeczny: 75 punktów
   - Miejski: 70 punktów

## 10. Kategoryzacja Tras i Algorytmy Klasyfikacji (ZAKTUALIZOWANE)

### 10.1 🆕 Automatyczna Kategoryzacja Tras
**Lokalizacja**: `recommendation/trail_recommender.py -> _categorize_trail()`

System automatycznie kategoryzuje trasy na podstawie inteligentnego algorytmu:

1. **Trasy Rodzinne**:
   - **Podstawowe kryteria** (wszystkie wymagane):
     * Trudność: poziom 1 (łatwy)
     * Długość: < 5 km
     * Przewyższenie: < 200m
   - **Dodatkowe wskaźniki**:
     * Tagi: leisure, park, playground, family
     * Słowa kluczowe: "rodzin", "łatw", "spokojna", "dziec"
   - **Priorytet**: Najwyższy (sprawdzane jako pierwsze)

2. **Trasy Widokowe**:
   - **Podstawowe kryteria**:
     * Długość: < 15 km (nie za długie)
     * Obecność punktów widokowych
   - **Wskaźniki**:
     * Tagi: viewpoint, scenic, tourism, view_point, panorama
     * Słowa kluczowe: "widok", "panoram", "scenic", "krajobraz", "punkt widokowy"
   - **Priorytet**: Drugi (po rodzinnych)

3. **Trasy Ekstremalne**:
   - **Kryteria** (jedno wystarczy):
     * Trudność: poziom 3 (trudny)
     * Długość: > 15 km
     * Przewyższenie: > 800m
   - **Wskaźniki**:
     * Tagi: climbing, alpine, via_ferrata, extreme
     * Słowa kluczowe: "ekstre", "trudna", "wymagając", "alpejsk"
   - **Priorytet**: Trzeci

4. **Trasy Sportowe**:
   - **Kryteria**:
     * Trudność: poziom 2 AND długość 5-15 km
     * LUB słowa kluczowe sportowe
   - **Wskaźniki**:
     * Słowa kluczowe: "sport", "aktyw", "kondycyj", "wysiłk"
   - **Priorytet**: Czwarty

5. **Algorytm Fallback**:
   - Jeśli trasa nie pasuje do żadnej kategorii:
     * Długość < 5km → rodzinna
     * Długość > 15km OR trudność 3 → ekstremalna  
     * Trudność 2 OR długość 5-15km → sportowa
     * W ostateczności → widokowa (najbezpieczniejsza opcja)

## 11. 🆕 Obliczanie Czasu Przejścia (ZAKTUALIZOWANE)

### 11.1 Nowy Algorytm Obliczania Czasu
**Lokalizacja**: `recommendation/trail_recommender.py -> _calculate_trail_time()`

**Wzór**: `Czas = Długość × Mnożnik_Trudności × Mnożnik_Terenu`

### 11.2 Parametry Bazowe
- **Bazowa jednostka**: 1 km = 1 godzina bazowego czasu
- **Zakres wyników**: 0.1 - 20+ godzin
- **Precyzja**: Wynik zaokrąglany do 0.1 godziny

### 11.3 🆕 Mnożniki Trudności
1. **Poziom 1 (łatwy)**: 1.0 (bez modyfikacji)
2. **Poziom 2 (średni)**: 1.4 (+40% czasu)
3. **Poziom 3 (trudny)**: 1.8 (+80% czasu)

**Wzór**: `1.0 + (trudność - 1) × 0.4`

### 11.4 🆕 Mnożniki Terenowe
1. **Miejski**: 0.8 (najszybszy - chodniki, asfalт)
2. **Nizinny**: 1.0 (bazowy teren)
3. **Nadrzeczny**: 1.1 (lekko trudniejszy)
4. **Leśny**: 1.2 (ścieżki leśne)
5. **Mieszany**: 1.3 (różnorodny teren)
6. **Górski**: 1.6 (najtrudniejszy - stromizny, kamienie)

### 11.5 Przykłady Obliczeń
1. **Trasa rodzinna**: 3 km, trudność 1, teren miejski
   - Czas = 3 × 1.0 × 0.8 = **2.4 godziny**

2. **Trasa sportowa**: 10 km, trudność 2, teren leśny  
   - Czas = 10 × 1.4 × 1.2 = **16.8 godzin**

3. **Trasa ekstremalna**: 20 km, trudność 3, teren górski
   - Czas = 20 × 1.8 × 1.6 = **57.6 godzin**

### 11.6 Wyświetlanie Czasu
System pokazuje czas w formacie:
- **Tylko godziny**: "5h" (dla 5.0h)
- **Godziny i minuty**: "3h 30min" (dla 3.5h)
- **Tylko minuty**: "45min" (dla 0.75h)

## 12. 📚 STARE FUNKCJONALNOŚCI (ZACHOWANE)

### 12.1 Ocena Trudności Trasy
System ocenia trudność w skali 1-3 na podstawie:

1. **Długości**:
   - > 20 km: poziom 3
   - > 10 km: poziom 2  
   - ≤ 10 km: poziom 1

2. **Przewyższenia**:
   - > 1000m: poziom 3
   - > 500m: poziom 2
   - ≤ 500m: poziom 1

3. **Skali SAC**:
   - alpine: poziom 3
   - mountain: poziom 2
   - inne: poziom 1

### 12.2 Podstawowe Funkcje Systemu

**Analiza Pogody**:
- `WeatherUtils.is_sunny_day()` - sprawdza słoneczność
- `WeatherUtils.is_rainy_day()` - sprawdza opady
- `WeatherUtils.calculate_hiking_comfort()` - indeks komfortu

**Operacje na Danych**:
- `TrailDataHandler.load_trails()` - wczytywanie tras
- `ResultExporter` - eksport do CSV/JSON/TXT
- `TrailFilter.filter_trails()` - filtrowanie tras

**Rekomendacje**:
- `TrailRecommender.recommend_trails()` - główny algorytm
- `TrailFilter.sort_trails()` - sortowanie wyników

## 2. 🆕 NOWE FUNKCJONALNOŚCI - ETAP 3

### 2.1 System Przetwarzania Tekstu (TextProcessor)
**Lokalizacja**: `extractors/text_processor.py`

**Co robi**: Analizuje opisy tras i wydobywa z nich informacje używając wyrażeń regularnych.

**Główne funkcje**:
1. **Ekstrakcja czasu przejścia** (`extract_time_info()`):
   - Rozpoznaje formaty: "2h 30min", "150 minut", "2.5 godziny"
   - Wzorce regex: `r'(\d+(?:\.\d+)?)\s*(?:h|godz|hours?)'`, `r'(\d+)\s*(?:min|minut)'`
   - Przykład: "Trasa zajmuje około 3h 45min" → 3.75 godziny

2. **Identyfikacja punktów charakterystycznych** (`extract_landmarks()`):
   - Znajduje: schroniska, szczyty, przełęcze, punkty widokowe
   - Wzorce: `r'(schronisko|szczyt|przełęcz|punkt widokowy)'`

3. **Rozpoznawanie ostrzeżeń** (`extract_warnings()`):
   - Wykrywa: śliskie kamienie, trudne warunki, zagrożenia
   - Wzorce: `r'(uwaga|ostrożnie|niebezpieczne|śliskie)'`

**Jak używać**:
```python
processor = TextProcessor()
time_info = processor.extract_time_info("Czas przejścia około 2h 30min")
# Wynik: {'hours': 2, 'minutes': 30, 'total_hours': 2.5}
```

### 2.2 System Analizy Recenzji (ReviewAnalyzer)
**Lokalizacja**: `analyzers/review_analyzer.py`

**Co robi**: Analizuje recenzje użytkowników i określa ich sentiment oraz wydobywa informacje.

**Główne funkcje**:
1. **Analiza sentymentu** (`analyze_sentiment()`):
   - Określa czy recenzja jest pozytywna, negatywna czy neutralna
   - Słowa pozytywne: "wspaniały", "piękny", "polecam", "świetny"
   - Słowa negatywne: "trudny", "niebezpieczny", "nie polecam", "problem"
   - Obsługuje negację: "nie polecam" = negatywne

2. **Ekstrakcja ocen** (`extract_rating()`):
   - Rozpoznaje formaty: "4.5/5", "8/10", "★★★★★"
   - Normalizuje do skali 1-5

3. **Identyfikacja aspektów** (`extract_aspects()`):
   - Wykrywa tematy: widoki, trudność, oznakowanie, dojazd
   - Przykład: "Piękne widoki ale trudne oznakowanie" → ['widoki', 'oznakowanie']

4. **Analiza sezonowości** (`extract_season()`):
   - Rozpoznaje: "wiosną", "latem", "jesienią", "zimą"

**Gdzie zobaczyć wyniki**:
- **Opcja 3** w menu głównym: "Analiza konkretnej trasy"
- Każda recenzja pokazuje: 📊 Sentiment: 😊 Pozytywna/😞 Negatywna/😐 Neutralna

### 2.3 System Generowania Recenzji
**Lokalizacja**: `data_handlers/trail_data.py -> _generate_sample_reviews()`

**Co robi**: Automatycznie generuje różnorodne, realistyczne recenzje dla tras.

**Typy recenzji**:
1. **Pozytywne (60% szans)**: "Fantastyczna trasa!", "Wspaniałe widoki!"
2. **Neutralne (25% szans)**: "Trasa w porządku", "Przeciętna trasa"
3. **Negatywne (15% szans)**: "Rozczarowanie", "Źle oznakowana"
4. **Specyficzne dla trudności**: Różne opinie dla łatwych/trudnych tras
5. **Specyficzne dla terenu**: Góry, las, miasto - różne komentarze
6. **Sezonowe**: Opinie związane z porami roku

**Przykład wygenerowanych recenzji**:
```
1. Fantastyczna trasa! Szlak zachwyca na każdym kroku. 5/5
   📊 Sentiment: 😊 Pozytywna
   ⭐ Ocena: 5.0/5
   🔑 Aspekty: widoki

2. Trasa w porządku, oznakowanie mogłoby być lepsze. 3/5
   📊 Sentiment: 😐 Neutralna
   ⭐ Ocena: 3.0/5
   🔑 Aspekty: oznakowanie
```

### 2.4 System Raportów PDF
**Lokalizacja**: `reporters/pdf_report_generator.py`

**Co robi**: Generuje profesjonalne raporty PDF z rekomendacjami tras.

**Zawartość raportu**:
1. **Strona tytułowa**: Data, parametry wyszukiwania
2. **Podsumowanie wykonawcze**: Najważniejsze wnioski
3. **Szczegółowe opisy tras**: Z mapami i profilami
4. **Wykresy porównawcze**: Długość, oceny, kategorie
5. **Tabela zbiorcza**: Wszystkie parametry tras
6. **Obsługa polskich znaków**: Fonty Arial, Calibri, DejaVu Sans

**Jak używać**:
- **Opcja 2** w menu głównym: "Rekomendacje z raportem PDF"
- System pyta o nazwę pliku
- Automatycznie otwiera wygenerowany PDF

### 2.5 System Wykresów i Wizualizacji
**Lokalizacja**: `reporters/chart_generator.py`

**Co robi**: Tworzy wykresy do raportów PDF i analizy danych.

**Typy wykresów**:
1. **Histogram długości tras**: Rozkład długości wszystkich tras
2. **Wykres kołowy kategorii**: Podział na rodzinne/sportowe/ekstremalne
3. **Wykres słupkowy ocen**: Rozkład ocen użytkowników
4. **Mapa ciepła sezonowości**: Popularność tras w różnych miesiącach
5. **Wykres radarowy**: Ocena tras pod różnymi kryteriami

**Funkcje**:
- Automatyczne kolorowanie
- Polskie opisy i etykiety
- Eksport do PNG dla PDF
- Obsługa różnych rozmiarów

### 2.6 System Analizy Najlepszych Okresów
**Lokalizacja**: `main.py -> analyze_specific_trail()` (linie 550-620)

**Co robi**: Analizuje dane pogodowe i określa najlepsze okresy dla wędrówek.

**Algorytm oceny komfortu**:
1. **Temperatura (50% wagi)**:
   - Optymalna: 15-25°C = +30 punktów
   - Dobra: 10-15°C lub 25-30°C = +20 punktów
   - Przeciętna: 5-10°C lub 30-35°C = +10 punktów
   - Słaba: poniżej 5°C lub powyżej 35°C = -10 punktów

2. **Opady (35% wagi)**:
   - Niskie (<30mm) = +20 punktów
   - Średnie (30-60mm) = +10 punktów
   - Wysokie (60-100mm) = 0 punktów
   - Bardzo wysokie (>100mm) = -15 punktów

3. **Słońce (15% wagi)**:
   - Dużo (>7h) = +15 punktów
   - Średnio (5-7h) = +10 punktów
   - Mało (3-5h) = +5 punktów

**Wynik**: Ranking 12 miesięcy z indeksem komfortu 0-100

### 2.7 Naprawiony System Wag
**Lokalizacja**: `utils/weight_calculator.py`

**Problem**: System w kółko pytał o wagi dla każdego miasta
**Rozwiązanie**: Wagi pobierane tylko raz na początku

**Nowe funkcje**:
1. **Obsługa pustych wartości**: ENTER = domyślne wagi
2. **Częściowe wypełnienie**: Można podać tylko niektóre wagi
3. **Walidacja**: Sprawdza czy suma wag nie jest zerem
4. **Lepsze komunikaty**: Jasne informacje o procesie

**Jak działa teraz**:
```
⚖️ === USTAWIENIE WAG KRYTERIÓW ===
Aktualne wagi kryteriów:
- length: 25%
- difficulty: 25%
- weather: 25%
- terrain: 25%

Podaj nowe wagi (0-100) lub wciśnij ENTER dla wartości domyślnych:
Waga długości trasy: [ENTER dla domyślnej]
✅ Użyto domyślnych wag
```

## 3. 🔧 POPRAWKI I ULEPSZENIA

### 3.1 Naprawione Gwiazdki w PDF
**Problem**: Gwiazdki (★) wyświetlały się jako prostokąty
**Rozwiązanie**: Zastąpiono opisowym tekstem
- `4.2/5 (Bardzo dobra)` zamiast `4.2/5 (****-)`
- Skala: Doskonała (4.5+), Bardzo dobra (4.0+), Dobra (3.0+), Przeciętna (2.0+), Słaba (<2.0)

### 3.2 Poprawione Preferencje Sezonowe
**Problem**: `Preferencje sezonowe: {'wiosna': 1}` - pokazywało liczby
**Rozwiązanie**: `Preferencje sezonowe: wiosna, lato` - tylko nazwy

### 3.3 Naprawiona Analiza Błędów PDF
**Problem**: `cannot access local variable 'avg_rating_str'`
**Rozwiązanie**: Poprawione wcięcia w `analyzers/review_analyzer.py`

### 3.4 Usunięte Duplikaty Tras
**Funkcja**: `_remove_duplicates()` w `data_handlers/trail_data.py`
**Kryteria**: Identyczna nazwa, długość i region
**Wynik**: System loguje ile duplikatów usunął

## 4. 📍 STRUKTURA MENU I OPCJE

### 4.1 Menu Główne
```
=== 🏔️ SYSTEM REKOMENDACJI TRAS TURYSTYCZNYCH ===
1. 🎯 Standardowe rekomendacje tras
2. 📊 Rekomendacje z raportem PDF  
3. 🔍 Analiza konkretnej trasy
4. 🌐 Zbieranie danych z internetu
5. 📈 Generowanie wykresów
6. 🔤 Demonstracja przetwarzania tekstu
7. 🚪 Wyjście
```

### 4.2 Szczegółowy Opis Opcji

**Opcja 1: Standardowe rekomendacje**
- Wybór miasta/miast i daty
- Ustawienie kryteriów wyszukiwania
- **NOWE**: Jednorazowe ustawienie wag (nie pyta dla każdego miasta)
- Analiza najlepszych okresów z prawdziwymi danymi pogodowymi
- Eksport do CSV/JSON/TXT

**Opcja 2: Rekomendacje z PDF**
- Wszystko jak opcja 1 + generowanie raportu PDF
- Możliwość podania własnej nazwy pliku
- Automatyczne otwieranie PDF po wygenerowaniu
- **NOWE**: Poprawione gwiazdki i polskie znaki

**Opcja 3: Analiza konkretnej trasy**
- **NAJLEPSZE MIEJSCE DO ZOBACZENIA ANALIZY SENTYMENTU!**
- Wybór konkretnej trasy z listy
- Szczegółowa analiza każdej recenzji z emoji
- Pełna analiza najlepszych okresów (12 miesięcy)
- **NOWE**: Pokazuje sentiment każdej recenzji osobno

**Opcja 4: Zbieranie danych z internetu**
- Demonstracja WebDataCollector
- Symulacja pobierania danych z portali turystycznych

**Opcja 5: Generowanie wykresów**
- Tworzenie wszystkich typów wykresów
- Zapisywanie do plików PNG
- **NOWE**: Używa headless matplotlib (bez Qt)

**Opcja 6: Demonstracja przetwarzania tekstu**
- Pokazuje działanie TextProcessor
- Przykłady z updatelist.txt
- Ekstrakcja czasu, punktów, ostrzeżeń

## 5. 🗂️ STRUKTURA PLIKÓW I POŁĄCZENIA

### 5.1 Główne Moduły
```
projekt3xd/
├── main.py                 # Menu główne i logika aplikacji
├── analyzers/              # Analiza tekstu i recenzji
│   └── review_analyzer.py  # Sentiment, oceny, aspekty
├── extractors/             # Przetwarzanie tekstu
│   └── text_processor.py   # Regex, ekstrakcja informacji
├── reporters/              # Generowanie raportów
│   ├── pdf_report_generator.py  # Raporty PDF
│   └── chart_generator.py       # Wykresy i wizualizacje
├── utils/                  # Narzędzia pomocnicze
│   └── weight_calculator.py     # System wag (NAPRAWIONY)
└── data_handlers/          # Obsługa danych
    └── trail_data.py       # Generowanie recenzji, duplikaty
```

### 5.2 Przepływ Danych

**Standardowe rekomendacje**:
1. `main.py` → pobiera kryteria od użytkownika
2. `weight_calculator.py` → ustawia wagi JEDEN RAZ
3. `trail_recommender.py` → filtruje trasy dla każdego miasta
4. `review_analyzer.py` → analizuje recenzje
5. `export_results.py` → eksportuje wyniki

**Analiza konkretnej trasy**:
1. `main.py` → wybór trasy
2. `trail_data.py` → generuje recenzje
3. `review_analyzer.py` → analizuje każdą recenzję
4. `weather_utils.py` → analiza najlepszych okresów
5. Wyświetlenie szczegółowych wyników z emoji

**Raport PDF**:
1. `main.py` → standardowe rekomendacje
2. `chart_generator.py` → tworzy wykresy
3. `pdf_report_generator.py` → łączy wszystko w PDF
4. Automatyczne otwieranie pliku

## 6. 🎯 JAK PRZETESTOWAĆ NOWE FUNKCJE

### 6.1 Test Analizy Sentymentu
1. Uruchom: `python main.py`
2. Wybierz opcję **3** (Analiza konkretnej trasy)
3. Wybierz miasto (np. Gdańsk)
4. Wybierz trasę z listy
5. Zobacz szczegółową analizę każdej recenzji z emoji!

### 6.2 Test Naprawionego Systemu Wag
1. Uruchom: `python main.py`
2. Wybierz opcję **1** (Standardowe rekomendacje)
3. Wybierz **wszystkie miasta** (ENTER)
4. Ustaw wagi JEDEN RAZ na początku
5. System nie będzie już pytał o wagi dla każdego miasta!

### 6.3 Test Raportu PDF
1. Uruchom: `python main.py`
2. Wybierz opcję **2** (Rekomendacje z PDF)
3. Podaj nazwę raportu lub ENTER
4. Zobacz poprawnie wyświetlone oceny (bez prostokątów)
5. Raport automatycznie się otworzy

### 6.4 Test Przetwarzania Tekstu
1. Uruchom: `python main.py`
2. Wybierz opcję **6** (Demonstracja przetwarzania tekstu)
3. Zobacz jak system wydobywa informacje z opisów tras
4. Przykłady z updatelist.txt w akcji!

## 7. 🔍 ROZWIĄZYWANIE PROBLEMÓW

### 7.1 Częste Problemy i Rozwiązania

**Problem**: "Qt error" przy wykresach
**Rozwiązanie**: Dodano `matplotlib.use('Agg')` w chart_generator.py

**Problem**: Polskie znaki w PDF
**Rozwiązanie**: Używamy fontów Arial, Calibri, DejaVu Sans

**Problem**: Nieskończona pętla wag
**Rozwiązanie**: Naprawiono obsługę pustych wartości w weight_calculator.py

**Problem**: Brak danych pogodowych
**Rozwiązanie**: System używa weather_dataa.json z prawdziwymi danymi

### 7.2 Logi i Debugowanie
- Wszystkie błędy są logowane do konsoli
- ReviewAnalyzer loguje statystyki analizy
- System pokazuje postęp operacji
- Fallback na domyślne wartości przy błędach

## 8. 🚀 PRZYSZŁE ROZSZERZENIA (updatelist2.txt)

System jest przygotowany na **Etap 4: Integracja z Bazą Danych**:
- Migracja z CSV/JSON do SQLite
- Repozytoria danych (RouteRepository, WeatherRepository)
- Backup i restore bazy danych
- Nowe opcje menu administracyjnego

Wszystkie obecne funkcjonalności będą zachowane i rozszerzone o obsługę bazy danych.

