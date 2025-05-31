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
  
## 2. System Wag i Obliczanie Wyników

### 2.1 Domyślne Wagi Kryteriów i Ich Działanie
System wykorzystuje następujący rozkład wag przy ocenie tras:

1. Długość trasy (30% wagi końcowej):
   - Bazowa waga: 0.3
   - Sposób obliczania:
     * Dla każdej trasy obliczana jest odległość od optymalnego zakresu (5-15 km)
     * Jeśli trasa mieści się w zakresie: 100 punktów
     * Za każdy km poniżej 5km: -5 punktów
     * Za każdy km powyżej 15km: -5 punktów
     * Przykład: trasa 18km = 100 - (18-15)*5 = 85 punktów
   - Lokalizacja: `utils/weight_calculator.py -> calculate_length_score()`

2. Trudność (25% wagi końcowej):
   - Bazowa waga: 0.25
   - Sposób obliczania:
     * Poziom 1 (łatwy) = 100 punktów
     * Poziom 2 (średni) = 66.66 punktów
     * Poziom 3 (trudny) = 33.33 punktów
     * Dodatkowe modyfikatory:
       - Przewyższenie > 500m: -10 punktów
       - Przewyższenie > 1000m: -20 punktów
   - Lokalizacja: `utils/weight_calculator.py -> calculate_difficulty_score()`

3. Warunki pogodowe (25% wagi końcowej):
   - Bazowa waga: 0.25
   - Wykorzystuje indeks komfortu (0-100)
   - Dodatkowe modyfikatory:
     * Deszczowy dzień: -30 punktów
     * Silny wiatr (>20 km/h): -20 punktów
   - Lokalizacja: `utils/weather_utils.py -> calculate_hiking_comfort()`

4. Typ terenu (20% wagi końcowej):
   - Bazowa waga: 0.2
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

## 3. Kategoryzacja Tras i Algorytmy Klasyfikacji

### 3.1 Automatyczna Kategoryzacja Tras
System automatycznie kategoryzuje trasy na podstawie zestawu kryteriów i wag:

1. Trasy Rodzinne (Algorytm klasyfikacji):
   - Podstawowe kryteria:
     * Trudność: poziom 1 (wymagane)
     * Długość: < 5 km (wymagane)
     * Przewyższenie: < 200m (wymagane)
   - Dodatkowe punkty:
     * Znaczniki: leisure (+10), park (+10), playground (+15), family (+15)
     * Nawierzchnia utwardzona: +10 punktów
     * Bliskość udogodnień: +5 punktów za każde
   - Wymagana minimalna liczba punktów: 40
   - Lokalizacja: `utils/trail_filter.py -> classify_family_trail()`

2. Trasy Widokowe (Algorytm klasyfikacji):
   - Podstawowe kryteria:
     * Długość: < 15 km (zalecane)
     * Minimum jeden punkt widokowy (wymagane)
   - System punktacji:
     * Każdy punkt widokowy: +20 punktów
     * Znaczniki: viewpoint (+15), scenic (+15), tourism (+10), panorama (+20)
     * Wysokość względna > 300m: +10 punktów
     * Lokalizacja w górach: +15 punktów
   - Wymagana minimalna liczba punktów: 50
   - Lokalizacja: `utils/trail_filter.py -> classify_scenic_trail()`
   
2. Trasy Widokowe:
   - Długość: < 15 km
   - Znaczniki: viewpoint, scenic, tourism, panorama
   
3. Trasy Sportowe:
   - Długość: 5-15 km
   - Trudność: poziom 2
   - Lub znaczniki: sport, aktywny, kondycyjny
   
4. Trasy Ekstremalne:
   - Trudność: poziom 3 lub
   - Długość: > 15 km lub
   - Przewyższenie: > 800m
   - Znaczniki: climbing, alpine, via_ferrata

## 4. Obliczanie Czasu Przejścia

### 4.1 Parametry Bazowe
- Bazowa prędkość marszu: 4 km/h

### 4.2 Modyfikatory Prędkości
1. Typ Terenu:
   - Góry: -1.0 km/h
   - Pagórki: -0.5 km/h
   - Las: -0.2 km/h
   - Mieszany: -0.3 km/h
   - Miejski: 0 km/h
   - Nadrzeczny: 0 km/h

2. Trudność:
   - Poziom 2: -0.5 km/h
   - Poziom 3: -1.0 km/h

3. Przewyższenie:
   - > 500m: -0.5 km/h
   - > 1000m: -1.0 km/h

### 4.3 Mnożniki Terenowe
Alternatywnie, przy obliczaniu czasu używane są mnożniki:
- Górski: 1.6
- Miejski: 0.8
- Leśny: 1.2
- Nizinny: 1.0
- Mieszany: 1.3
- Nadrzeczny: 1.1

## 5. Ocena Trudności Trasy

### 5.1 Komponenty Trudności
System ocenia trudność w skali 1-3 na podstawie:

1. Długości:
   - > 20 km: poziom 3
   - > 10 km: poziom 2
   - ≤ 10 km: poziom 1

2. Przewyższenia:
   - > 1000m: poziom 3
   - > 500m: poziom 2
   - ≤ 500m: poziom 1

3. Skali SAC:
   - alpine: poziom 3
   - mountain: poziom 2
   - inne: poziom 1

4. Powierzchni:
   - rock/scree: poziom 3
   - gravel/dirt: poziom 2
   - inne: poziom 1

5. Nachylenia:
   - > 15%: poziom 3
   - > 10%: poziom 2
   - ≤ 10%: poziom 1

## 6. Przewodnik po Funkcjonalnościach

### 6.1 Podstawowe Obliczenia

1. Obliczanie środka trasy:
   - Lokalizacja: `models/route.py -> Route.calculate_center()`
   - Opis: Oblicza geograficzny środek trasy na podstawie punktów trasy

2. Szacowanie czasu przejścia:
   - Lokalizacja: `utils/time_calculator.py -> TimeCalculator.estimate_time()`
   - Opis: Wykorzystuje system mnożników i modyfikatorów opisany w sekcji 4

3. Sprawdzanie dopasowania do preferencji:
   - Lokalizacja: `models/user_preference.py -> UserPreference.check_match()`
   - Opis: Porównuje parametry trasy z preferencjami użytkownika

### 6.2 Analiza Pogody

1. Sprawdzanie czy dzień jest słoneczny:
   - Lokalizacja: `utils/weather_utils.py -> WeatherUtils.is_sunny_day()`
   - Opis: Sprawdza zachmurzenie i godziny słoneczne

2. Sprawdzanie czy dzień jest deszczowy:
   - Lokalizacja: `utils/weather_utils.py -> WeatherUtils.is_rainy_day()`
   - Opis: Sprawdza poziom opadów

3. Obliczanie indeksu komfortu:
   - Lokalizacja: `utils/weather_utils.py -> WeatherUtils.calculate_hiking_comfort()`
   - Opis: Szczegółowy algorytm opisany w sekcji 1.1

### 6.3 Ocena i Zgodność

1. Obliczanie zgodności z trasą i pogodą:
   - Lokalizacja: `recommendation/trail_recommender.py -> TrailRecommender.calculate_match_score()`
   - Opis: Łączy oceny trasy, pogody i preferencji użytkownika

2. Aktualizacja preferencji:
   - Lokalizacja: `models/user_preference.py -> UserPreference.update()`
   - Opis: Aktualizuje preferencje na podstawie wyborów użytkownika

### 6.4 Operacje na Danych

1. Wczytywanie tras z plików:
   - Lokalizacja: `data_handlers/trail_data.py -> TrailDataHandler.load_trails()`
   - Opis: Parsuje i waliduje dane tras z różnych formatów

2. Filtrowanie tras wg kryteriów:
   - Lokalizacja: `utils/trail_filter.py -> TrailFilter.filter_trails()`
   - Opis: Implementuje wszystkie filtry opisane w dokumentacji

3. Zapisywanie wyników:
   - Lokalizacja: `utils/export_results.py -> ResultExporter`
   - Opis: Eksportuje wyniki do formatów TXT, JSON i CSV

### 6.5 Dane Pogodowe

1. Wczytywanie danych pogodowych:
   - Lokalizacja: `data_handlers/weather_data.py -> WeatherDataHandler.get_weather()`
   - Opis: Pobiera dane z API lub cache'u

2. Łączenie danych z lokalizacjami tras:
   - Lokalizacja: `recommendation/trail_recommender.py -> TrailRecommender.combine_trail_weather()`
   - Opis: Przypisuje dane pogodowe do tras

3. Statystyki pogodowe:
   - Lokalizacja: `utils/statistics.py -> WeatherStatistics`
   - Opis: Oblicza statystyki opisane w sekcji 5

### 6.6 Rekomendacje

1. Generowanie rekomendacji:
   - Lokalizacja: `recommendation/trail_recommender.py -> TrailRecommender.recommend_trails()`
   - Opis: Główny algorytm rekomendacji opisany w sekcji 2

2. Sortowanie tras:
   - Lokalizacja: `utils/trail_filter.py -> TrailFilter.sort_trails()`
   - Opis: Sortuje trasy według różnych kryteriów

### 6.7 Interfejs Użytkownika

1. Pobieranie preferencji:
   - Lokalizacja: `ui/user_interface.py -> UserInterface.get_preferences()`
   - Opis: Obsługuje wprowadzanie preferencji użytkownika

2. Wyświetlanie rekomendacji:
   - Lokalizacja: `ui/user_interface.py -> UserInterface.display_recommendations()`
   - Opis: Formatuje i wyświetla wyniki

3. Wizualizacje:
   - Lokalizacja: `ui/visualizer.py -> Visualizer`
   - Opis: Generuje wykresy i wizualizacje danych

