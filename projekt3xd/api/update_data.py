import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.trails_api import TrailsAPI
from api.weather_api import WeatherAPI
from config import CITY_COORDINATES
import json
from datetime import datetime, timedelta

def update_trails_data():
    api = TrailsAPI()
    all_trails = []

    print("Pobieranie danych o szlakach dla wszystkich regionów...")
    
    for region in CITY_COORDINATES.keys():
        print(f"\nPobieranie szlaków dla regionu: {region}")
        try:
            trails = api.get_hiking_trails(region)
            if trails:
                all_trails.extend(trails)
                print(f"Znaleziono {len(trails)} szlaków dla {region}")
        except Exception as e:
            print(f"Błąd podczas pobierania szlaków dla {region}: {e}")

    print(f"\nŁącznie znaleziono {len(all_trails)} szlaków")

    # Initialize empty file if it doesn't exist
    if not os.path.exists('trails_data.json'):
        with open('trails_data.json', 'w', encoding='utf-8') as f:
            json.dump([], f)

    # Save to trails_data.json
    try:
        with open('trails_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_trails, f, ensure_ascii=False, indent=2)
        print("Dane o szlakach zostały zapisane do pliku trails_data.json")
    except Exception as e:
        print(f"Błąd podczas zapisywania danych o szlakach: {e}")

def update_weather_data():
    api = WeatherAPI()
    all_weather = []

    print("\nPobieranie danych pogodowych dla wszystkich regionów...")
    
    # Get weather for next 7 days for each region
    for region in CITY_COORDINATES.keys():
        print(f"\nPobieranie prognozy pogody dla regionu: {region}")
        try:
            for i in range(7):  # Get forecast for next 7 days
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                weather = api.get_weather_forecast(region, date)
                if weather:
                    all_weather.append(weather)
                    print(f"Pobrano prognozę dla {region} na {date}")
        except Exception as e:
            print(f"Błąd podczas pobierania prognozy pogody dla {region}: {e}")

    print(f"\nŁącznie pobrano {len(all_weather)} prognoz pogody")

    # Initialize empty file if it doesn't exist
    if not os.path.exists('weather_dataa.json'):
        with open('weather_dataa.json', 'w', encoding='utf-8') as f:
            json.dump([], f)

    # Save to weather_dataa.json
    try:
        with open('weather_dataa.json', 'w', encoding='utf-8') as f:
            json.dump(all_weather, f, ensure_ascii=False, indent=2)
        print("Dane pogodowe zostały zapisane do pliku weather_dataa.json")
    except Exception as e:
        print(f"Błąd podczas zapisywania danych pogodowych: {e}")

if __name__ == "__main__":
    update_trails_data()
    update_weather_data() 