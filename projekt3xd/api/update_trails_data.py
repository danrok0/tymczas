import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.trails_api import TrailsAPI
from config import CITY_COORDINATES
import json

def update_trails_data():
    api = TrailsAPI()
    all_trails = []

    print("Pobieranie danych o szlakach dla wszystkich regionów...")
    
    for region in CITY_COORDINATES.keys():
        print(f"\nPobieranie szlaków dla regionu: {region}")
        try:
            trails = api.get_hiking_trails(region)
            all_trails.extend(trails)
            print(f"Znaleziono {len(trails)} szlaków dla {region}")
        except Exception as e:
            print(f"Błąd podczas pobierania szlaków dla {region}: {e}")

    print(f"\nŁącznie znaleziono {len(all_trails)} szlaków")

    # Save to trails_data.json
    try:
        with open('trails_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_trails, f, ensure_ascii=False, indent=2)
        print("Dane zostały zapisane do pliku trails_data.json")
    except Exception as e:
        print(f"Błąd podczas zapisywania danych: {e}")

if __name__ == "__main__":
    update_trails_data() 