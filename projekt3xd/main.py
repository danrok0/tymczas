import os
import sys
import json
from datetime import datetime
from typing import List

# Dodaj katalog projektu do ścieżki Pythona
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from data_handlers.trail_data import TrailDataHandler
from data_handlers.weather_data import WeatherDataHandler
from utils.trail_filter import TrailFilter
from utils.storage import save_results_to_file
from config import CITY_COORDINATES
from recommendation.trail_recommender import TrailRecommender
from utils.weather_utils import WeatherUtils

def display_weather_stats(cities: List[str], date: str, weather_handler) -> None:
    """Wyświetla statystyki pogodowe dla wybranych miast."""
    print("\n=== Warunki pogodowe ===")
    print(f"Data: {date}\n")
    
    for city in cities:
        weather = weather_handler.get_weather_forecast(city, date)
        if not weather:
            print(f"{city}: Brak danych pogodowych")
            continue
            
        temp_min = weather.get('temperature_min', 0)
        temp_max = weather.get('temperature_max', 0)
        avg_temp = round((temp_min + temp_max) / 2, 1) if temp_min != 0 or temp_max != 0 else 'N/A'
        
        comfort_index = WeatherUtils.calculate_hiking_comfort(weather)
        weather_condition = WeatherUtils.get_weather_condition(weather)
        
        print(f"=== {city} ===")
        print(f"Temperatura średnia: {avg_temp}°C")
        print(f"Minimalna temperatura: {weather.get('temperature_min', 'N/A')}°C")
        print(f"Maksymalna temperatura: {weather.get('temperature_max', 'N/A')}°C")
        print(f"Opady: {weather.get('precipitation', 'N/A')} mm")
        print(f"Zachmurzenie: {weather.get('cloud_cover', 'N/A')}%")
        print(f"Godziny słoneczne: {weather.get('sunshine_hours', 0):.1f} h")
        print(f"Prędkość wiatru: {weather.get('wind_speed', 'N/A')} km/h")
        print(f"Stan pogody: {weather_condition}")
        print(f"Indeks komfortu: {comfort_index}/100")
        print()

def main():
    recommender = TrailRecommender()
    
    print("\n=== System rekomendacji szlaków turystycznych ===")
    print("Dostępne miasta: Gdańsk, Warszawa, Kraków, Wrocław")
    print("(Naciśnij ENTER, aby wybrać wszystkie miasta)")
    city = input("Wybierz miasto: ").strip()
    
    if not city:
        print("Wybrano wszystkie miasta")
        cities = list(CITY_COORDINATES.keys())
    elif city not in CITY_COORDINATES:
        print(f"Nieprawidłowe miasto. Wybierz jedno z: {', '.join(CITY_COORDINATES.keys())}")
        return
    else:
        cities = [city]

    # Choose data type
    print("\nWybierz typ danych pogodowych:")
    print("1. Dane historyczne (przeszłość)")
    print("2. Prognoza pogody (teraźniejszość i przyszłość)")
    data_type = input("Wybierz opcję (1 lub 2): ").strip()
    
    if data_type not in ["1", "2"]:
        print("Nieprawidłowy wybór. Wybierz 1 lub 2.")
        return

    # Get date input
    while True:
        date = input("\nPodaj datę (RRRR-MM-DD) lub wciśnij ENTER dla dzisiejszej daty: ").strip()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            break
        try:
            input_date = datetime.strptime(date, "%Y-%m-%d")
            today = datetime.now()
            
            if data_type == "1" and input_date.date() > today.date():
                print("Dla danych historycznych wybierz datę z przeszłości.")
                continue
            elif data_type == "2" and input_date.date() < today.date():
                print("Dla prognozy pogody wybierz datę dzisiejszą lub przyszłą.")
                continue
                
            break
        except ValueError:
            print("Nieprawidłowy format daty. Użyj formatu RRRR-MM-DD (np. 2024-03-20)")

    print("\nPodaj kryteria wyszukiwania (naciśnij ENTER, aby pominąć):")
    
    print("\nWybierz kategorię trasy:")
    print("1. Rodzinna (łatwe, krótkie trasy < 5km, małe przewyższenie < 200m)")
    print("2. Widokowa (trasy z punktami widokowymi i pięknymi krajobrazami)")
    print("3. Sportowa (trasy 5-15km, średnia trudność)")
    print("4. Ekstremalna (trudne trasy > 15km, duże przewyższenie > 800m)")
    print("(naciśnij ENTER, aby zobaczyć wszystkie kategorie)")
    category_choice = input("Wybierz kategorię (1-4): ")
    
    difficulty = input("\nPoziom trudności (1-3, gdzie: 1-łatwy, 2-średni, 3-trudny): ")
    terrain_type = input("Typ terenu (górski, nizinny, leśny, miejski): ")
    min_length = input("Minimalna długość trasy (km): ")
    max_length = input("Maksymalna długość trasy (km): ")
    min_sunshine = input("Minimalna liczba godzin słonecznych: ")
    max_precipitation = input("Maksymalne opady (mm): ")
    min_temperature = input("Minimalna temperatura (°C): ")
    max_temperature = input("Maksymalna temperatura (°C): ")
    
    # Konwersja parametrów
    difficulty = int(difficulty) if difficulty else None
    terrain_type = terrain_type.lower() if terrain_type else None
    min_length = float(min_length) if min_length else None
    max_length = float(max_length) if max_length else None
    min_sunshine = float(min_sunshine) if min_sunshine else None
    max_precipitation = float(max_precipitation) if max_precipitation else None
    min_temperature = float(min_temperature) if min_temperature else None
    max_temperature = float(max_temperature) if max_temperature else None
    
    # Konwersja wyboru kategorii
    category_map = {
        "1": "rodzinna",
        "2": "widokowa",
        "3": "sportowa",
        "4": "ekstremalna"
    }
    chosen_category = category_map.get(category_choice) if category_choice else None

    # Słowniki na rekomendacje i dane pogodowe dla każdego miasta
    trails_by_city = {}
    weather_by_city = {}
    
    # Pobierz rekomendacje dla każdego wybranego miasta
    total_trails = 0
    for current_city in cities:
        print(f"\nPobieranie rekomendacji dla miasta {current_city}...")
        trails = recommender.recommend_trails(
            city=current_city,
            date=date,
            difficulty=difficulty,
            terrain_type=terrain_type,
            min_length=min_length,
            max_length=max_length,
            min_sunshine=min_sunshine,
            max_precipitation=max_precipitation,
            min_temperature=min_temperature,
            max_temperature=max_temperature,
            category=chosen_category
        )
        if trails:
            trails_by_city[current_city] = trails
            total_trails += len(trails)
            # Pobierz dane pogodowe dla miasta
            weather = recommender.data_handler.weather_api.get_weather_forecast(current_city, date)
            if weather:
                weather_by_city[current_city] = weather

    # Wyświetl statystyki pogodowe przed trasami
    display_weather_stats(cities, date, recommender.data_handler.weather_api)

    # Wyświetl wszystkie znalezione trasy
    if total_trails == 0:
        print("\nNie znaleziono tras spełniających podane kryteria.")
        return

    print(f"\nŁącznie znaleziono {total_trails} tras spełniających kryteria.")

    # Eksportuj wyniki do różnych formatów
    from utils.export_results import ResultExporter
    ResultExporter.export_results(trails_by_city=trails_by_city, 
                                date=date, 
                                weather_by_city=weather_by_city)

    # Wyświetl wszystkie znalezione trasy
    for city, trails in trails_by_city.items():
        print(f"\n=== Trasy w mieście {city} ===")
        for i, trail in enumerate(trails, 1):
            print(f"\n{i}. {trail['name']}")
            print(f"   Miasto: {trail.get('region', city)}")
            print(f"   Długość: {trail['length_km']:.1f} km")
            print(f"   Poziom trudności: {trail['difficulty']}/3")
            print(f"   Typ terenu: {trail['terrain_type']}")
            print(f"   Kategoria trasy: {trail.get('category', 'nieskategoryzowana').upper()}")
            if 'comfort_index' in trail:
                print(f"   Indeks komfortu wędrówki: {trail['comfort_index']:.1f}/100")
            if trail.get('sunshine_hours'):
                print(f"   Godziny słoneczne: {trail.get('sunshine_hours', 0):.2f} h")
            if 'description' in trail:
                print(f"   Opis: {trail['description']}")
            if 'weighted_score' in trail:
                print(f"   Wynik ważony: {trail['weighted_score']:.2f}/100")
            # Wyświetl szacowany czas przejścia
            if 'estimated_time' in trail:
                hours = int(trail['estimated_time'])
                minutes = int((trail['estimated_time'] - hours) * 60)
                if hours > 0 and minutes > 0:
                    print(f"   Szacowany czas przejścia: {hours}h {minutes}min")
                elif hours > 0:
                    print(f"   Szacowany czas przejścia: {hours}h")
                else:
                    print(f"   Szacowany czas przejścia: {minutes}min")
            print(f"   ---")

    # Analizuj najlepsze okresy dla każdej trasy
    print("\n=== Analiza najlepszych okresów dla szlaków ===")
    for city, trails in trails_by_city.items():
        weather_data = {}
        try:
            # Próbujemy pobrać dane z weather_dataa.json dla miasta
            with open('api/weather_dataa.json', 'r', encoding='utf-8') as f:
                all_weather_data = json.load(f)
                # Filtrujemy dane tylko dla danego miasta
                weather_data = {entry['date']: entry 
                             for entry in all_weather_data 
                             if entry['region'] == city}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Nie udało się wczytać danych pogodowych: {e}")
            weather_data = {}

        for trail in trails:
            trail_name = trail.get('name', 'Nieznany szlak')
            trail_type = trail.get('terrain_type', 'nizinny')
            comfort_index = trail.get('comfort_index', 0)
            
            print(f"\nTrasa: {trail_name} ({city})")
            print(f"Typ terenu: {trail_type}")
            print(f"Aktualny indeks komfortu: {comfort_index}/100")
        
            # Pobierz analizę najlepszych okresów
            best_periods = WeatherUtils.analyze_best_periods(weather_data, trail_type)
            
            # Wyświetl najlepsze daty
            if best_periods["best_dates"]:
                print("\nNajlepsze daty dla tej trasy (najwyższy indeks komfortu):")
                for date_str in best_periods["best_dates"]:
                    try:
                        # Konwertuj datę na format polski
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        pl_date = date_obj.strftime("%d %B %Y")
                        weather = weather_data.get(date_str, {})
                        temp = weather.get('temperature', 'N/A')
                        precip = weather.get('precipitation', 'N/A')
                        sun = weather.get('sunshine_hours', 'N/A')
                        print(f"- {pl_date}:")
                        print(f"  Temperatura: {temp}°C")
                        print(f"  Opady: {precip} mm")
                        print(f"  Godziny słoneczne: {sun} h")
                    except ValueError:
                        print(f"- {date_str}")
                print(f"\nŚredni indeks komfortu: {best_periods['average_comfort']:.1f}/100")
                
                # Wyświetl rekomendacje sezonowe
                print("\nAnaliza sezonowa:")
                for season, score in best_periods["season_scores"].items():
                    print(f"- {season}: {score:.1f}/100")
                
                if best_periods["recommendations"]:
                    print(f"\nRekomendacje: {best_periods['recommendations']}")
            else:
                print("\nBrak wystarczających danych do analizy najlepszych okresów.")

if __name__ == "__main__":
    main()