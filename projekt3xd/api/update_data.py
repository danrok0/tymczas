"""
SKRYPT KOMPLEKSOWEJ AKTUALIZACJI DANYCH SYSTEMU
==============================================

Ten skrypt służy do pobierania i aktualizacji wszystkich danych zewnętrznych
używanych przez system rekomendacji tras turystycznych.

FUNKCJONALNOŚĆ:
- Pobiera dane o szlakach turystycznych dla wszystkich regionów
- Pobiera prognozy pogody na najbliższe 7 dni dla wszystkich miast
- Zapisuje dane do odpowiednich plików JSON (cache)
- Obsługuje błędy pobierania dla poszczególnych regionów/dat
- Inicjalizuje puste pliki jeśli nie istnieją

AKTUALIZOWANE DANE:
1. trails_data.json - dane o szlakach turystycznych
2. weather_dataa.json - prognozy pogody na 7 dni

UŻYCIE:
python api/update_data.py

WYMAGANIA:
- Działające połączenie internetowe
- Dostęp do Overpass API i Open-Meteo API
- Uprawnienia do zapisu w katalogu głównym projektu

AUTOR: System Rekomendacji Tras Turystycznych - Etap 4
"""

# ============================================================================
# KONFIGURACJA ŚCIEŻEK I IMPORTÓW
# ============================================================================

# Dodanie katalogu głównego projektu do ścieżki Python
# Umożliwia import modułów z katalogu nadrzędnego
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# IMPORTY MODUŁÓW PROJEKTU
# ============================================================================

from api.trails_api import TrailsAPI         # Klasa do pobierania danych o szlakach
from api.weather_api import WeatherAPI       # Klasa do pobierania danych pogodowych
from config import CITY_COORDINATES         # Słownik miast i ich współrzędnych
import json                                 # Obsługa formatu JSON
from datetime import datetime, timedelta    # Operacje na datach

# ============================================================================
# FUNKCJA AKTUALIZACJI DANYCH O SZLAKACH
# ============================================================================

def update_trails_data():
    """
    Pobiera i aktualizuje dane o szlakach turystycznych dla wszystkich regionów.
    
    Funkcja iteruje przez wszystkie miasta zdefiniowane w CITY_COORDINATES,
    pobiera dla każdego z nich dane o szlakach używając TrailsAPI,
    a następnie zapisuje zagregowane dane do pliku trails_data.json.
    
    Proces:
    1. Inicjalizacja API i pustej listy na wszystkie szlaki
    2. Iteracja przez wszystkie regiony z CITY_COORDINATES
    3. Pobieranie szlaków dla każdego regionu (z obsługą błędów)
    4. Agregacja wszystkich szlaków w jedną listę
    5. Zapis do pliku trails_data.json
    
    Obsługa błędów:
    - Błędy pobierania dla poszczególnych regionów nie przerywają procesu
    - Wszystkie błędy są logowane z informacją o regionie
    - Proces kontynuuje dla pozostałych regionów
    
    Returns:
        None: Funkcja zapisuje dane do pliku, nie zwraca wartości
    """
    # Inicjalizacja API do pobierania danych o szlakach
    api = TrailsAPI()
    
    # Lista na wszystkie szlaki ze wszystkich regionów
    all_trails = []

    print("Pobieranie danych o szlakach dla wszystkich regionów...")
    
    # ========================================================================
    # ITERACJA PRZEZ WSZYSTKIE REGIONY
    # ========================================================================
    
    # Pobieranie szlaków dla każdego miasta z konfiguracji
    for region in CITY_COORDINATES.keys():
        print(f"\nPobieranie szlaków dla regionu: {region}")
        
        try:
            # Próba pobrania szlaków dla danego regionu
            trails = api.get_hiking_trails(region)
            
            # Sprawdzenie czy pobrano jakieś dane
            if trails:
                # Dodanie pobranych szlaków do głównej listy
                all_trails.extend(trails)
                print(f"Znaleziono {len(trails)} szlaków dla {region}")
            else:
                print(f"Brak szlaków dla regionu {region}")
                
        except Exception as e:
            # Obsługa błędów - logowanie i kontynuacja
            print(f"Błąd podczas pobierania szlaków dla {region}: {e}")

    # ========================================================================
    # PODSUMOWANIE I ZAPIS DANYCH O SZLAKACH
    # ========================================================================
    
    print(f"\nŁącznie znaleziono {len(all_trails)} szlaków")

    # Inicjalizacja pustego pliku jeśli nie istnieje
    if not os.path.exists('trails_data.json'):
        with open('trails_data.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("Utworzono pusty plik trails_data.json")

    # Zapis wszystkich danych o szlakach do pliku JSON
    try:
        with open('trails_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_trails, f, ensure_ascii=False, indent=2)
        print("Dane o szlakach zostały zapisane do pliku trails_data.json")
        
    except Exception as e:
        print(f"Błąd podczas zapisywania danych o szlakach: {e}")

# ============================================================================
# FUNKCJA AKTUALIZACJI DANYCH POGODOWYCH
# ============================================================================

def update_weather_data():
    """
    Pobiera i aktualizuje prognozy pogody dla wszystkich regionów na najbliższe 7 dni.
    
    Funkcja iteruje przez wszystkie miasta zdefiniowane w CITY_COORDINATES,
    pobiera dla każdego z nich prognozy pogody na następne 7 dni używając WeatherAPI,
    a następnie zapisuje zagregowane dane do pliku weather_dataa.json.
    
    Proces:
    1. Inicjalizacja API i pustej listy na wszystkie prognozy
    2. Iteracja przez wszystkie regiony z CITY_COORDINATES
    3. Dla każdego regionu pobieranie prognoz na 7 dni (z obsługą błędów)
    4. Agregacja wszystkich prognoz w jedną listę
    5. Zapis do pliku weather_dataa.json
    
    Zakres dat:
    - Pobiera prognozy od dzisiaj do 6 dni w przyszłość (łącznie 7 dni)
    - Każda prognoza zawiera datę, region i parametry pogodowe
    
    Obsługa błędów:
    - Błędy pobierania dla poszczególnych regionów/dat nie przerywają procesu
    - Wszystkie błędy są logowane z informacją o regionie
    - Proces kontynuuje dla pozostałych regionów i dat
    
    Returns:
        None: Funkcja zapisuje dane do pliku, nie zwraca wartości
    """
    # Inicjalizacja API do pobierania danych pogodowych
    api = WeatherAPI()
    
    # Lista na wszystkie prognozy pogody ze wszystkich regionów
    all_weather = []

    print("\nPobieranie danych pogodowych dla wszystkich regionów...")
    
    # ========================================================================
    # ITERACJA PRZEZ WSZYSTKIE REGIONY I DATY
    # ========================================================================
    
    # Pobieranie prognoz pogody dla każdego miasta z konfiguracji
    for region in CITY_COORDINATES.keys():
        print(f"\nPobieranie prognozy pogody dla regionu: {region}")
        
        try:
            # Pobieranie prognoz na najbliższe 7 dni (0-6 dni od dzisiaj)
            for i in range(7):  # Get forecast for next 7 days
                # Obliczenie daty (dzisiaj + i dni)
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                
                # Próba pobrania prognozy dla danej daty
                weather = api.get_weather_forecast(region, date)
                
                # Sprawdzenie czy pobrano dane pogodowe
                if weather:
                    # Dodanie prognozy do głównej listy
                    all_weather.append(weather)
                    print(f"Pobrano prognozę dla {region} na {date}")
                else:
                    print(f"Brak prognozy dla {region} na {date}")
                    
        except Exception as e:
            # Obsługa błędów - logowanie i kontynuacja
            print(f"Błąd podczas pobierania prognozy pogody dla {region}: {e}")

    # ========================================================================
    # PODSUMOWANIE I ZAPIS DANYCH POGODOWYCH
    # ========================================================================
    
    print(f"\nŁącznie pobrano {len(all_weather)} prognoz pogody")

    # Inicjalizacja pustego pliku jeśli nie istnieje
    if not os.path.exists('weather_dataa.json'):
        with open('weather_dataa.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("Utworzono pusty plik weather_dataa.json")

    # Zapis wszystkich danych pogodowych do pliku JSON
    try:
        with open('weather_dataa.json', 'w', encoding='utf-8') as f:
            json.dump(all_weather, f, ensure_ascii=False, indent=2)
        print("Dane pogodowe zostały zapisane do pliku weather_dataa.json")
        
    except Exception as e:
        print(f"Błąd podczas zapisywania danych pogodowych: {e}")

# ============================================================================
# PUNKT WEJŚCIA SKRYPTU
# ============================================================================

if __name__ == "__main__":
    """
    Punkt wejścia skryptu - wykonuje kompleksową aktualizację danych.
    
    Sprawdza czy skrypt jest uruchamiany jako główny program (nie importowany)
    i jeśli tak, wywołuje obie funkcje aktualizacji:
    1. update_trails_data() - aktualizacja danych o szlakach
    2. update_weather_data() - aktualizacja prognoz pogody
    
    Kolejność wykonania jest ważna - najpierw szlaki, potem pogoda.
    """
    print("=== ROZPOCZĘCIE KOMPLEKSOWEJ AKTUALIZACJI DANYCH ===")
    print("1. Aktualizacja danych o szlakach turystycznych")
    update_trails_data()
    
    print("\n" + "="*60)
    print("2. Aktualizacja prognoz pogody")
    update_weather_data()
    
    print("\n" + "="*60)
    print("=== ZAKOŃCZENIE AKTUALIZACJI DANYCH ===")
    print("Wszystkie dane zostały zaktualizowane!") 